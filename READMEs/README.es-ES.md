# 🔁 simplicio-tasks — El orquestador de IA universal en bucle

<p align="center">
  <img src="../assets/simplicio-tasks-logo.svg" alt="simplicio-tasks" width="920" />
</p>

<p align="center">
  <a href="https://github.com/wesleysimplicio/simplicio-tasks/stargazers"><img src="https://img.shields.io/github/stars/wesleysimplicio/simplicio-tasks?style=social" alt="Stars"></a>
  <a href="https://github.com/wesleysimplicio/simplicio-tasks"><img src="https://img.shields.io/badge/skill-runtime--agnostic-39FF14" alt="Runtime-agnostic"></a>
  <a href="#-los-43-puntos-de-extensión"><img src="https://img.shields.io/badge/extension%20points-43-00E08A" alt="43 extension points"></a>
  <a href="#-economía-de-tokens"><img src="https://img.shields.io/badge/tokens-up%20to%2096%25%20fewer-green" alt="Up to 96% fewer tokens"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License"></a>
</p>

<p align="center">
  <a href="#-tldr">TL;DR</a> ·
  <a href="#-vs-caveman--rtk">vs caveman & rtk</a> ·
  <a href="#-los-43-puntos-de-extensión">43 puntos</a> ·
  <a href="#-todo-lo-que-incluye">Todo lo que incluye</a> ·
  <a href="#-instalación--uso">Instalación</a>
</p>

<p align="center">
  <strong>🌍 Idiomas:</strong><br>
  <a href="../README.md">🇬🇧 English</a> |
  <a href="README.pt-BR.md">🇧🇷 Português</a> |
  <strong>🇪🇸 Español</strong> |
  <a href="README.fr-FR.md">🇫🇷 Français</a> |
  <a href="README.de-DE.md">🇩🇪 Deutsch</a> |
  <a href="README.it-IT.md">🇮🇹 Italiano</a> |
  <a href="README.ja-JP.md">🇯🇵 日本語</a> |
  <a href="README.ko-KR.md">🇰🇷 한국어</a> |
  <a href="README.zh-CN.md">🇨🇳 简体中文</a> |
  <a href="README.ru-RU.md">🇷🇺 Русский</a> |
  <a href="README.pl-PL.md">🇵🇱 Polski</a> |
  <a href="README.tr-TR.md">🇹🇷 Türkçe</a> |
  <a href="README.nl-NL.md">🇳🇱 Nederlands</a> |
  <a href="README.hi-IN.md">🇮🇳 हिन्दी</a> |
  <a href="README.ar-SA.md">🇸🇦 العربية</a>
</p>

---

## ⚡ TL;DR

**simplicio-tasks** es una única **skill** independiente del runtime que convierte
cualquier LLM potente (Claude, Codex, Copilot, Gemini, Grok, modelos locales) en un
**orquestador autónomo en bucle**. Lo apuntas a un cuerpo de trabajo — *«termina
todas las issues abiertas»*, *«vacía la cola de CI»*, *«drena el tablero de Jira»* —
y ejecuta todo el ciclo de vida por sí solo:

> **descubrir → entender → decidir → actuar → verificar → corregir → registrar → repetir**

Descubre trabajo desde cualquier fuente, elimina duplicados, autoescala una flota de
agentes según tu máquina, implementa cada elemento a través de un bucle de calidad
que **ejecuta el código (no solo lo compila)**, abre PRs, resuelve el feedback de
CI/revisión, hace merge y sigue vigilando **24/7** en busca de trabajo nuevo — todo
ello tras barreras de seguridad y un interruptor de corte de coste estricto.

Lleva **43 puntos de extensión con nombre**. Cada uno tiene un fallback por LLM que
siempre funciona, y cada uno *se enlaza al comando nativo de un runtime anfitrión*
cuando hay uno presente — haciendo el paso determinista y de coste de tokens casi
nulo. **La skill no nombra ningún runtime; el runtime detecta la skill.** Esa
inversión es todo el truco: un protocolo universal, con velocidad nativa opcional
inyectada por debajo.

```text
/simplicio-tasks termine as issues abertas
→ identity + pre-flight (kill-switch, auth, watcher)
→ discover 50 issues · dedup · build dependency DAG
→ autoscale fleet = 14 · pipeline implement→review→merge
→ each item: read body+ACs → orient code → plan → edit → run → verify → PR
→ merge · close with evidence · rollback if main breaks
→ keep polling every ~2 min for new work
```

---

## 🆚 vs caveman & rtk

