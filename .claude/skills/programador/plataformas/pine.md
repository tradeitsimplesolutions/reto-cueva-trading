# Pine Script v6 · TradingView

Archivos: robots/<idea>_pine_estrategia.pine y robots/<idea>_pine_indicador.pine
Primera línea siempre: `//@version=6`. Si el trader tiene un script en v5, avisa y escribe en v6.

## Estrategia
```pine
//@version=6
// Costes: 0,10 % por lado (fase 04, comision + deslizamiento juntos) -> todo en commission_value
// Ordenes: la regla decide AL CIERRE -> process_orders_on_close = true
strategy("<idea> · estrategia", overlay = true,
     initial_capital = 10000,
     commission_type = strategy.commission.percent, commission_value = 0.10,
     slippage = 0,
     margin_long = 100, margin_short = 100,
     process_orders_on_close = true,
     calc_on_every_tick = false,
     pyramiding = 0)

riesgo_pct = input.float(1.0, "Riesgo por operacion (%)")   // 1 % = medida estandar de la fase 04
// Cuenta para el tamano. Backtest: capital inicial + operaciones cerradas (fase 04).
// En vivo (alertas): solo suman las operaciones en tiempo real; las del historico son simuladas.
var float ganancia_historico = na
if barstate.isrealtime and na(ganancia_historico)
    ganancia_historico := strategy.netprofit
cuenta = strategy.initial_capital + strategy.netprofit - nz(ganancia_historico)
// tamano = 1 % de la cuenta / distancia al stop (igual que el backtest de la fase 04)
cantidad(precio_entrada, nivel_stop) => cuenta * riesgo_pct / 100 / math.abs(precio_entrada - nivel_stop)

// No volver a entrar en la vela de salida (protegido para cuando aun no hay operaciones cerradas)
salio_en_esta_vela = strategy.closedtrades > 0 and strategy.closedtrades.exit_bar_index(strategy.closedtrades - 1) == bar_index

// Entrada + stop EN LA MISMA VELA (si no, la primera vela de la operacion queda sin stop)
// if entrada and strategy.position_size == 0 and not salio_en_esta_vela
//     strategy.entry("Compra", strategy.long, qty = cantidad(close, stop_inicial))
//     strategy.exit("Stop", "Compra", stop = stop_inicial)
```
- **NUNCA pongas comentarios dentro de una llamada partida en varias líneas** (como `strategy(...)`
  arriba): puede impedir compilar. Los comentarios, encima. Las líneas que continúan llevan una
  sangría que NO sea múltiplo de 4 (5 espacios).
- **`process_orders_on_close`:** `true` si la regla compra o sale «al cierre de la vela» (lo más
  común en la cueva); `false` si dice «en la apertura de la siguiente». Escríbelo como supuesto.
- **Costes = los de la fase 04, nunca otros.** Si la fase 04 da un solo % por lado (comisión +
  deslizamiento juntos, como los «Costes por defecto»), va entero en `commission_value` y
  `slippage = 0`: si no, se cobra dos veces. Si los da por separado: comisión en %
  (o `strategy.commission.cash_per_order` si es dinero por operación) y el deslizamiento en
  ticks = deslizamiento en precio ÷ `syminfo.mintick`, redondeado hacia arriba, con la cuenta en
  un comentario. Sin fase 04: los «Costes por defecto» de METODO.md, «(supuesto)».
- **No uses `stop` como nombre de variable**: choca con el argumento `stop =` de `strategy.exit`.
- **Tamaño = 1 % de riesgo hasta el stop**, como la fase 04, para que los resultados se puedan
  comparar. Si la entrada es en la apertura siguiente, calcula con `close` y dilo como supuesto.
  Nunca con `strategy.equity`: suma todas las operaciones simuladas del histórico, y una alerta
  en vivo calcularía el tamaño con ganancias que no son de tu cuenta. Con el bloque de arriba,
  en el histórico la cuenta es la de la fase 04 (la misma que `strategy.equity`, porque solo se
  entra sin posición abierta) y en vivo arranca en `initial_capital`. Dile al trader: antes de
  crear la alerta, pon en **Propiedades → Capital inicial** lo que tiene su cuenta. Cada vez que
  la estrategia se vuelve a calcular desde el principio (editar o volver a crear la alerta, o si
  TradingView la reinicia), la cuenta vuelve a empezar en el capital inicial: antes, pon ahí el
  saldo real de ese momento. Si al crear la alerta la estrategia tiene una posición abierta del
  histórico, su cierre en vivo suma un resultado simulado: mejor crearla sin posición abierta.
  Solo importa si el puente usa la cantidad de la estrategia (por ejemplo,
  `{{strategy.order.contracts}}` en el mensaje).
- **Margen:** usa el apalancamiento que dice la fase 04 (si dice «sin apalancamiento», 100). Solo
  si la fase 04 lo usó: `margin_long = 100 / apalancamiento` (1:30 → 3,33), como supuesto de
  plataforma. No lo preguntes.
- Los números de la regla van como constantes, no como `input` (solo el riesgo es `input`):
  así nadie optimiza sin querer desde la ventana de propiedades.
