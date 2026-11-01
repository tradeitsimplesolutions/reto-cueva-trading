"""Tus límites en números · skill objetivos (cueva TIS).

Traduce el plan del trader (riesgo por operación, caída máxima, frecuencia, reglas de fondeo)
a lo que va a vivir, con una simulación de Monte Carlo (muchas secuencias de operaciones al azar).

Uso:
  python .claude/skills/objetivos/limites.py --riesgo 1 --caida 15 --ops-mes 20 \
      --operaciones resultados/<idea>_operaciones.csv
  python .claude/skills/objetivos/limites.py --riesgo 1 --caida 15 --ops-mes 20 \
      --acierto 45 --ratio 1.5          # sin backtest: estimación con supuestos
  Fondeo: --total 10 --diario 5 --objetivo 8 --dias-min 4 (sin --caida; --total-arrastrada si la empresa
      mide la pérdida total desde el punto más alto)
  Opcionales: --dias-mes 17 (no opera todos los días) · --ops-dia 3 · --para-tras 3 (para el día tras 3 pérdidas)
Al final dice el riesgo máximo que cumple el límite (provisional del Reto: 20 % de probabilidad de tocar
la caída propia en 12 meses; en fondeo, 10 % de tocar la pérdida total y 3 pérdidas sin romper el diario).

--operaciones: CSV con una columna de resultado por operación en R (múltiplos del riesgo) o en
dinero (columna «r», «resultado», «profit» o «pnl»; si es dinero se pasa a R con la pérdida media).
Si trae la columna «tramo» (DM/FM, la del validador), usa solo las de fuera de muestra (FM); si no la
trae, usa todas y avisa.
Límites: --riesgo como mucho 10 %, --ops-mes como mucho 500 y como mucho 6000 operaciones por cuenta
simulada (ops-mes × meses). Con muchas operaciones al mes, si no pones --sims, simula menos cuentas
(nunca menos de 2000) para no tardar minutos; la línea «Supuestos» dice cuántas.
Solo usa números: no necesita ni guarda datos de la cuenta.
"""
import argparse, builtins, csv, math, re, random, statistics as st, sys
import numpy as np

# mensajes de argparse (errores en los argumentos y ayuda) en español
ES = {'usage: ': 'uso: ', 'options': 'opciones', 'positional arguments': 'argumentos',
      'show this help message and exit': 'muestra esta ayuda y sale',
      'argument %(argument_name)s: %(message)s': 'argumento %(argument_name)s: %(message)s',
      'the following arguments are required: %s': 'faltan estos argumentos obligatorios: %s',
      'unrecognized arguments: %s': 'no reconozco estos argumentos: %s',
      'expected one argument': 'le falta su valor',
      'invalid choice: %(value)r (choose from %(choices)s)': 'no acepta %(value)r (elige entre %(choices)s)',
      'invalid %(type)s value: %(value)r': 'valor no válido: %(value)r (tiene que ser un número)',
      'ambiguous option: %(option)s could match %(matches)s': 'opción ambigua: %(option)s puede ser %(matches)s',
      ' (default: %(default)s)': ' (por defecto: %(default)s)'}
argparse._ = lambda m: ES.get(m, m)

def print(*a):  # decimales con coma, como en español
    builtins.print(*(re.sub(r'(\d)\.(\d)', r'\1,\2', str(x)) for x in a))

def leer_r(ruta):
    with open(ruta, newline='', encoding='utf-8-sig') as f:
        filas = list(csv.DictReader(f))
    if not filas:
        sys.exit('El CSV de operaciones está vacío.')
    cols = {c.lower().strip(): c for c in filas[0].keys() if c}
    if 'tramo' in cols:      # solo fuera de muestra: las de dentro de muestra suelen salir mejor de lo real
        filas = [f for f in filas if (f[cols['tramo']] or '').strip().upper() == 'FM']
        if not filas:
            sys.exit('El CSV tiene columna «tramo» pero ninguna operación FM (fuera de muestra): no hay con qué simular.')
        nota = 'solo fuera de muestra, tramo FM'
    else:
        nota = 'AVISO: no tiene columna «tramo», uso todas, también las de dentro de muestra'
    for nombre in ('r', 'resultado_r', 'resultado', 'profit', 'pnl', 'beneficio'):
        if nombre in cols:
            col = cols[nombre]; break
    else:
        sys.exit('No encontré la columna de resultado (r, resultado, profit o pnl).')
    vals = []
    for fila in filas:
        t = (fila[col] or '').replace(',', '.').strip()
        if t:
            vals.append(float(t))
    if col.lower() != 'r' and col.lower() != 'resultado_r':
        perd = [v for v in vals if v < 0]
        if not perd:
            sys.exit('No hay operaciones perdedoras: no puedo medir el riesgo en R.')
        unidad = -st.mean(perd)          # supuesto: la pérdida media ≈ 1 R
        vals = [v / unidad for v in vals]
    if not vals:
        sys.exit('El CSV de operaciones no tiene ningún resultado.')
    return vals, nota

