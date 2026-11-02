---
name: aed
description: Análisis exploratorio de datos (fase 01 del método TIS) — escucha al activo y mide si el comportamiento que quieres explotar es ventaja o ruido. Úsala primero, con una idea o sin ella, antes de escribir la hipótesis (fase 02).
---
Es la primera fase: primero se escucha al activo y después viene la idea. Dos caminos:
- SIN IDEA (lo normal): haz el paso 1b. El trader elige una pista y esa pista es lo que mides.
- CON IDEA: el trader la escribe en una frase ANTES de mirar los datos (mejor con
  pre-registro: predicción, línea base, «la descarto si» y dónde más debería aparecer). Cópialo
  tal cual, con su fecha, en «Qué se hizo» del bloque «Fase 01» antes de medir. No lo reescribas
  ni lo mejores. Si pide cambiarlo, es una ENMIENDA: va con fecha y la anterior se conserva.
  El AED confirma o descarta su idea.

Entrada: la ficha de la idea (fichas/) si ya existe, su PRE-REGISTRO si lo tiene, la ficha técnica
del activo (activos/) si existe, la ficha de pistas de AED CLUES si existe
(resultados/<misma ficha>_pistas.html) y un CSV de precios en datos/ (ver datos/LEEME.md).
AED CLUES es una herramienta opcional del Reto que deja esa ficha de pistas; no viene en la
cueva. Si no existe el archivo, sáltate el paso 0 y no la menciones al trader.

0. SI HAY FICHA DE PISTAS DE AED CLUES, esa es tu fuente de números: léela y usa sus casos (n),
   su efecto y su semáforo (clara · se insinúa · nada). No recalcules nada. Respeta su corte:
   los datos reservados no se miran ahora, son para la prueba fuera de muestra de la fase 04.
   Si la pista de la predicción no está en la ficha (por ejemplo, es por hora o por sesión),
   la fase 01 queda PENDIENTE de medición exacta, que se hace con código (codigo/<ficha>_aed.py).

1. REVISA LOS DATOS: nunca uses un CSV que termine en `_nuevo.csv` o `_anterior.csv` (son
   copias apartadas por el agente datos). Nº de velas, primera y última fecha, zona horaria y huecos. Si existe su
   informe resultados/<archivo>_calidad.md y dice NO APTA, PARA y propone /datos. Si dice APTA
   CON AVISOS, sigue y copia los avisos en una frase dentro de «Supuestos» del bloque.
   Si la idea usa otra temporalidad que el CSV, arma las velas como dice metodo/METODO.md
   (Otra temporalidad). Costes: los que dio el trader; si no, los de activos/<activo>.md; si no, los
   «Costes por defecto» de metodo/METODO.md «(supuesto)». No los preguntes y anótalos en
   «Supuestos» del bloque Fase 01: la fase 04 usa los mismos.
   CORTA el 70/30 ANTES de medir nada: usa SOLO el 70 % más antiguo y di la fecha del corte.
   El 30 % más reciente no se mira en esta fase: es el examen de la fase 04.
   Si la ficha técnica de activos/ avisa de días extremos, confirma con el trader que son reales.
1b. SIN IDEA · ESCUCHA AL ACTIVO (solo con el 70 % más antiguo, ya cortado): quién es
    (línea base de velas al alza, movimiento medio, rango de una vela, tendencia de fondo), cómo
    se comporta (si lo de hoy sigue o se devuelve mañana, qué pasa tras días fuertes, sustos,
    rachas de volatilidad, si seguir una media móvil paga) y lo que cuesta frente a lo que se
    mueve. Guárdalo en la ficha técnica activos/<activo>.md. Cada hallazgo, marcado CLARA,
    SE INSINÚA o RUIDO. Con las pistas CLARA o SE INSINÚA propón 2-3 comportamientos concretos
    para medir (A, B, C: condición y horizonte, en palabras sencillas) y la familia a probar
    primero (tendencia o reversión a la media). La pregunta del mensaje es cuál mide. Lo que
    elija abre su ficha en fichas/ y se mide con el paso 2 (sin pre-registro).
    Son pistas del tramo de diseño, no una estrategia: nunca digas que «funciona».
    Anota en «Supuestos» cuántos hallazgos exploraste: cuentan como ideas probadas sobre ese
    CSV (metodo/METODO.md). La pista se buscó en el mismo 70 %: el examen de verdad es el 30 %
    de la fase 04.
