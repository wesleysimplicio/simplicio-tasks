# 🔁 simplicio-tasks — Der universelle, schleifenfähige KI-Orchestrator

<p align="center">
  <img src="../assets/simplicio-tasks-logo.svg" alt="simplicio-tasks" width="920" />
</p>

<p align="center">
  <a href="https://github.com/wesleysimplicio/simplicio-tasks/stargazers"><img src="https://img.shields.io/github/stars/wesleysimplicio/simplicio-tasks?style=social" alt="Stars"></a>
  <a href="https://github.com/wesleysimplicio/simplicio-tasks"><img src="https://img.shields.io/badge/skill-runtime--agnostic-39FF14" alt="Runtime-agnostic"></a>
  <a href="#-die-43-erweiterungspunkte"><img src="https://img.shields.io/badge/extension%20points-43-00E08A" alt="43 extension points"></a>
  <a href="#-token-ökonomie"><img src="https://img.shields.io/badge/tokens-up%20to%2096%25%20fewer-green" alt="Up to 96% fewer tokens"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License"></a>
</p>

<p align="center">
  <a href="#-tldr">TL;DR</a> ·
  <a href="#-vs-caveman--rtk">vs caveman & rtk</a> ·
  <a href="#-die-43-erweiterungspunkte">43 Punkte</a> ·
  <a href="#-alles-drin">Alles drin</a> ·
  <a href="#-installation--nutzung">Installation</a>
</p>

<p align="center">
  <strong>🌍 Sprachen:</strong><br>
  <a href="../README.md">🇬🇧 English</a> |
  <a href="README.pt-BR.md">🇧🇷 Português</a> |
  <a href="README.es-ES.md">🇪🇸 Español</a> |
  <a href="README.fr-FR.md">🇫🇷 Français</a> |
  <strong>🇩🇪 Deutsch</strong> |
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

**simplicio-tasks** ist eine einzige, laufzeitunabhängige **Skill**, die jedes
starke LLM (Claude, Codex, Copilot, Gemini, Grok, lokale Modelle) in einen
**autonomen, schleifenfähigen Orchestrator** verwandelt. Du richtest es auf einen
Arbeitsumfang aus — *„schließe alle offenen Issues ab"*, *„arbeite die CI-Warteschlange
ab"*, *„leere das Jira-Board"* — und es durchläuft den gesamten Lebenszyklus
eigenständig:

> **entdecken → verstehen → entscheiden → handeln → verifizieren → korrigieren → festhalten → wiederholen**

Es entdeckt Arbeit aus jeder beliebigen Quelle, entfernt Duplikate, skaliert eine
Agentenflotte automatisch auf deine Maschine, setzt jedes Element über eine
Qualitätsschleife um, die **den Code ausführt (nicht nur kompiliert)**, eröffnet
PRs, löst CI-/Review-Feedback auf, merged und behält **rund um die Uhr** neue Arbeit
im Blick — alles hinter Sicherheits-Gates und einem harten Kostenschalter (Kill-Switch).

Es trägt **43 benannte Erweiterungspunkte**. Jeder hat einen immer funktionierenden
LLM-Fallback und jeder *bindet sich an den nativen Befehl einer Host-Laufzeit*, sobald
einer vorhanden ist — was den Schritt deterministisch und nahezu tokenfrei macht.
**Die Skill benennt keine Laufzeit; die Laufzeit erkennt die Skill.** Diese Umkehrung
ist der ganze Trick: ein universelles Protokoll, mit optionaler nativer Geschwindigkeit,
die darunter eingespeist wird.

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

simplicio-tasks wurde **nach gründlichem Studium** der beiden besten Token-Sparer auf
GitHub gebaut — [**caveman**](https://github.com/JuliusBrussee/caveman) (74k★, *die
Konversation komprimieren*) und [**rtk**](https://github.com/rtk-ai/rtk) (63k★, *die
Befehle komprimieren*). Es vereint das Beste aus **beiden** in einem vollständigen
Orchestrator. Sie reduzieren Tokens; simplicio-tasks **erledigt die Arbeit** und
reduziert dabei Tokens.

