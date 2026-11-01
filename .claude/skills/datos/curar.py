"""Curación de datos de precios · skill datos (cueva TIS).

Lee un CSV crudo de cualquier fuente, lo deja en un formato único y revisa su calidad.
No inventa precios: elimina lo imposible, marca lo dudoso y reporta los huecos.

Uso:
  python .claude/skills/datos/curar.py datos/crudos/btc-usd_1h_yahoo.csv \
      --mercado cripto --temporalidad 1h --zona UTC \
      --salida datos/btc-usd_1h_yahoo.csv \
      --informe resultados/btc-usd_1h_yahoo_calidad.md

--mercado (horario en hora de Nueva York):
  cripto  · 24/7, sin feriados
  forex   · domingo 17:00 a viernes 17:00 · cierra 25-dic y 1-ene (24-dic y 31-dic, cierre anticipado)
  metales · oro y plata: domingo 18:00 a viernes 17:00, pausa diaria 17:00-18:00 · feriados de EE. UU.
  indices · índices de EE. UU. CFD o futuros (NAS100, US500, US30...): mismo horario que metales
  bolsa   · acciones y ETF: lunes a viernes · feriados de la bolsa de Nueva York
  sesion  · cualquier otro horario (GER40, petróleo, un bróker con horario propio...): aprende de los
            propios datos qué horas de la semana opera (las que tienen datos en al menos el 75 % de
            las semanas) y cuenta como faltante solo lo que falta dentro de ese horario.
            --zona-sesion auto (por defecto): prueba las zonas habituales y usa la que mejor encaja.
            Perdona un feriado de EE. UU. o de Europa solo si ese día de verdad cerró o cerró antes.
            En diario (--temporalidad 1d) aprende qué días de la semana opera y cuenta los días sin datos.
--zona: zona horaria de las fechas del CSV crudo si vienen sin zona (UTC, America/New_York, EST...).
--hasta AAAA-MM-DD (opcional): la fecha final que pediste al descargar. Si los datos terminan más de
  5 días antes, la descarga quedó incompleta: NO APTA.
--forzar: si --salida ya existe y lo nuevo cubre menos fechas, lo sobrescribe igual. Sin --forzar, lo
  nuevo se guarda aparte en <salida>_nuevo.csv (y su informe en <informe>_nuevo.md) y sale con código 3.
Salida: fecha (UTC, ISO), open, high, low, close, volume. Volumen vacío si la fuente no lo trae.
Columnas: las reconoce por su nombre, en inglés o en español, con o sin tildes (fecha/date/día, open/apertura/
  abre, high/máximo/alto, low/mínimo/bajo, close/cierre/último/price, volume/volumen/vol/tickvol). Nunca por
  su posición si el archivo trae encabezado: si no las reconoce, NO APTA y dice cómo renombrarlas. Solo sin
  encabezado (la primera fila ya es una vela, como en HistData) usa el orden fecha, open, high, low, close, volume.
Acepta separador coma, punto y coma o tabulador, y coma decimal (Excel en español).
Export de MetaTrader 5: <DATE> y <TIME> separados (se unen), fechas 2024.01.02, y si <VOL> es todo cero
  usa <TICKVOL> como volumen.
Las velas que faltan en horas de mercado cerrado no cuentan como huecos. En un feriado o un día de cierre
anticipado no cuenta ninguna (cada bróker cierra a una hora distinta): el informe dice cuántas fueron.
Las filas repetidas exactas (un export pegado dos veces) se eliminan y se avisan, pero no cuentan para el
5 % de eliminadas. La misma fecha con precios distintos sí cuenta.
Si hay más de 10 saltos raros, la lista completa queda en <informe>_saltos.md (con _calidad cambiado por _saltos).
Si el resultado es NO APTA (no se puede curar o no pasa los umbrales), escribe solo el informe, no guarda
ningún CSV (el crudo sigue en su carpeta: no se pierde nada) y sale con código 1. Así en datos/ solo quedan
CSV que sirven para un backtest. Si --salida ya existía, no se toca: el informe va a <informe>_nuevo.md.
"""
import argparse, os, re, sys, unicodedata
from datetime import datetime
import numpy as np
import pandas as pd
from pandas.tseries.holiday import (AbstractHolidayCalendar, Holiday, EasterMonday, GoodFriday, USLaborDay,
                                    USMartinLutherKingJr, USMemorialDay, USPresidentsDay,
                                    USThanksgivingDay, nearest_workday)
from pandas.tseries.offsets import Day

# mensajes de argparse (errores en los argumentos y ayuda) en español
ES = {'usage: ': 'uso: ', 'options': 'opciones', 'positional arguments': 'argumentos',
      'show this help message and exit': 'muestra esta ayuda y sale',
      'argument %(argument_name)s: %(message)s': 'argumento %(argument_name)s: %(message)s',
      'the following arguments are required: %s': 'faltan estos argumentos obligatorios: %s',
      'unrecognized arguments: %s': 'no reconozco estos argumentos: %s',
      'expected one argument': 'le falta su valor',
      'invalid choice: %(value)r (choose from %(choices)s)': 'no acepta %(value)r (elige entre %(choices)s)',
      'invalid choice: %(value)r, maybe you meant %(closest)r? (choose from %(choices)s)':
          'no acepta %(value)r; ¿quisiste decir %(closest)r? (elige entre %(choices)s)',
      'invalid %(type)s value: %(value)r': 'valor no válido: %(value)r (tiene que ser un número)',
      'ambiguous option: %(option)s could match %(matches)s': 'opción ambigua: %(option)s puede ser %(matches)s',
      ' (default: %(default)s)': ' (por defecto: %(default)s)'}
argparse._ = lambda m: ES.get(m, m)

