# 🔁 simplicio-tasks — De universele lussende AI-orkestrator

<p align="center">
  <img src="../assets/simplicio-tasks-logo.svg" alt="simplicio-tasks" width="920" />
</p>

<p align="center">
  <a href="https://github.com/wesleysimplicio/simplicio-tasks/stargazers"><img src="https://img.shields.io/github/stars/wesleysimplicio/simplicio-tasks?style=social" alt="Stars"></a>
  <a href="https://github.com/wesleysimplicio/simplicio-tasks"><img src="https://img.shields.io/badge/skill-runtime--agnostic-39FF14" alt="Runtime-agnostic"></a>
  <a href="#-de-43-uitbreidingspunten"><img src="https://img.shields.io/badge/extension%20points-43-00E08A" alt="43 extension points"></a>
  <a href="#-token-economie"><img src="https://img.shields.io/badge/tokens-up%20to%2096%25%20fewer-green" alt="Up to 96% fewer tokens"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License"></a>
</p>

<p align="center">
  <a href="#-tldr">TL;DR</a> ·
  <a href="#-vs-caveman--rtk">vs caveman & rtk</a> ·
  <a href="#-de-43-uitbreidingspunten">43 punten</a> ·
  <a href="#-alles-wat-erin-zit">Alles wat erin zit</a> ·
  <a href="#-installeren--gebruiken">Installeren</a>
</p>

<p align="center">
  <strong>🌍 Talen:</strong><br>
  <a href="../README.md">🇬🇧 English</a> |
  <a href="README.pt-BR.md">🇧🇷 Português</a> |
  <a href="README.es-ES.md">🇪🇸 Español</a> |
  <a href="README.fr-FR.md">🇫🇷 Français</a> |
  <a href="README.de-DE.md">🇩🇪 Deutsch</a> |
  <a href="README.it-IT.md">🇮🇹 Italiano</a> |
  <a href="README.ja-JP.md">🇯🇵 日本語</a> |
  <a href="README.ko-KR.md">🇰🇷 한국어</a> |
  <a href="README.zh-CN.md">🇨🇳 简体中文</a> |
  <a href="README.ru-RU.md">🇷🇺 Русский</a> |
  <a href="README.pl-PL.md">🇵🇱 Polski</a> |
  <a href="README.tr-TR.md">🇹🇷 Türkçe</a> |
  <strong>🇳🇱 Nederlands</strong> |
  <a href="README.hi-IN.md">🇮🇳 हिन्दी</a> |
  <a href="README.ar-SA.md">🇸🇦 العربية</a>
</p>

---

## ⚡ TL;DR

**simplicio-tasks** is een enkele, runtime-onafhankelijke **skill** die elke sterke LLM
(Claude, Codex, Copilot, Gemini, Grok, lokale modellen) verandert in een **autonome lussende
orkestrator**. Je wijst hem op een hoeveelheid werk — *"maak alle open issues af"*,
*"werk de CI-wachtrij weg"*, *"leeg het Jira-board"* — en hij draait de hele levenscyclus
helemaal zelf:

> **ontdekken → begrijpen → beslissen → handelen → verifiëren → corrigeren → vastleggen → herhalen**

Hij ontdekt werk uit elke bron, ontdubbelt, schaalt automatisch een agentvloot op naar jouw
machine, implementeert elk item via een kwaliteitslus die **de code uitvoert (niet alleen
compileert)**, opent PR's, verwerkt CI-/reviewfeedback, merget, en blijft **24/7** speuren
naar nieuw werk — allemaal achter veiligheidspoorten en een harde noodstop voor de kosten.

Hij draagt **43 benoemde uitbreidingspunten** met zich mee. Elk punt heeft een altijd-werkende
LLM-fallback, en elk *bindt aan het native commando van een host-runtime* wanneer dat aanwezig is —
waardoor de stap deterministisch en bijna-zero-token wordt. **De skill noemt geen enkele runtime;
de runtime detecteert de skill.** Die omkering is de hele truc: één universeel protocol, met
optionele native snelheid die eronder wordt geïnjecteerd.

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