| | 🪨 **caveman** | ⚙️ **rtk** | 🔁 **simplicio-tasks** |
|---|---|---|---|
| **Was es ist** | Claude-Code-Skill | Rust-CLI-Proxy | Laufzeitunabhängige Skill |
| **Kernidee** | Knapper reden (Füllwörter weglassen) | Ausgabe von Dev-Befehlen reduzieren | **Den gesamten Auftrag orchestrieren** |
| **Geltungsbereich** | LLM-Prosa-Ausgabe | Ausgabe von Shell-Befehlen | Vollständiger Arbeitslebenszyklus, von Anfang bis Ende |
| **Token-Einsparung** | ~65 % bei Antworten | 60–90 % bei Befehlen | Beides — Katalog + Obergrenzen + Clamping |
| **Erledigt es die Arbeit?** | ❌ nur Formatierung | ❌ nur Proxy | ✅ entdecken→umsetzen→mergen→schließen |
| **Mehrstufige Autonomie** | ❌ | ❌ | ✅ kontinuierlicher Worker-Pool |
| **Qualitäts-Gates** | — | — | ✅ AC-Gate · Lauf-Verifikation · adversariale Verifikation · Delivery-Gate |
| **Sicherheit** | — | semgrep, Haftungsausschlüsse | ✅ 4-Zustands-Urteil · Attestierung · Secret-Scan · Human-Gate · Kill-Switch |
| **24/7-Schleife** | ❌ | ❌ | ✅ dauerhafter Watcher, selbstheilend |
| **Laufzeitbindung** | Claude/Codex/Gemini | beliebig (PATH-Proxy) | **beliebig** (43 Erweiterungspunkte) |
| **Was wir übernommen haben** | knappe Worker-Berichte, Dichtestufen, Niemals-paraphrasieren-Schutz, ehrliche Baseline | Reduktionskatalog pro Befehl, signalgestaffelte Obergrenzen, Compound-Clamping, Fail-Open, 4-Zustands-Urteil | — |
| **Was wir weggelassen haben** | grammatikalisches Wort-Weglassen (verschlechtert die Code-Qualität) | sprachspezifische Registries (laufzeitabhängig) | — |

> Wir haben cavemans „Höhlenmensch-Sprech"-Wort-Weglassen **bewusst verworfen** —
> knappe *Prosa* ist in Ordnung, aber verstümmelte Grammatik verschlechtert Code und
> Bestätigungen. Wir haben die *Disziplin* behalten (niemals Code/URLs/Pfade
> paraphrasieren), nicht den Gimmick.

<p align="center">
  <img src="../assets/architecture.svg" alt="architecture" width="900" />
</p>

---

## 🧩 Die 43 Erweiterungspunkte

Jeder Arbeitsschritt findet an einem **benannten Erweiterungspunkt** statt. Wenn eine
Host-Laufzeit eine native Fähigkeit bereitstellt, **bindet** sie sich daran
(deterministisch, nahezu tokenfrei). Andernfalls führt das LLM den **Fallback** mit
Standardwerkzeugen aus (Shell, git, gh, Dateibearbeitung, Web). Die Skill hängt von
der Abstraktion ab, niemals von einer bestimmten Laufzeit.

