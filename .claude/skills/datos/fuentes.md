# Fuentes de datos gratuitas · cómo descargar cada una con Python

Todas guardan el archivo CRUDO en `datos/crudos/<activo>_<temporalidad>_<fuente>.csv`.
Después, siempre, pasa por `curar.py`. Revisadas en octubre de 2026: si una librería cambió y da
error, lee el mensaje, revisa su documentación y corrige; no inventes funciones.

| Fuente | Mercados | Registro | Volumen | Límites que debes decir |
| --- | --- | --- | --- | --- |
| Yahoo Finance (`yfinance`) | acciones, ETF, índices, cripto, algunas divisas | no | sí (acciones y cripto) | 1 h: últimos ~730 días · 15 min o menos: últimos ~60 días · 1 min: ~30 días |
| Alpaca (`alpaca-py`) | acciones de EE. UU. y cripto | cripto no · acciones sí (claves gratis) | sí | acciones: con el plan gratis puede pedir `feed=DataFeed.IEX` |
| Binance (API pública, sin librería) | cripto (pares contra USDT) | no | sí (real del exchange) | historia desde que el par existe en Binance (ETH y BTC: agosto de 2017) · precio de Binance, puede diferir un poco de otros exchanges |
| Dukascopy (`dukascopy-python`) | forex, metales, índices CFD, algunas cripto | no | de ticks (actividad del bróker, no volumen real del mercado) | precios bid o ask, elige uno y dilo |
| HistData (`histdata`) | forex, algunos índices y petróleo | no | no (siempre 0) | solo 1 minuto · hora de Nueva York SIN cambio de verano (`--zona EST`) · un archivo por mes |
| MetaTrader 5 (exportado a mano) | lo que ofrezca TU bróker | tu cuenta (demo sirve) | de ticks | el historial que guarde tu bróker · hora del SERVIDOR del bróker |
| Tu propio CSV | cualquiera | — | según la fuente | Investing, TradingView, Excel: pásalo directo por `curar.py` |

La lista no es cerrada: si el trader trae otra fuente, úsala con su librería oficial o su API documentada.

Instalar (en Windows usa `python -m pip`: `pip` a secas a veces no existe):
- Lo mínimo, para curar y para las fases 02 a 06:
  `python -m pip install --timeout 120 --retries 10 pandas numpy matplotlib`
- Y solo la librería de la fuente que uses:
  Yahoo `python -m pip install --timeout 120 --retries 10 yfinance` ·
  Alpaca `python -m pip install --timeout 120 --retries 10 alpaca-py` ·
  Dukascopy `python -m pip install --timeout 120 --retries 10 dukascopy-python` ·
  HistData `python -m pip install --timeout 120 --retries 10 histdata`
- Binance no necesita librería: usa `urllib`, que viene con Python.
(`--timeout 120 --retries 10`: con internet lento, espera más y reintenta en vez de fallar a la mitad.)

## Yahoo Finance
```python
import yfinance as yf
df = yf.download("BTC-USD", period="5y", interval="1d", auto_adjust=True, multi_level_index=False)
df.reset_index().to_csv("datos/crudos/btc-usd_1d_yahoo.csv", index=False)
```
- Símbolos de Yahoo: `AAPL`, `SPY`, `^GSPC` (índice), `BTC-USD`, `EURUSD=X`, `GC=F` (futuro de oro).
- `auto_adjust=True` = precios ajustados por splits y dividendos. Decláralo en el informe.
- `period` o `start`/`end`. Para 1 h usa como mucho `period="730d"`.
- Zona: las fechas diarias vienen sin hora; las intradía, con zona del mercado. `--zona America/New_York` para acciones de EE. UU.