simplicio-tasks is gebouwd **na een grondige studie** van de twee beste token-besparers op
GitHub — [**caveman**](https://github.com/JuliusBrussee/caveman) (74k★, *comprimeer het
gepraat*) en [**rtk**](https://github.com/rtk-ai/rtk) (63k★, *comprimeer de commando's*).
Het vouwt het beste van **beide** samen tot een volwaardige orkestrator. Zij verminderen tokens;
simplicio-tasks **doet het werk** en vermindert tokens terwijl het dat doet.

| | 🪨 **caveman** | ⚙️ **rtk** | 🔁 **simplicio-tasks** |
|---|---|---|---|
| **Wat het is** | Claude Code-skill | Rust CLI-proxy | Runtime-onafhankelijke skill |
| **Kernidee** | Korter praten (vulwoorden weglaten) | Output van dev-commando's verminderen | **De hele klus orkestreren** |
| **Reikwijdte** | LLM-prozaoutput | Output van shell-commando's | Volledige werklevenscyclus, van begin tot eind |
| **Tokenbesparing** | ~65% op antwoorden | 60–90% op commando's | Beide — catalogus + plafonds + clamping |
| **Doet het het werk?** | ❌ alleen opmaak | ❌ alleen proxy | ✅ ontdekken→implementeren→mergen→sluiten |
| **Autonomie over meerdere stappen** | ❌ | ❌ | ✅ continue worker-pool |
| **Kwaliteitspoorten** | — | — | ✅ AC-poort · run-verificatie · adversariële verificatie · leveringspoort |
| **Veiligheid** | — | semgrep, disclaimers | ✅ 4-statusoordeel · attestatie · secret-scan · menselijke poort · kill-switch |
| **24/7-lus** | ❌ | ❌ | ✅ duurzame watcher, zelfherstellend |
| **Runtime-binding** | Claude/Codex/Gemini | elke (PATH-proxy) | **elke** (43 uitbreidingspunten) |
| **Wat we overnamen** | beknopte workerrapporten, dichtheidstiers, never-paraphrase-bewaking, eerlijke baseline | reductiecatalogus per commando, signaal-getrapte plafonds, compound-clamping, fail-open, 4-statusoordeel | — |
| **Wat we lieten liggen** | grammaticaal woorden weglaten (verslechtert codekwaliteit) | registers per taal (runtime-specifiek) | — |

> We hebben caveman's "praat-als-een-holbewoner"-woordweglating bewust **verworpen** — beknopt
> *proza* is prima, maar het verminken van grammatica verslechtert code en bevestigingen. We hielden
> de *discipline* vast (parafraseer nooit code/URL's/paden), niet het trucje.

<p align="center">
  <img src="../assets/architecture.svg" alt="architecture" width="900" />
</p>

---

## 🧩 De 43 uitbreidingspunten

Elke werkstap gebeurt op een **benoemd uitbreidingspunt**. Als een host-runtime een native
capaciteit aanbiedt, **bindt** het zich daaraan (deterministisch, bijna-zero-token). Anders voert de
LLM de **fallback** uit met standaardgereedschap (shell, git, gh, bestandsbewerking, web). De
skill leunt op de abstractie, nooit op een specifieke runtime.

### Orkestratie & schaal
| Punt | Wat het doet |
|---|---|
| `orient` | Gecomprimeerde repo-/werkkaart |
| `normalize` | Werkitem → canoniek schema |
| `intake` | Werk inlezen vanuit een sprint-/boardlink |
| `source_adapter` | Uniforme bronconnector (list/get/claim/update/attach/close) |
| `autoscale` | Veilige vlootgrootte op basis van machineprofiel |
| `plan` / `decide` | Plannings- & beslissingsondersteuning |
| `execute` | Lokale agent fan-out voor massaal/mechanisch werk |
| `issue_factory` | Volledige lus: discover→claim→implement→PR |
| `claim` | Atomaire, cross-sessie-veilige claim van een werkitem |
| `worktree` | Per item geïsoleerde checkout |
| `dependency_graph` | Hervatbare DAG-ordening tussen items |
| `durable_workflow` | Pijplijn per item als een hervatbare fase-toestandsmachine |
| `work_queue` | Duurzame prioriteitswachtrij met auto-retry + write-lock |
| `resource_governor` | Dynamische throttle midden in de lus + plafonds per machinetier |
| `model_route` | Goedkoopst werkbaar substraat per subtaak (L0→remote) |
| `model_preflight` | Een bruikbaar model aftasten vóór generatierouting |

### Bewerken, kwaliteit & bewijs
| Punt | Wat het doet |
|---|---|
| `deterministic_edit` | Mechanische, zero-token toepassing van een besloten wijziging |
| `diagnostics` | Build-/testoutput parsen → gestructureerde fouten → itereren |
| `toolchain_detect` | De echte build-/lint-/typecheck-/teststack van de repo detecteren |
| `validate` / `smoke` | Run-verificatie: "werkt, niet alleen compileert" |
| `delivery_gate` | DoD: AC-check + regressie + diffreview + certificaat |
| `endpoint_compare` | Web↔API↔agent-drift → vervolgitems |
| `web_verify` | Een echte browser aansturen om te bewijzen dat een UI-wijziging werkt |
| `pr` / `evidence` | PR openen/bijwerken + verifieerbaar bewijsregister |
| `retry` | Geclassificeerde retry+backoff per faalklasse |
| `reuse_precedent` | Een eerder opgeloste run matchen → hergebruiken, niet opnieuw genereren |
| `trajectory` | Runresultaat vastleggen voor zelfverbetering |
| `learn` | Leren van een run — precedenten/geheugen bijwerken |
| `status` | Live observability-dashboard |
| `capability_rank` | Rangschikken welke skill/tool bij een subtaak past |

### Tokens, context & veiligheid
| Punt | Wat het doet |
|---|---|
| `recall` | Eerdere beslissingen / precedenten |
| `compress` | Contextcompressie / output-clamping |
| `prompt_budget` | Token-gebudgetteerde prompt-envelop + fragmentcache |
| `shell_exec` | Geclampte shell-uitvoering (gestructureerd, begrensd) |
| `transform_guard` | Verifiëren dat een compactie elke code-/URL-/pad-/versietoken behield |
| `action_gate` | Elke mutatie op risico classificeren (safe/auto/ask) vóór uitvoering |
| `security` | Supply-chain- / secret-scan |
| `human_gate` | Asynchroon kanaal voor menselijke goedkeuring |
| `notify` | Voortgang/blokkade/digest pushen + goedkeuringen ontvangen |
| `checkpoint_restore` | Toestand snapshotten vóór een riskante batch; herstellen bij falen |
| `watcher` | Duurzame scheduler / poller (overleeft herstart) |
| `savings_ledger` | Echte tokenbesteding bijhouden per sessie |
| `web_research` | Actuele externe kennis ophalen, gated, met herkomst |

---

## 📦 Alles wat erin zit

Een volledige inventaris van wat de skill draagt — elk mechanisme, met bronvermelding.

### De lus (7 stappen + substappen)
- **Stap 0** — Laad het contract (canoniek protocol).
- **Stap 1** — Identiteit + goedkope omgevingsdetectie.
- **Stap 1b** — De 43 uitbreidingspunten (native binden of LLM-fallback).
- **Stap 1c** — Token-economiepoort: `THINK / NO-THINK`, `INTERNET off by default`,
  `terminal-first execution`, **output-reductiecatalogus**, **signaal-getrapte plafonds**,
  **success-collapse + dedup**, **compound-command clamping**, **consument-gerouteerde
  dichtheidstiers**, **fail-open**, **auto-clarity (veiligheid gaat boven beknoptheid)**.
- **Stap 1d** — Pre-flight: kill-switch-budget, bronauthenticatie, de watcher scherpstellen.
- **Stap 2** — Werkitems ontdekken + normaliseren (elke source-adapter).
- **Stap 2b** — Diepe intake: volledige body + comments lezen, **acceptatiecriteria**
  extraheren, de **codebase oriënteren**, **signatures-only leesmodus**, een plan bouwen.
- **Stap 2c** — Dependency-DAG + topologische scheduling.
- **Stap 3** — Dual-path router: **fast-path** vs **heavy-path** continue worker-pool
  · **conflict-bewuste isolatie** · **worker-rapportcontract** · **correctie-geheugen**.
- **Stap 3b** — Continue intake: intra-run-poller + idle watcher (zie elke minuut nieuw werk).
- **Stap 3c** — Snelheidsmodel: pijplijn (geen barrière), gedeelde compile-cache,
  verify-once-at-merge, **gedeelde context-digest**.
- **Stap 3d** — Modelrouting L0→L4 (deterministisch → lokaal → mid → reasoning → betaald).
- **Stap 4** — Kwaliteitslus · **AC-poort (echte DoD)** · **run-verificatie** ·
  **adversariële multi-stem-verificatie** · **statische-analysepoort**.
- **Stap 5** — Veiligheidspoorten: secret-scan, menselijke poort voor onomkeerbare operaties, **4-status
  pre-executieoordeel**, **per-segment compound-attestatie**, **trust-before-load-
  config**, **supply-chain-integriteitspoort**, **transform_guard**.
- **Stap 6** — Leveren + sluiten + zelfaudit · **bewijspakket** · **realiteit
  verifiëren (vertrouw nooit het zelfrapport)** · **rollback-guard als de merge main breekt**.
- **Stap 6b** — De feedbacklus sluiten: CI → fix, reviewcommentaar → oplossen,
  branch-behind → verzoenen, volledige **PR-levenscyclus** tot merge-klaar.
- **Stap 7** — 24/7 staande lus (10 assen): duurzame driver, totale dekkingsmatrix,
  duurzame toestand, **kostenbeheersing + harde kill-switch**, onbewaakte veiligheid,
  zelfherstel + **intelligente retry per faalklasse**, prioritering/WIP,
  observability + **periodieke besparingsaudit** + **snapshotmeting**,
  zelfverbetering, coördinatie & schone stop.

### Token-economie (samengevouwen uit rtk + caveman)
- Terminal-first uitvoering — simuleer nooit een commando.
- **Cross-platform** substitutietabel (Windows / macOS / Linux): 30+ feiten die de
  terminal goedkoper beantwoordt dan de LLM.
- **Output-reductiecatalogus** als data: recept per commando, verwachte-besparing %,
  `skip-if-structured`-bewaking.
- **Signaal-getrapte plafonds**: `CAP_ERRORS / CAP_WARNINGS / CAP_LIST / CAP_INVENTORY`.
- **Success-collapse** + **dedup-with-counts** (met een `unless errors`-bewaking).
- **Compound-command clamping** — per segment, pipe-/redirect-veilig, fail-open.
- **Dichtheidstiers per consument** (machine vs mens); sla reeds-dichte content over.
- **Worker-rapportcontract** — status-token-eerst beknopt schema voor sub-agents.
- **Eerlijke besparingsbaseline** = realistische controlearm, **gebonden aan een geslaagde
  kwaliteitspoort** (compressie die haar poort niet haalt, verdient nul krediet).

### Kwaliteit & levering
- Acceptatiecriteria-DoD-checklist · run-verificatie · adversariële verificatie ·
  statische-analysepoort · leveringscertificaat · herverificatie van de realiteit ·
  automatische rollback.

### Veiligheid
- Secret-scan · menselijke poort voor onomkeerbare operaties · 4-statusoordeel (escaleer nooit
  privileges) · compound-command-attestatie · trust-before-load · supply-chain-
  integriteit · prompt-injectie-verharding · harde $-kill-switch voor onbewaakte runs.

### 24/7-autonomie
- Duurzame scheduler · live wachtrij + idle watcher · duurzaam journaal/toestand ·
  circuit breakers · dead-letter-quarantaine · zelfverbetering & meta-review ·
  multi-instance atomaire claims · schoon STOP-signaal.

---

## 🚀 Installeren & gebruiken

simplicio-tasks is een **skill** — een enkele map die je neerzet in elke runtime die
skills laadt. Geen dependency, geen binary nodig.

```bash
# Claude Code (project or user skills dir)
git clone https://github.com/wesleysimplicio/simplicio-tasks
cp -r simplicio-tasks/.claude/skills/simplicio-tasks  <your-repo>/.claude/skills/

# then, in your agent:
/simplicio-tasks finish all the open issues
```

Andere runtimes (Codex, Gemini, Copilot, lokale agents) laden dezelfde
`SKILL.md` — zie [`AGENTS.md`](../AGENTS.md), [`CLAUDE.md`](../CLAUDE.md) en
[`GEMINI.md`](../GEMINI.md) voor de instappunten per runtime. Waar een host-runtime
native commando's blootstelt, bindt hij die automatisch aan de uitbreidingspunten; anders dekken de
LLM-fallbacks **100%** van het werk.

**Vóór een onbewaakte 24/7-run:** stel een kostenplafond in (`.orchestrator/loop-budget.json`,
`daily_usd_ceiling > 0`), bevestig dat bronauthenticatie persistent is, en houd de
menselijke poort voor onomkeerbare operaties + secret-scan aan. Met `ceiling = 0` weigert de watcher
onbewaakt te draaien (fail-safe).

---

## 📊 Token-economie

Elk bericht eindigt met een eerlijke besparingsregel:

```
simplicio-tasks: ~<spent> tokens · baseline ~<control-arm> · saved ~<saved> (<pct>%)
```

De baseline is het **goedkoopste verstandige niet-georkestreerde pad** naar hetzelfde resultaat —
geen breedsprakige stroman — en besparingen worden **alleen gecrediteerd wanneer de
run-verificatie en de acceptatiecriteria-poort van het item slagen**. Ruwe compressie wordt op
zichzelf nooit als succes geteld.

---

## 📄 Licentie

MIT — zie [LICENSE](../LICENSE). Onderdeel van het [Simplicio](https://github.com/wesleysimplicio)-ecosysteem.