- **Órdenes:** `strategy.entry("Compra", strategy.long)` y `strategy.close("Compra")` para
  salidas por condición. Stop y objetivo fijos: `strategy.exit("Salida", "Compra", stop = nivel_stop, limit = nivel_objetivo)`,
  llamado en la MISMA vela que `strategy.entry`. El parámetro `when` ya no existe: usa `if`.
- **Stop frente a salida al cierre:** la orden de `strategy.exit` se vigila DENTRO de la vela; una
  salida decidida al cierre (`strategy.close`) llega después. Así, si en la misma vela se toca el
  stop y se cumple la salida al cierre, gana el stop (lo habitual en las fichas).
- **Stop con hueco:** si la vela abre ya por debajo del stop, TradingView lo llena a la apertura.
  Es lo que piden las fichas («si abrió por debajo, salgo a la apertura»).
- **Misma vela con stop y objetivo:** TradingView supone un recorrido dentro de la vela (si abre más
  cerca del máximo, va primero al máximo). Escríbelo como supuesto. Con plan Premium o superior se
  puede activar `use_bar_magnifier = true`, que usa velas menores para decidir el orden.
- **Cantidades:** en cripto TradingView acepta decimales; en acciones y futuros redondea a
  unidades enteras (y con poco capital puede dar 0: avísalo, paso 0.5 de la skill).
- **Historial:** TradingView solo prueba las velas que carga el plan del trader (puede ser menos
  que la fase 04) y lleva una sola cuenta (no separa dentro y fuera de muestra): dilo.
- **Horario:** `en_sesion = not na(time(timeframe.period, "0930-1600", "America/New_York"))`.
  Escribe siempre la zona horaria explícita.

## No mirar el futuro ni redibujar
- Decide con valores de velas cerradas. Con `calc_on_every_tick = false` el script corre al cierre:
  `close`, `high`, `low` son de la vela que acaba de cerrar. `high[1]` es la anterior.
- «Los 5 días anteriores sin contar hoy»: `ta.lowest(low, 5)[1]`.
- **Temporalidad mayor** (por ejemplo, el cierre diario en un gráfico de 1 hora), sin redibujar:
  `cierre_ayer = request.security(syminfo.tickerid, "D", close[1], lookahead = barmerge.lookahead_on)`.
  Nunca `lookahead_on` sin el `[1]`.
- Prohibido: `varip`, `barstate.isrealtime` para cambiar la lógica (solo se usa para la cuenta
  del tamaño, arriba), `timenow` en las reglas,
  `request.security` sobre otra temporalidad sin la regla de arriba.

## Alertas (para automatizar con webhook)
- En cada orden de la estrategia añade `alert_message`, por ejemplo:
  `strategy.entry("Compra", strategy.long, alert_message = '{"accion":"compra","simbolo":"' + syminfo.ticker + '"}')`.
  El formato exacto del mensaje lo define el puente que recibe la alerta (el servicio que la
  pasa al bróker o a MetaTrader 5). No lo preguntes al programar: deja este JSON simple marcado
  «(supuesto)» y di que, cuando elija puente, se cambia por el formato de su documentación.
- Al crear la alerta en TradingView, el mensaje es `{{strategy.order.alert_message}}`.
- Los webhooks solo funcionan con plan de pago de TradingView y verificación en dos pasos.

## Indicador
```pine
//@version=6
indicator("<idea> · indicador", overlay = true)
// mismas condiciones que la estrategia, copiadas paso a paso
plotshape(entrada, "Entrada", shape.triangleup, location.belowbar, color.new(color.green, 0), size = size.small)
plotshape(salida, "Salida", shape.xcross, location.abovebar, color.new(color.red, 0), size = size.small)
plot(nivel_stop, "Stop", color.new(color.red, 40), style = plot.style_linebr)
// y una linea por cada nivel que usa la regla (por ejemplo, el maximo de N velas)
alertcondition(entrada and barstate.isconfirmed, "Entrada", "Entrada <idea>")
```
- El indicador no sabe si hay una operación abierta como la estrategia. Lleva esa cuenta con una
  variable `var bool dentro = false` que cambia en la entrada y la salida, con el MISMO orden que
  la estrategia (stop antes que la salida al cierre, sin reentrar en la vela de salida).
- Las alertas de entrada y de salida al cierre llevan `and barstate.isconfirmed`: si no, en vivo
  pueden avisar a mitad de vela y luego desaparecer. La del stop puede ir sin él (el stop actúa
  dentro de la vela); dilo.
- Los `plot` van siempre en el nivel principal del script, nunca dentro de un `if`.

## Dónde pegarlo y cómo compilar (para el trader)
1. Abre un gráfico del activo y la temporalidad de la regla.
2. Abajo, pestaña **Pine Editor** → menú del script → **Crear nuevo** (estrategia o indicador).
3. Borra lo que trae, pega el código y pulsa **Guardar**.
4. Pulsa **Añadir al gráfico**. Si hay errores, salen en la consola de abajo con el número de
   línea: cópialos tal cual y pégaselos al agente.
5. Costes: en la estrategia, ⚙ **Configuración** → **Propiedades** (comisión y deslizamiento).
   Resultados: pestaña **Probador de estrategias**.
