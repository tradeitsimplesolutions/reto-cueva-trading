# NinjaScript · NinjaTrader 8

Archivos: robots/<idea>_ninjatrader_estrategia.cs y robots/<idea>_ninjatrader_indicador.cs
Lenguaje: C#. La CLASE va en PascalCase sin guiones ni tildes (eth-usdt_ruptura_4h →
`EthUsdtRuptura4hEstrategia`): un guion no es válido en C#. Dentro de NinjaTrader el archivo se
crea con el nombre de la clase (paso 2 de abajo); el nombre del archivo en robots/ puede ser otro.
Comentarios en ASCII. Los menús de NinjaTrader suelen estar en inglés: nómbralos en inglés.

## Estrategia
```csharp
#region Using declarations
using System;
using System.ComponentModel.DataAnnotations;
using NinjaTrader.Cbi;
using NinjaTrader.NinjaScript;
using NinjaTrader.NinjaScript.Strategies;
#endregion

namespace NinjaTrader.NinjaScript.Strategies
{
    public class NombreIdeaEstrategia : Strategy
    {
        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "NombreIdeaEstrategia";
                Calculate = Calculate.OnBarClose;        // decide solo al cierre de cada vela
                EntriesPerDirection = 1;                 // una operacion a la vez
                EntryHandling = EntryHandling.AllEntries;
                IsExitOnSessionCloseStrategy = false;    // revisar: si es true cierra todo al final de la sesion
                BarsRequiredToTrade = 21;                // periodo mas largo de la regla + 1, ni mas ni menos
                Slippage = 0;                            // el coste en % va en la plantilla de comision (ver abajo)
            }
            else if (State == State.Configure)
            {
                IncludeTradeHistoryInBacktest = true;    // guarda las operaciones: el tamano las necesita
            }
        }

        protected override void OnBarUpdate()
        {
            if (CurrentBar < BarsRequiredToTrade) return;
            // Paso 1 - ...
        }
    }
}
```
- **No mirar el futuro:** con `Calculate.OnBarClose`, `Close[0]` es la vela que ACABA de cerrar y
  `Close[1]` la anterior. Nunca uses `Calculate.OnEachTick` u `OnPriceChange` para decidir: con
  eso `[0]` es la vela que se está formando.
- «Mínimo de los 5 anteriores sin contar la actual»: `MIN(Low, 5)[1]`.
- **Temporalidad mayor:** en `State.Configure` → `AddDataSeries(BarsPeriodType.Day, 1);`.
  En `OnBarUpdate` trabaja solo cuando `BarsInProgress == 0` y lee `Closes[1][0]`, que es la
  última vela diaria cerrada.
- **Entrada y salidas al cierre:** con `OnBarClose`, una orden decidida al cierre (entrada o
  salida por condición) se llena en la apertura de la vela siguiente. Si la regla dice «al
  cierre», márcalo «(supuesto de plataforma)» para las DOS (entrada y salida).
- **Órdenes:** `EnterLong(contratos, "Compra")`, `ExitLong("Salida", "Compra")`. Stop fijo:
  `SetStopLoss("Compra", CalculationMode.Price, nivel_stop, false)` ANTES de `EnterLong`: queda
  activo desde que se llena la compra y, si hay hueco, se llena a la apertura. Si la regla da el
  stop en ticks o en puntos desde la entrada (por ejemplo, `loss = 200` de Pine, que son TICKS),
  usa `SetStopLoss("Compra", CalculationMode.Ticks, 200, false)`: se mide desde el precio real de
  llenado, como en Pine. No uses
  `ExitLongStopMarket` para el stop inicial: la vela en que se llena la compra queda sin stop.
- **No volver a entrar en la vela de salida:** con una variable propia (por ejemplo,
  «esperaba estar dentro y ya no lo estoy»), NO con `BarsSinceExitExecution() == 0`: como las
  salidas se llenan en la vela siguiente, bloquearía compras válidas.
