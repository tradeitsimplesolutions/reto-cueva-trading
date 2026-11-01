# EasyLanguage (TradeStation) · PowerLanguage (MultiCharts)

Los dos lenguajes son casi iguales: el mismo código suele servir en las dos plataformas.
Igual se entregan por separado, porque cambian los menús y algunos detalles.

Archivos:
- TradeStation: robots/<idea>_tradestation_estrategia.txt y robots/<idea>_tradestation_indicador.txt
- MultiCharts: robots/<idea>_multicharts_estrategia.txt y robots/<idea>_multicharts_indicador.txt
(Es texto para pegar en el editor. TradeStation exporta .eld y MultiCharts .pla: no hace falta.)

En MultiCharts las estrategias se llaman **Signals**. En TradeStation, **Strategies**.

## Estrategia
```
{ <idea> - estrategia - regla de la fase 03 (o regla del trader, sin validar)
  Supuestos: ... }

[IntrabarOrderGeneration = false]   { decide solo al cierre de cada vela }

Inputs:
    Periodo(5);                       { solo los números de la regla }

Vars:
    Minimo5(0), NivelStop(0);

{ Paso 1 · mínimo de los 5 anteriores, sin contar la vela actual }
Minimo5 = Lowest(Low, Periodo)[1];

{ Paso 2 · entrada }
If MarketPosition = 0 and Close < Minimo5 then
    Buy ("Compra") next bar at market;

{ Paso 3 · salida }
If MarketPosition = 1 and Close > Close[1] then
    Sell ("Salida") next bar at market;
```
- **No mirar el futuro:** el código corre al cierre de cada vela; `Close`, `High` y `Low` son de la
  vela que acaba de cerrar. Nunca uses `Open next bar` ni `High next bar` en una condición.
- **Entrada:** `next bar at market` entra en la apertura de la vela siguiente (lo realista).
  `this bar on close` entra al cierre de la vela que decide: úsalo solo si la regla dice
  «al cierre» y márcalo «(supuesto de plataforma)».
- **Stop:** una orden de stop que se envía en cada vela mientras se está dentro:
  `If MarketPosition = 1 then Sell ("Stop") next bar at NivelStop stop;`
  **Y TAMBIÉN en la vela de la entrada.** Si la compra es `this bar on close`, al correr el
  script `MarketPosition` todavía es 0 y la línea de arriba no envía nada: la vela siguiente
  quedaría SIN stop. Junto a la compra, envía el stop inicial:
  ```
  If MarketPosition = 0 and <condicion de entrada> then begin
      NivelStop = <stop de la regla>;
      Buy ("Compra") Tamano contracts this bar on close;
      Sell ("Stop inicial") next bar at NivelStop stop;
  end;
  ```
  TradeStation y MultiCharts aceptan esa orden de salida y la activan en cuanto la compra se
  llena (pide al trader que lo compruebe en la primera operación). Si la vela abre por debajo
  del stop, se llena a la apertura.
  `SetStopLoss` trabaja en dinero por posición, no en precio: no lo uses si la regla da un precio.
- **Stop frente a salida al cierre:** el stop `next bar ... stop` actúa durante la vela; la salida
  `this bar on close` se decide al cierre. Si ya saltó el stop, `MarketPosition` es 0 al cierre y
  la otra salida no se envía: gana el stop.
- **No volver a entrar en la vela de salida:** `SalioEnEstaVela = TotalTrades > 0 and BarsSinceExit(1) = 0;`
  (el `TotalTrades > 0` evita leer `BarsSinceExit` sin operaciones). Con salida `this bar on
  close`, `MarketPosition` sigue en 1 al correr el script y también bloquea la compra.
- **Tamaño al 1 %:** al automatizar la estrategia, la plataforma primero la calcula sobre el
  histórico y `NetProfit` suma esas operaciones SIMULADAS. En vivo, el tamaño sale solo de las
  operaciones en tiempo real: se guarda `NetProfit` en el primer cálculo en tiempo real y se resta.
  En el backtest nunca hay tiempo real y queda igual que la fase 04 (capital + cerradas, compuesto):
  ```
  Inputs: CapitalInicial(10000), RiesgoPct(1);   { junto a los numeros de la regla }
  Vars: EnVivo(false), GananciaHistorico(0), Cuenta(0), Tamano(0);   { junto a las demas Vars }

  { En vivo solo cuentan las operaciones en tiempo real: las del historico son simuladas }
  If EnVivo = false and GetAppInfo(aiRealTimeCalc) = 1 then begin
      EnVivo = true;
      GananciaHistorico = NetProfit;
  end;
  Cuenta = CapitalInicial + NetProfit - GananciaHistorico;

  { Tamano DENTRO de la entrada, despues de fijar el stop de ESTA operacion }
  If MarketPosition = 0 and <condicion de entrada> then begin
      NivelStop = <stop de la regla>;
      Tamano = Cuenta * RiesgoPct / 100 / ((Close - NivelStop) * BigPointValue);
      Buy ("Compra") Tamano contracts this bar on close;
      Sell ("Stop inicial") next bar at NivelStop stop;
  end;
  ```
  `CapitalInicial`: en el backtest, igual al capital inicial de las Propiedades y al de la fase
  04 (en MultiCharts puedes usar `InitialCapital`); en vivo, lo que tiene la cuenta al activarla
  (dilo al trader). Cada vez que la estrategia se vuelve a calcular desde el principio (apagar y
  encender la automatización, cambiar un input, recargar el gráfico), la cuenta vuelve a empezar
  en `CapitalInicial`: antes de activarla otra vez, pon ahí el saldo real de ese momento.
  En MultiCharts, `aiRealTimeCalc` también vale 1 en Playback y con `RecalcLastBarAfter`: no uses
  `RecalcLastBarAfter`. No uses `GetRTAccountNetWorth`: es el saldo actual de toda la cuenta
  (otras estrategias incluidas), no el del backtest. Si al activarla viene con una posición
  abierta del histórico, esa primera operación en vivo lleva una entrada simulada: dilo al trader.
  TradeStation trabaja con unidades ENTERAS y trunca: con poco capital, muchas operaciones dan 0
  y no se hacen. Antes de programar, mira el paso 0.5 de la skill; si el trader solo quiere
  comparar con la fase 04, usa un capital de referencia alto (por ejemplo, 1.000.000 en código y
  en Propiedades; en vivo, otra vez el de su cuenta) y lee los resultados en %. Si da 0, no
  entra y sigue la posición «virtual» de la regla (paso 3 de la skill).
