# 🔁 simplicio-tasks — L'orchestrateur d'IA en boucle universel

<p align="center">
  <img src="../assets/simplicio-tasks-logo.svg" alt="simplicio-tasks" width="920" />
</p>

<p align="center">
  <a href="https://github.com/wesleysimplicio/simplicio-tasks/stargazers"><img src="https://img.shields.io/github/stars/wesleysimplicio/simplicio-tasks?style=social" alt="Stars"></a>
  <a href="https://github.com/wesleysimplicio/simplicio-tasks"><img src="https://img.shields.io/badge/skill-runtime--agnostic-39FF14" alt="Runtime-agnostic"></a>
  <a href="#-les-43-points-dextension"><img src="https://img.shields.io/badge/extension%20points-43-00E08A" alt="43 extension points"></a>
  <a href="#-économie-de-tokens"><img src="https://img.shields.io/badge/tokens-up%20to%2096%25%20fewer-green" alt="Up to 96% fewer tokens"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License"></a>
</p>

<p align="center">
  <a href="#-tldr">TL;DR</a> ·
  <a href="#-vs-caveman--rtk">vs caveman & rtk</a> ·
  <a href="#-les-43-points-dextension">43 Points</a> ·
  <a href="#-tout-ce-quelle-contient">Tout l'intérieur</a> ·
  <a href="#-installation--utilisation">Installation</a>
</p>

<p align="center">
  <strong>🌍 Langues :</strong><br>
  <a href="../README.md">🇬🇧 English</a> |
  <a href="README.pt-BR.md">🇧🇷 Português</a> |
  <a href="README.es-ES.md">🇪🇸 Español</a> |
  <strong>🇫🇷 Français</strong> |
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

**simplicio-tasks** est une **skill** unique, indépendante du runtime, qui transforme
n'importe quel LLM performant (Claude, Codex, Copilot, Gemini, Grok, modèles locaux)
en un **orchestrateur autonome fonctionnant en boucle**. Vous le pointez vers un corps
de travail — *« termine toutes les issues ouvertes »*, *« vide la file d'attente CI »*,
*« épuise le tableau Jira »* — et il exécute l'ensemble du cycle de vie tout seul :

> **découvrir → comprendre → décider → agir → vérifier → corriger → enregistrer → répéter**

Il découvre le travail à partir de n'importe quelle source, déduplique, met à l'échelle
automatiquement une flotte d'agents adaptée à votre machine, implémente chaque élément
via une boucle de qualité qui **exécute le code (et ne se contente pas de le compiler)**,
ouvre des PR, résout les retours CI/revue, fusionne, et reste à l'affût **24h/24, 7j/7**
de nouveau travail — le tout derrière des garde-fous de sécurité et un coupe-circuit de
coût strict.

Elle embarque **43 points d'extension nommés**. Chacun dispose d'un repli LLM qui
fonctionne toujours, et chacun *se lie à la commande native d'un runtime hôte* lorsqu'elle
est présente — rendant l'étape déterministe et quasi sans consommation de tokens.
**La skill ne nomme aucun runtime ; c'est le runtime qui détecte la skill.** Cette
inversion est toute l'astuce : un protocole universel unique, avec une vitesse native
optionnelle injectée en dessous.

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

