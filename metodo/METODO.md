# El método TIS · tu línea de producción de estrategias

> Edítalo: es TU método. El Director (AGENTS.md) lo sigue tal como esté escrito aquí.

Una estrategia es una línea de producción. Entra una idea; sale **validada** o **descartada**.
Cada fase deja su bloque en la FICHA (`metodo/plantillas/FICHA.md`) con un veredicto:
**APRUEBA**, **NO APRUEBA** o **PENDIENTE** (y qué falta).

## Las 8 fases

| Fase | Qué responde | Tipo | Quién en la cueva |
|---|---|---|---|
| 01 AED | ¿Qué hace el activo y el comportamiento que quieres explotar es ventaja o ruido? (AED = análisis exploratorio de datos) | CRITERIO + DATOS | Director + skill aed |
| 02 Hipótesis | ¿Qué regla explota ese comportamiento y por qué existiría la ventaja? | CRITERIO | agente hipotesis + skill escritor-hipotesis |
| 03 Reglas | ¿La regla está escrita sin una sola duda? (pseudocódigo) | MOTOR | agente reglas |
| 04 Backtest | ¿Pasa los 4 números fuera de muestra, con costes? | MOTOR | agente validador + skill validador-4de4 |
| 05 Optimización | ¿Funciona en una meseta de parámetros, no en un pico? | MOTOR | Director + skill optimizar |
| 06 Robustez | ¿Aguanta costes ×2, Monte Carlo y años malos? | MOTOR | Director + skill robustez |
| 07 Tamaño y riesgo | ¿Cuánto riesgo merece? | CRITERIO | tú |
| 08 Puesta en marcha | Demo, servidor, seguimiento | DOCUMENTACIÓN | (se construye en el Reto) |

**Por qué el AED va primero.** Primero se escucha al activo y después viene la idea: como en el
médico, primero los exámenes y después el diagnóstico. Hay dos caminos y los dos empiezan en la 01:
- **Sin idea (lo normal):** el AED explora el activo (quién es, cómo se comporta, lo que cuesta) y
  deja pistas. El trader elige una pista y esa es la que se mide en la 01.
- **Con idea:** el trader la escribe en una frase ANTES de mirar los datos (mejor con pre-registro)
  y el AED la confirma o la descarta.
En los dos casos, la hipótesis completa (fase 02) se escribe con lo que dijo el AED. Única
excepción: si el trader trajo su idea escrita y la 01 queda PENDIENTE por falta de datos, se
pueden adelantar las fases 02 y 03; la 04 nunca aprueba sin la 01.

**Los tres tipos de fase**
- **CRITERIO**: lo decides tú; la IA te ordena las ideas y te pregunta.
- **MOTOR**: lo hace una máquina con datos (la IA con tus datos, un programa).
- **DOCUMENTACIÓN**: dejarlo escrito para poder repetirlo y vigilarlo.

## El Criterio TIS · cuándo aprueba cada fase

| Fase | Aprueba si |
|---|---|
| 01 AED | Con un CSV real y solo en el 70 % más antiguo, el comportamiento que se va a explotar (la idea del trader o la pista que eligió) no es ruido: con pre-registro, cumple lo que escribió el trader; sin pre-registro, cumple las 4 condiciones de abajo. Sin CSV: PENDIENTE. |
| 02 Hipótesis | La regla que explota ese comportamiento tiene activo, entrada, salida, stop y horario medibles, y un porqué escrito (ineficiencia o prima de riesgo). Si el porqué lo propuso la IA, el trader lo confirma o lo cambia antes de la fase 04. |
| 03 Reglas | Pseudocódigo completo: dos personas marcarían las mismas operaciones. Supuestos declarados, ninguno «por definir». |
| 04 Backtest | 4/4 en los 4 números (abajo), fuera de muestra y con costes. |
| 05 Optimización | Meseta: dentro de muestra, todos los vecinos inmediatos tienen factor de beneficio ≥ 1,3, al menos 30 operaciones y conservan al menos el 70 % del factor de beneficio elegido. Y los 4 números siguen 4/4 fuera de muestra. (Provisional del Reto.) |
| 06 Robustez | 4/4: costes ×2 con factor de beneficio ≥ 1,1 · Monte Carlo del orden con caída del percentil 95 < 30 % (al 1 % de riesgo) · remuestreo con factor de beneficio del percentil 5 > 1 · al menos la mitad de los años gana y, sin el mejor año, factor de beneficio > 1. (Provisional del Reto.) |
| 07 Tamaño y riesgo | Riesgo por operación y caída esperada dentro de lo que el trader acepta. Umbral: se fija en el Reto. |
| 08 Puesta en marcha | Ficha completa, demo, servidor y plan de seguimiento con regla de apagado. Umbral: se fija en el Reto. |

