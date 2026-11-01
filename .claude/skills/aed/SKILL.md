---
name: aed
description: Análisis exploratorio de datos (fase 02 del método TIS) — ¿la hipótesis tiene una ventaja estructural o es ruido? Úsala después de aprobar la fase 01.
---
Entrada: la ficha de la hipótesis (fichas/), su PRE-REGISTRO si lo tiene, la ficha técnica
del activo (activos/) si existe, la ficha de pistas de AED CLUES si existe
(resultados/<misma ficha>_pistas.html) y un CSV de precios en datos/ (ver datos/LEEME.md).
AED CLUES es una herramienta opcional del Reto que deja esa ficha de pistas; no viene en la
cueva. Si no existe el archivo, sáltate el paso 0 y no la menciones al trader.

0. SI HAY FICHA DE PISTAS DE AED CLUES, esa es tu fuente de números: léela y usa sus casos (n),
   su efecto y su semáforo (clara · se insinúa · nada). No recalcules nada. Respeta su corte:
   los datos reservados no se miran ahora, son para la prueba fuera de muestra de la fase 04.
   Si la pista de la predicción no está en la ficha (por ejemplo, es por hora o por sesión),
   la fase 02 queda PENDIENTE de medición exacta, que se hace con código el Día 3.

1. REVISA LOS DATOS: nunca uses un CSV que termine en `_nuevo.csv` o `_anterior.csv` (son
   copias apartadas por el agente datos). Nº de velas, primera y última fecha, zona horaria y huecos. Si existe su
   informe resultados/<archivo>_calidad.md y dice NO APTA, PARA y propone /datos. Si dice APTA
   CON AVISOS, sigue y copia los avisos en una frase dentro de «Supuestos» del bloque.
   Si la regla usa otra temporalidad que el CSV, arma las velas como dice metodo/METODO.md
   (Otra temporalidad). Costes: los que dio el trader o, si no, los «Costes por defecto» de
   metodo/METODO.md «(supuesto)»; no los preguntes.
   CORTA el 70/30 ANTES de medir nada: usa SOLO el 70 % más antiguo y di la fecha del corte.
   El 30 % más reciente no se mira en esta fase: es el examen de la fase 04.
   Si la ficha técnica de activos/ avisa de días extremos, confirma con el trader que son reales.
2. CON PRE-REGISTRO, júzgala SOLO contra él:
   - Mide la PREDICCIÓN tal como está escrita (el mismo número, la misma condición).
   - Compárala con la LÍNEA BASE que eligió (todas las velas, el mismo horario sin la señal
     o comprar y mantener). Para la línea base de velas al alza, usa la de activos/ si existe.
   - Mira si se cumplió lo que escribió en «LA DESCARTO SI». Si se cumplió, NO APRUEBA,
     aunque «casi» pase. Nunca cambies el pre-registro, el umbral ni la regla para que pase.
   - Si el trader quiere cambiar algo después de ver el resultado, es una ENMIENDA: va con
     fecha, la anterior se conserva, y la nueva versión se mide con datos que no usó (otros
     años u otro activo).
   SIN PRE-REGISTRO: mide el comportamiento que la hipótesis dice explotar, sin reglas de
   entrada todavía, y júzgalo con las 4 condiciones de metodo/METODO.md (fase 02 sin
   pre-registro): casos ≥ 30 · ventaja después de costes al horizonte de la hipótesis (o 20
   velas) frente a cualquier vela · placebo de 1.000 sorteos al azar con semilla 42, menos del
   5 % lo iguala · positiva en al menos la mitad de los años con 5 casos o más.
   Muestra también 1 y 5 velas como contexto, pero el veredicto sale solo del horizonte elegido
   ANTES de medir (escríbelo antes de correr el código). Si la hipótesis es de venta, la ventaja
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
   condición o se cumplió lo que la tumba: di cuál y vuelve a la hipótesis; NO se hacen las
   fases 03 a 08 con esta regla aunque se hayan pedido seguidas; cierra como dice AGENTS.md,
   punto 2) · PENDIENTE (faltan datos).
   En el mensaje, cada condición va con su explicación en lenguaje llano: casos («¿pasó
   suficientes veces?»), ventaja («¿gana más que entrar en cualquier momento, pagando costes?»),
   placebo («¿entrar al azar da lo mismo o mejor?») y años («¿funciona en la mayoría de los años?»).
6. Escribe el bloque «Fase 02» con la plantilla metodo/plantillas/FICHA.md. En «Resultado»:
   la predicción medida, la línea base, la diferencia, el nº de casos y la huella si la hubo.
   Con menos de 30 casos, dilo: es una pista, no una conclusión (y sin pre-registro, NO APRUEBA).
Prohibido: dar el veredicto por intuición, sin números; mover la meta del pre-registro.
