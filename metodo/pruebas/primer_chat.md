# Prueba · primer chat con la cueva

Conversación real (sin editar) con el modelo **DeepSeek (deepseek-chat)**, el 2026-10-07.

> **Aviso:** esta prueba se grabó con el orden anterior del método (01 Hipótesis, 02 AED).
> Desde noviembre de 2026 el orden es **01 AED, 02 Hipótesis**: primero se escucha al activo y
> después se escribe la regla. La conversación se deja tal cual porque es un registro real.
Instrucciones cargadas: `AGENTS.md` + agente `reglas` + skills `escritor-hipotesis` y `aed` +
`metodo/plantillas/FICHA.md`. En la prueba la IA no podía escribir archivos, por eso entrega la ficha en
el chat y dice dónde guardarla; con Copilot (modo Agent) o Claude Code la guarda ella misma en `fichas/`.

Qué se comprobó:
- Empieza cada fase con «Fase XX · nombre · agente o skill».
- No pregunta nada porque la regla ya es concreta: declara supuestos y avanza.
- Fase 02 queda PENDIENTE sin CSV y no inventa cifras.
- Fase 03: pseudocódigo paso a paso, sin código de ninguna plataforma.
- La FICHA sale con la plantilla fija (cabecera + bloque de 7 líneas por fase).

Puede que tu IA elija otros supuestos (por ejemplo, «rompe» con la mecha o con el cierre):
está bien mientras los declare. Si no te gusta uno, díselo y que lo cambie.

---

### Alumno

Director, esta es mi idea: Compro NAS100 cuando en las 2 primeras velas de 15 min tras la apertura de Nueva York rompe el máximo de la sesión anterior, y en las 8 velas siguientes vuelve a tocar ese nivel y cierra por encima. Salgo si pierde el nivel o al cierre de la sesión. Stop: mínimo de la vela del retesteo.
Pásala por las fases 01 a 03 y guarda la ficha.

---

### Director (DeepSeek)

Fase 01 · Hipótesis · skill escritor-hipotesis

Tu idea ya es concreta (activo, entrada, salida, stop, horario), así que no pregunto: avanzo con supuestos declarados.

**Regla:** Compro NAS100 cuando, en las 2 primeras velas de 15 min tras la apertura de Nueva York, el precio rompe el máximo de la sesión anterior, y en las 8 velas siguientes vuelve a tocar ese nivel y cierra por encima. Salgo si pierde el nivel o al cierre de la sesión. Stop: mínimo de la vela del retesteo. Horario: apertura de Nueva York (9:30 ET).

**Por qué funcionaría (propuesta, confírmala):** el máximo de la sesión previa es un nivel que muchos vigilan. Al romperlo y luego volver a tocarlo, los que compraron en la ruptura aguantan y los que vendieron en el nivel se ven obligados a cubrirse. Es una ineficiencia de comportamiento, no una prima de riesgo.

**Campos:** activo ✅ · temporalidad ✅ · entrada ✅ · salida ✅ · stop ✅ · horario ✅ (con supuestos).

**Supuestos:** (1) «rompe» = la mecha supera el máximo previo. (2) «toca» = la mecha vuelve al nivel. (3) «cierra por encima» = cierre de vela por encima del nivel. (4) apertura NY = 9:30 ET. (5) una sola operación por día.

**Veredicto:** APRUEBA.
**Siguiente paso:** fase 02, AED.

---

Fase 02 · AED · skill aed

No tengo tu CSV en `datos/`, así que no invento cifras. La fase queda **PENDIENTE**.

**Qué bajar:** NAS100 (o NASDAQ:NDX) en velas de 15 min, 3–5 años. En TradingView (computadora) → Exportar datos del gráfico. Solo baja las velas cargadas; para años, usa diario o 1 hora.

**Qué número esperaría ver si la ventaja existe:** que el retorno medio a 5 y 20 velas después del retesteo sea claramente mayor que el retorno medio de cualquier vela, y que se cumpla en varios años, no solo en uno.

**Veredicto:** PENDIENTE (falta el CSV).
**Siguiente paso:** bajar el CSV y repetir la fase 02.

---

Fase 03 · Reglas · agente reglas

```
DATOS: NAS100, velas de 15 min. Hora de referencia: apertura de Nueva York = 9:30 ET.
NIVEL = máximo de la sesión anterior (máximo de todas las velas entre 9:30 y 16:00 ET del día hábil previo).

CADA DÍA, desde la apertura de Nueva York:
  1. VELA DE RUPTURA = la primera de las 2 primeras velas de 15 min (9:30–10:00 ET) cuyo máximo > NIVEL.
     SI ninguna de las 2 velas supera NIVEL → hoy no se opera. FIN del día.
  2. Desde VELA DE RUPTURA, cuento 8 velas siguientes (VENTANA).
     MIENTRAS esté dentro de VENTANA, en cada vela nueva:
       a. SI la vela toca NIVEL (su mínimo ≤ NIVEL) Y cierra por encima de NIVEL:
            COMPRA al cierre de esa vela. STOP = mínimo de esa vela. Ve al paso 3.
       b. SI se agota VENTANA sin cumplirse a. → hoy no se opera. FIN del día.
  3. MIENTRAS esté dentro, en cada vela nueva, en este orden:
       a. SI el precio toca STOP → SALGO.
       b. SI el precio pierde NIVEL (cierre por debajo de NIVEL) → SALGO.
       c. SI llega el cierre de la sesión (16:00 ET) → SALGO.
  4. FIN del día.
```