## Alpaca
Cripto (sin claves):
```python
from datetime import datetime
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
c = CryptoHistoricalDataClient()
r = CryptoBarsRequest(symbol_or_symbols="BTC/USD", timeframe=TimeFrame.Hour, start=datetime(2021, 1, 1))
c.get_crypto_bars(r).df.reset_index().to_csv("datos/crudos/btc-usd_1h_alpaca.csv", index=False)
```
Acciones (con claves): el trader crea sus claves gratis en alpaca.markets y las escribe ÉL en el
archivo `.env` de la cueva (que nunca se sube a GitHub):
```
ALPACA_API_KEY=...
ALPACA_SECRET_KEY=...
```
Tú NUNCA le pides las claves, no las escribes en el chat ni en ningún archivo, y no las imprimes.
```python
import os
from datetime import datetime
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import Adjustment, DataFeed
env = dict(l.strip().split("=", 1) for l in open(".env") if "=" in l and not l.startswith("#"))
c = StockHistoricalDataClient(env["ALPACA_API_KEY"], env["ALPACA_SECRET_KEY"])
r = StockBarsRequest(symbol_or_symbols="QQQ", timeframe=TimeFrame.Hour, start=datetime(2020, 1, 1),
                     adjustment=Adjustment.ALL, feed=DataFeed.IEX)
c.get_stock_bars(r).df.reset_index().to_csv("datos/crudos/qqq_1h_alpaca.csv", index=False)
```
- Las fechas de Alpaca vienen en UTC. Si no existe `.env` o falta una clave, PARA y explica cómo crearla.

## Binance
Sin claves ni registro. Pide de a 1.000 velas y avanza:
```python
import csv, json, time, urllib.request
PAR, INTERVALO = "ETHUSDT", "4h"          # cámbialos: 1m 5m 15m 30m 1h 4h 1d
URL = (f"https://data-api.binance.vision/api/v3/klines?symbol={PAR}&interval={INTERVALO}&limit=1000"
       "&startTime={}")
filas, desde, ahora = [], 0, int(time.time() * 1000)
while True:
    lote = json.load(urllib.request.urlopen(URL.format(desde)))
    filas += [v[:6] for v in lote if v[6] < ahora]          # solo velas ya cerradas
    if len(lote) < 1000: break
    desde = lote[-1][0] + 1
with open(f"datos/crudos/eth-usdt_{INTERVALO}_binance.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["timestamp", "open", "high", "low", "close", "volume"]); w.writerows(filas)
```
- Intervalos: `1m 5m 15m 30m 1h 4h 1d`. Fechas en milisegundos UTC (`curar.py` las reconoce): `--zona UTC`.
- Al curar: `--mercado cripto`.

## Dukascopy
Por años: cada año se guarda en `datos/crudos/partes/` apenas termina. Si se corta internet, se
vuelve a correr el mismo comando y sigue donde quedó (los años pasados ya bajados no se repiten).
```python
import os, sys, time
from datetime import datetime, timezone
import pandas as pd
import dukascopy_python as d
from dukascopy_python.instruments import INSTRUMENT_FX_MAJORS_EUR_USD
SALIDA, PARTES = "datos/crudos/eurusd_1h_dukascopy.csv", "datos/crudos/partes"
INICIO, FIN = datetime(2019, 1, 1), datetime.now(timezone.utc).replace(tzinfo=None)
os.makedirs(PARTES, exist_ok=True)
nombre = os.path.splitext(os.path.basename(SALIDA))[0]
archivos, desde = [], INICIO
while desde < FIN:
    hasta = min(datetime(desde.year + 1, 1, 1), FIN)
    parte = f"{PARTES}/{nombre}_{desde.year}.csv"
    archivos.append(parte)
    if not (os.path.exists(parte) and hasta.year > desde.year):    # año pasado ya bajado: se salta
        for intento in range(1, 5):                                  # 4 intentos: espera 10, 20 y 40 s
            try:
                print(f"Descargando {desde.year} (intento {intento} de 4)...")
                df = d.fetch(INSTRUMENT_FX_MAJORS_EUR_USD, d.INTERVAL_HOUR_1, d.OFFER_SIDE_BID, desde, hasta)
                break
            except Exception as e:
                if intento == 4:
                    sys.exit(f"Se cortó en el año {desde.year} ({e}). Vuelve a correr el mismo comando y sigue donde quedó.")
                time.sleep(10 * 2 ** (intento - 1))
        df.reset_index().to_csv(parte + ".tmp", index=False)
        os.replace(parte + ".tmp", parte)                            # nunca queda un año a medias
    desde = hasta
df = pd.concat([pd.read_csv(p) for p in archivos])
df.drop_duplicates(subset=df.columns[0], keep="last").to_csv(SALIDA, index=False)
```
- Ejemplo completo con mensajes: `codigo/descargar_xauusd_15m_dukascopy.py`.
- Intervalos: `INTERVAL_MIN_1`, `_MIN_5`, `_MIN_15`, `_MIN_30`, `INTERVAL_HOUR_1`, `_HOUR_4`, `INTERVAL_DAY_1`.
- Los instrumentos están en `dukascopy_python.instruments` (por ejemplo `INSTRUMENT_FX_METALS_XAU_USD`,
  `INSTRUMENT_IDX_AMERICA_E_NQ_100`; el DAX/GER40 es `INSTRUMENT_IDX_EUROPE_E_DAAX`). Búscalo con
  `dir()` si no lo conoces.
