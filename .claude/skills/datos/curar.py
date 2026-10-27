"""Curación de datos de precios · skill datos (cueva TIS).

Lee un CSV crudo de cualquier fuente, lo deja en un formato único y revisa su calidad.
No inventa precios: elimina lo imposible, marca lo dudoso y reporta los huecos.

Uso:
  python .claude/skills/datos/curar.py datos/crudos/btc-usd_1h_yahoo.csv \
      --mercado cripto --temporalidad 1h --zona UTC \
      --salida datos/btc-usd_1h_yahoo.csv \
      --informe resultados/btc-usd_1h_yahoo_calidad.md

El calendario NO se supone: se aprende del propio archivo. El script mira en qué días y a qué horas
suele haber velas (en al menos la mitad de las semanas) y solo cuenta como hueco lo que falta dentro
de ese horario. Así respeta las pausas diarias (oro, índices CFD, petróleo), los fines de semana y el
24/7 de cripto. Los días enteros sin sesión (festivos, cierres) se informan aparte como aviso.
--mercado es opcional e informativo (cripto, forex, bolsa, cfd...).
--zona: zona horaria de las fechas del CSV crudo si vienen sin zona (UTC, America/New_York, EST...).
Salida: fecha (UTC, ISO), open, high, low, close, volume. Volumen vacío si la fuente no lo trae.
"""
import argparse, sys
try:
    sys.stdout.reconfigure(encoding='utf-8')   # Windows: que los acentos no rompan la consola
except Exception:
    pass
import numpy as np
import pandas as pd

ALIAS = {
    'fecha': ['fecha', 'date', 'datetime', 'time', 'timestamp', 'gmt time', 'local time', 'data'],
    'open': ['open', 'apertura', 'abertura', 'o'],
    'high': ['high', 'maximo', 'máximo', 'max', 'h'],
    'low': ['low', 'minimo', 'mínimo', 'min', 'l'],
    'close': ['close', 'cierre', 'fechamento', 'c', 'adj close', 'último', 'ultimo', 'price', 'precio', 'last'],
    'volume': ['volume', 'volumen', 'vol', 'vol.', 'v', 'tick volume', 'tickvol', 'real volume'],
}
PASO = {'1m': '1min', '5m': '5min', '15m': '15min', '30m': '30min', '1h': '1h', '4h': '4h', '1d': '1D'}
MIN_ANIOS_APTA, MIN_ANIOS = 3.0, 1.0      # provisional: menos de 1 año = NO APTA; de 1 a 3 = aviso
MAX_ELIMINADAS, MAX_HUECOS = 0.05, 0.05    # provisional: más del 5 % = NO APTA


def numero(serie):
    """Convierte precios escritos de cualquier forma: 2.345,67 · 2,345.67 · 1,23K · 4.5M."""
    t = serie.astype(str).str.strip().str.replace('\u00a0', '', regex=False).str.replace(' ', '', regex=False)
    mult = pd.Series(1.0, index=t.index)
    for suf, m in (('K', 1e3), ('M', 1e6), ('B', 1e9)):
        es = t.str.upper().str.endswith(suf)
        mult[es] = m
        t = t.where(~es, t.str[:-1])
    coma_dec = t.str.fullmatch(r'-?[\d.]*,\d+')          # 2.345,67 o 0,5
    t = t.where(~coma_dec, t.str.replace('.', '', regex=False).str.replace(',', '.', regex=False))
    t = t.str.replace(',', '', regex=False)                 # 2,345.67
    return pd.to_numeric(t.str.replace('%', '', regex=False), errors='coerce') * mult