**Supuestos:** (1) «rompe» = mecha supera NIVEL. (2) «toca» = mecha toca NIVEL. (3) «cierra por encima» = cierre de vela > NIVEL. (4) apertura NY = 9:30 ET. (5) una operación por día. (6) si en la misma vela se tocan stop y salida, manda el stop (se comprueba primero). (7) si la vela de retesteo es la última de la ventana, igual vale. (8) sin operaciones en fin de semana ni festivos de NYSE.

**Veredicto:** APRUEBA (pseudocódigo sin huecos, con supuestos declarados).
**Siguiente paso:** fase 04, cuando tengas el CSV y la fase 02 aprobada.

---

FICHA · nas100_ruptura_retesteo_ny

Regla: Compro NAS100 cuando, en las 2 primeras velas de 15 min tras la apertura de Nueva York, el precio rompe el máximo de la sesión anterior, y en las 8 velas siguientes vuelve a tocar ese nivel y cierra por encima. Salgo si pierde el nivel o al cierre de la sesión. Stop: mínimo de la vela del retesteo. Horario: apertura de Nueva York (9:30 ET).

Por qué funcionaría: el máximo de la sesión previa es un nivel muy vigilado; tras romperlo y retestearlo, los compradores aguantan y los vendedores se cubren. Ineficiencia de comportamiento. (propuesta, confírmala)

## Fase 01 · Hipótesis · CRITERIO
Agente / skill: escritor-hipotesis
Qué se hizo: convertir la idea en regla medible con entrada, salida, stop y horario.
Resultado: regla completa; todos los campos medibles.
Supuestos: rompe = mecha; toca = mecha; cierra por encima = cierre de vela; apertura NY = 9:30 ET; una operación por día.
Veredicto: APRUEBA
Siguiente paso: fase 02, AED.

## Fase 02 · AED · CRITERIO + DATOS
Agente / skill: aed
Qué se hizo: revisar si hay datos para medir la ventaja.
Resultado: no hay CSV en datos/; no se inventan cifras.
Supuestos: NAS100 en 15 min, 3–5 años.
Veredicto: PENDIENTE (falta el CSV de NAS100 en 15 min)
Siguiente paso: bajar el CSV y repetir la fase 02.

## Fase 03 · Reglas · MOTOR
Agente / skill: reglas
Qué se hizo: escribir el pseudocódigo sin ambigüedades.
Resultado: pseudocódigo completo (abajo).
Supuestos: (1) rompe = mecha supera NIVEL. (2) toca = mecha toca NIVEL. (3) cierra por encima = cierre de vela > NIVEL. (4) apertura NY = 9:30 ET. (5) una operación por día. (6) si en la misma vela se tocan stop y salida, manda el stop. (7) la vela de retesteo puede ser la última de la ventana. (8) sin operar en festivos de NYSE.
Veredicto: APRUEBA
Siguiente paso: fase 04 cuando la fase 02 esté aprobada.

```
DATOS: NAS100, velas de 15 min. Hora de referencia: apertura de Nueva York = 9:30 ET.
NIVEL = máximo de la sesión anterior (máximo de todas las velas entre 9:30 y 16:00 ET del día hábil previo).

CADA DÍA, desde la apertura de Nueva York:
  1. VELA DE RUPTURA = la primera de las 2 primeras velas de 15 min (9:30–10:00 ET) cuyo máximo > NIVEL.
     SI ninguna de las 2 velas supera NIVEL → hoy no se opera. FIN del día.
  2. Desde VELA DE RUPTURA, cuento 8 velas siguientes (VENTANA).
     MIENTRAS esté dentro de VENTANA, en cada vela nueva:
       a. SI la vela toca NIVEL (su mínimo ≤ NIVEL) Y cierra por encima de NIVEL:
            COMPRA al cierre de esa vela. STOP = mínimo de esa vela. Ve al paso 3.
       b. SI se agota VENTANA sin cumplirse a. → hoy no se opera. FIN del día.
  3. MIENTRAS esté dentro, en cada vela nueva, en este orden:
       a. SI el precio toca STOP → SALGO.
       b. SI el precio pierde NIVEL (cierre por debajo de NIVEL) → SALGO.
       c. SI llega el cierre de la sesión (16:00 ET) → SALGO.
  4. FIN del día.
```

**Guarda esta ficha en:** `fichas/nas100_ruptura_retesteo_ny.md` (no puedo escribir archivos en este entorno).

---