simplicio-tasks se construyó **tras estudiar a fondo** los dos mejores ahorradores
de tokens de GitHub — [**caveman**](https://github.com/JuliusBrussee/caveman) (74k★,
*comprime la conversación*) y [**rtk**](https://github.com/rtk-ai/rtk) (63k★,
*comprime los comandos*). Integra lo mejor de **ambos** en un orquestador completo.
Ellos reducen tokens; simplicio-tasks **hace el trabajo** y reduce tokens mientras lo
hace.

| | 🪨 **caveman** | ⚙️ **rtk** | 🔁 **simplicio-tasks** |
|---|---|---|---|
| **Qué es** | Skill de Claude Code | Proxy CLI en Rust | Skill independiente del runtime |
| **Idea central** | Hablar más conciso (sin relleno) | Reducir la salida de comandos de desarrollo | **Orquestar todo el trabajo** |
| **Alcance** | Salida de prosa del LLM | Salida de comandos de shell | Ciclo de vida completo del trabajo, de principio a fin |
| **Ahorro de tokens** | ~65% en las respuestas | 60–90% en los comandos | Ambos — catálogo + topes + acotado |
| **¿Hace el trabajo?** | ❌ solo formato | ❌ solo proxy | ✅ descubrir→implementar→merge→cerrar |
| **Autonomía multipaso** | ❌ | ❌ | ✅ pool de workers continuo |
| **Barreras de calidad** | — | — | ✅ gate de AC · verificación-por-ejecución · verificación adversarial · gate de entrega |
| **Seguridad** | — | semgrep, descargos | ✅ veredicto de 4 estados · atestación · escaneo de secretos · gate humano · kill-switch |
| **Bucle 24/7** | ❌ | ❌ | ✅ watcher duradero, autorreparable |
| **Enlace con el runtime** | Claude/Codex/Gemini | cualquiera (proxy de PATH) | **cualquiera** (43 puntos de extensión) |
| **Qué tomamos** | informes concisos de los workers, niveles de densidad, guardia de nunca-parafrasear, línea base honesta | catálogo de reducción por comando, topes por nivel de señal, acotado compuesto, fail-open, veredicto de 4 estados | — |
| **Qué dejamos** | recorte gramatical de palabras (degrada la calidad del código) | registros por lenguaje (específicos del runtime) | — |

> **Rechazamos** a propósito el recorte de palabras estilo «hablar-como-cavernícola»
> de caveman — la *prosa* concisa está bien, pero destrozar la gramática degrada el
> código y las confirmaciones. Mantuvimos la *disciplina* (nunca parafrasear
> código/URLs/rutas), no el truco.

<p align="center">
  <img src="../assets/architecture.svg" alt="architecture" width="900" />
</p>

---

## 🧩 Los 43 puntos de extensión

Cada paso del trabajo ocurre en un **punto de extensión con nombre**. Si un runtime
anfitrión expone una capacidad nativa, esta **se enlaza** (determinista, coste de
tokens casi nulo). En caso contrario, el LLM ejecuta el **fallback** con herramientas
estándar (shell, git, gh, edición de archivos, web). La skill depende de la
abstracción, nunca de un runtime concreto.

### Orquestación y escala
| Punto | Qué hace |
|---|---|
| `orient` | Mapa comprimido del repo/trabajo |
| `normalize` | Elemento de trabajo → esquema canónico |
| `intake` | Ingerir trabajo desde un enlace de sprint/tablero |
| `source_adapter` | Conector de fuente uniforme (list/get/claim/update/attach/close) |
| `autoscale` | Tamaño de flota seguro según el perfil de la máquina |
| `plan` / `decide` | Apoyo a la planificación y la decisión |
| `execute` | Fan-out de agentes locales para trabajo masivo/mecánico |
| `issue_factory` | Bucle completo: descubrir→reclamar→implementar→PR |
| `claim` | Reclamación de elementos atómica y segura entre sesiones |
| `worktree` | Checkout aislado por elemento |
| `dependency_graph` | Ordenamiento DAG reanudable entre elementos |
| `durable_workflow` | Pipeline por elemento como máquina de estados de fases reanudable |
| `work_queue` | Cola de prioridad duradera con reintento automático + bloqueo de escritura |
| `resource_governor` | Estrangulamiento dinámico a mitad de bucle + techos por nivel de máquina |
| `model_route` | El sustrato viable más barato por subtarea (L0→remoto) |
| `model_preflight` | Sondear un modelo usable antes de enrutar la generación |

