# FICHA · NAS100 ruptura y retesteo en la apertura de Nueva York
Regla: Compro NAS100 cuando en las 2 primeras velas de 15 min tras la apertura de Nueva York rompe el máximo de la sesión anterior y, en las 8 velas siguientes, vuelve a tocar ese nivel y cierra por encima. Salgo cuando pierde el nivel o al cierre de la sesión. Stop: mínimo de la vela del retesteo. Horario: sesión de Nueva York, 9:30-16:00 (hora de Nueva York).
Por qué funcionaría: la apertura concentra órdenes; si el precio supera el máximo de ayer y ese nivel aguanta al volver a probarlo, los vendedores que defendían el máximo se rinden y los que se quedaron fuera compran tarde (ineficiencia de horario). Pierde dinero quien vendió en el máximo esperando un rechazo. (propuesta, confírmala)

## Fase 01 · AED · CRITERIO + DATOS
Agente / skill: director · aed
Qué se hizo: el trader trajo la idea ya escrita, antes de mirar los datos (camino «con idea»: el AED la confirma o la descarta). No hay CSV en datos/; no se mide nada ni se inventan cifras.
Resultado: falta el CSV de NAS100 en velas de 15 min (TradingView → Exportar datos del gráfico; ver datos/LEEME.md). Qué se va a medir: si los días que rompe el máximo de ayer en la apertura y lo retestea, el retorno hasta el cierre es claramente mayor que el de un día cualquiera a esa hora.
Supuestos: ninguno.
Veredicto: PENDIENTE (falta el CSV de NAS100 en 15 min, con al menos 1-2 años)
Siguiente paso: bajar el CSV y repetir la fase 01; mientras tanto, se pueden escribir la hipótesis y las reglas (fases 02 y 03).

## Fase 02 · Hipótesis · CRITERIO
Agente / skill: hipotesis · escritor-hipotesis
Qué se hizo: regla revisada campo a campo con la idea de la fase 01; todos ✅ medibles salvo «sesión anterior» y «rompe», que pasan a supuestos.
Resultado: hipótesis completa: activo, entrada, salida, stop y horario definidos; solo compras.
Supuestos: sesión anterior = 9:30-16:00 de Nueva York del día hábil anterior; «rompe» = el máximo de la vela supera el nivel.
Veredicto: APRUEBA
Siguiente paso: fase 03, pasar la regla a pseudocódigo.

## Fase 03 · Reglas · MOTOR
Agente / skill: reglas
Qué se hizo: la regla en español pasada a pseudocódigo paso a paso, sin código de ninguna plataforma.
Resultado: pseudocódigo sin huecos (abajo); 6 supuestos declarados.
Supuestos: ver la lista debajo del pseudocódigo.
Veredicto: APRUEBA
Siguiente paso: fase 04 con el agente validador cuando la fase 01 tenga datos (tu CSV en datos/).

```
DATOS: velas de 15 minutos de NAS100. Todas las horas en hora de Nueva York.
       Sesión = de 9:30 a 16:00. Vela 1 = la de 9:30, vela 2 = la de 9:45.

CADA DÍA DE MERCADO:
  1. NIVEL = el precio más alto de la sesión anterior (9:30-16:00 del día hábil anterior).

  2. RUPTURA: revisa la vela 1 y luego la vela 2.
       SI el máximo de la vela supera NIVEL → esa es la VELA DE RUPTURA. Ve al paso 3.
       SI ninguna de las dos lo supera → hoy no se opera. FIN del día.

  3. RETESTEO: revisa, una a una, las 8 velas que vienen después de la VELA DE RUPTURA.
       SI el mínimo de la vela es igual o menor que NIVEL
          Y la vela cierra por encima de NIVEL → esa es la VELA DE RETESTEO. Ve al paso 4.
       SI pasan las 8 velas sin retesteo → hoy no se opera. FIN del día.

  4. ENTRADA: COMPRA al cierre de la VELA DE RETESTEO.
       STOP = el mínimo de la VELA DE RETESTEO.

  5. MIENTRAS esté dentro, en cada vela nueva, en este orden:
       a. SI el mínimo de la vela toca STOP → SALGO en STOP.
       b. SI NO, SI la vela cierra por debajo de NIVEL → SALGO al cierre de esa vela.
       c. SI NO, SI es la última vela de la sesión (la de 15:45) → SALGO a su cierre.

  6. Como máximo, una operación por día. FIN del día.
```
Supuestos:
1. Sesión anterior = 9:30-16:00 de Nueva York del día hábil anterior (sin horario extendido).
2. «Rompe» = el máximo de la vela supera NIVEL (basta la mecha, no hace falta cerrar arriba).
3. Las 8 velas del retesteo se cuentan desde la vela siguiente a la de ruptura.
4. «Pierde el nivel» = una vela de 15 min cierra por debajo de NIVEL.
5. Si en la misma vela se toca el STOP y cierra bajo NIVEL, manda el STOP (el peor caso).
6. Una sola operación por día; si se sale, no se vuelve a entrar.
