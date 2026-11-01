# Reto Cueva de Trading · tu repositorio base

Este es tu repositorio para los 5 días del Reto. Aquí vive tu **Cueva TIS**: un **Director**
que conoce el método TIS, **7 agentes**, **skills** (manuales de trabajo) y **herramientas** que llevan cada
idea de trading por las fases del método y la dejan escrita en una **FICHA**.

Lo abres en VS Code, trabajas con tu IA dentro de esta carpeta y lo guardas en tu GitHub.

> La cueva no opera, no da señales y no promete rentabilidad. Ordena tu trabajo para que
> cada idea pase por el método. Tú pones el criterio y decides.

---

## 1 · Crea tu copia (una sola vez)

Un **repositorio** es una carpeta de proyecto guardada en GitHub (una web donde se guardan
proyectos con todas sus versiones). Este es una **plantilla**: un modelo que no editas aquí;
haces tu propia copia privada.

1. Inicia sesión en GitHub (si no tienes cuenta, el video de GitHub del Día 1 la crea contigo).
2. En la página de este repositorio **en GitHub** (en el navegador, no en VS Code), arriba a la
   derecha: **Use this template** → **Create a new repository**.
3. Nombre: `mi-cueva-tis` (o el que quieras) · Visibilidad: **Private** → **Create repository**.

Tu copia es **privada**: ahí van a estar tus estrategias.

## 2 · Ábrela en VS Code

**Antes, instala Git** (una sola vez). GitHub es la web; Git es el programa que guarda las
versiones de tus archivos y que usa VS Code para bajar tu copia. Sin Git, no te aparece «Git: Clone».
- **Windows:** git-scm.com/downloads → Windows → abre el archivo → **Next** en todo → **Install**.
- **Mac:** abre la Terminal, escribe `git --version` y acepta instalar.
- Cierra VS Code por completo y vuelve a abrirlo.
- ¿Ya lo tienes? En VS Code, icono de las ramitas (Control de código fuente): si ves
  «Download Git», te falta.

Conecta tu cuenta: abajo a la izquierda, icono de la personita (Cuentas) → **Iniciar sesión con
GitHub** → **Authorize** en el navegador → vuelve a VS Code.

```
Ctrl+Shift+P (en Mac: Cmd+Shift+P) → escribe «clon» → Git: Clone (o Git: Clonar) → Clone from GitHub
   └─ elige tu repositorio mi-cueva-tis → elige una carpeta (Documentos) → Open / Abrir
```
Si VS Code pregunta «¿Confías en los autores de los archivos de esta carpeta?», responde **Sí, confío**.
Comprueba que en el panel de la izquierda ves `AGENTS.md`, `fichas/` y `metodo/`.

Una sola vez, dile a Git quién eres (menú Terminal → New Terminal), con el mismo correo de GitHub:
```
git config --global user.name "Tu Nombre"
git config --global user.email "tu-correo@ejemplo.com"
```

### Python (para los datos y el backtest)
En esa misma terminal escribe `python --version`.
- Si sale `Python 3.10` o mayor, ya lo tienes.
- Si dice que no se reconoce, o se abre la Microsoft Store: descárgalo de python.org → Downloads.
  Si el instalador muestra la casilla **«Add python.exe to PATH»**, márcala; si se abre una
  ventana negra que pregunta, responde que sí (escribe `y` y Enter). Cierra y vuelve a abrir
  VS Code y prueba otra vez `python --version` (en Windows también vale `py --version`).

Después instala las librerías de la cueva (unas decenas de MB). Si tu internet se corta, o sale
`Could not find a version that satisfies the requirement` (casi siempre es el internet, no que
falte la librería), vuelve a escribir el mismo comando: lo que ya se instaló no se repite.
```
python -m pip install -r requirements.txt --timeout 120 --retries 10
```

## 3 · Activa tu IA (elige UNA)