### Orchestrierung & Skalierung
| Punkt | Was er tut |
|---|---|
| `orient` | Komprimierte Repo-/Arbeitskarte |
| `normalize` | Arbeitselement → kanonisches Schema |
| `intake` | Arbeit aus einem Sprint-/Board-Link aufnehmen |
| `source_adapter` | Einheitlicher Quellen-Connector (list/get/claim/update/attach/close) |
| `autoscale` | Sichere Flottengröße aus dem Maschinenprofil |
| `plan` / `decide` | Planungs- & Entscheidungsunterstützung |
| `execute` | Lokales Agenten-Fan-out für Massen-/mechanische Arbeit |
| `issue_factory` | Vollständige Schleife: entdecken→beanspruchen→umsetzen→PR |
| `claim` | Atomares, sitzungsübergreifend sicheres Beanspruchen eines Arbeitselements |
| `worktree` | Isolierter Checkout pro Element |
| `dependency_graph` | Wiederaufnehmbare DAG-Anordnung zwischen Elementen |
| `durable_workflow` | Pro-Element-Pipeline als wiederaufnehmbare Phasen-Zustandsmaschine |
| `work_queue` | Dauerhafte Prioritätswarteschlange mit Auto-Retry + Schreibsperre |
| `resource_governor` | Dynamische Drosselung mitten in der Schleife + Maschinenstufen-Obergrenzen |
| `model_route` | Günstigstes brauchbares Substrat pro Teilaufgabe (L0→remote) |
| `model_preflight` | Vor dem Routing der Generierung ein nutzbares Modell prüfen |

### Bearbeitung, Qualität & Nachweis
| Punkt | Was er tut |
|---|---|
| `deterministic_edit` | Mechanisches, tokenfreies Anwenden einer beschlossenen Änderung |
| `diagnostics` | Build-/Test-Ausgabe parsen → strukturierte Fehler → iterieren |
| `toolchain_detect` | Den echten Build-/Lint-/Typecheck-/Test-Stack des Repos erkennen |
| `validate` / `smoke` | Lauf-Verifikation: „funktioniert, nicht nur kompiliert" |
| `delivery_gate` | DoD: AC-Prüfung + Regression + Diff-Review + Zertifikat |
| `endpoint_compare` | Web↔API↔Agent-Drift → Folgeelemente |
| `web_verify` | Einen echten Browser steuern, um eine UI-Änderung zu beweisen |
| `pr` / `evidence` | PR öffnen/aktualisieren + verifizierbares Nachweis-Ledger |
| `retry` | Klassifizierter Retry+Backoff nach Fehlerklasse |
| `reuse_precedent` | Einen früher gelösten Lauf abgleichen → wiederverwenden, nicht neu generieren |
| `trajectory` | Lauf-Ergebnis für Selbstverbesserung festhalten |
| `learn` | Aus einem Lauf lernen — Präzedenzfälle/Memory aktualisieren |
| `status` | Live-Observability-Dashboard |
| `capability_rank` | Bewerten, welche Skill/welches Tool zu einer Teilaufgabe passt |

### Tokens, Kontext & Sicherheit
| Punkt | Was er tut |
|---|---|
| `recall` | Frühere Entscheidungen / Präzedenzfälle |
| `compress` | Kontextkompression / Ausgabe-Clamping |
| `prompt_budget` | Token-budgetierte Prompt-Hülle + Fragment-Cache |
| `shell_exec` | Geklemmte Shell-Ausführung (strukturiert, begrenzt) |
| `transform_guard` | Prüfen, dass eine Verdichtung jedes Code-/URL-/Pfad-/Versions-Token bewahrt hat |
| `action_gate` | Jede Mutation risikoklassifizieren (safe/auto/ask), bevor sie läuft |
| `security` | Supply-Chain-/Secret-Scan |
| `human_gate` | Asynchroner menschlicher Freigabekanal |
| `notify` | Fortschritt/Blocker/Digest pushen + Freigaben empfangen |
| `checkpoint_restore` | Zustand vor einem riskanten Batch sichern; bei Fehler wiederherstellen |
| `watcher` | Dauerhafter Scheduler / Poller (übersteht Neustart) |
| `savings_ledger` | Echtes Token-Verbrauchs-Tracking pro Sitzung |
| `web_research` | Aktuelles externes Wissen abrufen, gated, mit Herkunftsnachweis |

---

## 📦 Alles drin

Eine vollständige Bestandsaufnahme dessen, was die Skill mitbringt — jeder Mechanismus,
mit Beleg.

