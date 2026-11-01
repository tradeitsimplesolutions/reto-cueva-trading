# MQL5 · MetaTrader 5

Archivos: robots/<idea>_mt5_estrategia.mq5 (Asesor Experto, EA) y robots/<idea>_mt5_indicador.mq5
Los compilados (.ex5) no se suben a GitHub.

## Estrategia (Asesor Experto)
Estructura mínima:
```mql5
#include <Trade\Trade.mqh>
CTrade trade;

input double riesgo_pct   = 1.0;    // % de la cuenta hasta el stop (1 % = estandar de la fase 04)
input long   numero_magico = 20261;  // identifica las operaciones de este robot
// Solo si la regla tiene horario: input int desfase_horas = 0; (hora del servidor - hora de la regla)

int OnInit()
{
   // PERIOD_H4 = la temporalidad de la regla (cambiala si es otra)
   if(_Period != PERIOD_H4) { Print("Pon el grafico en la temporalidad de la regla"); return INIT_PARAMETERS_INCORRECT; }
   trade.SetExpertMagicNumber(numero_magico);
   trade.SetTypeFillingBySymbol(_Symbol);   // evita el error 10030 (modo de llenado)
   return INIT_SUCCEEDED;
}

void OnTick()
{
   // Decide solo una vez por vela, cuando la anterior acaba de cerrar
   static datetime ultima_vela = 0;
   datetime vela_actual = iTime(_Symbol, _Period, 0);
   if(vela_actual == 0 || vela_actual == ultima_vela) return;
   ultima_vela = vela_actual;

   // A partir de aqui: la vela que decide (la que acaba de cerrar) es el indice 1
   double cierre = iClose(_Symbol, _Period, 1);
   // Paso 1 - ...
}
```
- **No mirar el futuro:** el índice 0 es la vela que se está formando. Nunca la uses para decidir.
  La vela que decide es la 1; las «N velas ANTERIORES a ella» empiezan en el índice 2:
  «mínimo de las 10 velas anteriores, sin contar la que decide» =
  `iLow(_Symbol, _Period, iLowest(_Symbol, _Period, MODE_LOW, 10, 2))`. (Empezar en 1 incluiría la
  vela que decide: un error de una vela que cambia la regla.) Fíjate en que `iLowest` devuelve el
  ÍNDICE de la vela, no el precio.
- **Variables y comentarios en ASCII** (sin tildes ni «ñ»): MetaEditor puede romperlos.
- **Pips y puntos:** en MetaTrader 5, `_Point` es el «punto» (el último decimal). En forex con 5
  decimales (3 en pares con JPY), 1 pip = 10 puntos: «stop de 30 pips» = 300 × `_Point` = 0,0030
  en EURUSD. Un stop «de X pips» se mide desde el precio real de la compra (el Ask); el bróker lo
  ejecuta cuando el Bid llega a él, así que el spread se come parte de esos pips: dilo.
- **Indicadores:** crea el «handle» en `OnInit` (por ejemplo `iMA(...)`) y lee con
  `CopyBuffer(handle, 0, 1, n, buffer)` empezando en 1. Comprueba que `CopyBuffer` devolvió datos.
- **Temporalidad mayor:** `iClose(_Symbol, PERIOD_D1, 1)` es el cierre diario de ayer, ya cerrado.
- **Entrada:** la orden sale en la apertura de la vela nueva (se ejecuta en `OnTick` de la
  primera vela tras el cierre). Si la regla dice «al cierre», es lo más cercano posible en
  MetaTrader 5: márcalo «(supuesto de plataforma)».
- **Órdenes:** `trade.Buy(lotes, _Symbol, 0, stop, objetivo)`; cerrar: `trade.PositionClose(ticket)`.
  **El stop va DENTRO de la orden** (el `stop` de `Buy`): así lo vigila el bróker en cada tick y
  está activo desde el primer momento, aunque el robot solo decida una vez por vela. Si el bróker
  lo rechaza (distancia mínima), el robot lo vigila en cada tick, ANTES de la comprobación de
  vela nueva, y lo dice como supuesto. Si al entrar el precio ya está en el stop o por debajo,
  no entra.
- **Si una orden falla** (`trade.Buy` o `PositionClose` devuelven false): escribe
  `trade.ResultRetcodeDescription()` con `Print` y vuelve a intentarlo en los ticks siguientes de
  la misma vela (una bandera «cierre_pendiente»); nunca marques la operación como cerrada si no
  se cerró.
- **No volver a entrar en la vela de salida:** con una variable propia (por ejemplo, si al empezar
  la vela había posición y ahora no la hay), no leyendo el historial a ciegas.