- **Comentarios en ASCII** (sin tildes ni «ñ»), entre llaves `{ }` sin anidar.
- **Ventas:** `SellShort ("Venta") next bar at market;` y `BuyToCover ("Cubre") next bar at market;`
- **Una operación a la vez:** comprueba `MarketPosition = 0` antes de entrar. En Propiedades,
  deja la piramidación desactivada.
- **Temporalidad mayor:** agrega el mismo símbolo como Data2 en el gráfico. `Close of Data2` es
  la última vela de Data2 ya cerrada. Si la regla dice «ayer», compruébalo una vez con
  `Print(Date, " ", Time, " ", Close of Data2);` antes de confiar.
- **Hora:** `Time` es HHMM (la hora de CIERRE de la vela) en la zona horaria del gráfico (de la
  bolsa o local, según la configuración). `Date` tiene formato 1AAMMDD. Escribe la conversión.
  Python fecha por la APERTURA: una vela de 4 h de las 04:00 aquí sale como 0800 (con un feed
  que pone la hora de cierre). Para un mercado 24/7, gráfico en UTC y velas de 4 h desde 00:00.
- **Velas necesarias (MaxBarsBack):** en «automático», o exactamente el periodo más largo de la
  regla + 1 (por ejemplo, 21 para 20 velas). Con más, se pierden las primeras operaciones.
- **Datos:** TradeStation usa sus propios datos (no importa el CSV de la cueva) y puede no tener
  el mismo símbolo; MultiCharts sí puede importar el CSV con QuoteManager. Con otros datos, las
  operaciones no coincidirán una a una con la fase 04: dilo.
- **Costes:** MultiCharts acepta comisión en % del valor. En TradeStation los costes son por
  acción/contrato o por operación: aproxima el % con el precio típico y di que el coste real
  cambia con el precio. Si la fase 04 da un solo % (comisión + deslizamiento), deslizamiento 0.
- **TradeStation y MultiCharts no son idénticos:** cambian los menús, `InitialCapital` (solo MC),
  «Look-Inside-Bar» (TS) frente a «Bar Magnifier» (MC); déjalos desactivados para que el orden
  dentro de la vela sea el de arriba.

## Indicador
```
Inputs: Periodo(5);
Vars: Minimo5(0), Dentro(false), NivelStop(0);
Minimo5 = Lowest(Low, Periodo)[1];
If Dentro = false and Close < Minimo5 then begin
    Plot1(Close, "Entrada");  Dentro = true;  NivelStop = <stop de la regla>;
end else NoPlot(1);
If Dentro and Close > Close[1] then begin
    Plot2(Close, "Salida");  Dentro = false;
end else NoPlot(2);
If Dentro then Plot3(NivelStop, "Stop") else NoPlot(3);
Plot4(Minimo5, "Minimo");          { una linea por cada nivel que usa la regla }
```
- En las propiedades: Plot1 y Plot2 como puntos o flechas; Plot3 y Plot4 como línea.
- `Dentro` copia la lógica de posición de la estrategia (incluido el orden stop → salida y el no
  reentrar) para no repetir entradas. Marca al precio de la regla, no en `High`/`Low`.

## Dónde pegarlo y cómo compilar · TradeStation
1. Abre **TradeStation Development Environment** (TDE).
2. **Archivo → Nuevo → Strategy** (o **Indicator**) con el nombre de la ficha.
3. Pega el código y pulsa **Verify** (verificar). Los errores salen abajo con la línea.
4. En el gráfico: **Insertar → Estrategia** (o Indicador) y elige la tuya.
5. Costes: **Formato → Estrategias → Propiedades para todas → Costes** (comisión y deslizamiento).
   Resultados: **Strategy Performance Report**. Siempre en simulación.

## Dónde pegarlo y cómo compilar · MultiCharts
1. Abre **PowerLanguage Editor**.
2. **Archivo → Nuevo → Signal** (o **Indicator**) con el nombre de la ficha.
3. Pega el código y pulsa **Compilar**. Los errores salen abajo con la línea.
4. En el gráfico: **Insertar → Estrategia** (o Indicador), añade la señal.
5. Costes: **Formato → Propiedades de la estrategia** (comisión y deslizamiento).
   Resultados: **Ver → Informe de rendimiento de la estrategia**. Siempre en simulación.