Mientras un umbral diga «se fija en el Reto», esa fase no se puede aprobar: queda PENDIENTE.
Los umbrales «provisionales del Reto» sí se aplican: puedes cambiarlos aquí, nunca para que algo pase.

**Fase 01 sin pre-registro · las 4 condiciones** (solo con el 70 % más antiguo; el 30 % se guarda para la fase 04):
1. **Casos:** al menos 30 casos SIN SOLAPARSE: después de un caso, las velas de su horizonte no
   cuentan como casos nuevos (como «una operación a la vez»). Se excluyen los casos cuyo horizonte
   cruza el corte 70/30.
2. **Ventaja:** el retorno medio de cierre a cierre después de la condición, al horizonte que dice
   la idea (si no lo dice, 20 velas), supera al de cualquier vela en más que el coste de ida y
   vuelta (comisión + deslizamiento de las dos puntas: los «Costes por defecto» de abajo). Sin stop:
   la AED mide el comportamiento, no la regla. Si la salida es a una hora fija, el horizonte va hasta
   esa hora y «cualquier vela» son las velas de la misma hora de entrada en todos los días.
3. **No es azar (placebo):** 1.000 veces se sortean, sin reemplazo, tantas velas como casos entre
   todas las velas válidas del 70 %, y se calcula la misma ventaja; menos del 5 % de los sorteos
   iguala o supera a la de la condición (semilla fija, 42).
4. **Se repite:** la ventaja (casos del año frente a cualquier vela del MISMO año, menos el coste)
   sale positiva en al menos la mitad de los años con 5 casos o más.
Con 4/4, APRUEBA. Si falla una, NO APRUEBA y se dice cuál.
Aprobar la fase 04 no hace a una estrategia «validada»: le faltan las fases 05 a 08.

**Costes por defecto (fases 01 y 04 a 06).** Si el trader no da los de su bróker, NO se le pregunta:
se usan los de activos/<activo>.md si existe y, si no, estos, marcados «(supuesto)»:
cripto 0,10 % por lado · oro y plata 0,02 % por lado · índices 0,02 % por lado · acciones y ETF
0,02 % por lado · forex 1 pip por lado. «Por lado» = al entrar y otra vez al salir (comisión +
deslizamiento). Son estimaciones prudentes del Reto, no los costes de un bróker concreto.
Los mismos costes en la fase 01 y en la 04.

**Indicadores por defecto (todas las fases).** Si la regla no dice cómo se calcula un indicador,
se usa el estándar de TradingView y MetaTrader, sin preguntar y sin elegir otro:
ATR (rango medio de las velas) = el de Wilder, 14 velas · media = simple · RSI = Wilder, 14 ·
«el máximo / mínimo de N velas» = de las N velas ANTERIORES, sin la actual · todo se calcula al
cierre de la vela. Si el trader dice otra cosa, manda lo suyo. Lo que cambia la entrada, la
salida o el stop nunca lo decide la IA: o lo dice la regla, o el estándar de aquí.

**Medidas exactas de la fase 01.** «Cualquier vela» = todas las velas del 70 % con horizonte
completo dentro del 70 %, incluidas las de la señal. «Velas válidas» del placebo = esas mismas.
Si la idea tiene una condición Y una ventana horaria (por ejemplo, «si rompe el rango asiático,
entre 07:00 y 10:00»), «cualquier vela» y el placebo usan solo las velas de esa misma ventana,
con el mismo horizonte o la misma hora de salida: se compara con «entrar a esa hora sin la señal».
Si la idea ES el horario (por ejemplo, «comprar a las 16:00 y salir a las 20:00»), se compara con
entrar a cualquier otra hora y mantener la misma duración: «cualquier vela» y el placebo son todas
las velas del 70 %, con el mismo número de velas de horizonte.
Cada ficha anota en «Supuestos» de la fase 01 cuántas ideas se han probado ya sobre ese CSV:
cuantas más, más fácil que una pase por suerte.