### Die Schleife (7 Schritte + Teilschritte)
- **Schritt 0** — Den Vertrag laden (kanonisches Protokoll).
- **Schritt 1** — Identität + günstige Umgebungserkennung.
- **Schritt 1b** — Die 43 Erweiterungspunkte (native binden oder LLM-Fallback).
- **Schritt 1c** — Token-Ökonomie-Gate: `THINK / NO-THINK`, `INTERNET off by default`,
  `terminal-first execution`, **Ausgabe-Reduktionskatalog**, **signalgestaffelte
  Obergrenzen**, **Success-Collapse + Dedup**, **Compound-Command-Clamping**,
  **konsumentengerichtete Dichtestufen**, **Fail-Open**, **Auto-Klarheit (Sicherheit
  geht vor Knappheit)**.
- **Schritt 1d** — Pre-Flight: Kill-Switch-Budget, Quellen-Auth, den Watcher scharfschalten.
- **Schritt 2** — Arbeitselemente entdecken + normalisieren (beliebiger Source-Adapter).
- **Schritt 2b** — Tiefe Aufnahme: vollständigen Body + Kommentare lesen,
  **Akzeptanzkriterien** extrahieren, **die Codebasis orientieren**, **Signaturen-only-
  Lesemodus**, einen Plan erstellen.
- **Schritt 2c** — Abhängigkeits-DAG + topologische Planung.
- **Schritt 3** — Dual-Pfad-Router: **Fast-Path** vs. **Heavy-Path** kontinuierlicher
  Worker-Pool · **konfliktbewusste Isolierung** · **Worker-Report-Vertrag** ·
  **Korrektur-Memory**.
- **Schritt 3b** — Kontinuierliche Aufnahme: Intra-Run-Poller + Idle-Watcher (sieht neue
  Arbeit in jeder Minute).
- **Schritt 3c** — Geschwindigkeitsmodell: Pipeline (keine Barriere), gemeinsamer
  Compile-Cache, Verify-once-at-merge, **gemeinsamer Kontext-Digest**.
- **Schritt 3d** — Modell-Routing L0→L4 (deterministisch → lokal → mittel → reasoning → bezahlt).
- **Schritt 4** — Qualitätsschleife · **AC-Gate (echtes DoD)** · **Lauf-Verifikation** ·
  **adversariale Mehrfach-Abstimmungs-Verifikation** · **Statik-Analyse-Gate**.
- **Schritt 5** — Sicherheits-Gates: Secret-Scan, Human-Gate für irreversible Operationen,
  **4-Zustands-Vorausführungs-Urteil**, **Compound-Attestierung pro Segment**,
  **Trust-before-load-Konfiguration**, **Supply-Chain-Integritäts-Gate**,
  **transform_guard**.
- **Schritt 6** — Liefern + schließen + Selbstaudit · **Nachweispaket** · **Realität
  verifizieren (niemals dem Selbstbericht vertrauen)** · **Rollback-Schutz, falls der
  Merge main bricht**.
- **Schritt 6b** — Die Feedbackschleife schließen: CI → Fix, Review-Kommentare → auflösen,
  Branch-hinterher → abgleichen, vollständiger **PR-Lebenszyklus** bis zur Merge-Reife.
- **Schritt 7** — 24/7-Dauerschleife (10 Achsen): dauerhafter Treiber, vollständige
  Abdeckungsmatrix, dauerhafter Zustand, **Kosten-Governance + harter Kill-Switch**,
  unbeaufsichtigte Sicherheit, Selbstheilung + **intelligenter Retry nach Fehlerklasse**,
  Priorisierung/WIP, Observability + **periodisches Savings-Audit** +
  **Snapshot-Messung**, Selbstverbesserung, Koordination & sauberer Stopp.

### Token-Ökonomie (eingebunden aus rtk + caveman)
- Terminal-first-Ausführung — niemals einen Befehl simulieren.
- **Plattformübergreifende** Substitutionstabelle (Windows / macOS / Linux): über 30
  Fakten, die das Terminal günstiger beantwortet als das LLM.
- **Ausgabe-Reduktionskatalog** als Daten: Rezept pro Befehl, erwartete Einsparungs-%,
  `skip-if-structured`-Schutz.
