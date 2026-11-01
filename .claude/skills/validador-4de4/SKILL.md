---
name: validador-4de4
description: Backtest con costes y veredicto de los 4 números TIS fuera de muestra (fase 04 del método TIS). Úsala cuando la regla ya está en pseudocódigo (fase 03) y hay un CSV de precios en datos/.
---
Entrada: el pseudocódigo de la fase 03 y un CSV de precios en datos/ (nunca uno que termine en
`_nuevo.csv` o `_anterior.csv`). Si existe su informe de calidad
(resultados/<archivo>_calidad.md), léelo: con NO APTA, no hagas el backtest y propone /datos; con
APTA CON AVISOS, copia los avisos en el bloque de la fase 04.
1. La regla se prueba EXACTAMENTE como está escrita. Si algo es ambiguo, pregunta.
2. Backtest con los mismos costes de la fase 02 (o los «Costes por defecto» de metodo/METODO.md,
   «(supuesto)»; no los preguntes). Antes de correr el código, comprueba las librerías
   (AGENTS.md, punto 10).
   Tamaño: SIEMPRE 1 % de riesgo fijo por operación (medida estándar de metodo/METODO.md):
   tamaño = 1 % de la cuenta actual ÷ distancia al stop. Nunca todo el capital ni otro riesgo.
   Caída máxima sobre la curva vela a vela, con operaciones abiertas. Si hace falta apalancamiento,
   dilo en «Supuestos». Escribe el código en codigo/<activo>_<idea_corta>.py (mismo nombre que la
   ficha) para que la fase 05 lo encuentre.
   Guarda las operaciones en resultados/<activo>_<idea_corta>_operaciones.csv con una columna
   «r» (resultado de cada operación en múltiplos del riesgo, con costes) y otra «tramo» (DM/FM):
   la usan la skill objetivos y la fase 06.
   Guarda también la curva vela a vela en resultados/<activo>_<idea_corta>_curva.csv (columnas
   fecha, tramo, cuenta) para que cualquiera pueda comprobar la caída máxima. En el bloque, di
   «caída vela a vela» y, como contexto, la caída cerrando operación por operación.
3. 70 % de datos más antiguos = dentro de muestra; 30 % más recientes = fuera de muestra.
4. Tabla con ✓/✕, fuera de muestra: factor de beneficio ≥ 1,3 · ≥ 30 operaciones ·
   caída máxima < 20 % · factor de beneficio sin la mejor operación > 1.
   Si un número pasa por menos de un 10 % de margen (por ejemplo, sin la mejor operación 1,04,
   o caída de 18,5 %), añade una línea: «pasa justo: es frágil». No cambia el veredicto.
5. Veredicto X/4 (4/4 = APRUEBA). Si falla, di qué número falla y cierra como dice AGENTS.md,
   punto 2 (ideas nuevas, no variantes de esta regla).
6. Escribe el bloque «Fase 04» con la plantilla metodo/plantillas/FICHA.md.
Si no puedes ejecutar un backtest con el CSV, no estimes nada: la fase queda PENDIENTE,
la regla queda lista en piezas y el backtest con código se monta el Día 3 del Reto (carpeta codigo/).
Prohibido: optimizar parámetros para que pase e inventar o estimar resultados.