def leer(ruta):
    df = pd.read_csv(ruta, sep=None, engine='python')
    if len(df.columns) in (5, 6) and not any(str(c).strip().lower() in ALIAS['fecha'] for c in df.columns):
        df = pd.read_csv(ruta, sep=None, engine='python', header=None)   # sin encabezado (HistData)
        df.columns = ['fecha', 'open', 'high', 'low', 'close', 'volume'][:len(df.columns)]
    df.columns = [str(c).strip().strip('<>').strip() for c in df.columns]   # MetaTrader: <DATE>, <OPEN>...
    low = {c.lower(): c for c in df.columns}
    if 'date' in low and 'time' in low:                   # fecha y hora en columnas separadas
        df['fecha'] = df[low['date']].astype(str) + ' ' + df[low['time']].astype(str)
        df = df.drop(columns=[low['date'], low['time']])
    cols = {}
    for c in df.columns:
        n = str(c).strip().lower()
        for k, alias in ALIAS.items():
            if n in alias and k not in cols.values():
                cols[c] = k
                break
    df = df.rename(columns=cols)
    falta = [k for k in ('fecha', 'open', 'high', 'low', 'close') if k not in df.columns]
    if falta:
        sys.exit(f'No encuentro las columnas {falta}. Columnas del archivo: {list(df.columns)}')
    if 'volume' not in df.columns:
        df['volume'] = np.nan
    return df[['fecha', 'open', 'high', 'low', 'close', 'volume']]


def a_utc(serie, zona):
    t = serie.astype(str).str.strip()
    if t.str.fullmatch(r'\d{8} \d{6}').all():
        f = pd.to_datetime(t, format='%Y%m%d %H%M%S', errors='coerce')
    elif t.str.fullmatch(r'\d{10,13}').all():
        f = pd.to_datetime(t.astype('int64'), unit='ms' if t.str.len().max() > 10 else 's', utc=True)
    else:
        # día primero si algún primer número pasa de 12 (31/01/2024, 26.10.2026)
        pri = t.str.extract(r'^(\d{1,2})[/.\-]\d{1,2}[/.\-]\d{2,4}')[0].dropna().astype(int)
        f = pd.to_datetime(t, errors='coerce', format='mixed', dayfirst=bool(len(pri) and (pri > 12).any()))
    if getattr(f.dt, 'tz', None) is None:
        if zona.upper() == 'EST':   # hora de Nueva York sin cambio de verano (HistData)
            f = f + pd.Timedelta(hours=5)
            return f.dt.tz_localize('UTC')
        return f.dt.tz_localize(zona, ambiguous='NaT', nonexistent='NaT').dt.tz_convert('UTC')
    return f.dt.tz_convert('UTC')