# nombres de columna que se reconocen (se comparan sin tildes, sin mayúsculas y sin <> ni puntos)
ALIAS = {
    'fecha': ['fecha', 'dia', 'date', 'day', 'data', 'datetime', 'date time', 'fecha y hora', 'time', 'timestamp',
              'gmt time', 'local time', 'time (utc)', 'open time'],
    'open': ['open', 'apertura', 'abre', 'abertura', 'o'],
    'high': ['high', 'maximo', 'max', 'alto', 'h'],
    'low': ['low', 'minimo', 'min', 'bajo', 'l'],
    'close': ['close', 'cierre', 'ultimo', 'price', 'precio', 'fechamento', 'c', 'adj close'],
    'volume': ['volume', 'volumen', 'vol', 'v', 'real volume', 'tick volume', 'tickvol', 'tick vol'],
}
DIA, HORA = ('fecha', 'dia', 'date', 'day', 'data'), ('time', 'hora')   # fecha y hora en columnas separadas (MT5)
PASO = {'1m': '1min', '5m': '5min', '15m': '15min', '30m': '30min', '1h': '1h', '4h': '4h', '1d': '1D'}
MIN_ANIOS_APTA, MIN_ANIOS = 3.0, 1.0      # provisional: menos de 1 año = NO APTA; de 1 a 3 = aviso
MAX_ELIMINADAS, MAX_HUECOS = 0.05, 0.05    # provisional: más del 5 % = NO APTA
DIAS_FIN_VIEJO = 30    # la última vela tiene más de 30 días: la descarga pudo cortarse (aviso)
DIAS_HASTA = 5         # con --hasta: terminar más de 5 días antes de lo pedido = descarga incompleta (NO APTA)
MEZCLA = 'fechas en formatos mezclados: no se puede saber el día y el mes'


class DatosMalos(Exception):
    """El archivo no se puede curar. El mensaje dice por qué, en español."""


def pl(n, uno, varios):
    # singular o plural según el número: «1 vela», «2 velas»
    return f'{n} {uno if n == 1 else varios}'


def dec(x, n=1):
    # decimales con coma, como en español: 3,4
    return f'{x:.{n}f}'.replace('.', ',')


def pc(x, n=1, signo=False):
    # porcentaje con coma decimal y espacio: 0,1 %
    return f'{x * 100:{"+" if signo else ""}.{n}f} %'.replace('.', ',')