def racha_max(seq):
    m = c = 0
    for v in seq:
        c = c + 1 if v < 0 else 0
        m = max(m, c)
    return m

def pct(x, p):
    x = sorted(x); return x[min(len(x) - 1, int(p / 100 * len(x)))]

def perdidas_hasta(limite, riesgo):
    k = 0; eq = 100.0
    while (100 - eq) < limite:
        eq *= 1 - riesgo / 100; k += 1
    return k

MAX_P_CAIDA, MAX_P_TOTAL = 20, 10       # % de probabilidad en 12 meses (provisional del Reto)
MAX_RIESGO, MAX_OPS_MES, MAX_OPS_CUENTA = 10, 500, 6000   # más que esto no tiene sentido (o tarda demasiado)
OPS_TOTALES = 6_000_000                 # sin --sims: operaciones simuladas en total como mucho
SIMS_BUSQUEDA = 2000                    # cuentas de la búsqueda del riesgo máximo


def main():
    a = argparse.ArgumentParser(description='Traduce tu plan de riesgo a lo que vas a vivir (Monte Carlo).')
    a.add_argument('--riesgo', type=float, required=True, help='%% de la cuenta por operación')
    a.add_argument('--caida', type=float, help='cuenta propia: caída máxima que aguanta, %% desde el punto más alto')
    a.add_argument('--ops-mes', type=float, required=True, help='operaciones al mes')
    a.add_argument('--dias-mes', type=int, default=21, help='días que opera al mes (21 = todos los de mercado)')
    a.add_argument('--ops-dia', type=int, help='operaciones máximas por día (si no lo dice: 3 veces su media diaria)')
    a.add_argument('--para-tras', type=int, help='deja de operar el día tras N pérdidas seguidas')
    a.add_argument('--meses', type=int, default=12, help='meses que se simulan')
    a.add_argument('--operaciones', help='CSV de operaciones del backtest')
    a.add_argument('--acierto', type=float, help='%% de ganadoras (sin backtest)')
    a.add_argument('--ratio', type=float, help='ganancia media / pérdida media (sin backtest)')
    a.add_argument('--diario', type=float, help='fondeo: pérdida máxima diaria, %% del saldo al empezar el día')
    a.add_argument('--total', type=float, help='fondeo: pérdida máxima total, %%')
    a.add_argument('--total-arrastrada', action='store_true',
                   help='fondeo: la pérdida total se mide desde el punto más alto (si no, desde el saldo inicial)')
    a.add_argument('--objetivo', type=float, help='fondeo: objetivo de ganancia del examen, %%')
    a.add_argument('--dias-min', type=int, default=0, help='fondeo: días mínimos operados')
    a.add_argument('--sims', type=int, help='cuántas simulaciones (por defecto 10000; menos si hay muchas operaciones)')
    o = a.parse_args()
    if o.caida is None and o.total is None:
        sys.exit('Falta --caida (cuenta propia) o --total (fondeo).')
    # números imposibles: se explica y se sale (un riesgo de 0 % nunca toca la caída: la cuenta no se mueve)
    pct_ok = lambda v: v is None or 0 < v < 100
    num = lambda v: f'{v:g}' if v is not None else v    # 140 y no 140.0
    errores = [m for ok, m in [
        (o.riesgo > 0, f'--riesgo tiene que ser mayor que 0 (es el % por operación); pusiste {o.riesgo:g}.'),
        (o.riesgo <= MAX_RIESGO, f'--riesgo como mucho {MAX_RIESGO} %: nadie debería arriesgar más del {MAX_RIESGO} % '
                                 f'en una operación; pusiste {o.riesgo:g}.'),
        (o.ops_mes > 0, f'--ops-mes tiene que ser mayor que 0; pusiste {o.ops_mes:g}.'),
        (o.ops_mes <= MAX_OPS_MES, f'--ops-mes como mucho {MAX_OPS_MES} (más de 20 al día): con tantas, revisa si de '
                                   f'verdad son operaciones; pusiste {o.ops_mes:g}.'),
        (o.ops_mes * o.meses <= MAX_OPS_CUENTA or o.ops_mes > MAX_OPS_MES,
         f'--ops-mes × --meses como mucho {MAX_OPS_CUENTA} operaciones (por ejemplo 500 al mes en 12 meses): '
         f'la simulación tardaría demasiado; pusiste {o.ops_mes:g} × {o.meses}.'),
        (pct_ok(o.caida), f'--caida tiene que estar entre 0 y 100 (sin incluirlos); pusiste {num(o.caida)}.'),
        (pct_ok(o.total), f'--total tiene que estar entre 0 y 100 (sin incluirlos); pusiste {num(o.total)}.'),
        (pct_ok(o.diario), f'--diario tiene que estar entre 0 y 100 (sin incluirlos); pusiste {num(o.diario)}.'),
        (pct_ok(o.acierto), f'--acierto tiene que estar entre 0 y 100 (sin incluirlos); pusiste {num(o.acierto)}.'),
        (o.ratio is None or o.ratio > 0, f'--ratio tiene que ser mayor que 0; pusiste {num(o.ratio)}.'),
        (o.objetivo is None or o.objetivo > 0, f'--objetivo tiene que ser mayor que 0; pusiste {num(o.objetivo)}.'),
        (1 <= o.dias_mes <= 31, f'--dias-mes tiene que estar entre 1 y 31; pusiste {o.dias_mes}.'),
        (o.ops_dia is None or o.ops_dia >= 1, f'--ops-dia tiene que ser 1 o más; pusiste {o.ops_dia}.'),
        (o.para_tras is None or o.para_tras >= 1, f'--para-tras tiene que ser 1 o más; pusiste {o.para_tras}.'),
        (o.dias_min >= 0, f'--dias-min no puede ser negativo; pusiste {o.dias_min}.'),
        (o.meses >= 1, f'--meses tiene que ser 1 o más; pusiste {o.meses}.'),
        (o.sims is None or o.sims >= 1, f'--sims tiene que ser 1 o más; pusiste {o.sims}.')] if not ok]
    if errores:
        print('Hay números que no pueden ser:\n- ' + '\n- '.join(errores))
        sys.exit(2)
    menos_sims = o.sims is None and o.ops_mes * o.meses * 10000 > OPS_TOTALES
    if o.sims is None:   # con muchas operaciones por cuenta, menos cuentas (nunca menos de 2000): si no, tarda minutos
        o.sims = min(10000, max(SIMS_BUSQUEDA, int(OPS_TOTALES / (o.ops_mes * o.meses)) // 100 * 100))

    if o.operaciones:
        R, nota = leer_r(o.operaciones); fuente = f'backtest ({len(R)} operaciones de {o.operaciones}; {nota})'
        sorteo = lambda: random.choice(R)
        media = st.mean(R)
        g, pe = sum(v for v in R if v > 0), -sum(v for v in R if v < 0)
        fb = g / pe if pe else float('inf')
    elif o.acierto is not None and o.ratio is not None:
        p = o.acierto / 100
        fuente = f'ESTIMACIÓN con supuestos: {o.acierto:.0f} % de acierto, ratio {o.ratio}'
        sorteo = lambda: o.ratio if random.random() < p else -1.0
        media = p * o.ratio - (1 - p)
        fb = p * o.ratio / (1 - p) if p < 1 else float('inf')
    else:
        sys.exit('Falta --operaciones o el par --acierto y --ratio.')

    dias = o.meses * o.dias_mes
    lam = o.ops_mes / o.dias_mes                         # operaciones medias por día que opera
    tope = o.ops_dia or max(1, math.ceil(3 * lam))
    q = min(1.0, lam / tope)

    rnd = random.random

    def ops_hoy():                                       # cuántas operaciones hay hoy (nunca más que el tope)
        return sum([rnd() < q for _ in range(tope)])

    def roto(eq, pico, inicio_dia):
        base = pico if o.total_arrastrada else 100.0
        diario = o.diario and (inicio_dia - eq) / inicio_dia * 100 >= o.diario
        total = o.total and (base - eq) / base * 100 >= o.total
        return diario, total

    def cuenta():
        # las operaciones de una cuenta simulada y, para el límite diario, dónde empieza el día de cada una.
        # No dependen del riesgo: con la misma semilla, la misma secuencia sirve para cualquier riesgo.
        seq, ini = [], []
        for _d in range(dias):
            seguidas = 0; empieza = len(seq)
            for _k in range(ops_hoy()):
                r = sorteo(); seq.append(r); ini.append(empieza)
                seguidas = seguidas + 1 if r < 0 else 0
                if o.para_tras and seguidas >= o.para_tras:
                    break
        return seq, ini

    def evaluar(r, ini, riesgo):
        # la cuenta operación a operación: eq *= 1 + r × riesgo / 100, en el mismo orden que a mano (mismos
        # números, más rápido). Devuelve la peor caída y si rompió la pérdida total y la diaria.
        eq = np.cumprod(np.concatenate([[100.0], 1 + r * riesgo / 100]))
        pico = np.maximum.accumulate(eq)
        eq1, pico1 = eq[1:], pico[1:]
        peor = float(((pico1 - eq1) / pico1 * 100).max(initial=0.0))
        base = pico1 if o.total_arrastrada else 100.0
        t_roto = bool(o.total) and bool(((base - eq1) / base * 100 >= o.total).any())
        d_roto = False
        if o.diario and ini is not None and len(r):
            inicio_dia = eq[ini]                      # saldo al empezar el día de cada operación
            d_roto = bool(((inicio_dia - eq1) / inicio_dia * 100 >= o.diario).any())
        return peor, t_roto, d_roto

    # una sola pasada (semilla 42): las cuentas sirven para el riesgo elegido y las primeras 2000 se guardan
    # para buscar el riesgo máximo. Mismos resultados que volver a simular cada riesgo, en mucho menos tiempo.
    busca = media > 0.005
    rachas, caidas, n_caida, n_total, n_diario, guardadas = [], [], 0, 0, 0, []
    valores = np.unique(R) if o.operaciones else np.array(sorted({o.ratio, -1.0}))   # resultados posibles
    tipo = np.uint16 if len(valores) < 65536 else np.int64
    random.seed(42)
    for i in range(max(o.sims, SIMS_BUSQUEDA if busca else 0)):
        seq, ini = cuenta()
        r, ini = np.array(seq, dtype=float), np.array(ini, dtype=np.int32)
        if i < o.sims:
            peor, t, d = evaluar(r, ini, o.riesgo)
            rachas.append(racha_max(seq)); caidas.append(peor)
            n_caida += o.caida is not None and peor >= o.caida
            n_total += t; n_diario += d
        if busca and i < SIMS_BUSQUEDA:
            guardadas.append(np.searchsorted(valores, r).astype(tipo))   # guardada en poco espacio
    s = dict(rachas=rachas, caidas=caidas, p_caida=n_caida / o.sims * 100,
             p_total=n_total / o.sims * 100, p_diario=n_diario / o.sims * 100)

    def cumple(riesgo):
        # con las 2000 cuentas guardadas: ¿este riesgo cumple el límite?
        n_c = n_t = 0
        for g in guardadas:
            peor, t, _ = evaluar(valores[g], None, riesgo)   # el diario no entra en esta regla
            n_c += o.caida is not None and peor >= o.caida; n_t += t
        if o.total:
            k_ok = not o.diario or perdidas_hasta(o.diario, riesgo) >= 4      # 3 pérdidas seguidas no lo alcanzan
            return n_t / len(guardadas) * 100 <= MAX_P_TOTAL and k_ok
        return n_c / len(guardadas) * 100 <= MAX_P_CAIDA

    print(f'# Tus límites en números\nFuente: {fuente}')
    print(f'Supuestos: {o.riesgo:g} % por operación, {o.ops_mes:g} operaciones al mes en {o.dias_mes} días '
          f'(máximo {tope} al día{f", para tras {o.para_tras} pérdidas seguidas" if o.para_tras else ""}), '
          f'{o.meses} meses, {o.sims} simulaciones'
          + (' (menos que las 10000 habituales: cada cuenta ya tiene muchas operaciones)' if menos_sims else '')
          + ', semilla 42.')
    print(f'Ventaja de esta fuente: {media:+.2f} R por operación · factor de beneficio '
          + ('sin pérdidas (infinito)' if fb == float('inf') else f'{fb:.2f}') + '\n')
    if o.riesgo > 5:
        print(f'AVISO: {o.riesgo:g} % por operación es un riesgo muy alto: unas pocas pérdidas seguidas se llevan '
              'una parte grande de la cuenta.\n')
    if media <= 0.005:                                   # sin ventaja (con margen por redondeo)
        print('AVISO: con estos números el sistema NO tiene ventaja (pierde o empata a la larga). Con cualquier '
              'riesgo, la cuenta termina tocando su caída máxima: la simulación no sirve para decidir el riesgo.\n')
    if o.caida is not None:
        print(f'- Pérdidas seguidas hasta tu caída máxima del {o.caida:g} %: {perdidas_hasta(o.caida, o.riesgo)}')
    print(f'- Peor racha de pérdidas seguidas en {o.meses} meses: la mitad de las veces {pct(s["rachas"],50)} o más; '
          f'1 de cada 20 veces, {pct(s["rachas"],95)} o más')
    print(f'- Peor caída en {o.meses} meses: típica {pct(s["caidas"],50):.1f} %; 1 de cada 20 veces '
          f'{pct(s["caidas"],95):.1f} % o más')
    if o.caida is not None:
        print(f'- Probabilidad de tocar tu caída máxima del {o.caida:g} % en {o.meses} meses: {s["p_caida"]:.1f} %')
    if o.total:
        print(f'- Fondeo: pérdidas seguidas hasta la pérdida total del {o.total:g} % '
              f'({"desde el punto más alto" if o.total_arrastrada else "desde el saldo inicial"}): '
              f'{perdidas_hasta(o.total, o.riesgo)} · probabilidad de tocarla en {o.meses} meses: {s["p_total"]:.1f} %')
    if o.diario:
        k = perdidas_hasta(o.diario, o.riesgo)
        print(f'- Fondeo: la pérdida {k}.ª seguida ya rompe el límite diario del {o.diario:g} % '
              f'({"puede pasar" if k <= tope else "no puede pasar"} en un día con máximo {tope} operaciones) · '
              f'probabilidad de romperlo algún día en {o.meses} meses: {s["p_diario"]:.1f} %')
    if o.objetivo:
        random.seed(42)
        pasa = falla = 0; dias_pasa = []
        for _ in range(o.sims):
            eq = pico = 100.0; operados = 0; fin = None
            for d in range(dias):
                inicio_dia = eq; n = ops_hoy(); operados += n > 0; seguidas = 0
                for _k in range(n):
                    r = sorteo(); eq *= 1 + r * o.riesgo / 100; pico = max(pico, eq)
                    if any(roto(eq, pico, inicio_dia)):
                        fin = 'falla'; break
                    seguidas = seguidas + 1 if r < 0 else 0
                    if o.para_tras and seguidas >= o.para_tras:
                        break
                if fin: break
                if eq - 100 >= o.objetivo and operados >= o.dias_min:
                    fin = 'pasa'; dias_pasa.append(d + 1); break
            pasa += fin == 'pasa'; falla += fin == 'falla'
        print(f'- Fondeo, examen (objetivo +{o.objetivo:g} %, mínimo {o.dias_min} días operados), SI la estrategia '
              f'tiene de verdad esta ventaja: pasa {pasa/o.sims*100:.0f} % · falla por pérdida {falla/o.sims*100:.0f} % · '
              f'sin terminar en {o.meses} meses {(o.sims-pasa-falla)/o.sims*100:.0f} %'
              + (f' · cuando pasa, tarda unos {pct(dias_pasa,50)} días de mercado' if dias_pasa else ''))

    # el riesgo máximo que cumple el límite (búsqueda de 0,05 en 0,05, hasta el 5 %)
    if media > 0.005:
        regla = (f'probabilidad de tocar la pérdida total ≤ {MAX_P_TOTAL} % y 3 pérdidas seguidas sin romper el diario'
                 if o.total else f'probabilidad de tocar tu caída máxima ≤ {MAX_P_CAIDA} %')
        lo, hi = 0, 100                                   # en pasos de 0,05 %
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if cumple(mid * 0.05): lo = mid
            else: hi = mid - 1
        print(f'\nRiesgo máximo que cumple ({regla}): '
              + ('5 % o más (el tope de la búsqueda): mira la caída típica antes de elegir' if lo == 100 else
                 f'{lo * 0.05:.2f} % por operación' if lo else 'ninguno, ni con 0,05 %'))
    print('\nEsto describe el riesgo que eliges, no promete resultados. Con menos de 30 operaciones de '
          'backtest, o sin backtest, es solo una estimación.')


if __name__ == '__main__':
    main()
