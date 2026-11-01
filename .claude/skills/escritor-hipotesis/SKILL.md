---
name: escritor-hipotesis
description: Convierte una intuición de trading en una hipótesis completa y comprobable (fase 01 del método TIS). Úsala cuando el trader trae una idea nueva o una regla para pasar por la fase 01.
---
1. Escucha la idea. Si es vaga, propón 2-3 versiones concretas (activo, temporalidad,
   qué la dispara) y pregunta cuál. Una pregunta por mensaje, máximo 3 en total.
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
5. Veredicto fase 01: APRUEBA (núcleo del trader y todo medible, aunque los detalles sean
   supuestos) → pasa a AED · PENDIENTE (falta algo del núcleo o algo que solo el trader puede
   decidir: di qué). Si falta el stop, propón uno simple y pregunta si lo acepta: hasta que
   diga que sí, la fase queda PENDIENTE (falta confirmar el stop). Si el trader ya dijo
   «ponlo tú» o similar, eso cuenta como su sí (AGENTS.md, punto 4).
   Si la ficha ya tenía un bloque «Fase 01» (por ejemplo, de la skill auditor), reemplázalo
   (AGENTS.md, punto 9): nunca dos bloques de la misma fase.
   Si la idea es de velas diarias (o mayores), avisa en una línea: la fase 02 necesita 30
   casos sin solaparse en el 70 % de los datos; con 5 años diarios y un horizonte de 20 velas
   casi no se llega. Propón un horizonte más corto o más años de datos (10 o más).
6. Escribe el bloque «Fase 01» con la plantilla metodo/plantillas/FICHA.md.
7. Si la hipótesis trae PRE-REGISTRO (predicción, línea base, «la descarto si» y dónde más
   debería aparecer), cópialo tal cual, con su fecha y su huella, en «Qué se hizo» del bloque
   «Fase 01». No lo reescribas ni lo mejores: es lo que el trader se comprometió a medir.
   Si pide cambiarlo, es una ENMIENDA: añade la nueva versión con su fecha y deja la anterior.
Prohibido: prometer que funcionará, añadir lo que no dijo (ventas si solo compra,
indicadores, filtros). Las opciones A/B/C, en palabras sencillas.