- Las fechas vienen en UTC. En 1 minuto, cada año tarda: si quieres tramos más cortos, cambia el año por meses.
- Al curar, pasa `--hasta` con la fecha final que pediste: si la descarga quedó incompleta, `curar.py` lo dice.
- Al curar: oro y plata `--mercado metales`, índices de EE. UU. `--mercado indices`, divisas
  `--mercado forex`. Índices europeos o asiáticos, petróleo y cualquier otro: `--mercado sesion`
  (europeos con `--zona-sesion Europe/Berlin`).

## HistData
```python
from histdata import download_hist_data
# años ya cerrados: el año completo, con month=None
download_hist_data(year="2024", month=None, pair="eurusd", time_frame="M1", platform="ASCII",
                   output_directory="datos/crudos")
# año en curso: mes a mes
download_hist_data(year="2026", month="9", pair="eurusd", time_frame="M1", platform="ASCII",
                   output_directory="datos/crudos")
```
- Años cerrados: SOLO con `month=None` (pedirlos por mes da error). Año en curso: SOLO por mes.
- Cada descarga es un .zip: descomprímelo y une los CSV en uno solo antes de curar. Vienen sin encabezado, con `;` y fecha `AAAAMMDD HHMMSS`:
  `curar.py` los reconoce.
- Siempre `--zona EST` al curar (hora de Nueva York sin cambio de verano). Divisas `--mercado forex`;
  índices (NSXUSD, SPXUSD) `--mercado indices`; petróleo (WTIUSD) y los demás índices
  `--mercado sesion`.
- Para otras temporalidades, primero cura en 1 minuto y después agrupa (resample) a la que necesites.

## MetaTrader 5 (los datos de tu bróker)
Lo más fiel si vas a operar en MT5: es el precio, el horario y el instrumento de tu bróker.
Expórtalo a mano: en MT5, **Ver → Símbolos** (Ctrl+U) → pestaña **Barras** → elige el símbolo, la
temporalidad y las fechas → **Solicitar** → **Exportar barras**. Guarda el CSV en `datos/crudos/`.
- `curar.py` reconoce sus columnas (`<DATE> <TIME> <OPEN>…`).
- Las fechas vienen en la HORA DEL SERVIDOR del bróker: elige `--zona` como dice SKILL.md (paso 4).
- Si en MT5 no ves tantos años, abre el gráfico de ese símbolo y retrocede: MT5 baja más historial.
- La librería de Python `MetaTrader5` (`mt5.copy_rates_range`) también sirve, pero en nuestras
  pruebas falló en Windows con «IPC initialize failed». Si falla, usa el export a mano.

## Investing.com y otras webs sin API
No tienen librería fiable: el trader descarga el CSV a mano (en Investing: Datos históricos → elige
fechas y temporalidad → Descargar; pide una cuenta gratis). `curar.py` entiende sus columnas en
español (Fecha, Último, Apertura, Máximo, Mínimo, Vol.), los números con coma decimal y las fechas
día/mes/año.

## Tu propio CSV (TradingView, Excel, cualquier otro)
Guárdalo en `datos/crudos/` y pásalo por `curar.py`. Reconoce los encabezados más comunes (en inglés,
español y portugués), las fechas UNIX de TradingView y los números con formato de Excel (`;` y coma
decimal). Si no reconoce una columna, dice cuál falta.