**Otra temporalidad.** Si la regla usa velas más grandes que las del CSV (por ejemplo, 4 h con un
CSV de 15 min), se arman así: bloques en hora UTC que empiezan en 00:00 (4 h → 0, 4, 8…; 1 día →
00:00 UTC), apertura = la primera vela, cierre = la última, máximo y mínimo = los extremos,
volumen = la suma. Un bloque al que le falta más de la mitad de sus velas no se usa.

## Los 4 números (fase 04)
Siempre **fuera de muestra** (el 30 % de datos más reciente, que la estrategia no "vio" al
diseñarse) y **con costes**:

1. **Factor de beneficio ≥ 1,3** — lo que ganan las ganadoras ÷ lo que pierden las perdedoras.
2. **Al menos 30 operaciones** — con menos, puede ser suerte.
3. **Caída máxima < 20 %** — la peor bajada desde un máximo de la cuenta.
4. **Factor de beneficio sin la mejor operación > 1** — si sin ella ya no gana, dependía de un golpe de suerte.

Veredicto **X/4**. Solo 4/4 aprueba. **No se bajan nunca** para que algo pase.

**Por qué estos números** (son el criterio de TIS, no una ley del mercado):
- 1,3 y no 1,0: en real todo sale algo peor que en el backtest (costes, ejecución, mercado que
  cambia); un 1,3 deja margen para que, aun así, la estrategia siga ganando.
- 30 operaciones: por debajo, unas pocas operaciones con suerte cambian todo el resultado.
- 20 % de caída al 1 % de riesgo: tras bajar un 20 % hace falta ganar un 25 % para recuperarse;
  más abajo, la recuperación se alarga y cuesta seguir la estrategia sin abandonarla.
- Sin la mejor operación > 1: comprueba que la ventaja está repartida y no viene de un solo golpe.

**Idea nueva o variante.** Una regla que dio NO APRUEBA no vuelve a pasar el mismo examen
cambiándole un número (otro stop, otro periodo, otra hora): eso es una VARIANTE, y su 30 % fuera
de muestra ya está «visto». Una idea nueva cambia el comportamiento que explota (otro porqué),
o se prueba en datos que la regla no usó (otro activo, o años nuevos que aún no existían).
Antes de tener un resultado de la fase 04, el trader sí puede corregir su regla: se rehacen los
bloques desde la fase afectada y se anota la fecha y el cambio en «Qué se hizo».

**Medida estándar del backtest (fases 04 a 06): 1 % de riesgo fijo por operación.**
Cada operación arriesga el 1 % de la cuenta en ese momento: si salta el stop, se pierde el 1 % (más
los costes). El tamaño sale de la distancia al stop: `tamaño = 1 % de la cuenta ÷ (entrada − stop)`.
La caída máxima se mide sobre la curva de la cuenta vela a vela, con las operaciones abiertas
valoradas al cierre de cada vela, ya descontado el coste de salida (como si se cerraran ahí). Dentro y fuera de muestra son dos cuentas separadas que empiezan
igual; una operación abierta en el corte se cierra en la última vela de su tramo. El factor de
beneficio y «la mejor operación» se miden en R (resultado de cada operación ÷ su riesgo, con costes).
Si para arriesgar el 1 % hace falta apalancamiento (comprar más que lo que vale la cuenta), se permite
y se dice cuánto. Sin stop no hay tamaño: la regla no pasa la fase 03.
Es una vara de medir igual para todas las estrategias, no el riesgo con el que vas a operar:
ese se decide en la fase 07, con MI_PLAN.md.

## Reglas de la cueva
- Nunca se salta una fase. Nunca se optimiza para que algo pase.
- Sin datos no hay cifras: la fase queda PENDIENTE.
- 70 % de datos para diseñar, 30 % más reciente para juzgar. Sin costes, el resultado no cuenta.
- Lo que no está documentado no existe: cada fase deja su bloque en la ficha.
- La IA no da señales ni promete rentabilidad. Tú pones el criterio y decides.
- Este criterio es una forma de trabajar, no una garantía de rentabilidad.