### Edición, calidad y evidencia
| Punto | Qué hace |
|---|---|
| `deterministic_edit` | Aplicación mecánica y de cero tokens de un cambio decidido |
| `diagnostics` | Parsear la salida de build/test → errores estructurados → iterar |
| `toolchain_detect` | Detectar la pila real de build/lint/typecheck/test del repo |
| `validate` / `smoke` | Verificación-por-ejecución: «funciona, no solo compila» |
| `delivery_gate` | DoD: comprobación de AC + regresión + revisión del diff + certificado |
| `endpoint_compare` | Deriva Web↔API↔agente → elementos de seguimiento |
| `web_verify` | Conducir un navegador real para probar que un cambio de UI funciona |
| `pr` / `evidence` | Apertura/actualización de PR + libro de evidencia verificable |
| `retry` | Reintento+backoff clasificado por clase de fallo |
| `reuse_precedent` | Emparejar una ejecución resuelta previa → reutilizar, no regenerar |
| `trajectory` | Registrar el resultado de la ejecución para la automejora |
| `learn` | Aprender de una ejecución — actualizar precedentes/memoria |
| `status` | Panel de observabilidad en vivo |
| `capability_rank` | Clasificar qué skill/herramienta encaja en una subtarea |

### Tokens, contexto y seguridad
| Punto | Qué hace |
|---|---|
| `recall` | Decisiones / precedentes previos |
| `compress` | Compresión de contexto / acotado de salida |
| `prompt_budget` | Envoltura de prompt con presupuesto de tokens + caché de fragmentos |
| `shell_exec` | Ejecución de shell acotada (estructurada, limitada) |
| `transform_guard` | Verificar que una compactación conservó cada token de código/URL/ruta/versión |
| `action_gate` | Clasificar el riesgo de cada mutación (safe/auto/ask) antes de ejecutarla |
| `security` | Escaneo de cadena de suministro / secretos |
| `human_gate` | Canal de aprobación humana asíncrono |
| `notify` | Enviar progreso/bloqueo/resumen + recibir aprobaciones |
| `checkpoint_restore` | Capturar el estado antes de un lote arriesgado; restaurar en caso de fallo |
| `watcher` | Planificador / sondeador duradero (sobrevive a reinicios) |
| `savings_ledger` | Seguimiento real del gasto de tokens por sesión |
| `web_research` | Obtener conocimiento externo actual, controlado, con procedencia |

---

## 📦 Todo lo que incluye

Un inventario completo de lo que lleva la skill — cada mecanismo, citado.

### El bucle (7 pasos + subpasos)
- **Paso 0** — Cargar el contrato (protocolo canónico).
- **Paso 1** — Identidad + detección barata del entorno.
- **Paso 1b** — Los 43 puntos de extensión (enlace nativo o fallback por LLM).
- **Paso 1c** — Gate de economía de tokens: `THINK / NO-THINK`, `INTERNET off by default`,
  `terminal-first execution`, **catálogo de reducción de salida**, **topes por nivel de señal**,
  **colapso de éxitos + dedup**, **acotado de comandos compuestos**, **niveles de densidad
  enrutados por consumidor**, **fail-open**, **auto-claridad (la seguridad anula la brevedad)**.
- **Paso 1d** — Pre-flight: presupuesto del kill-switch, auth de la fuente, armar el watcher.
- **Paso 2** — Descubrir + normalizar elementos de trabajo (cualquier adaptador de fuente).
- **Paso 2b** — Ingesta profunda: leer el cuerpo + comentarios completos, extraer **criterios
  de aceptación**, **orientar el código**, **modo de lectura solo-firmas**, construir un plan.
- **Paso 2c** — DAG de dependencias + planificación topológica.
- **Paso 3** — Enrutador de doble vía: pool de workers continuo **vía rápida** vs **vía pesada**
  · **aislamiento consciente de conflictos** · **contrato de informe del worker** · **memoria
  de correcciones**.
- **Paso 3b** — Ingesta continua: sondeador intra-ejecución + watcher en reposo (ve trabajo
  nuevo en cualquier minuto).
- **Paso 3c** — Modelo de velocidad: pipeline (no barrera), caché de compilación compartida,
  verificar-una-vez-al-merge, **digest de contexto compartido**.
- **Paso 3d** — Enrutamiento de modelos L0→L4 (determinista → local → medio → razonamiento → pago).
- **Paso 4** — Bucle de calidad · **gate de AC (DoD real)** · **verificación-por-ejecución** ·
  **verificación adversarial multi-voto** · **gate de análisis estático**.
- **Paso 5** — Barreras de seguridad: escaneo de secretos, gate humano para ops irreversibles,
  **veredicto pre-ejecución de 4 estados**, **atestación compuesta por segmento**, **config
  de confiar-antes-de-cargar**, **gate de integridad de la cadena de suministro**, **transform_guard**.
- **Paso 6** — Entregar + cerrar + autoauditoría · **paquete de evidencia** · **verificar
  la realidad (nunca confiar en el autoinforme)** · **rollback-guard si el merge rompe main**.