simplicio-tasks a été conçu **après une étude approfondie** des deux meilleurs
économiseurs de tokens sur GitHub — [**caveman**](https://github.com/JuliusBrussee/caveman)
(74k★, *compresser la conversation*) et [**rtk**](https://github.com/rtk-ai/rtk)
(63k★, *compresser les commandes*). Il intègre le meilleur des **deux** dans un
orchestrateur complet. Eux réduisent les tokens ; simplicio-tasks **fait le travail**
et réduit les tokens en le faisant.

| | 🪨 **caveman** | ⚙️ **rtk** | 🔁 **simplicio-tasks** |
|---|---|---|---|
| **Ce que c'est** | Skill Claude Code | Proxy CLI en Rust | Skill indépendante du runtime |
| **Idée centrale** | Parler plus concis (supprimer le superflu) | Réduire la sortie des commandes dev | **Orchestrer tout le travail** |
| **Portée** | Sortie en prose du LLM | Sortie des commandes shell | Cycle de vie complet du travail, de bout en bout |
| **Économie de tokens** | ~65 % sur les réponses | 60–90 % sur les commandes | Les deux — catalogue + plafonds + clamping |
| **Fait-il le travail ?** | ❌ mise en forme uniquement | ❌ proxy uniquement | ✅ découvrir→implémenter→fusionner→clôturer |
| **Autonomie multi-étapes** | ❌ | ❌ | ✅ pool de workers continu |
| **Garde-fous qualité** | — | — | ✅ gate AC · vérification par exécution · vérification adverse · gate de livraison |
| **Sécurité** | — | semgrep, avertissements | ✅ verdict à 4 états · attestation · scan de secrets · gate humain · kill-switch |
| **Boucle 24h/24** | ❌ | ❌ | ✅ watcher durable, auto-réparation |
| **Liaison au runtime** | Claude/Codex/Gemini | n'importe lequel (proxy PATH) | **n'importe lequel** (43 points d'extension) |
| **Ce que nous avons repris** | rapports de workers concis, paliers de densité, garde-fou « ne jamais paraphraser », baseline honnête | catalogue de réduction par commande, plafonds par paliers de signal, clamping composé, fail-open, verdict à 4 états | — |
| **Ce que nous avons laissé** | suppression de mots grammaticaux (dégrade la qualité du code) | registres par langage (spécifiques au runtime) | — |

> Nous avons **rejeté** délibérément la suppression de mots « parler-comme-un-homme-des-cavernes »
> de caveman — une *prose* concise est très bien, mais malmener la grammaire dégrade le
> code et les confirmations. Nous avons conservé la *discipline* (ne jamais paraphraser
> le code/les URL/les chemins), pas le gadget.

<p align="center">
  <img src="../assets/architecture.svg" alt="architecture" width="900" />
</p>

---

## 🧩 Les 43 points d'extension

Chaque étape du travail se déroule au sein d'un **point d'extension nommé**. Si un
runtime hôte expose une capacité native, il s'y **lie** (déterministe, quasi sans
consommation de tokens). Sinon, le LLM exécute le **repli** avec des outils standard
(shell, git, gh, édition de fichiers, web). La skill dépend de l'abstraction, jamais
d'un runtime spécifique.

### Orchestration et mise à l'échelle
| Point | Ce qu'il fait |
|---|---|
| `orient` | Carte compressée du dépôt/du travail |
| `normalize` | Élément de travail → schéma canonique |
| `intake` | Ingérer le travail depuis un lien de sprint/tableau |
| `source_adapter` | Connecteur de source uniforme (list/get/claim/update/attach/close) |
| `autoscale` | Taille de flotte sûre à partir du profil machine |
| `plan` / `decide` | Aide à la planification et à la décision |
| `execute` | Fan-out d'agents locaux pour le travail massif/mécanique |
| `issue_factory` | Boucle complète : découvrir→réclamer→implémenter→PR |
| `claim` | Réclamation atomique d'un élément, sûre entre sessions |
| `worktree` | Checkout isolé par élément |
| `dependency_graph` | Ordonnancement reprenable d'un DAG entre éléments |
| `durable_workflow` | Pipeline par élément en machine à états de phases reprenable |
| `work_queue` | File de priorité durable avec réessai auto + verrou d'écriture |
| `resource_governor` | Limitation dynamique en cours de boucle + plafonds par palier machine |
| `model_route` | Substrat viable le moins coûteux par sous-tâche (L0→distant) |
| `model_preflight` | Sonder un modèle utilisable avant de router la génération |

### Édition, qualité et preuve
| Point | Ce qu'il fait |
|---|---|
| `deterministic_edit` | Application mécanique, sans tokens, d'un changement décidé |
| `diagnostics` | Analyser la sortie build/test → erreurs structurées → itérer |
| `toolchain_detect` | Détecter la véritable stack build/lint/typecheck/test du dépôt |
| `validate` / `smoke` | Vérification par exécution : « ça marche, pas juste ça compile » |
| `delivery_gate` | DoD : vérification AC + régression + revue du diff + certificat |
| `endpoint_compare` | Dérive Web↔API↔agent → éléments de suivi |
| `web_verify` | Piloter un vrai navigateur pour prouver qu'un changement d'UI fonctionne |
| `pr` / `evidence` | Ouverture/mise à jour de PR + registre de preuves vérifiable |
| `retry` | Réessai+backoff classifié par classe d'échec |
| `reuse_precedent` | Faire correspondre un run résolu antérieur → réutiliser, pas régénérer |
| `trajectory` | Enregistrer le résultat du run pour l'auto-amélioration |
| `learn` | Apprendre d'un run — mettre à jour précédents/mémoire |
| `status` | Tableau de bord d'observabilité en direct |
| `capability_rank` | Classer quelle skill/quel outil convient à une sous-tâche |

### Tokens, contexte et sécurité
| Point | Ce qu'il fait |
|---|---|
| `recall` | Décisions / précédents antérieurs |
| `compress` | Compression du contexte / clamping de la sortie |
| `prompt_budget` | Enveloppe de prompt à budget de tokens + cache de fragments |
| `shell_exec` | Exécution shell bornée (structurée, limitée) |
| `transform_guard` | Vérifier qu'une compaction a conservé chaque token de code/URL/chemin/version |
| `action_gate` | Classer le risque de chaque mutation (safe/auto/ask) avant son exécution |
| `security` | Scan chaîne d'approvisionnement / secrets |
| `human_gate` | Canal d'approbation humaine asynchrone |
| `notify` | Pousser progression/blocage/résumé + recevoir les approbations |
| `checkpoint_restore` | Capturer l'état avant un batch risqué ; restaurer en cas d'échec |
| `watcher` | Planificateur / scrutateur durable (survit au redémarrage) |
| `savings_ledger` | Suivi réel de la dépense de tokens par session |
| `web_research` | Récupérer des connaissances externes actuelles, gated, avec provenance |

---

## 📦 Tout ce qu'elle contient

Un inventaire complet de ce qu'embarque la skill — chaque mécanisme, cité.

### La boucle (7 étapes + sous-étapes)
- **Étape 0** — Charger le contrat (protocole canonique).
- **Étape 1** — Identité + détection peu coûteuse de l'environnement.
- **Étape 1b** — Les 43 points d'extension (liaison native ou repli LLM).
- **Étape 1c** — Gate d'économie de tokens : `THINK / NO-THINK`, `INTERNET off by default`,
  `terminal-first execution`, **catalogue de réduction de sortie**, **plafonds par paliers
  de signal**, **collapse-succès + dédup**, **clamping de commande composée**, **paliers de
  densité routés par consommateur**, **fail-open**, **auto-clarté (la sécurité prime sur la
  concision)**.
- **Étape 1d** — Pré-vol : budget kill-switch, authentification source, armement du watcher.
- **Étape 2** — Découvrir + normaliser les éléments de travail (n'importe quel adaptateur de source).
- **Étape 2b** — Ingestion approfondie : lire le corps complet + commentaires, extraire les
  **critères d'acceptation**, **orienter dans le code**, **mode lecture signatures seules**,
  construire un plan.
- **Étape 2c** — DAG de dépendances + ordonnancement topologique.
- **Étape 3** — Routeur à deux voies : pool de workers continu **voie rapide** vs **voie lourde**
  · **isolation tenant compte des conflits** · **contrat de rapport de worker** · **mémoire des
  corrections**.
- **Étape 3b** — Ingestion continue : scrutateur intra-run + watcher au repos (voir le nouveau
  travail à tout moment).
- **Étape 3c** — Modèle de vitesse : pipeline (pas barrière), cache de compilation partagé,
  vérifier-une-fois-au-merge, **résumé de contexte partagé**.
- **Étape 3d** — Routage de modèle L0→L4 (déterministe → local → intermédiaire → raisonnement → payant).
- **Étape 4** — Boucle de qualité · **gate AC (vrai DoD)** · **vérification par exécution** ·
  **vérification adverse multi-vote** · **gate d'analyse statique**.
- **Étape 5** — Garde-fous de sécurité : scan de secrets, gate humain pour op irréversible,
  **verdict pré-exécution à 4 états**, **attestation composée par segment**, **config
  confiance-avant-chargement**, **gate d'intégrité de la chaîne d'approvisionnement**,
  **transform_guard**.
- **Étape 6** — Livrer + clôturer + auto-audit · **paquet de preuves** · **vérifier la réalité
  (ne jamais croire l'auto-rapport)** · **rollback-guard si le merge casse main**.
- **Étape 6b** — Boucler la boucle de feedback : CI → corriger, commentaires de revue → résoudre,
  branche-en-retard → réconcilier, **cycle de vie complet de la PR** jusqu'à être prête à fusionner.
- **Étape 7** — Boucle permanente 24h/24 (10 axes) : driver durable, matrice de couverture totale,
  état durable, **gouvernance des coûts + kill-switch strict**, sécurité sans surveillance,
  auto-réparation + **réessai intelligent par classe d'échec**, priorisation/WIP, observabilité
  + **audit périodique des économies** + **mesure par snapshot**, auto-amélioration, coordination
  et arrêt propre.

### Économie de tokens (intégrée depuis rtk + caveman)
- Exécution terminal-first — ne jamais simuler une commande.
- Table de substitution **multiplateforme** (Windows / macOS / Linux) : 30+ faits auxquels le
  terminal répond moins cher que le LLM.
- **Catalogue de réduction de sortie** sous forme de données : recette par commande,
  % d'économie attendu, garde-fou `skip-if-structured`.
- **Plafonds par paliers de signal** : `CAP_ERRORS / CAP_WARNINGS / CAP_LIST / CAP_INVENTORY`.
- **Collapse-succès** + **dédup-avec-comptes** (avec un garde-fou `unless errors`).
- **Clamping de commande composée** — par segment, sûr pour les pipes/redirections, fail-open.
- **Paliers de densité par consommateur** (machine vs humain) ; ignorer le contenu déjà dense.
- **Contrat de rapport de worker** — schéma concis status-token-first pour les sous-agents.
- **Baseline d'économie honnête** = bras de contrôle réaliste, **lié au passage d'un gate de
  qualité** (une compression qui échoue à son gate ne reçoit aucun crédit).

### Qualité et livraison
- Checklist DoD des critères d'acceptation · vérification par exécution · vérification adverse ·
  gate d'analyse statique · certificat de livraison · re-vérification de la réalité ·
  rollback automatique.

### Sécurité
- Scan de secrets · gate humain pour op irréversible · verdict à 4 états (ne jamais élever les
  privilèges) · attestation de commande composée · confiance-avant-chargement · intégrité de la
  chaîne d'approvisionnement · durcissement contre l'injection de prompt · kill-switch $ strict
  pour les runs sans surveillance.

### Autonomie 24h/24
- Planificateur durable · file en direct + watcher au repos · journal/état durable · disjoncteurs ·
  quarantaine dead-letter · auto-amélioration et méta-revue · réclamations atomiques multi-instances ·
  signal d'arrêt STOP propre.

---

## 🚀 Installation et utilisation

simplicio-tasks est une **skill** — un simple dossier que vous déposez dans n'importe quel
runtime qui charge des skills. Aucune dépendance, aucun binaire requis.

```bash
# Claude Code (project or user skills dir)
git clone https://github.com/wesleysimplicio/simplicio-tasks
cp -r simplicio-tasks/.claude/skills/simplicio-tasks  <your-repo>/.claude/skills/

# then, in your agent:
/simplicio-tasks finish all the open issues
```

Les autres runtimes (Codex, Gemini, Copilot, agents locaux) chargent le même
`SKILL.md` — voir [`AGENTS.md`](../AGENTS.md), [`CLAUDE.md`](../CLAUDE.md) et
[`GEMINI.md`](../GEMINI.md) pour les points d'entrée propres à chaque runtime. Là où un
runtime hôte expose des commandes natives, il les lie automatiquement aux points
d'extension ; sinon, les replis LLM couvrent **100 %** du travail.

**Avant un run 24h/24 sans surveillance :** fixez un plafond de coût
(`.orchestrator/loop-budget.json`, `daily_usd_ceiling > 0`), confirmez que
l'authentification source est persistante, et gardez activés le gate humain pour op
irréversible + le scan de secrets. Avec `ceiling = 0`, le watcher refuse de tourner sans
surveillance (fail-safe).

---

## 📊 Économie de tokens

Chaque message se termine par une ligne d'économie honnête :

```
simplicio-tasks: ~<spent> tokens · baseline ~<control-arm> · saved ~<saved> (<pct>%)
```

La baseline est le **chemin non orchestré le moins coûteux et sensé** vers le même
résultat — pas un épouvantail verbeux — et les économies ne sont **créditées que lorsque
la vérification par exécution de l'élément et le gate des critères d'acceptation passent**.
La compression brute n'est jamais comptée comme un succès à elle seule.

---

## 📄 Licence

MIT — voir [LICENSE](../LICENSE). Fait partie de l'écosystème [Simplicio](https://github.com/wesleysimplicio).
