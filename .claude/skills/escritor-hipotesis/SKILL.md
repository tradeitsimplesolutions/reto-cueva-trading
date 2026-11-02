---
name: escritor-hipotesis
description: Convierte el comportamiento que midió el AED (fase 01) en una hipótesis completa y comprobable: la regla y su porqué (fase 02 del método TIS). Úsala después de la fase 01.
---
0. Lee el bloque «Fase 01 · AED» de la ficha: el comportamiento medido, su horizonte y sus
   números. La regla explota ESE comportamiento: la entrada es su condición y la salida, su
   horizonte (o lo que diga el trader). Si no hay bloque «Fase 01», se hace primero (skill aed).
   Si dice NO APRUEBA, no se escribe hipótesis con esa idea: vuelve a la fase 01 con otra.
   Si dice PENDIENTE por falta de datos, solo puedes escribirla si el trader trajo su idea
   escrita antes de mirar (AGENTS.md, punto 8); si no hay idea ni pista, primero el AED.
1. Escucha la idea. El activo y la condición ya vienen de la fase 01: no cambian. Si falta
   algo, propón 2-3 versiones concretas de salida, stop y horario y pregunta cuál. Una pregunta por mensaje, máximo 3 en total.
   Si ya es concreta (activo, entrada, salida, stop, horario), no preguntes: avanza.
2. Escribe la regla: «Compro/Vendo ___ cuando ___. Salgo cuando ___.» + stop + horario.
   Respeta su dirección: si dijo «compro», solo compras. El tamaño es de la fase 07.
   Si propones un stop, que sea simple (un % o el último mínimo), sin siglas.
3. Escribe el PORQUÉ en 2-3 líneas: ¿ineficiencia (la gente o el horario crean un
   patrón) o prima de riesgo (cobras por aguantar un riesgo que otros no quieren)?
   ¿Quién pierde el dinero que tú ganas? Si el trader no lo dio, márcalo «propuesta, confírmala».
   Un porqué propuesto no frena la fase (no es del núcleo): la fase puede aprobar y el trader
   lo corrige cuando quiera; si lo cambia, el nuevo porqué reemplaza al propuesto.
4. Marca cada campo ✅ medible o ⚠️ ambiguo. Un ⚠️ de DETALLE (si «cruza» es al cierre,
   cuántas operaciones por día, la zona horaria) sin respuesta pasa a «(supuesto)» declarado.
   El NÚCLEO de la idea es del trader y nunca se supone: el activo, QUÉ dispara la entrada,
   QUÉ dispara la salida y el STOP (el stop decide el tamaño de cada operación en el backtest). Si la idea era vaga y el trader no eligió entre tus opciones A/B/C,
   la fase queda PENDIENTE (no elijas tú la A), salvo que te pida expresamente que elijas tú
   (AGENTS.md, punto 4).
5. Veredicto fase 02: APRUEBA (núcleo del trader y todo medible, aunque los detalles sean
   supuestos) → pasa a la fase 03 (reglas) · PENDIENTE (falta algo del núcleo o algo que solo el trader puede
   decidir: di qué). Si falta el stop, propón uno simple y pregunta si lo acepta: hasta que
   diga que sí, la fase queda PENDIENTE (falta confirmar el stop). Si el trader ya dijo
   «ponlo tú» o similar, eso cuenta como su sí (AGENTS.md, punto 4).
   Si la ficha ya tenía un bloque «Fase 02», reemplázalo (AGENTS.md, punto 9): nunca dos
   bloques de la misma fase.
   Si la entrada o la salida que pide el trader no son las que midió el AED, dilo: ese
   comportamiento nuevo se mide primero en la fase 01.
6. Escribe el bloque «Fase 02 · Hipótesis · CRITERIO» con la plantilla metodo/plantillas/FICHA.md
   y completa la línea Regla y la de Por qué arriba de la ficha.
7. El PRE-REGISTRO, si lo hubo, ya está en el bloque «Fase 01»: no lo cambies.
Prohibido: prometer que funcionará, añadir lo que no dijo (ventas si solo compra,
indicadores, filtros). Las opciones A/B/C, en palabras sencillas.