### En el Reto usamos · Claude Code (de pago)
Necesitas una suscripción de pago de Claude (Pro o superior; mira el precio actual en
claude.com/pricing). Lo usamos con la extensión
de VS Code, que ya trae Claude Code adentro (video 5 del Día 1):
```
Ctrl+Shift+X (Extensiones) → busca «Claude Code» (de Anthropic) → Install
   └─ abre un archivo → icono de chispa, arriba a la derecha → Sign in
```
Abajo del cuadro de texto está el modo de permisos: esta semana elige el modo que **te pide
permiso** antes de cada cambio y cada comando (su nombre cambia según la versión: por ejemplo
«Manual» o «Ask before edits»). Evita los modos automáticos.
Claude Code lee solo `CLAUDE.md` (que remite a `AGENTS.md`), los agentes y las skills.

### Opción gratis · GitHub Copilot (plan Copilot Free)
Copilot ya viene dentro de VS Code. Solo necesitas tu cuenta de GitHub.
```
Barra de abajo → icono de Copilot → «Use AI Features» → inicia sesión → plan Copilot Free
```
Abre el chat (**Ctrl+Alt+I**, en Mac Ctrl+Cmd+I), elige **Agent** para que pueda crear archivos.
Copilot lee `AGENTS.md` solo. El plan gratis tiene un límite mensual de uso.

### Alternativa · DeepSeek con la extensión Cline (pagas solo lo que usas; precios en platform.deepseek.com)
```
Ctrl+Shift+X → busca «Cline» → Install → ⚙️ → API Provider: DeepSeek → pega tu clave
```
Tu clave de API es como una contraseña: no la pegues en ningún archivo ni en el grupo.
Con Cline, empieza tu primer mensaje con: «Lee AGENTS.md y actúa como el Director.»

## 4 · Primer uso

**Con Claude Code** escribe: `/primer-uso`
Revisa que todo esté en su sitio, te explica tu cueva, anota tus niveles en `MI_RETO.md`
y comprueba que tu repositorio está conectado a GitHub.
Luego escribe: `/objetivos`. Arma tu plan de trader (`MI_PLAN.md`): para qué operas, cuánto
riesgo aguantas, tu tiempo. La cueva lo usa para avisarte si una idea no encaja contigo.

**Con Copilot o Cline** escribe:
```
Lee AGENTS.md y explícame en 5 líneas qué hay en esta carpeta y para qué sirve.
```
Y después, para ver al Director trabajar con el Criterio TIS:
```
Director, abre fichas/EJEMPLO_nas100_apertura_ny.md y dime en qué fase está esta idea
y qué le falta para pasar la fase 04.
```
Qué esperar: empieza con «Fase XX · nombre · agente o skill», no inventa cifras (la fase 02
del ejemplo está PENDIENTE porque no hay CSV) y te dice qué falta.

## 5 · Audita tu historial (Misión 1)

1. Abre `herramientas/auditor-tis.html` con doble clic. Se abre en tu navegador, sin internet.
2. Suelta ahí el informe de tu cuenta de MetaTrader 5 (HTML o Excel). Si no tienes, usa el ejemplo.
   Paso a paso en `herramientas/LEEME.md`.
3. Pulsa **Copiar para el Director**, vuelve a Claude Code y, en UN solo mensaje, escribe
   `/auditor`, un espacio, y pega el informe (Ctrl+V; en Mac Cmd+V). Luego Enter.
   El Director guarda 3 fichas de hipótesis en `fichas/` y te pregunta cuál trabajar en el Reto.
   Si usaste el historial de ejemplo, las fichas son de práctica: no describen cómo operas tú.

## Lo que hay en tu cueva