- **Signalgestaffelte Obergrenzen**: `CAP_ERRORS / CAP_WARNINGS / CAP_LIST / CAP_INVENTORY`.
- **Success-Collapse** + **Dedup-with-counts** (mit einem `unless errors`-Schutz).
- **Compound-Command-Clamping** — pro Segment, pipe-/redirect-sicher, Fail-Open.
- **Dichtestufen nach Konsument** (Maschine vs. Mensch); bereits dichte Inhalte überspringen.
- **Worker-Report-Vertrag** — status-token-first knappes Schema für Sub-Agenten.
- **Ehrliche Savings-Baseline** = realistischer Kontrollarm, **an ein bestandenes
  Qualitäts-Gate gebunden** (Kompression, die ihr Gate nicht besteht, erhält null Gutschrift).

### Qualität & Lieferung
- Akzeptanzkriterien-DoD-Checkliste · Lauf-Verifikation · adversariale Verifikation ·
  Statik-Analyse-Gate · Lieferzertifikat · Realitäts-Neuverifikation · automatisches Rollback.

### Sicherheit
- Secret-Scan · Human-Gate für irreversible Operationen · 4-Zustands-Urteil (niemals
  Rechte eskalieren) · Compound-Command-Attestierung · Trust-before-load ·
  Supply-Chain-Integrität · Härtung gegen Prompt-Injection · harter $-Kill-Switch für
  unbeaufsichtigte Läufe.

### 24/7-Autonomie
- Dauerhafter Scheduler · Live-Queue + Idle-Watcher · dauerhaftes Journal/Zustand ·
  Circuit Breaker · Dead-Letter-Quarantäne · Selbstverbesserung & Meta-Review ·
  atomare Mehr-Instanz-Beanspruchungen · sauberes STOP-Signal.

---

## 🚀 Installation & Nutzung

simplicio-tasks ist eine **Skill** — ein einziger Ordner, den du in jede Laufzeit
ablegst, die Skills lädt. Keine Abhängigkeit, kein Binary erforderlich.

```bash
# Claude Code (project or user skills dir)
git clone https://github.com/wesleysimplicio/simplicio-tasks
cp -r simplicio-tasks/.claude/skills/simplicio-tasks  <your-repo>/.claude/skills/

# then, in your agent:
/simplicio-tasks finish all the open issues
```

Andere Laufzeiten (Codex, Gemini, Copilot, lokale Agenten) laden dieselbe
`SKILL.md` — siehe [`AGENTS.md`](../AGENTS.md), [`CLAUDE.md`](../CLAUDE.md) und
[`GEMINI.md`](../GEMINI.md) für die laufzeitspezifischen Einstiegspunkte. Wo eine
Host-Laufzeit native Befehle bereitstellt, bindet sie diese automatisch an die
Erweiterungspunkte; andernfalls decken die LLM-Fallbacks **100 %** der Arbeit ab.

**Vor einem unbeaufsichtigten 24/7-Lauf:** lege eine Kostenobergrenze fest
(`.orchestrator/loop-budget.json`, `daily_usd_ceiling > 0`), bestätige, dass die
Quellen-Auth persistent ist, und halte das Human-Gate für irreversible Operationen +
den Secret-Scan aktiviert. Bei `ceiling = 0` weigert sich der Watcher, unbeaufsichtigt
zu laufen (Fail-Safe).

---

## 📊 Token-Ökonomie

Jede Nachricht endet mit einer ehrlichen Savings-Zeile:

```
simplicio-tasks: ~<spent> tokens · baseline ~<control-arm> · saved ~<saved> (<pct>%)
```

Die Baseline ist der **günstigste vernünftige nicht-orchestrierte Pfad** zum selben
Ergebnis — kein aufgeblähter Strohmann — und Einsparungen werden **nur gutgeschrieben,
wenn die Lauf-Verifikation und das Akzeptanzkriterien-Gate des Elements bestehen**. Rohe
Kompression wird für sich allein niemals als Erfolg gezählt.

---

## 📄 Lizenz

MIT — siehe [LICENSE](../LICENSE). Teil des [Simplicio](https://github.com/wesleysimplicio)-Ökosystems.
