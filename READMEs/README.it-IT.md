# 🔁 simplicio-tasks — L'orchestratore IA universale a ciclo continuo

<p align="center">
  <img src="../assets/simplicio-tasks-logo.svg" alt="simplicio-tasks" width="920" />
</p>

<p align="center">
  <a href="https://github.com/wesleysimplicio/simplicio-tasks/stargazers"><img src="https://img.shields.io/github/stars/wesleysimplicio/simplicio-tasks?style=social" alt="Stars"></a>
  <a href="https://github.com/wesleysimplicio/simplicio-tasks"><img src="https://img.shields.io/badge/skill-runtime--agnostic-39FF14" alt="Runtime-agnostic"></a>
  <a href="#-i-43-extension-point"><img src="https://img.shields.io/badge/extension%20points-43-00E08A" alt="43 extension points"></a>
  <a href="#-economia-dei-token"><img src="https://img.shields.io/badge/tokens-up%20to%2096%25%20fewer-green" alt="Up to 96% fewer tokens"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License"></a>
</p>

<p align="center">
  <a href="#-tldr">TL;DR</a> ·
  <a href="#-vs-caveman--rtk">vs caveman & rtk</a> ·
  <a href="#-i-43-extension-point">43 Punti</a> ·
  <a href="#-tutto-quello-che-cè-dentro">Tutto quello che c'è dentro</a> ·
  <a href="#-installazione--uso">Installazione</a>
</p>

<p align="center">
  <strong>🌍 Lingue:</strong><br>
  <a href="../README.md">🇬🇧 English</a> |
  <a href="README.pt-BR.md">🇧🇷 Português</a> |
  <a href="README.es-ES.md">🇪🇸 Español</a> |
  <a href="README.fr-FR.md">🇫🇷 Français</a> |
  <a href="README.de-DE.md">🇩🇪 Deutsch</a> |
  <strong>🇮🇹 Italiano</strong> |
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

**simplicio-tasks** è un'unica **skill** indipendente dal runtime che trasforma qualsiasi
LLM potente (Claude, Codex, Copilot, Gemini, Grok, modelli locali) in un **orchestratore
autonomo a ciclo continuo**. La punti verso un corpo di lavoro — *"completa tutte le issue
aperte"*, *"svuota la coda della CI"*, *"esaurisci la board di Jira"* — e lei esegue l'intero
ciclo di vita da sola:

> **scopri → comprendi → decidi → agisci → verifica → correggi → registra → ripeti**

Scopre il lavoro da qualsiasi fonte, deduplica, ridimensiona automaticamente una flotta di
agenti in base alla tua macchina, implementa ogni elemento attraverso un loop di qualità che
**esegue il codice (non si limita a compilarlo)**, apre le PR, risolve i feedback di CI/review,
fa il merge e continua a sorvegliare **24/7** in cerca di nuovo lavoro — il tutto dietro
gate di sicurezza e un kill-switch rigido sui costi.

Porta con sé **43 extension point nominati**. Ognuno ha un fallback LLM che funziona sempre, e
ognuno *si lega al comando nativo di un runtime host* quando ne è presente uno — rendendo lo
step deterministico e quasi a zero token. **La skill non nomina alcun runtime; è il runtime
a rilevare la skill.** Questa inversione è tutto il trucco: un unico protocollo universale,
con velocità nativa opzionale iniettata sotto.

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

