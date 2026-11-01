# Herramientas de tu Cueva

Páginas que se abren con doble clic en tu navegador. Funcionan sin internet y lo que
cargas en ellas no sale de tu computador. Solo lo que copias y pegas en el chat llega a tu IA.

| Herramienta | Día | Para qué sirve |
|---|---|---|
| `auditor-tis.html` | 1 | Lee el historial de tu cuenta de MetaTrader 5 y te dice qué te funciona, qué te cuesta dinero y qué 3 hipótesis vale la pena probar. Luego, en Claude Code: `/auditor`. |

## Cómo usar el Auditor TIS
1. En MetaTrader 5: **Ver → Caja de herramientas → Historial**. Clic derecho → **Todo el historial**.
   Otra vez clic derecho → **Informe → HTML** o **Excel**. Guárdalo en `datos/` (no se sube a GitHub).
2. Abre `herramientas/auditor-tis.html` con doble clic y suelta ahí tu informe.
   ¿No tienes historial? Pulsa **Ver con un historial de ejemplo** (sirve para practicar: no
   describe cómo operas tú, y la cueva no lo usará para tu plan).
3. Pulsa **Copiar para el Director** y abre Claude Code en tu Cueva. En UN solo mensaje escribe
   `/auditor`, un espacio, y pega el informe (Ctrl+V; en Mac Cmd+V). Luego Enter.

Con menos de 30 operaciones, el informe sirve para hacerte preguntas, no para sacar conclusiones.
Tu historial real no es un backtest.
