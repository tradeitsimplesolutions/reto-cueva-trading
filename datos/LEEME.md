# datos/ · Aquí van tus CSV de precios

La cueva no tiene datos de mercado propios. Sin un CSV tuyo, la fase 02 (AED) y la
fase 04 (Backtest) quedan PENDIENTE: es lo correcto, no un error.

## ¿De dónde saco los datos? Fuentes gratis

**La forma más fácil:** escribe `/datos` en el chat de tu IA. El agente datos te pregunta qué
necesitas, tú eliges la fuente (Yahoo Finance, Alpaca, Binance, Dukascopy o HistData), y él los
descarga con Python, los cura y te deja aquí un CSV limpio con su informe de calidad.
Si una fuente pide claves (Alpaca para acciones), las escribes TÚ en un archivo `.env` en la
raíz de la cueva; nunca las pegues en el chat.

**A mano**, sin Python, cualquier CSV de precios sirve: el agente datos lo cura igual (dile
«cura mi CSV datos/crudos/<archivo>.csv»). Estas fuentes no piden pago (algunas piden una
cuenta gratis):

| Fuente | Sirve para | Cómo |
|---|---|---|
| **Tu MetaTrader 5** | Lo que opera tu bróker: índices, divisas, oro, cripto | Ver → Símbolos → elige el símbolo → pestaña Barras → elige temporalidad y fechas → Solicitar → Exportar barras |
| **Yahoo Finance** | Acciones, ETF, índices y cripto, en diario | Busca el ticker → Historical Data → periodo Max → Download. Si pide iniciar sesión, la cuenta es gratis |
| **Stooq** (stooq.com) | Índices, acciones, ETF, divisas, materias primas y cripto | Diario con muchos años; 1 hora y 5 minutos solo con las últimas velas. Pide un captcha para descargar |
| **Dukascopy** (dukascopy.com → Historical data export) | Divisas, oro, índices y materias primas, también intradía | Elige instrumento, temporalidad y fechas → descarga en CSV. Puede pedir registrarte gratis |
| **TradingView** | Casi todo | Según tu plan, exportar puede pedir una suscripción de pago. Pasos abajo |

**Qué elegir:**
- Al menos **3 años** (mejor 5 o más): el 30 % más reciente se guarda para el examen de la fase 04.
- Idea de varios días: **velas diarias**. Idea por hora o por sesión: 1 hora o 15 minutos de
  **tu MetaTrader** o de **Dukascopy**.
- Guarda el archivo descargado a mano en `datos/crudos/` y pide al agente datos que lo cure.

## Cómo exportar el CSV desde TradingView
1. Abre TradingView en la computadora (en el celular no se puede exportar).
2. Abre el gráfico del activo (por ejemplo NAS100) y elige la temporalidad (por ejemplo 15 min).
3. Deja el gráfico limpio: sin indicadores (cada indicador añade columnas al archivo).
4. Desplázate hacia la izquierda para cargar todo el historial que quieras: solo se
   exportan las velas que el gráfico tiene cargadas.
5. Menú del gráfico (la flecha junto al nombre del diseño, arriba a la derecha) →
   «Exportar datos del gráfico…» → formato de hora ISO → Exportar.
6. Guarda el archivo en `datos/crudos/` con un nombre claro: `nas100_15m_tradingview.csv`.

Ojo: según tu plan, exportar desde TradingView puede pedir una suscripción de pago, y los
planes gratuitos cargan menos historial. Si no puedes exportar, usa una de las fuentes de arriba.

## Formato del CSV
**Crudo** (lo que bajas a mano, en `datos/crudos/`): tal cual sale de la fuente, sin abrirlo
ni guardarlo en Excel (Excel cambia las comas y las fechas). Por ejemplo, de TradingView:
```
time,open,high,low,close,Volume
2026-01-05T09:30:00-05:00,21500.25,21540.00,21490.50,21530.75,1234
```
Al exportar, elige la hora en formato ISO (con zona horaria).

**Curado** (el que usan las fases, en `datos/`): lo deja el agente datos, siempre igual:
```
fecha,open,high,low,close,volume
2026-01-05T14:30:00Z,21500.25,21540.00,21490.50,21530.75,1234
```
- fecha: fecha y hora de la vela en UTC (hora universal; Nueva York va 4 o 5 horas detrás) ·
  open: apertura · high: máximo · low: mínimo · close: cierre · volume: volumen (puede venir vacío).
- Si tu regla usa una hora local (por ejemplo, las 9:30 de Nueva York), la cueva la convierte desde UTC.

Nada de esta carpeta se sube a GitHub (está en .gitignore): tus datos son tuyos.