```
mi-cueva-tis/
├─ MI_RETO.md        ← tu progreso: niveles y entregables de cada día
├─ MI_PLAN.md        ← tu plan de trader: hazlo primero, antes de tu primera idea (agente objetivos)
├─ fichas/           ← una FICHA por idea (hay un ejemplo de NAS100)
├─ datos/            ← tus CSV de precios (no se suben a GitHub · lee LEEME.md)
├─ activos/          ← Día 2 · una ficha técnica por activo: costes, horario y línea base
├─ codigo/           ← Día 2-3 · el código de la AED, del backtest y de las descargas
├─ requirements.txt  ← las librerías de Python que usa la cueva
├─ resultados/       ← Día 3 · curvas de equity y reportes
├─ robots/           ← Día 3 · tu estrategia en código para tu plataforma
├─ portafolio/       ← Día 5 · tus estrategias combinadas
├─ herramientas/     ← páginas con doble clic · Día 1: el Auditor TIS
├─ metodo/           ← el método TIS y el Criterio TIS (METODO.md), la plantilla de ficha
└─ AGENTS.md, CLAUDE.md, .claude/, .vscode/  ← el cerebro de tu cueva: no los muevas
```

## Tu semana en la cueva

| Día | Tema | Dónde trabajas | Entregable |
|---|---|---|---|
| 1 · dom 25 | Intro y Fast Start | Toda la cueva · `herramientas/` | Cueva lista + auditoría de tu historial + 3 hipótesis |
| 2 · lun 26 | Pensando en datos | `datos/` · `activos/` · `fichas/` | Hipótesis pre-registrada + ficha técnica + fase 02 |
| 3 · mar 27 | Backtesting y código | `codigo/` · `resultados/` | Skills para programar + primera curva de equity |
| 4 · mié 28 | Tu primer sistema automatizado | `robots/` | Estrategia automatizada y probada en MetaTrader 5 |
| 5 · jue 29 | La visión de portafolio | `portafolio/` | Segunda estrategia + mini portafolio |

## Guarda tu trabajo en GitHub

Cada vez que termines algo, dile a tu IA:
```
Guarda los cambios en GitHub con un mensaje que diga qué hicimos.
```
Si algo se daña: «Muéstrame las últimas versiones y vuelve a la de ayer.»
Nunca se suben tus CSV, tu `.env`, contraseñas ni claves (ya están en `.gitignore`).

## Privacidad · qué sale de tu computador
- **A GitHub** (tu copia privada): fichas, código, informes, `MI_PLAN.md` y `MI_RETO.md`, solo
  cuando tú dices «guarda». Nunca nada de `datos/`, ni `.env`. Si no quieres que tu capital
  quede en `MI_PLAN.md`, dale a /objetivos solo porcentajes («arriesgo 1 %»), no cantidades.
- **Al proveedor de tu IA** (Anthropic con Claude, Microsoft/GitHub con Copilot, DeepSeek con
  Cline): todo lo que escribes en el chat y los archivos que la IA lee para ayudarte, incluidos
  tus CSV y `MI_PLAN.md` (capital, riesgo). Revisa su política de privacidad. No escribas en el
  chat datos que no quieras compartir (claves, contraseñas, número de cuenta).
- **Nada sale**: el Auditor TIS (`herramientas/auditor-tis.html`) calcula todo en tu navegador.
  Solo lo que copias y pegas en el chat llega a la IA.
- Tu `.env` (tus claves) está bloqueado para la IA: no puede abrirlo ni mostrarlo con comandos
  de la terminal (`.claude/settings.json`). Tus scripts de Python sí lo leen, por dentro.
- Si pegas una clave por error en el chat: regenérala en la web del proveedor.

## Si algo no va
- **No veo los agentes** → abriste otra carpeta: abre la que tiene `AGENTS.md`.
- **La IA no actúa como Director** → escribe «Lee AGENTS.md y actúa como el Director».
- **No guarda la ficha** → en Copilot, elige **Agent** (no «Ask»); en Claude Code, acepta el permiso.
- **`/primer-uso` no aparece** → abre Claude Code desde esta carpeta, no desde otra.
- **Otra cosa** → captura de pantalla al grupo del Reto. Te ayudamos.