simplicio-tasks è stato costruito **dopo aver studiato a fondo** i due migliori risparmiatori
di token su GitHub — [**caveman**](https://github.com/JuliusBrussee/caveman) (74k★, *comprimi il
dialogo*) e [**rtk**](https://github.com/rtk-ai/rtk) (63k★, *comprimi i comandi*).
Fonde il meglio di **entrambi** in un orchestratore completo. Loro riducono i token;
simplicio-tasks **fa il lavoro** e riduce i token mentre lo fa.

| | 🪨 **caveman** | ⚙️ **rtk** | 🔁 **simplicio-tasks** |
|---|---|---|---|
| **Cos'è** | Skill di Claude Code | Proxy CLI in Rust | Skill indipendente dal runtime |
| **Idea centrale** | Parlare più stringato (eliminare il superfluo) | Ridurre l'output dei comandi di sviluppo | **Orchestrare l'intero lavoro** |
| **Ambito** | Output testuale dell'LLM | Output dei comandi shell | Ciclo di vita completo del lavoro, dall'inizio alla fine |
| **Risparmio di token** | ~65% sulle risposte | 60–90% sui comandi | Entrambi — catalogo + limiti + clamping |
| **Fa il lavoro?** | ❌ solo formattazione | ❌ solo proxy | ✅ discover→implement→merge→close |
| **Autonomia multi-step** | ❌ | ❌ | ✅ worker pool continuo |
| **Gate di qualità** | — | — | ✅ AC gate · run-verification · verifica avversariale · delivery gate |
| **Sicurezza** | — | semgrep, disclaimer | ✅ verdetto a 4 stati · attestation · secret-scan · gate umano · kill-switch |
| **Loop 24/7** | ❌ | ❌ | ✅ watcher durevole, auto-riparante |
| **Binding al runtime** | Claude/Codex/Gemini | qualsiasi (proxy su PATH) | **qualsiasi** (43 extension point) |
| **Cosa abbiamo preso** | report dei worker stringati, livelli di densità, guardia anti-parafrasi, baseline onesta | catalogo di riduzione per comando, limiti a livelli di segnale, compound-clamping, fail-open, verdetto a 4 stati | — |
| **Cosa abbiamo lasciato** | eliminazione grammaticale delle parole (degrada la qualità del codice) | registri per linguaggio (specifici del runtime) | — |

> Abbiamo **scartato** di proposito l'eliminazione di parole "alla caveman" — la *prosa*
> stringata va bene, ma storpiare la grammatica degrada il codice e le conferme. Abbiamo
> tenuto la *disciplina* (non parafrasare mai codice/URL/percorsi), non l'espediente.

<p align="center">
  <img src="../assets/architecture.svg" alt="architecture" width="900" />
</p>

---

## 🧩 I 43 extension point

Ogni step del lavoro avviene in un **extension point nominato**. Se un runtime host espone
una capacità nativa, lo step vi **si lega** (deterministico, quasi a zero token). Altrimenti
l'LLM esegue il **fallback** con strumenti standard (shell, git, gh, modifica di file, web).
La skill dipende dall'astrazione, mai da un runtime specifico.

### Orchestrazione e scala
| Punto | Cosa fa |
|---|---|
| `orient` | Mappa compressa del repo/lavoro |
| `normalize` | Work-item → schema canonico |
| `intake` | Acquisisce il lavoro da un link a sprint/board |
| `source_adapter` | Connettore uniforme alle fonti (list/get/claim/update/attach/close) |
| `autoscale` | Dimensione sicura della flotta in base al profilo della macchina |
| `plan` / `decide` | Supporto a pianificazione e decisione |
| `execute` | Fan-out di agenti locali per lavoro massivo/meccanico |
| `issue_factory` | Loop completo: discover→claim→implement→PR |
| `claim` | Presa in carico atomica di un work-item, sicura tra sessioni |
| `worktree` | Checkout isolato per ogni elemento |
| `dependency_graph` | Ordinamento DAG riprendibile tra elementi |
| `durable_workflow` | Pipeline per elemento come macchina a stati a fasi riprendibili |
| `work_queue` | Coda di priorità durevole con auto-retry + write-lock |
| `resource_governor` | Throttling dinamico durante il loop + soglie per fascia di macchina |
| `model_route` | Substrato più economico utilizzabile per sotto-task (L0→remoto) |
| `model_preflight` | Sonda un modello utilizzabile prima di instradare la generazione |

### Editing, qualità ed evidenze
| Punto | Cosa fa |
|---|---|
| `deterministic_edit` | Applicazione meccanica e a zero token di una modifica già decisa |
| `diagnostics` | Analizza l'output di build/test → errori strutturati → itera |
| `toolchain_detect` | Rileva il reale stack di build/lint/typecheck/test del repo |
| `validate` / `smoke` | Run-verification: "funziona, non solo compila" |
| `delivery_gate` | DoD: verifica AC + regressione + review del diff + certificato |
| `endpoint_compare` | Drift Web↔API↔agente → elementi di follow-up |
| `web_verify` | Pilota un browser reale per dimostrare che una modifica UI funziona |
| `pr` / `evidence` | Apertura/aggiornamento PR + ledger di evidenze verificabile |
| `retry` | Retry+backoff classificato per classe di fallimento |
| `reuse_precedent` | Trova un'esecuzione già risolta → riusa, non rigenerare |
| `trajectory` | Registra l'esito dell'esecuzione per il miglioramento continuo |
| `learn` | Impara da un'esecuzione — aggiorna precedenti/memoria |
| `status` | Dashboard di osservabilità in tempo reale |
| `capability_rank` | Classifica quale skill/strumento si adatta a un sotto-task |

### Token, contesto e sicurezza
| Punto | Cosa fa |
|---|---|
| `recall` | Decisioni / precedenti pregressi |
| `compress` | Compressione del contesto / clamping dell'output |
| `prompt_budget` | Envelope del prompt a budget di token + cache dei frammenti |
| `shell_exec` | Esecuzione shell con clamping (strutturata, limitata) |
| `transform_guard` | Verifica che una compattazione abbia preservato ogni token di codice/URL/percorso/versione |
| `action_gate` | Classifica il rischio di ogni mutazione (safe/auto/ask) prima che venga eseguita |
| `security` | Scansione supply-chain / secret |
| `human_gate` | Canale asincrono di approvazione umana |
| `notify` | Invia progressi/blocchi/digest + riceve approvazioni |
| `checkpoint_restore` | Snapshot dello stato prima di un batch rischioso; ripristino in caso di fallimento |
| `watcher` | Scheduler / poller durevole (sopravvive al riavvio) |
| `savings_ledger` | Tracciamento reale della spesa di token per sessione |
| `web_research` | Recupera conoscenza esterna aggiornata, gated, con provenienza |

---

## 📦 Tutto quello che c'è dentro

Un inventario completo di ciò che la skill porta con sé — ogni meccanismo, con riferimento.

### Il loop (7 step + sub-step)
- **Step 0** — Carica il contratto (protocollo canonico).
- **Step 1** — Identità + rilevamento economico dell'ambiente.
- **Step 1b** — I 43 extension point (binding nativo o fallback LLM).
- **Step 1c** — Gate di economia dei token: `THINK / NO-THINK`, `INTERNET off by default`,
  `terminal-first execution`, **catalogo di riduzione dell'output**, **limiti a livelli di
  segnale**, **success-collapse + dedup**, **clamping dei comandi composti**, **livelli di
  densità instradati per consumatore**, **fail-open**, **auto-clarity (la sicurezza prevale
  sulla brevità)**.
- **Step 1d** — Pre-flight: budget del kill-switch, auth della fonte, armare il watcher.
- **Step 2** — Scopri + normalizza i work-item (qualsiasi source adapter).
- **Step 2b** — Intake approfondito: leggere corpo completo + commenti, estrarre i **criteri
  di accettazione**, **orientarsi nel codebase**, **modalità di lettura solo-firme**, costruire
  un piano.
- **Step 2c** — DAG delle dipendenze + scheduling topologico.
- **Step 3** — Router a doppio percorso: worker pool continuo **fast-path** vs **heavy-path**
  · **isolamento consapevole dei conflitti** · **contratto del report dei worker** · **memoria
  delle correzioni**.
- **Step 3b** — Intake continuo: poller intra-esecuzione + watcher in idle (vede nuovo lavoro
  in qualsiasi momento).
- **Step 3c** — Modello di velocità: pipeline (non barriera), cache di compilazione condivisa,
  verifica-una-volta-al-merge, **digest di contesto condiviso**.
- **Step 3d** — Routing dei modelli L0→L4 (deterministico → locale → medio → reasoning → a pagamento).
- **Step 4** — Loop di qualità · **AC gate (DoD reale)** · **run-verification** ·
  **verifica avversariale multi-voto** · **gate di analisi statica**.
- **Step 5** — Gate di sicurezza: secret-scan, gate umano sulle operazioni irreversibili,
  **verdetto a 4 stati pre-esecuzione**, **attestation composta per segmento**, **config
  trust-before-load**, **gate di integrità della supply-chain**, **transform_guard**.
- **Step 6** — Consegna + chiusura + auto-audit · **pacchetto di evidenze** · **verifica della
  realtà (non fidarsi mai dei report autodichiarati)** · **rollback-guard se il merge rompe main**.
- **Step 6b** — Chiudere il feedback loop: CI → fix, commenti di review → risolvi,
  branch-indietro → riconcilia, **ciclo di vita completo della PR** fino alla pronta-al-merge.
- **Step 7** — Loop permanente 24/7 (10 assi): driver durevole, matrice di copertura totale,
  stato durevole, **governance dei costi + kill-switch rigido**, sicurezza non presidiata,
  auto-riparazione + **retry intelligente per classe di fallimento**, prioritizzazione/WIP,
  osservabilità + **audit periodico dei risparmi** + **misurazione tramite snapshot**,
  miglioramento continuo, coordinamento e stop pulito.

### Economia dei token (fusa da rtk + caveman)
- Esecuzione terminal-first — non simulare mai un comando.
- Tabella di sostituzione **cross-platform** (Windows / macOS / Linux): oltre 30 fatti a cui
  il terminale risponde più a buon mercato dell'LLM.
- **Catalogo di riduzione dell'output** come dati: ricetta per comando, % di risparmio atteso,
  guardia `skip-if-structured`.
- **Limiti a livelli di segnale**: `CAP_ERRORS / CAP_WARNINGS / CAP_LIST / CAP_INVENTORY`.
- **Success-collapse** + **dedup-with-counts** (con guardia `unless errors`).
- **Clamping dei comandi composti** — per segmento, sicuro su pipe/redirect, fail-open.
- **Livelli di densità per consumatore** (macchina vs umano); salta i contenuti già densi.
- **Contratto del report dei worker** — schema stringato con il token di stato in testa per
  i sub-agenti.
- **Baseline onesta dei risparmi** = braccio di controllo realistico, **vincolato al
  superamento di un gate di qualità** (una compressione che non supera il suo gate guadagna
  zero crediti).

### Qualità e consegna
- Checklist DoD dei criteri di accettazione · run-verification · verifica avversariale ·
  gate di analisi statica · certificato di consegna · ri-verifica della realtà ·
  rollback automatico.

### Sicurezza
- Secret-scan · gate umano sulle operazioni irreversibili · verdetto a 4 stati (non
  escalare mai i privilegi) · attestation dei comandi composti · trust-before-load ·
  integrità della supply-chain · hardening anti prompt-injection · kill-switch rigido in $
  per le esecuzioni non presidiate.

### Autonomia 24/7
- Scheduler durevole · coda live + watcher in idle · journal/stato durevole ·
  circuit breaker · quarantena dead-letter · miglioramento continuo e meta-review ·
  prese in carico atomiche multi-istanza · segnale di STOP pulito.

---

## 🚀 Installazione e uso

simplicio-tasks è una **skill** — una singola cartella che inserisci in qualsiasi runtime
che carica skill. Nessuna dipendenza, nessun binario richiesto.

```bash
# Claude Code (project or user skills dir)
git clone https://github.com/wesleysimplicio/simplicio-tasks
cp -r simplicio-tasks/.claude/skills/simplicio-tasks  <your-repo>/.claude/skills/

# then, in your agent:
/simplicio-tasks finish all the open issues
```

Altri runtime (Codex, Gemini, Copilot, agenti locali) caricano lo stesso
`SKILL.md` — vedi [`AGENTS.md`](../AGENTS.md), [`CLAUDE.md`](../CLAUDE.md) e
[`GEMINI.md`](../GEMINI.md) per i punti di ingresso specifici di ciascun runtime. Dove un
runtime host espone comandi nativi, li lega automaticamente agli extension point; altrimenti
i fallback LLM coprono il **100%** del lavoro.

**Prima di un'esecuzione non presidiata 24/7:** imposta un tetto di costo
(`.orchestrator/loop-budget.json`, `daily_usd_ceiling > 0`), conferma che l'auth della fonte
sia persistente e tieni attivi il gate umano sulle operazioni irreversibili + il secret-scan.
Con `ceiling = 0` il watcher rifiuta di girare in modalità non presidiata (fail-safe).

---

## 📊 Economia dei token

Ogni messaggio termina con una riga di risparmio onesta:

```
simplicio-tasks: ~<spent> tokens · baseline ~<control-arm> · saved ~<saved> (<pct>%)
```

La baseline è il **percorso non orchestrato più economico e ragionevole** verso lo stesso
risultato — non un fantoccio prolisso — e i risparmi sono **accreditati solo quando la
run-verification e il gate dei criteri di accettazione dell'elemento passano**. La compressione
grezza non viene mai conteggiata di per sé come successo.

---

## 📄 Licenza

MIT — vedi [LICENSE](../LICENSE). Parte dell'ecosistema [Simplicio](https://github.com/wesleysimplicio).
