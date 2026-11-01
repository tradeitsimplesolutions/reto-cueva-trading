"""Descarga XAU/USD (oro) en velas de 15 minutos desde Dukascopy (sin registro ni claves).

Guarda el CRUDO en datos/crudos/xauusd_15m_dukascopy.csv. Después hay que pasarlo por curar.py.
Precio BID (el de venta del bróker). Fechas en UTC. Volumen = de ticks (actividad en Dukascopy, no volumen real).
Descarga año por año y guarda cada año en datos/crudos/partes/ apenas termina: si se corta internet,
vuelves a correr el mismo comando y sigue donde quedó (los años pasados ya bajados no se repiten).
Uso: python codigo/descargar_xauusd_15m_dukascopy.py
"""
import os, sys, time
from datetime import datetime, timezone
import pandas as pd
import dukascopy_python as d
from dukascopy_python.instruments import INSTRUMENT_FX_METALS_XAU_USD

SALIDA = 'datos/crudos/xauusd_15m_dukascopy.csv'
PARTES = 'datos/crudos/partes'
INICIO, FIN = datetime(2021, 10, 27), datetime.now(timezone.utc).replace(tzinfo=None)
INTENTOS = 4                      # cada año se intenta hasta 4 veces, esperando 10, 20 y 40 segundos

os.makedirs(PARTES, exist_ok=True)
nombre = os.path.splitext(os.path.basename(SALIDA))[0]
archivos, desde = [], INICIO
while desde < FIN:
    hasta = min(datetime(desde.year + 1, 1, 1), FIN)
    parte = f'{PARTES}/{nombre}_{desde.year}.csv'
    archivos.append(parte)
    if os.path.exists(parte) and hasta.year > desde.year:   # año pasado ya completo: no se repite
        print(f'{desde.year}: ya estaba descargado ({parte}).')
        desde = hasta
        continue
    for intento in range(1, INTENTOS + 1):
        try:
            print(f'Descargando {desde:%Y-%m-%d} a {hasta:%Y-%m-%d} (intento {intento} de {INTENTOS})...')
            df = d.fetch(INSTRUMENT_FX_METALS_XAU_USD, d.INTERVAL_MIN_15, d.OFFER_SIDE_BID, desde, hasta)
            break
        except Exception as e:
            if intento == INTENTOS:
                sys.exit(f'Se cortó en el año {desde.year} ({type(e).__name__}: {e}). Vuelve a correr el mismo '
                         'comando y sigue donde quedó.')
            espera = 10 * 2 ** (intento - 1)
            print(f'Falló ({type(e).__name__}). Reintento en {espera} segundos...')
            time.sleep(espera)
    df.reset_index().to_csv(parte + '.tmp', index=False)
    os.replace(parte + '.tmp', parte)          # se escribe completo o no se escribe: nunca un año a medias
    print(f'{desde.year}: {len(df)} velas guardadas en {parte}')
    desde = hasta

# une las partes en el crudo (sin repetir velas en el borde entre años)
df = pd.concat([pd.read_csv(p) for p in archivos])
df = df.drop_duplicates(subset=df.columns[0], keep='last')
os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
df.to_csv(SALIDA, index=False)
print(f'{len(df)} velas guardadas en {SALIDA}')