- **Paso 6b** — Cerrar el bucle de feedback: CI → arreglar, comentarios de revisión → resolver,
  rama-atrasada → reconciliar, **ciclo de vida del PR** completo hasta estar listo para merge.
- **Paso 7** — Bucle permanente 24/7 (10 ejes): driver duradero, matriz de cobertura total,
  estado duradero, **gobernanza de costes + kill-switch estricto**, seguridad desatendida,
  autorreparación + **reintento inteligente por clase de fallo**, priorización/WIP,
  observabilidad + **auditoría periódica de ahorro** + **medición por snapshot**,
  automejora, coordinación y parada limpia.

### Economía de tokens (integrada desde rtk + caveman)
- Ejecución terminal-first — nunca simular un comando.
- Tabla de sustitución **multiplataforma** (Windows / macOS / Linux): más de 30 hechos que la
  terminal responde más barato que el LLM.
- **Catálogo de reducción de salida** como datos: receta por comando, % de ahorro esperado,
  guardia `skip-if-structured`.
- **Topes por nivel de señal**: `CAP_ERRORS / CAP_WARNINGS / CAP_LIST / CAP_INVENTORY`.
- **Colapso de éxitos** + **dedup-con-recuentos** (con una guardia `unless errors`).
- **Acotado de comandos compuestos** — por segmento, seguro con pipes/redirecciones, fail-open.
- **Niveles de densidad por consumidor** (máquina vs humano); omitir el contenido ya denso.
- **Contrato de informe del worker** — esquema conciso con el token de estado primero para los subagentes.
- **Línea base de ahorro honesta** = un brazo de control realista, **ligada a un gate de calidad
  que pasa** (la compresión que falla su gate gana cero crédito).

### Calidad y entrega
- Lista de verificación DoD de criterios de aceptación · verificación-por-ejecución · verificación
  adversarial · gate de análisis estático · certificado de entrega · reverificación de la realidad ·
  rollback automático.

### Seguridad
- Escaneo de secretos · gate humano para ops irreversibles · veredicto de 4 estados (nunca escalar
  privilegios) · atestación de comandos compuestos · confiar-antes-de-cargar · integridad de la
  cadena de suministro · endurecimiento contra inyección de prompts · kill-switch estricto en $
  para ejecuciones desatendidas.

### Autonomía 24/7
- Planificador duradero · cola en vivo + watcher en reposo · diario/estado duradero ·
  cortacircuitos · cuarentena dead-letter · automejora y meta-revisión ·
  reclamaciones atómicas multi-instancia · señal de PARADA limpia.

---

## 🚀 Instalación y uso

simplicio-tasks es una **skill** — una sola carpeta que sueltas en cualquier runtime
que cargue skills. Sin dependencias, sin binario requerido.

```bash
# Claude Code (project or user skills dir)
git clone https://github.com/wesleysimplicio/simplicio-tasks
cp -r simplicio-tasks/.claude/skills/simplicio-tasks  <your-repo>/.claude/skills/

# then, in your agent:
/simplicio-tasks finish all the open issues
```

Otros runtimes (Codex, Gemini, Copilot, agentes locales) cargan el mismo
`SKILL.md` — consulta [`AGENTS.md`](../AGENTS.md), [`CLAUDE.md`](../CLAUDE.md) y
[`GEMINI.md`](../GEMINI.md) para conocer los puntos de entrada por runtime. Donde un
runtime anfitrión expone comandos nativos, los autoenlaza a los puntos de extensión;
en caso contrario, los fallbacks del LLM cubren el **100%** del trabajo.

**Antes de una ejecución desatendida 24/7:** fija un techo de coste
(`.orchestrator/loop-budget.json`, `daily_usd_ceiling > 0`), confirma que la auth de
la fuente es persistente, y mantén activos el gate humano para ops irreversibles + el
escaneo de secretos. Con `ceiling = 0` el watcher se niega a ejecutarse desatendido
(fail-safe).

---

## 📊 Economía de tokens

Cada mensaje termina con una línea de ahorro honesta:

```
simplicio-tasks: ~<spent> tokens · baseline ~<control-arm> · saved ~<saved> (<pct>%)
```

La línea base es la **vía no orquestada sensata más barata** hacia el mismo resultado
— no un hombre de paja verboso — y el ahorro **solo se acredita cuando la
verificación-por-ejecución y el gate de criterios de aceptación del elemento pasan**.
La compresión cruda nunca cuenta como éxito por sí sola.

---

## 📄 Licencia

MIT — consulta [LICENSE](../LICENSE). Parte del ecosistema [Simplicio](https://github.com/wesleysimplicio).