def calendario(fechas, temporalidad):
    """Aprende el horario del activo a partir de sus propias velas.
    Devuelve (faltan_reales, dias_sin_sesion, n_esperadas, descripción del horario)."""
    f = pd.DatetimeIndex(fechas)
    cripto = (f.dayofweek >= 5).mean() > 0.2           # muchas velas en fin de semana: 24/7
    loc = f.tz_convert('UTC' if cripto else 'America/New_York')
    semanas = max(1, loc.tz_localize(None).to_period('W').nunique())
    if temporalidad == '1d':
        # vela diaria: su fecha es el día de sesión, tal como viene (sin cambiar de zona)
        dias = pd.DatetimeIndex(f.tz_convert('UTC').normalize().tz_localize(None).unique())
        normales = {d for d in range(7) if (dias.dayofweek == d).sum() >= 0.5 * semanas}
        exp = pd.date_range(dias.min(), dias.max(), freq='D')
        exp = exp[exp.dayofweek.isin(list(normales))]
        faltan = exp.difference(dias)
        # un día suelto que falta = festivo o cierre; 3 o más seguidos = hueco real
        s = pd.Series(1, index=faltan).reindex(exp, fill_value=0)
        grupo = (s != s.shift()).cumsum()
        largo = s.groupby(grupo).transform('sum') * s
        reales = faltan[(largo.loc[faltan] >= 3).values] if len(faltan) else faltan
        festivos = faltan.difference(reales)
        txt = 'días con sesión: ' + ', '.join('lun mar mié jue vie sáb dom'.split()[d] for d in sorted(normales))
        return reales, festivos, len(exp), txt
    paso = PASO[temporalidad]
    slot = loc.dayofweek * 1440 + loc.hour * 60 + loc.minute
    cuenta = pd.Series(slot).value_counts()
    normales = set(cuenta[cuenta >= 0.5 * semanas].index)
    tz = 'UTC' if cripto else 'America/New_York'
    rango = pd.date_range(f.min(), f.max(), freq=paso, tz='UTC')
    rl = rango.tz_convert(tz)
    exp = rango[pd.Index(rl.dayofweek * 1440 + rl.hour * 60 + rl.minute).isin(normales)]
    faltan = exp.difference(f)
    if len(faltan):
        dia_f = pd.Series(faltan.tz_convert(tz).normalize().tz_localize(None))
        dia_e = pd.Series(exp.tz_convert(tz).normalize().tz_localize(None)).value_counts().sort_index()
        por_dia = dia_f.value_counts()
        enteros = por_dia[por_dia >= dia_e.reindex(por_dia.index).values].index
        # día entero suelto = festivo o cierre; 3 o más días con sesión seguidos sin datos = hueco real
        s = pd.Series(dia_e.index.isin(enteros).astype(int), index=dia_e.index)
        grupo = (s != s.shift()).cumsum()
        largo = s.groupby(grupo).transform('sum') * s
        fest = set(largo[(largo > 0) & (largo < 3)].index)
        es_fest = dia_f.isin(fest).values
        festivos = pd.DatetimeIndex(sorted(fest))
        reales = faltan[~es_fest]
        n_exp = len(exp) - int(es_fest.sum())
    else:
        reales, festivos, n_exp = faltan, pd.DatetimeIndex([]), len(exp)
    horas = sorted({(x % 1440) // 60 for x in normales})
    txt = '24/7' if cripto and len(horas) == 24 else f'{len(horas)} de 24 horas con sesión (hora de {"UTC" if cripto else "Nueva York"})'
    return reales, festivos, n_exp, txt


def main():
    a = argparse.ArgumentParser()
    a.add_argument('crudo')
    a.add_argument('--mercado', default='auto', help='opcional e informativo: el calendario se aprende de los datos')
    a.add_argument('--temporalidad', required=True, choices=list(PASO))
    a.add_argument('--zona', default='UTC')
    a.add_argument('--salida', required=True)
    a.add_argument('--informe', required=True)
    o = a.parse_args()

    df = leer(o.crudo)
    n0 = len(df)
    df['fecha'] = a_utc(df['fecha'], o.zona)
    for c in ('open', 'high', 'low', 'close', 'volume'):
        df[c] = numero(df[c])

    sin_fecha = int(df['fecha'].isna().sum())
    df = df.dropna(subset=['fecha']).sort_values('fecha')

    dup_iguales = int(df.duplicated().sum())
    df = df.drop_duplicates()
    dup_distintas = int(df.duplicated('fecha').sum())
    df = df.drop_duplicates('fecha', keep='first')

    p = df[['open', 'high', 'low', 'close']]
    imposibles = (p.isna().any(axis=1) | (p <= 0).any(axis=1)
                  | (df['high'] < p[['open', 'close']].max(axis=1))
                  | (df['low'] > p[['open', 'close']].min(axis=1)))
    n_imp = int(imposibles.sum())
    df = df[~imposibles]

    # saltos raros: retorno muy lejos de lo normal (8 veces la desviación robusta). Se marcan, no se borran.
    r = np.log(df['close']).diff()
    mad = (r - r.median()).abs().median() * 1.4826
    saltos = df.loc[(r - r.median()).abs() > 8 * mad, 'fecha'] if mad > 0 else df['fecha'].iloc[:0]

    faltan, festivos, n_esp, horario = calendario(df['fecha'], o.temporalidad)
    p_huecos = len(faltan) / n_esp if n_esp else 0

    vol = df['volume']
    sin_vol = bool(vol.isna().all())
    vol_cero = float((vol == 0).mean()) if not sin_vol else 0.0

    anios = (df['fecha'].max() - df['fecha'].min()).days / 365.25 if len(df) else 0
    eliminadas = (n0 - len(df)) / n0 if n0 else 0
    avisos = []
    if sin_fecha: avisos.append(f'{sin_fecha} filas con fecha ilegible, eliminadas.')
    if dup_iguales: avisos.append(f'{dup_iguales} velas repetidas exactas, eliminadas.')
    if dup_distintas: avisos.append(f'{dup_distintas} velas con la misma fecha y precios distintos: se dejó la primera.')
    if n_imp: avisos.append(f'{n_imp} velas imposibles (precio vacío, cero o máximo/mínimo incoherente), eliminadas.')
    if len(saltos): avisos.append(f'{len(saltos)} saltos fuera de lo normal: revísalos en el gráfico (pueden ser reales).')
    if len(faltan): avisos.append(f'{len(faltan)} velas faltantes dentro del horario del activo ({p_huecos:.1%}). No se rellenaron.')
    if sin_vol: avisos.append('La fuente no trae volumen: la columna queda vacía. No uses reglas de volumen.')
    elif vol_cero > 0.2: avisos.append(f'{vol_cero:.0%} de las velas con volumen 0: no uses reglas de volumen.')
    if anios < MIN_ANIOS_APTA: avisos.append(f'Solo {anios:.1f} años de historia: el 30 % fuera de muestra queda corto.')

    if eliminadas > MAX_ELIMINADAS or p_huecos > MAX_HUECOS or anios < MIN_ANIOS or len(df) < 100:
        veredicto = 'NO APTA'
    elif avisos:
        veredicto = 'APTA CON AVISOS'
    else:
        veredicto = 'APTA'

    out = df.copy()
    out['fecha'] = out['fecha'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    out.to_csv(o.salida, index=False)

    L = [f'# Calidad de datos · {o.salida}', '',
         f'Veredicto: **{veredicto}** para backtest', '',
         f'- Origen: {o.crudo} · temporalidad {o.temporalidad} · zona original {o.zona}',
         f'- Desde {df["fecha"].min():%Y-%m-%d %H:%M} hasta {df["fecha"].max():%Y-%m-%d %H:%M} UTC · {anios:.1f} años',
         f'- Velas: {n0} en el crudo → {len(df)} curadas ({eliminadas:.1%} eliminadas)',
         f'- Horario aprendido de los datos: {horario}',
         f'- Velas faltantes dentro del horario: {len(faltan)} ({p_huecos:.1%})',
         f'- Días sin sesión (festivos o cierres, normal: no cuentan como hueco): {len(festivos)}',
         f'- Volumen: {"no viene" if sin_vol else f"{vol_cero:.0%} en cero"}', '',
         '## Avisos'] + ([f'- {x}' for x in avisos] or ['- Ninguno.'])
    if len(saltos):
        L += ['', '## Saltos para revisar (primeros 10)'] + [f'- {f:%Y-%m-%d %H:%M} UTC' for f in list(saltos)[:10]]
    if len(faltan):
        L += ['', '## Velas faltantes (primeras 10)'] + [f'- {pd.Timestamp(f):%Y-%m-%d %H:%M}' for f in list(faltan)[:10]]
    if len(festivos):
        L += ['', '## Días sin sesión (primeros 10)'] + [f'- {pd.Timestamp(f):%Y-%m-%d}' for f in list(festivos)[:10]]
    L += ['', 'Umbrales provisionales del Reto: NO APTA si se eliminó más del 5 %, faltan más del 5 % de las velas dentro del horario del activo,',
          'hay menos de 1 año o menos de 100 velas. Datos gratuitos: buenos para investigar, no iguales a datos de pago.']
    open(o.informe, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