- **Tamaño por riesgo:** `lotes = AccountInfoDouble(ACCOUNT_EQUITY) * riesgo_pct / 100 /
  (MathAbs(entrada - stop) / SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE) *
  SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE))`, redondeado hacia abajo a
  `SYMBOL_VOLUME_STEP` y dentro de `SYMBOL_VOLUME_MIN`/`SYMBOL_VOLUME_MAX`. Si el lote mínimo
  arriesga más del 1 %, NO entra, lo escribe con `Print` y sigue la posición «virtual» de la regla
  (paso 3 de la skill) para no entrar tarde con otra señal.
  Precios normalizados con `NormalizeDouble(precio, _Digits)`. Respeta la distancia mínima del
  bróker (`SYMBOL_TRADE_STOPS_LEVEL`); si el stop de la regla es menor, avisa, no lo cambies.
- **Una operación a la vez:** antes de entrar recorre las posiciones (`PositionsTotal`,
  `PositionGetTicket`) y cuenta solo las de este símbolo y este `numero_magico`.
- **Hora:** `TimeCurrent()` es la hora del SERVIDOR del bróker, que suele ser distinta de la de
  la regla. Si la regla tiene horario, convierte con `desfase_horas` y escribe el valor que usaste
  (ojo con el horario de verano, marzo y noviembre). Si no tiene horario, no pongas ese parámetro.
- **Velas y precios del bróker:** las velas de 4 h o diarias se arman en la hora del servidor, no
  en UTC, así que no empiezan a la misma hora que las de la fase 04. Y el precio es el del CFD del
  bróker (muchos CFD de cripto cierran el fin de semana). Avisa: las operaciones de MetaTrader 5
  no serán exactamente las de la fase 04, y eso no es un error del código.
- **Cuentas de cobertura (hedging) y de compensación (netting):** el código debe funcionar en las
  dos. Gestiona las posiciones por ticket y número mágico.
- **Costes:** desde el código NO se pueden fijar. El probador usa el spread del historial del
  bróker y la comisión de su configuración, no el % de la fase 04. Dilo como supuesto de
  plataforma y pide al trader que mire en el informe del probador cuánto cobró de verdad.

## Indicador
```mql5
#property indicator_chart_window
#property indicator_buffers 2
#property indicator_plots   2
#property indicator_type1   DRAW_ARROW
#property indicator_color1  clrLimeGreen
#property indicator_label1  "Entrada"
#property indicator_type2   DRAW_ARROW
#property indicator_color2  clrRed
#property indicator_label2  "Salida"
double entradas[], salidas[];
int OnInit()
{
   SetIndexBuffer(0, entradas, INDICATOR_DATA); PlotIndexSetInteger(0, PLOT_ARROW, 233);
   SetIndexBuffer(1, salidas,  INDICATOR_DATA); PlotIndexSetInteger(1, PLOT_ARROW, 234);
   PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   PlotIndexSetDouble(1, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   return INIT_SUCCEEDED;
}
```
- Añade un buffer `DRAW_LINE` por cada nivel que usa la regla (stop, máximos, mínimos), y sube
  `indicator_buffers` e `indicator_plots` a la vez (deben coincidir con los `SetIndexBuffer`).
- En `OnCalculate` recorre solo velas cerradas (no marques la vela actual, `rates_total - 1`).
- Lleva la cuenta de si hay operación abierta, igual que la estrategia, para no repetir entradas.
  La marca va en la vela que decide; el robot opera en la apertura siguiente: escríbelo.

## Compilar desde la cueva
Si MetaTrader 5 está instalado en este computador, compila tú antes de entregar (skill, paso 5):
`python .claude/skills/programador/compilar_mql.py robots/<archivo>.mq5`.

## Dónde pegarlo y cómo compilar (para el trader)
1. En MetaTrader 5: **Herramientas → MetaQuotes Language Editor** (o F4).
2. **Archivo → Nuevo → Asesor Experto (plantilla)** para la estrategia, o **Indicador personalizado**
   para el indicador. Ponle el nombre de la ficha y termina el asistente.
3. Borra todo lo que trae el archivo, pega el código y pulsa **Compilar**.
4. Los errores salen abajo, en **Caja de herramientas → Errores**, con la línea. Cópialos tal cual.
5. En MetaTrader 5: **Navegador → Asesores Expertos**, arrastra el robot al gráfico y activa
   **Trading algorítmico**. Para probarlo: **Ver → Probador de estrategias**, modelo
   «Cada tick basado en ticks reales» (o «OHLC en M1»: con «Solo precios de apertura» el stop
   dentro de la vela no se prueba bien). Siempre en cuenta demo.