def abrir(ruta):
    """Mira el principio del archivo: decide la codificación y el separador, o explica por qué no es un CSV.
    Devuelve también la primera línea, para saber si trae encabezado."""
    if os.path.isdir(ruta):
        raise DatosMalos(f'{ruta} es una carpeta, no un archivo. Pon la ruta del CSV, por ejemplo datos/crudos/mi_archivo.csv.')
    try:
        crudo = open(ruta, 'rb').read(65536)
    except FileNotFoundError:
        raise DatosMalos(f'No encuentro el archivo {ruta}. Revisa el nombre y la carpeta.')
    except PermissionError:
        raise DatosMalos(f'No tengo permiso para leer {ruta}. Ciérralo si está abierto en Excel u otro programa y prueba otra vez.')
    except OSError:
        raise DatosMalos(f'No puedo abrir {ruta}. Revisa que exista y que no esté abierto en otro programa.')
    if not crudo.strip():
        raise DatosMalos('El archivo está vacío: la descarga no guardó nada. Vuelve a descargarlo.')
    if crudo.startswith(b'PK\x03\x04'):
        raise DatosMalos('Es un Excel (.xlsx) o un .zip, no un CSV. Ábrelo y guárdalo como «CSV UTF-8», o descomprímelo.')
    par = crudo[:len(crudo) // 2 * 2]
    if crudo[:2] in (b'\xff\xfe', b'\xfe\xff') or par[1::2].count(0) > 0.4 * len(par) / 2:
        # UTF-16 (algunos exports de MetaTrader): cada letra ocupa 2 bytes
        cod = 'utf-16' if crudo[:2] in (b'\xff\xfe', b'\xfe\xff') else 'utf-16-le'
        texto = par.decode(cod, errors='ignore')
    elif b'\x00' in crudo:
        raise DatosMalos('No es un CSV de texto (parece un archivo binario). Revisa que sea tu archivo de precios.')
    else:
        try:
            texto, cod = crudo.decode('utf-8-sig'), 'utf-8-sig'
        except UnicodeDecodeError as e:
            if e.start > len(crudo) - 4:            # solo falla el final: es el corte de los 64 KB
                texto, cod = crudo[:e.start].decode('utf-8-sig'), 'utf-8-sig'
            else:                                   # Excel en Windows guarda en latin-1
                texto, cod = crudo.decode('latin-1'), 'latin-1'
    lineas = [l for l in texto.splitlines() if l.strip()][:200]
    if len(crudo) == 65536 and len(lineas) > 1:
        lineas = lineas[:-1]                    # la última puede estar cortada
    for sep in (';', '\t', '|', ','):          # el punto y coma primero: con coma decimal, la coma engaña
        n = [l.count(sep) for l in lineas]
        moda = max(set(n), key=n.count)
        if moda >= 4 and n.count(moda) >= 0.9 * len(n):
            return cod, sep, lineas[0]
    raise DatosMalos('No reconozco las columnas. Un CSV de precios necesita al menos 5 (fecha, open, high, '
                     'low, close), separadas por coma, punto y coma o tabulador.')


def norm(c):
    # «<OPEN>», «Último», «Vol.», «tick_volume» → «open», «ultimo», «vol», «tick volume»
    t = unicodedata.normalize('NFKD', str(c)).encode('ascii', 'ignore').decode()
    return re.sub(r'[\s_]+', ' ', re.sub(r'[<>."\']', '', t)).strip().lower()


FECHA_RE = r'\d{8}([ T]?\d{4,6})?|\d{10,13}|\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}([ T].*)?'
NUM_RE = r'[-+]?[\d.,\s\xa0]*\d[\d.,\s\xa0]*'
HORA_RE = r'\d{1,2}:\d{2}(:\d{2})?'


def sin_encabezado(linea, sep):
    """Si la primera fila ya es una vela (fecha + números), el archivo no trae encabezado (HistData):
    devuelve los nombres por posición. Si es texto, devuelve None: hay encabezado y manda su nombre."""
    c = [x.strip().strip('"\'') for x in linea.split(sep)]
    if len(c) < 5 or not re.fullmatch(FECHA_RE, c[0]):
        return None
    hora = bool(re.fullmatch(HORA_RE, c[1]))     # fecha y hora en dos columnas: 2024.01.02,17:00,...
    if len(c) < 5 + hora or not all(re.fullmatch(NUM_RE, x) for x in c[1 + hora:5 + hora]):
        return None
    return ['fecha'] + (['hora'] if hora else []) + ['open', 'high', 'low', 'close', 'volume']


def coma_decimal(df):
    # coma decimal si en la mayoría de los precios la coma va después del punto (1.234,56 o 2650,5)
    txt = [df[c].astype(str) for c in ('open', 'high', 'low', 'close') if not pd.api.types.is_numeric_dtype(df[c])]
    if not txt:
        return False
    t = pd.concat(txt)
    coma, punto = t.str.rfind(','), t.str.rfind('.')
    return int((coma > punto).sum()) > int((punto > coma).sum())


def a_numero(serie, coma):
    if pd.api.types.is_numeric_dtype(serie):
        return pd.to_numeric(serie, errors='coerce')
    t = serie.astype(str).str.replace(r'[\s\xa0]', '', regex=True)
    if coma:   # 1.234,56 → 1234.56
        t = t.str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    else:      # 1,234.56 → 1234.56
        t = t.str.replace(',', '', regex=False)
    return pd.to_numeric(t, errors='coerce')


def columnas(df):
    """Reconoce las columnas por su nombre. Nunca por su posición: si falta alguna, NO APTA y explica."""
    nombres = {c: norm(c) for c in df.columns}
    cols, vols = {}, []                         # vols: todas las de volumen (MT5 trae <TICKVOL> y <VOL>)
    for c, n in nombres.items():
        for k, alias in ALIAS.items():
            if n in alias:
                if k == 'volume':
                    vols.append(c)
                elif k not in cols.values():
                    cols[c] = k
                break
    # fecha y hora en columnas separadas (<DATE> y <TIME> de MetaTrader 5): se unen
    dia = next((c for c, n in nombres.items() if n in DIA), None)
    hora = next((c for c, n in nombres.items() if n in HORA), None)
    if dia is not None and hora is not None:
        h = df[hora].dropna().astype(str).str.strip().head(50)
        if len(h) and h.str.fullmatch(HORA_RE).all():
            df[dia] = df[dia].astype(str).str.strip() + ' ' + df[hora].astype(str).str.strip()
            cols = {c: k for c, k in cols.items() if k != 'fecha' and c != hora}
            cols[dia] = 'fecha'
    falta = [k for k in ('fecha', 'open', 'high', 'low', 'close') if k not in cols.values()]
    if falta:
        vistas = ', '.join(f'«{c}»' for c in df.columns)
        bien = ', '.join(f'«{c}» = {k}' for c, k in cols.items())
        raise DatosMalos(f'No reconozco todas las columnas. El archivo trae: {vistas}. '
                         + (f'Reconocí {bien}; ' if cols else 'No reconocí ninguna; ')
                         + f'me faltan: {", ".join(falta)}. Abre el CSV y cambia los nombres de la primera línea por '
                         'fecha, open, high, low, close, volume (el volumen es opcional). No asigno columnas por su '
                         'posición: si me equivoco, open y close quedan cambiados sin que nadie lo note.')
    return cols, sorted(vols, key=lambda c: 'tick' in nombres[c])   # el volumen real primero


def leer(ruta):
    cod, sep, primera = abrir(ruta)
    malas = []                                  # líneas con columnas de más: se saltan y se cuentan

    def csv(**k):
        try:
            try:
                return pd.read_csv(ruta, sep=sep, engine='python', encoding=cod, on_bad_lines=malas.append, **k)
            except UnicodeDecodeError:          # el archivo cambia de codificación más abajo
                malas.clear()
                return pd.read_csv(ruta, sep=sep, engine='python', encoding='latin-1', on_bad_lines=malas.append, **k)
        except (pd.errors.ParserError, pd.errors.EmptyDataError, ValueError) as e:
            raise DatosMalos(f'No pude leer el CSV ({str(e).splitlines()[0]}). Revisa que tenga una vela por línea.')

    pos = sin_encabezado(primera, sep)
    if pos:                                     # sin encabezado (HistData): la primera fila ya es una vela
        df = csv(header=None)
        df.columns = (pos + [f'extra{i}' for i in range(len(df.columns))])[:len(df.columns)]
    else:
        df = csv()
    cols, vols = columnas(df)
    if df.empty:
        raise DatosMalos('El CSV solo tiene el encabezado: no trae ninguna vela. Vuelve a descargarlo.')
    out = pd.DataFrame({k: df[c] for c, k in cols.items()})
    coma = coma_decimal(out)
    for c in ('open', 'high', 'low', 'close'):
        out[c] = a_numero(out[c], coma)
    # volumen: el primero que no sea todo cero (MT5: <VOL> suele venir en cero y el bueno es <TICKVOL>)
    v = [a_numero(df[c], coma) for c in vols]
    out['volume'] = next((x for x in v if (x.fillna(0) != 0).any()), v[0] if v else np.nan)
    return out[['fecha', 'open', 'high', 'low', 'close', 'volume']], len(malas), coma


def a_utc(serie, zona):
    t = serie.astype(str).str.strip()
    if t.str.fullmatch(r'\d{8} \d{6}').all():
        f = pd.to_datetime(t, format='%Y%m%d %H%M%S', errors='coerce')
    elif t.str.fullmatch(r'\d{10,13}').all():
        f = pd.to_datetime(t.astype('int64'), unit='ms' if t.str.len().max() > 10 else 's', utc=True)
    else:
        # año primero (2024-01-02): sin duda. Día y mes primero (02/01/2024): el día es la posición que
        # pasa de 12 alguna vez. Si no se sabe, o vienen formatos mezclados, no se adivina: NO APTA.
        anio_primero = t.str.match(r'\d{4}[-/.]\d{1,2}[-/.]\d{1,2}')
        dm = t.str.extract(r'^(\d{1,2})[-/.](\d{1,2})[-/.](\d{4}|\d{2})(?!\d)')
        es_dm = dm[0].notna()
        if anio_primero.any() and es_dm.any():
            raise DatosMalos(f'{MEZCLA} (unas como «{t[anio_primero].iloc[0]}», otras como «{t[es_dm].iloc[0]}»). '
                             'Vuelve a exportar el archivo con un solo formato de fecha, mejor AAAA-MM-DD.')
        if es_dm.any():
            a, b = dm.loc[es_dm, 0].astype(int), dm.loc[es_dm, 1].astype(int)
            dia_primero, mes_primero = bool((a > 12).any()), bool((b > 12).any())
            if dia_primero == mes_primero:      # las dos cosas (mezcla) o ninguna (no se puede saber)
                raise DatosMalos(f'{MEZCLA} (fechas como «{t[es_dm].iloc[0]}» pueden ser día/mes o mes/día). '
                                 'Vuelve a exportar el archivo con fechas AAAA-MM-DD.')
            d, m = (dm.loc[es_dm, 0], dm.loc[es_dm, 1]) if dia_primero else (dm.loc[es_dm, 1], dm.loc[es_dm, 0])
            y = dm.loc[es_dm, 2]
            y = y.where(y.str.len() == 4, '20' + y)
            t = t.copy()
            t[es_dm] = (y + '-' + m.str.zfill(2) + '-' + d.str.zfill(2)
                        + t[es_dm].str.replace(r'^\d{1,2}[-/.]\d{1,2}[-/.](\d{4}|\d{2})', '', regex=True))
        # año primero con puntos o barras (MetaTrader: 2024.01.02): sin duda, se pasa a 2024-01-02
        if t.str.match(r'\d{4}[/.]\d{1,2}[/.]\d{1,2}').any():
            t = t.str.replace(r'^(\d{4})[/.](\d{1,2})[/.](\d{1,2})',
                              lambda g: f'{g[1]}-{int(g[2]):02d}-{int(g[3]):02d}', regex=True)
        f = pd.to_datetime(t, errors='coerce', format='mixed')
    if getattr(f.dt, 'tz', None) is None:
        if zona.upper() == 'EST':   # hora de Nueva York sin cambio de verano (HistData)
            f = f + pd.Timedelta(hours=5)
            return f.dt.tz_localize('UTC')
        return f.dt.tz_localize(zona, ambiguous='NaT', nonexistent='NaT').dt.tz_convert('UTC')
    return f.dt.tz_convert('UTC')


class FeriadosEEUU(AbstractHolidayCalendar):
    # feriados de la bolsa de Nueva York; también cierran (o cierran antes) metales e índices
    rules = [Holiday('Año Nuevo', month=1, day=1, observance=nearest_workday), USMartinLutherKingJr,
             USPresidentsDay, GoodFriday, USMemorialDay,
             Holiday('Juneteenth', month=6, day=19, start_date='2022-01-01', observance=nearest_workday),
             Holiday('Independencia', month=7, day=4, observance=nearest_workday), USLaborDay,
             USThanksgivingDay, Holiday('Navidad', month=12, day=25, observance=nearest_workday)]


def feriados(ini, fin, mercado):
    """Días operativos (fecha de Nueva York) en que el mercado cierra o cierra antes."""
    anios = range(ini.year, fin.year + 2)
    fijos = lambda m, d: [pd.Timestamp(a, m, d) for a in anios]
    if mercado == 'forex':
        dias = fijos(12, 24) + fijos(12, 25) + fijos(12, 31) + fijos(1, 1)
    elif mercado == 'sesion':   # horario desconocido: feriados de EE. UU. y de Europa
        dias = list(FeriadosEEUU().holidays(f'{ini.year}-01-01', f'{fin.year + 1}-12-31'))
        dias += fijos(12, 24) + fijos(12, 26) + fijos(12, 31) + fijos(1, 1) + fijos(5, 1) + fijos(7, 3)
        dias += list(pd.DatetimeIndex(EasterMonday.dates(f'{ini.year}-01-01', f'{fin.year + 1}-12-31')))
        dias += list(pd.DatetimeIndex(USThanksgivingDay.dates(f'{ini.year}-01-01', f'{fin.year + 1}-12-31')) + Day(1))
    else:
        dias = list(FeriadosEEUU().holidays(f'{ini.year}-01-01', f'{fin.year + 1}-12-31'))
        if mercado != 'bolsa':   # cierres anticipados de metales e índices
            dias += fijos(12, 24) + fijos(12, 31) + fijos(7, 3)
            dias += list(pd.DatetimeIndex(USThanksgivingDay.dates(f'{ini.year}-01-01', f'{fin.year + 1}-12-31')) + Day(1))
    return pd.DatetimeIndex(sorted(set(dias))).date


def dia_operativo(idx, mercado):
    # la sesión del día D empieza la tarde anterior: forex a las 17:00, metales e índices a las 18:00
    ny = idx.tz_convert('America/New_York')
    return (ny + pd.Timedelta(hours=7 if mercado == 'forex' else 6)).date


DIAS_SEM = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
ZONAS_SESION = ['America/New_York', 'Europe/Berlin', 'Europe/London', 'Asia/Tokyo', 'Australia/Sydney', 'UTC']


def faltan_sesion(fechas, paso, zona):
    """Horario aprendido en una zona: huecos (día de la semana, hora) con datos en al menos el 75 % de las
    semanas. Un feriado solo se perdona si ese día de verdad cerró o cerró antes (le falta al menos un 10 % de su horario)."""
    fechas = pd.DatetimeIndex(fechas)
    loc = fechas.tz_convert(zona)
    clave = lambda t: t.day_of_week * 1440 + t.hour * 60 + t.minute
    semanas = max(1, (loc.max() - loc.min()).days / 7)
    frec = pd.Series(clave(loc)).value_counts() / semanas
    abiertas = set(frec[frec >= 0.75].index)
    idx = pd.date_range(fechas.min(), fechas.max(), freq=paso, tz='UTC')
    exp = idx[pd.Index(clave(idx.tz_convert(zona))).isin(abiertas)]
    faltan = exp.difference(fechas)
    dia_exp = pd.Series(exp.tz_convert(zona).date).value_counts()
    dia_falta = pd.Series(faltan.tz_convert(zona).date).value_counts()
    cerrado = (dia_falta / dia_exp.reindex(dia_falta.index)) >= 0.10
    fer_dias = set(feriados(exp.min(), exp.max(), 'sesion'))
    cerro = {d for d in cerrado[cerrado].index if d in fer_dias}   # feriados en que de verdad cerró
    lf = faltan.tz_convert(zona)
    # se perdona el feriado y la tarde anterior (la sesión del feriado puede empezar la víspera)
    fer = pd.Index(lf.date).isin(list(cerro)) | (
        pd.Index((lf + pd.Timedelta(days=1)).date).isin(list(cerro)) & (lf.hour >= 17))
    fuera = int((~pd.Index(clave(loc)).isin(abiertas)).sum())        # velas con datos fuera del horario aprendido
    return faltan[~fer], int(fer.sum()), len(abiertas), fuera


def esperadas(ini, fin, paso, mercado):
    idx = pd.date_range(ini, fin, freq=paso, tz='UTC')
    if mercado == 'cripto':
        return idx
    ny = idx.tz_convert('America/New_York')
    dia, hora = ny.day_of_week, ny.hour
    if mercado == 'forex':
        abierto = ~((dia == 5) | ((dia == 4) & (hora >= 17)) | ((dia == 6) & (hora < 17)))
    elif mercado in ('metales', 'indices'):
        abierto = ~((dia == 5) | ((dia == 4) & (hora >= 17)) | ((dia == 6) & (hora < 18)) | (hora == 17))
    else:
        abierto = dia < 5
    return idx[abierto]


def fecha_arg(txt):
    try:
        return pd.Timestamp(datetime.strptime(txt, '%Y-%m-%d'), tz='UTC')
    except ValueError:
        raise argparse.ArgumentTypeError(f'fecha no válida «{txt}»: escríbela como AAAA-MM-DD')


def nuevo(ruta):
    base, ext = os.path.splitext(ruta)
    return f'{base}_nuevo{ext}'


def rango(ruta):
    # primera y última fecha de un CSV curado que ya existe (None si no se puede leer)
    try:
        f = pd.to_datetime(pd.read_csv(ruta, usecols=['fecha'])['fecha'], utc=True, errors='coerce').dropna()
        return (f.min(), f.max()) if len(f) else None
    except Exception:
        return None


def zona_arg(txt):
    # una zona horaria que exista (base IANA: UTC, America/New_York, Europe/Berlin...) o EST
    if txt.upper() == 'EST':
        return 'EST'
    try:
        pd.Timestamp('2024-01-01').tz_localize(txt)
        return txt
    except Exception:
        raise argparse.ArgumentTypeError(f'la zona horaria «{txt}» no existe. Usa un nombre como UTC, '
                                         'America/New_York, Europe/Berlin, Europe/London o EST')


def zona_sesion_arg(txt):
    return 'auto' if txt.lower() == 'auto' else zona_arg(txt)


def escribir(ruta, hacer):
    # escribe un archivo; si no se puede (es una carpeta, está abierto en Excel...), lo explica en español
    try:
        if os.path.isdir(ruta):
            raise IsADirectoryError
        os.makedirs(os.path.dirname(ruta) or '.', exist_ok=True)
        hacer(ruta)
    except IsADirectoryError:
        sys.exit(f'No puedo escribir {ruta}: es una carpeta. Pon la ruta de un archivo (por ejemplo datos/mi_activo.csv).')
    except PermissionError:
        sys.exit(f'No tengo permiso para escribir {ruta}. Ciérralo si está abierto en Excel u otro programa y prueba otra vez.')
    except OSError:
        sys.exit(f'No puedo escribir {ruta}. Revisa que la carpeta exista y que el nombre no tenga caracteres raros.')


def guardar(ruta, texto):
    escribir(ruta, lambda r: open(r, 'w', encoding='utf-8').write(texto))


def informe_no_apta(o):
    # con NO APTA no se toca nada que ya exista: si --salida ya estaba, el informe va aparte (_nuevo.md)
    return nuevo(o.informe) if os.path.exists(o.salida) else o.informe


def fallar(o, motivo):
    # no hay nada que curar: informe NO APTA, ningún CSV, código 1. Si ya hay datos curados, no se tocan.
    informe = informe_no_apta(o)
    L = [f'# Calidad de datos · {o.salida}', '', 'Veredicto: **NO APTA** para backtest', '',
         f'- Origen: {o.crudo} · mercado {o.mercado} · temporalidad {o.temporalidad} · zona original {o.zona}',
         f'- Motivo: {motivo}', '- No se guardó ningún CSV curado.']
    if informe != o.informe:
        L.append(f'- {o.salida} ya existía y no se tocó (ni su informe {o.informe}).')
    guardar(informe, '\n'.join(L) + '\n')
    print('\n'.join(L))
    sys.exit(1)


def main():
    a = argparse.ArgumentParser(description='Cura un CSV de precios y escribe su informe de calidad.')
    a.add_argument('crudo', help='el CSV crudo (datos/crudos/...)')
    a.add_argument('--mercado', required=True, choices=['cripto', 'forex', 'metales', 'indices', 'bolsa', 'sesion'],
                   help='decide qué horas son de mercado cerrado')
    a.add_argument('--zona-sesion', default='auto', type=zona_sesion_arg,
                   help='auto = prueba las zonas habituales y se queda con la que mejor encaja')
    a.add_argument('--temporalidad', required=True, choices=list(PASO), help='duración de cada vela')
    a.add_argument('--zona', default='UTC', type=zona_arg, help='zona horaria de las fechas crudas si vienen sin zona')
    a.add_argument('--salida', required=True, help='CSV curado (datos/...)')
    a.add_argument('--informe', required=True, help='informe de calidad (resultados/..._calidad.md)')
    a.add_argument('--hasta', type=fecha_arg, help='fecha final que pediste al descargar (AAAA-MM-DD)')
    a.add_argument('--forzar', action='store_true', help='sobrescribe --salida aunque lo nuevo cubra menos fechas')
    o = a.parse_args()
    for r, que in ((o.salida, '--salida'), (o.informe, '--informe')):
        if os.path.isdir(r):
            sys.exit(f'{que} {r} es una carpeta: pon la ruta de un archivo (por ejemplo datos/mi_activo.csv).')

    try:
        df, n_malas, coma = leer(o.crudo)
        n0 = len(df) + n_malas
        df['fecha'] = a_utc(df['fecha'], o.zona)
    except DatosMalos as e:
        fallar(o, str(e))

    sin_fecha = int(df['fecha'].isna().sum())
    df = df.dropna(subset=['fecha']).sort_values('fecha')
    if df.empty:
        fallar(o, 'No se pudo leer ninguna fecha. Revisa la columna de fecha y el --zona.')
    ahora = pd.Timestamp.now(tz='UTC')
    futuras = int((df['fecha'] > ahora).sum())  # una vela que todavía no empezó es imposible
    df = df[df['fecha'] <= ahora]

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
    if df.empty:
        fallar(o, f'Después de curar no queda ninguna vela ({pl(n0, "vela", "velas")} en el crudo: '
                  'fechas futuras, repetidas o precios imposibles). Revisa el archivo.')

    # saltos raros: retorno muy lejos de lo normal (8 veces la desviación robusta). Se marcan, no se borran.
    r = np.log(df['close']).diff()
    mad = (r - r.median()).abs().median() * 1.4826
    lejos = (r - r.median()).abs()
    saltos = df.loc[lejos > 8 * mad, 'fecha'] if mad > 0 else df['fecha'].iloc[:0]
    mayores = lejos[saltos.index].nlargest(10).index   # los 10 más grandes, del mayor al menor

    paso = PASO[o.temporalidad]
    cerradas, dias_vacios, velas_dia = 0, [], 0   # cerradas: faltan en feriados o cierres anticipados, no cuentan
    if o.mercado == 'cripto':
        horario = '- Horario: 24/7, toda vela que falta cuenta'
    else:
        horario = ('- Mercado cerrado (fines de semana, pausa diaria, feriados y cierres anticipados): no cuenta'
                   ' · {} sin datos en feriados o cierres anticipados')
    if o.temporalidad == '1d':
        # el día en UTC: las fuentes fechan la vela diaria a las 00:00 UTC o a la medianoche de Nueva York (04-05 UTC)
        dias = df['fecha'].dt.normalize()
        tiene = pd.DatetimeIndex(dias.dt.tz_localize(None).unique())
        exp = pd.date_range(tiene.min(), tiene.max(), freq='D')
        if o.mercado == 'sesion':
            # diario con horario propio: opera los días de la semana con datos en al menos el 75 % de las semanas
            frec = pd.Series(tiene.day_of_week).value_counts() / max(1, len(exp) / 7)
            dias_sem = sorted(frec[frec >= 0.75].index)
            exp = exp[exp.day_of_week.isin(dias_sem)]
            horario = (f'- Horario aprendido de los datos (diario): opera {", ".join(DIAS_SEM[d] for d in dias_sem)}'
                       ' · se cuentan los días de ese horario sin datos · {} sin datos en feriados, no cuentan')
        elif o.mercado != 'cripto':
            exp = exp[exp.day_of_week < 5]
        if o.mercado != 'cripto':
            fer = exp.isin(pd.DatetimeIndex(feriados(exp.min(), exp.max(), o.mercado)))
            cerradas, exp = len(exp[fer].difference(tiene)), exp[~fer]
        faltan = exp.difference(tiene)
    elif o.mercado == 'bolsa':
        # intradía de bolsa: huecos dentro de cada día con datos (la sesión cambia según el activo)
        # y días hábiles enteros sin datos que no sean feriados
        fechas_ny = df['fecha'].dt.tz_convert('America/New_York').dt.date
        faltan = []
        for _, g in df.groupby(fechas_ny):
            exp = pd.date_range(g['fecha'].min(), g['fecha'].max(), freq=paso)
            faltan += list(exp.difference(pd.DatetimeIndex(g['fecha'])))
        faltan, exp = pd.DatetimeIndex(faltan), None
        habiles = pd.bdate_range(fechas_ny.min(), fechas_ny.max())
        habiles = habiles[~habiles.isin(pd.DatetimeIndex(feriados(habiles.min(), habiles.max(), 'bolsa')))]
        dias_vacios = sorted(set(habiles.date) - set(fechas_ny))
        velas_dia = int(fechas_ny.value_counts().median())
    elif o.mercado == 'sesion':
        # el horario de cada bróker sigue el cambio de hora de algún país: se prueba cada zona y se queda
        # la que mejor explica los datos (menos huecos + menos velas fuera de su horario); el informe dice cuál
        zonas = ZONAS_SESION if o.zona_sesion == 'auto' else [o.zona_sesion]
        prueba = {z: faltan_sesion(df['fecha'], paso, z) for z in zonas}
        o.zona_sesion = min(prueba, key=lambda z: len(prueba[z][0]) + prueba[z][3])
        faltan, cerradas, n_huecos_sem, _ = prueba[o.zona_sesion]
        horario = (f'- Horario aprendido de los datos ({o.zona_sesion}): {n_huecos_sem} velas por semana'
                   ' · {} sin datos en feriados, no cuentan')
    else:
        exp = esperadas(df['fecha'].min(), df['fecha'].max(), paso, o.mercado)
        faltan = exp.difference(pd.DatetimeIndex(df['fecha']))
        if o.mercado != 'cripto':
            fer = pd.Index(dia_operativo(faltan, o.mercado)).isin(feriados(exp.min(), exp.max(), o.mercado))
            cerradas, faltan = int(fer.sum()), faltan[~fer]
    if ' · {}' in horario:    # cuántas velas sin datos en feriados (solo si hubo)
        antes, despues = horario.split(' · {}')
        horario = antes + (f' · {pl(cerradas, "vela", "velas")}{despues}' if cerradas else '')
    n_faltan = len(faltan) + len(dias_vacios) * velas_dia
    n_esp = len(df) + n_faltan
    p_huecos = n_faltan / n_esp if n_esp else 0

    vol = df['volume']
    sin_vol = bool(vol.isna().all())
    vol_cero = float((vol == 0).mean()) if not sin_vol else 0.0

    anios = (df['fecha'].max() - df['fecha'].min()).days / 365.25 if len(df) else 0
    # las repetidas exactas (un export pegado dos veces) no son datos malos: no cuentan para el 5 %
    n_reales = n0 - dup_iguales
    eliminadas = (n_reales - len(df)) / n_reales if n_reales else 0
    fin = df['fecha'].max()
    incompleta = o.hasta is not None and (min(o.hasta, ahora) - fin).days > DIAS_HASTA
    avisos = []
    if coma: avisos.append('Los precios venían con coma decimal (Excel en español): se leyeron bien.')
    if n_malas: avisos.append(f'{pl(n_malas, "línea con columnas de más, eliminada", "líneas con columnas de más, eliminadas")}.')
    if sin_fecha: avisos.append(f'{pl(sin_fecha, "fila con fecha ilegible, eliminada", "filas con fecha ilegible, eliminadas")}.')
    if futuras: avisos.append(f'{pl(futuras, "vela con fecha futura (imposible), eliminada", "velas con fecha futura (imposibles), eliminadas")}.')
    if dup_iguales: avisos.append(f'{pl(dup_iguales, "fila repetida exacta (idéntica a otra), eliminada", "filas repetidas exactas (idénticas a otra), eliminadas")}: '
                                  'suele ser un export pegado dos veces. No cuentan para el 5 % de eliminadas.')
    if dup_distintas: avisos.append(f'{pl(dup_distintas, "vela con la misma fecha que otra y precios distintos", "velas con la misma fecha y precios distintos")}: se dejó la primera.')
    if n_imp: avisos.append(f'{pl(n_imp, "vela imposible", "velas imposibles")} (precio vacío, cero o máximo/mínimo incoherente), '
                            f'{"eliminada" if n_imp == 1 else "eliminadas"}.')
    if len(saltos): avisos.append(f'{pl(len(saltos), "salto fuera de lo normal", "saltos fuera de lo normal")}: '
                                  'revísalos en el gráfico (pueden ser reales).')
    if n_faltan: avisos.append(f'{pl(n_faltan, "vela faltante", "velas faltantes")} con el mercado abierto ({pc(p_huecos)}). '
                               f'No se {"rellenó" if n_faltan == 1 else "rellenaron"}.')
    if dias_vacios: avisos.append(f'{pl(len(dias_vacios), "día hábil", "días hábiles")} sin ningún dato '
                                  f'(cuenta{"" if len(dias_vacios) == 1 else "n"} como {pl(velas_dia, "vela", "velas")} cada uno): '
                                  + ', '.join(map(str, dias_vacios[:10])) + (' ...' if len(dias_vacios) > 10 else ''))
    if sin_vol: avisos.append('La fuente no trae volumen: la columna queda vacía. No uses reglas de volumen.')
    elif vol_cero > 0.2: avisos.append(f'{pc(vol_cero, 0)} de las velas con volumen 0: no uses reglas de volumen.')
    if round(anios, 1) < MIN_ANIOS_APTA: avisos.append(f'Solo {dec(anios)} años de historia: el 30 % fuera de muestra queda corto.')
    if incompleta:
        avisos.append(f'Descarga incompleta: pediste hasta el {o.hasta:%Y-%m-%d} y los datos terminan el {fin:%Y-%m-%d}. '
                      'Vuelve a descargar.')
    elif o.hasta is None and (ahora - fin).days > DIAS_FIN_VIEJO:
        avisos.append(f'Los datos terminan el {fin:%Y-%m-%d}: si pediste hasta hoy, la descarga pudo cortarse.')

    motivos = [m for mal, m in [
        (eliminadas > MAX_ELIMINADAS, f'se eliminó el {pc(eliminadas)} de las velas (máximo 5 %)'),
        (p_huecos > MAX_HUECOS, f'faltan el {pc(p_huecos)} de las velas con el mercado abierto (máximo 5 %)'),
        (anios < MIN_ANIOS, f'solo {dec(anios)} años de historia (mínimo 1)'),
        (len(df) < 100, f'solo {pl(len(df), "vela curada", "velas curadas")} (mínimo 100)'),
        (incompleta, 'la descarga quedó incompleta (mira los avisos)')] if mal]
    if motivos:
        veredicto = 'NO APTA'
    elif avisos:
        veredicto = 'APTA CON AVISOS'
    else:
        veredicto = 'APTA'

    salida, informe, protegido, guardado = o.salida, o.informe, None, []
    if motivos:
        # NO APTA: solo el informe; ningún CSV (en datos/ quedan solo los que sirven) y nada existente se toca
        informe = informe_no_apta(o)
        guardado = [f'- No se guardó ningún CSV curado: estos datos no sirven para un backtest. El crudo sigue en {o.crudo}.']
        if informe != o.informe:
            guardado.append(f'- {o.salida} ya existía y no se tocó (ni su informe {o.informe}).')
    else:
        # no se pisan datos buenos: si ya hay un curado que cubre más fechas, lo nuevo va a _nuevo.csv
        viejo = rango(o.salida) if os.path.exists(o.salida) and not o.forzar else None
        if viejo and (df['fecha'].min() > viejo[0] or fin < viejo[1]):
            salida, informe = nuevo(o.salida), nuevo(o.informe)
            protegido = (f'OJO: {o.salida} ya tiene datos del {viejo[0]:%Y-%m-%d} al {viejo[1]:%Y-%m-%d} y estos cubren menos '
                         f'(del {df["fecha"].min():%Y-%m-%d} al {fin:%Y-%m-%d}). No lo sobrescribí: lo nuevo quedó en {salida} '
                         f'y su informe en {informe}. Si de verdad quieres reemplazarlo, repite el comando con --forzar.')

    # primero se arma todo (informe y saltos); los archivos se escriben al final
    base, ext = os.path.splitext(informe)
    f_saltos = (base.replace('_calidad', '_saltos') if '_calidad' in base else base + '_saltos') + ext
    cambio = lambda i: pc(np.expm1(r[i]), signo=True)
    L = [f'# Calidad de datos · {salida}', ''] + ([protegido, ''] if protegido else []) + [
         f'Veredicto: **{veredicto}** para backtest', ''] + (
         [f'- Motivo: {"; ".join(motivos)}.'] + guardado if motivos else []) + [
         f'- Origen: {o.crudo} · mercado {o.mercado} · temporalidad {o.temporalidad} · zona original {o.zona}',
         f'- Desde {df["fecha"].min():%Y-%m-%d %H:%M} hasta {fin:%Y-%m-%d %H:%M} UTC · {dec(anios)} años',
         f'- Velas: {n0} en el crudo → {len(df)} curadas ({pc(eliminadas)} eliminadas'
         + (f'; aparte, {pl(dup_iguales, "fila repetida exacta", "filas repetidas exactas")})' if dup_iguales else ')'),
         f'- Velas faltantes con el mercado abierto: {n_faltan} ({pc(p_huecos)})',
         horario,
         f'- Volumen: {"no viene" if sin_vol else f"{pc(vol_cero, 0)} en cero"}', '',
         '## Avisos'] + ([f'- {x}' for x in avisos] or ['- Ninguno.'])
    if len(saltos):
        L += ['', f'## Saltos para revisar ({"los 10 mayores" if len(saltos) > 10 else "todos"})',
              'En oro, índices o cripto suelen ser noticias reales; mira '
              + ('estos 10' if len(saltos) >= 10 else 'estos') + ' en el gráfico.'
              + (f' La lista completa está en {f_saltos}.' if len(saltos) > 10 else '')]
        L += [f'- {df.at[i, "fecha"]:%Y-%m-%d %H:%M} UTC · {cambio(i)}' for i in mayores]
    if len(faltan):
        L += ['', '## Velas faltantes (primeras 10)'] + [f'- {pd.Timestamp(f):%Y-%m-%d %H:%M} UTC' for f in list(faltan)[:10]]
    L += ['', 'Umbrales provisionales del Reto: NO APTA si se eliminó más del 5 %, faltan más del 5 % de las velas,',
          'hay menos de 1 año o menos de 100 velas. Datos gratuitos: buenos para investigar, no iguales a datos de pago.']
    S = None
    if len(saltos) > 10:   # la lista completa, en orden de fecha
        S = [f'# Saltos para revisar · {salida}', '',
             f'Lista completa de los {len(saltos)} saltos que marcó la curación (cambio de cierre a cierre mayor que '
             '8 veces lo normal).', 'Fecha y hora = APERTURA de la vela, en UTC. En TradingView pon la zona horaria '
             'del gráfico en UTC.', 'Cambio = variación del cierre de esa vela frente al cierre de la vela anterior. '
             'No se borró ninguno.', '', '| Fecha (UTC) | Hora | Cambio | Cierre |', '| --- | --- | --- | --- |']
        S += [f'| {df.at[i, "fecha"]:%Y-%m-%d} | {df.at[i, "fecha"]:%H:%M} | {cambio(i)} | '
              f'{dec(df.at[i, "close"], 2)} |' for i in saltos.index]

    if not motivos:
        out = df.copy()
        out['fecha'] = out['fecha'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        escribir(salida, lambda ruta: out.to_csv(ruta, index=False))
    guardar(informe, '\n'.join(L) + '\n')
    if S:
        guardar(f_saltos, '\n'.join(S) + '\n')
    print('\n'.join(L))
    if motivos:            # NO APTA: código 1, como cuando no se puede curar
        sys.exit(1)
    if protegido:          # el curado bueno se conservó: avisa con error para que nadie use el _nuevo sin querer
        print('\n' + protegido)
        sys.exit(3)


if __name__ == '__main__':
    main()