2. CON PRE-REGISTRO, júzgala SOLO contra él:
   - Mide la PREDICCIÓN tal como está escrita (el mismo número, la misma condición).
   - Compárala con la LÍNEA BASE que eligió (todas las velas, el mismo horario sin la señal
     o comprar y mantener). Para la línea base de velas al alza, usa la de activos/ si existe.
   - Mira si se cumplió lo que escribió en «LA DESCARTO SI». Si se cumplió, NO APRUEBA,
     aunque «casi» pase. Nunca cambies el pre-registro, el umbral ni la regla para que pase.
   - Si el trader quiere cambiar algo después de ver el resultado, es una ENMIENDA: va con
     fecha, la anterior se conserva, y la nueva versión se mide con datos que no usó (otros
     años u otro activo).
   SIN PRE-REGISTRO: mide el comportamiento elegido (la idea o la pista), sin reglas de
   entrada todavía, y júzgalo con las 4 condiciones de metodo/METODO.md (fase 01 sin
   pre-registro): casos ≥ 30 · ventaja después de costes al horizonte de la idea (o 20
   velas) frente a cualquier vela · placebo de 1.000 sorteos al azar con semilla 42, menos del
   5 % lo iguala · positiva en al menos la mitad de los años con 5 casos o más.
   Muestra también 1 y 5 velas como contexto, pero el veredicto sale solo del horizonte elegido
   ANTES de medir (escríbelo antes de correr el código). Si la idea es de velas diarias (o
   mayores), avisa: hacen falta 30 casos sin solaparse en el 70 %; con 5 años diarios y un
   horizonte de 20 velas casi no se llega (propón un horizonte más corto o 10 años o más).
   Si la idea es de venta, la ventaja
   es que el precio BAJE más que en cualquier vela.
   Si la salida es a una hora fija, el horizonte llega hasta esa hora (metodo/METODO.md, condición 2).
   Escribe el código en codigo/<activo>_<idea_corta>_aed.py para que se pueda repetir.
   Antes de correrlo, comprueba las librerías (AGENTS.md, punto 10).
3. HUELLA: si el pre-registro dice dónde más debería aparecer y hay un segundo CSV, mide la
   misma predicción ahí, sin cambiar nada. Anota si aparece o no.
4. SIN CSV, o si en este computador no puedes ejecutar código (no porque falten librerías: eso
   se instala), NO inventes ni busques cifras.
   Di qué CSV bajar (activo, temporalidad, años) y cómo (datos/LEEME.md). Veredicto: PENDIENTE.
5. Veredicto: APRUEBA (con pre-registro: la predicción supera a la línea base y no se cumplió
   «la descarto si» · sin pre-registro: 4/4 condiciones) · NO APRUEBA (no la supera, falla una
   condición o se cumplió lo que la tumba: di cuál; NO se hacen las fases 02 a 08 con esta idea
   aunque se hayan pedido seguidas; se vuelve al inicio con otra pista u otra idea;
   cierra como dice AGENTS.md, punto 2) · PENDIENTE (faltan datos). Con APRUEBA, el siguiente paso es la fase 02: escribir la
   regla completa que explota este comportamiento (agente hipotesis).
   En el mensaje, cada condición va con su explicación en lenguaje llano: casos («¿pasó
   suficientes veces?»), ventaja («¿gana más que entrar en cualquier momento, pagando costes?»),
   placebo («¿entrar al azar da lo mismo o mejor?») y años («¿funciona en la mayoría de los años?»).
6. Escribe el bloque «Fase 01 · AED · CRITERIO + DATOS» con la plantilla metodo/plantillas/FICHA.md.
   Si la ficha aún no tiene regla completa, la línea Regla dice qué se mide (AGENTS.md · la ficha).
   En «Resultado»: la predicción medida, la línea base, la diferencia, el nº de casos y la huella si la hubo.
   Con menos de 30 casos, dilo: es una pista, no una conclusión (y sin pre-registro, NO APRUEBA).
Prohibido: dar el veredicto por intuición, sin números; mover la meta del pre-registro.