- **Tamaño al 1 %:** al activar la estrategia en vivo, NinjaTrader primero recorre el histórico
  y hace operaciones VIRTUALES; `AllTrades` las incluye. En vivo, el tamaño sale solo de las
  operaciones en tiempo real (`RealTimeTrades`); en el backtest nunca hay tiempo real y queda
  igual que la fase 04 (capital inicial + operaciones cerradas, con interés compuesto):
  ```csharp
  // Cuenta para el tamano. Backtest: capital + todas las operaciones cerradas (fase 04).
  // En vivo: capital + solo las operaciones en tiempo real (las del historico son virtuales).
  double ganancia = State == State.Realtime
      ? SystemPerformance.RealTimeTrades.TradesPerformance.Currency.CumProfit
      : SystemPerformance.AllTrades.TradesPerformance.Currency.CumProfit;
  double cuenta = CapitalInicial + ganancia;
  int contratos = (int)Math.Floor(cuenta * riesgo_pct / 100 /
      ((Close[0] - nivel_stop) * Instrument.MasterInstrument.PointValue));
  ```
  Va DENTRO de la entrada, después de fijar `nivel_stop` de ESA operación.
  `CapitalInicial` es el único parámetro extra permitido: en el backtest, el de la fase 04; en
  vivo, lo que tiene la cuenta al activarla (dilo al trader). Cada vez que la estrategia se
  vuelve a calcular desde el principio (desactivarla y activarla, cambiar un parámetro, recargar
  el NinjaScript), la cuenta vuelve a empezar en `CapitalInicial`: antes de activarla otra vez,
  pon ahí el saldo real de ese momento. No uses
  `Account.Get(AccountItem.CashValue, Currency.UsDollar)`: es el saldo real, pero suma otras
  estrategias y operaciones manuales y en el backtest no es tu capital. Con el arranque por
  defecto (Start behavior = Wait until flat), si la estrategia trae una posición del histórico,
  NinjaTrader la cierra en virtual y no manda órdenes reales hasta quedar plana; esa operación
  virtual puede sumarse a la cuenta del tamaño. Lo más simple: actívala cuando la estrategia esté
  plana en el gráfico. Dilo al trader. Los contratos son ENTEROS: si da 0, no entra, lo escribe con `Print` y sigue la posición «virtual» de la
  regla (paso 3 de la skill) para no entrar tarde con otra señal. Antes de programar, pregunta el
  instrumento (paso 0.5): con 1 contrato = 1 unidad (ETH, BTC al contado) y poco capital, casi
  ninguna operación llega a 1 contrato; un micro (por ejemplo, el micro de ETH de CME) sí, pero
  no cotiza 24/7 y su precio no es el de los datos de la fase 04.
- **Cierre al final de la sesión:** `IsExitOnSessionCloseStrategy` cierra todo al final del día.
  Ponlo como dice la regla, nunca lo dejes por defecto sin decirlo.
- **Hora:** `ToTime(Time[0])` da HHmmss en la zona horaria de NinjaTrader (Tools → Options →
  General). `Time[0]` es la hora de CIERRE de la vela (Python fecha por la apertura: una vela de
  4 h de las 04:00 aquí es 08:00). Escribe la conversión. Velas de 4 h en un mercado 24/7: usa
  una plantilla de horario 24/7 en UTC para que empiecen a las 00:00 UTC.
- **Costes:** NinjaTrader no cobra comisión en %. Si la fase 04 da un % por lado, conviértelo en
  una plantilla de comisión por contrato ≈ % × precio típico × PointValue, y `Slippage = 0`; di
  que el coste real cambia con el precio (si el activo subió mucho, cambia bastante). El «precio
  típico» es el último cierre del CSV de la cueva si existe; si no hay datos, no lo inventes:
  deja la fórmula y que el trader ponga el precio actual de su gráfico. Si la fase 04 da
  comisión y deslizamiento separados, comisión en la plantilla y deslizamiento en ticks.
  Dónde: la plantilla de comisiones se elige en la cuenta de simulación o en las propiedades del
  Strategy Analyzer (en inglés, «Commission»); si el trader no la encuentra, que busque
  «Commission Templates» en la ayuda de NinjaTrader.
- **Parámetros:** propiedades públicas con `[NinjaScriptProperty]`, `[Range]` y `[Display(Name,
  Order, GroupName)]`, solo las de la regla, el riesgo y `CapitalInicial`.

## Indicador
- Clase en `namespace NinjaTrader.NinjaScript.Indicators`, hereda de `Indicator`,
  `Calculate = Calculate.OnBarClose`, `IsOverlay = true`.
- Marcas: `Draw.ArrowUp(this, "entrada" + CurrentBar, false, 0, Low[0] - 2 * TickSize, Brushes.LimeGreen);`
  y `Draw.ArrowDown(this, "salida" + CurrentBar, false, 0, High[0] + 2 * TickSize, Brushes.Red);`
  (necesita `using System.Windows.Media;` y `using NinjaTrader.NinjaScript.DrawingTools;`).
- Lleva la cuenta de si hay operación abierta para no repetir entradas, con el mismo orden que la
  estrategia. Marca la vela que decide; la estrategia opera en la apertura siguiente: dilo.
- Niveles de la regla (stop, máximos, mínimos) con `AddPlot(Brushes.X, "Nombre")` en SetDefaults
  y `Values[k][0] = valor;` en OnBarUpdate.
- Si la estrategia no entra por falta de contratos, el indicador igual marca la señal de la
  regla: avisa al trader de que verá flechas sin operación.
- NinjaTrader añade solo, al compilar, un bloque «NinjaScript generated code» al final del
  indicador. No lo escribas tú.

## Dónde pegarlo y cómo compilar (para el trader)
1. En NinjaTrader: **New → NinjaScript Editor**.
2. Clic derecho en la carpeta **Strategies** (o **Indicators**) → **New Strategy** → ponle
   exactamente el nombre de la clase (sin guiones).
3. Borra todo el contenido del archivo, pega el código y pulsa **Compilar** (F5).
4. Los errores salen abajo con archivo, línea y código (por ejemplo CS0103). Cópialos tal cual.
   Ojo: un error en CUALQUIER script de la carpeta impide compilar todos.
5. Para probar: **New → Strategy Analyzer**, o en el gráfico clic derecho → **Strategies**,
   añádela y marca **Enabled**. Siempre en cuenta de simulación (Sim101).
