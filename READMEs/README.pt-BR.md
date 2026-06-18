# 🔁 simplicio-tasks — O Orquestrador de IA Universal em Loop

<p align="center">
  <img src="../assets/simplicio-tasks-logo.svg" alt="simplicio-tasks" width="920" />
</p>

<p align="center">
  <a href="https://github.com/wesleysimplicio/simplicio-tasks/stargazers"><img src="https://img.shields.io/github/stars/wesleysimplicio/simplicio-tasks?style=social" alt="Stars"></a>
  <a href="https://github.com/wesleysimplicio/simplicio-tasks"><img src="https://img.shields.io/badge/skill-runtime--agnostic-39FF14" alt="Runtime-agnostic"></a>
  <a href="#-os-43-pontos-de-extensão"><img src="https://img.shields.io/badge/extension%20points-43-00E08A" alt="43 extension points"></a>
  <a href="#-economia-de-tokens"><img src="https://img.shields.io/badge/tokens-up%20to%2096%25%20fewer-green" alt="Up to 96% fewer tokens"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License"></a>
</p>

<p align="center">
  <a href="#-tldr">TL;DR</a> ·
  <a href="#-vs-caveman--rtk">vs caveman & rtk</a> ·
  <a href="#-os-43-pontos-de-extensão">43 Pontos</a> ·
  <a href="#-tudo-por-dentro">Tudo por Dentro</a> ·
  <a href="#-instalação--uso">Instalação</a>
</p>

<p align="center">
  <strong>🌍 Idiomas:</strong><br>
  <a href="../README.md">🇬🇧 English</a> |
  <strong>🇧🇷 Português</strong> |
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
  <a href="README.nl-NL.md">🇳🇱 Nederlands</a> |
  <a href="README.hi-IN.md">🇮🇳 हिन्दी</a> |
  <a href="README.ar-SA.md">🇸🇦 العربية</a>
</p>

---

## ⚡ TL;DR

O **simplicio-tasks** é uma única **skill** agnóstica de runtime que transforma qualquer
LLM forte (Claude, Codex, Copilot, Gemini, Grok, modelos locais) em um **orquestrador
autônomo em loop**. Você o aponta para um corpo de trabalho — *"finalize todas as issues
abertas"*, *"limpe a fila do CI"*, *"esvazie o board do Jira"* — e ele executa todo o
ciclo de vida sozinho:

> **descobrir → entender → decidir → agir → verificar → corrigir → registrar → repetir**

Ele descobre trabalho a partir de qualquer fonte, faz deduplicação, autoescala uma frota
de agentes de acordo com a sua máquina, implementa cada item através de um loop de qualidade
que **roda o código (não apenas o compila)**, abre PRs, resolve feedback de CI/revisão,
faz merge e segue observando **24/7** por novo trabalho — tudo por trás de portões de
segurança e um kill-switch de custo rígido.

Ele carrega **43 pontos de extensão nomeados**. Cada um tem um fallback de LLM que sempre
funciona, e cada um *se vincula ao comando nativo de um runtime hospedeiro* quando há um
presente — tornando o passo determinístico e quase-zero-token. **A skill não nomeia
nenhum runtime; o runtime detecta a skill.** Essa inversão é o truque inteiro: um protocolo
universal, com velocidade nativa opcional injetada por baixo.

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

O simplicio-tasks foi construído **após estudar a fundo** os dois melhores economizadores
de tokens do GitHub — o [**caveman**](https://github.com/JuliusBrussee/caveman) (74k★,
*comprime a conversa*) e o [**rtk**](https://github.com/rtk-ai/rtk) (63k★, *comprime os
comandos*). Ele incorpora o melhor de **ambos** em um orquestrador completo. Eles reduzem
tokens; o simplicio-tasks **faz o trabalho** e reduz tokens enquanto o faz.

| | 🪨 **caveman** | ⚙️ **rtk** | 🔁 **simplicio-tasks** |
|---|---|---|---|
| **O que é** | Skill do Claude Code | Proxy de CLI em Rust | Skill agnóstica de runtime |
| **Ideia central** | Falar mais conciso (cortar enchimento) | Reduzir saída de dev-commands | **Orquestrar o trabalho inteiro** |
| **Escopo** | Saída de prosa do LLM | Saída de comandos de shell | Ciclo de trabalho completo, de ponta a ponta |
| **Economia de tokens** | ~65% nas respostas | 60–90% nos comandos | Ambos — catálogo + limites + clamping |
| **Faz o trabalho?** | ❌ só formatação | ❌ só proxy | ✅ descobre→implementa→faz merge→fecha |
| **Autonomia multi-passo** | ❌ | ❌ | ✅ pool de workers contínuo |
| **Portões de qualidade** | — | — | ✅ portão de AC · run-verification · verificação adversarial · portão de entrega |
| **Segurança** | — | semgrep, avisos legais | ✅ veredito de 4 estados · atestação · varredura de segredos · portão humano · kill-switch |
| **Loop 24/7** | ❌ | ❌ | ✅ watcher durável, auto-recuperável |
| **Vínculo com runtime** | Claude/Codex/Gemini | qualquer um (proxy de PATH) | **qualquer um** (43 pontos de extensão) |
| **O que pegamos** | relatórios concisos de worker, camadas de densidade, guarda contra paráfrase, baseline honesto | catálogo de redução por comando, limites por nível de sinal, clamping composto, fail-open, veredito de 4 estados | — |
| **O que deixamos de fora** | corte de palavras gramaticais (degrada a qualidade do código) | registros por linguagem (específicos de runtime) | — |

> Nós **rejeitamos** de propósito o corte de palavras "fale-como-homem-das-cavernas" do
> caveman — *prosa* concisa é boa, mas mutilar a gramática degrada código e confirmações.
> Mantivemos a *disciplina* (nunca parafrasear código/URLs/caminhos), não o truque.

<p align="center">
  <img src="../assets/architecture.svg" alt="architecture" width="900" />
</p>

---

## 🧩 Os 43 pontos de extensão

Cada passo do trabalho acontece em um **ponto de extensão nomeado**. Se um runtime hospedeiro
expõe uma capacidade nativa, ele **se vincula** (determinístico, quase-zero token). Caso
contrário, o LLM executa o **fallback** com ferramentas padrão (shell, git, gh, edição de
arquivos, web). A skill depende da abstração, nunca de um runtime específico.

### Orquestração e escala
| Ponto | O que faz |
|---|---|
| `orient` | Mapa comprimido do repositório/trabalho |
| `normalize` | Item de trabalho → schema canônico |
| `intake` | Ingerir trabalho a partir de um link de sprint/board |
| `source_adapter` | Conector de fonte uniforme (list/get/claim/update/attach/close) |
| `autoscale` | Tamanho de frota seguro a partir do perfil da máquina |
| `plan` / `decide` | Suporte a planejamento e decisão |
| `execute` | Fan-out de agentes locais para trabalho em massa/mecânico |
| `issue_factory` | Loop completo: descobrir→reivindicar→implementar→PR |
| `claim` | Reivindicação de item de trabalho atômica e segura entre sessões |
| `worktree` | Checkout isolado por item |
| `dependency_graph` | Ordenação de DAG retomável entre itens |
| `durable_workflow` | Pipeline por item como uma máquina de estados de fases retomável |
| `work_queue` | Fila de prioridade durável com auto-retry + write-lock |
| `resource_governor` | Throttle dinâmico em pleno loop + tetos por nível de máquina |
| `model_route` | Substrato viável mais barato por sub-tarefa (L0→remoto) |
| `model_preflight` | Sondar um modelo utilizável antes de rotear a geração |

### Edição, qualidade e evidência
| Ponto | O que faz |
|---|---|
| `deterministic_edit` | Aplicação mecânica e zero-token de uma mudança decidida |
| `diagnostics` | Parsear saída de build/teste → erros estruturados → iterar |
| `toolchain_detect` | Detectar a stack real de build/lint/typecheck/test do repositório |
| `validate` / `smoke` | Run-verification: "funciona, não apenas compila" |
| `delivery_gate` | DoD: checagem de AC + regressão + revisão de diff + certificado |
| `endpoint_compare` | Divergência Web↔API↔agente → itens de acompanhamento |
| `web_verify` | Dirigir um navegador real para provar que uma mudança de UI funciona |
| `pr` / `evidence` | Abrir/atualizar PR + ledger de evidências verificável |
| `retry` | Retry+backoff classificado por classe de falha |
| `reuse_precedent` | Casar uma execução anterior resolvida → reutilizar, não regerar |
| `trajectory` | Registrar o resultado da execução para autoaperfeiçoamento |
| `learn` | Aprender com uma execução — atualizar precedentes/memória |
| `status` | Dashboard de observabilidade ao vivo |
| `capability_rank` | Ranquear qual skill/ferramenta se encaixa em uma sub-tarefa |

### Tokens, contexto e segurança
| Ponto | O que faz |
|---|---|
| `recall` | Decisões / precedentes anteriores |
| `compress` | Compressão de contexto / clamping de saída |
| `prompt_budget` | Envelope de prompt com orçamento de tokens + cache de fragmentos |
| `shell_exec` | Execução de shell com clamping (estruturada, limitada) |
| `transform_guard` | Verificar se uma compactação preservou todo token de código/URL/caminho/versão |
| `action_gate` | Classificar o risco de cada mutação (safe/auto/ask) antes de executar |
| `security` | Varredura de cadeia de suprimentos / segredos |
| `human_gate` | Canal de aprovação humana assíncrona |
| `notify` | Enviar progresso/bloqueio/resumo + receber aprovações |
| `checkpoint_restore` | Snapshot de estado antes de um lote arriscado; restaurar em caso de falha |
| `watcher` | Agendador / poller durável (sobrevive a reboot) |
| `savings_ledger` | Rastreamento real de gasto de tokens por sessão |
| `web_research` | Buscar conhecimento externo atual, com portão, com proveniência |

---

## 📦 Tudo por dentro

Um inventário completo do que a skill carrega — cada mecanismo, com citação.

### O loop (7 passos + sub-passos)
- **Passo 0** — Carregar o contrato (protocolo canônico).
- **Passo 1** — Identidade + detecção barata de ambiente.
- **Passo 1b** — Os 43 pontos de extensão (vincular nativo ou fallback do LLM).
- **Passo 1c** — Portão de economia de tokens: `THINK / NO-THINK`, `INTERNET off by default`,
  `terminal-first execution`, **catálogo de redução de saída**, **limites por nível de sinal**,
  **success-collapse + dedup**, **clamping de comandos compostos**, **camadas de densidade
  roteadas por consumidor**, **fail-open**, **auto-clareza (segurança sobrepõe brevidade)**.
- **Passo 1d** — Pre-flight: orçamento do kill-switch, autenticação da fonte, armar o watcher.
- **Passo 2** — Descobrir + normalizar itens de trabalho (qualquer adaptador de fonte).
- **Passo 2b** — Intake profundo: ler corpo completo + comentários, extrair **critérios de
  aceitação**, **orientar-se na base de código**, **modo de leitura só de assinaturas**,
  construir um plano.
- **Passo 2c** — DAG de dependências + agendamento topológico.
- **Passo 3** — Roteador de caminho duplo: pool de workers contínuo de **fast-path** vs
  **heavy-path** · **isolamento ciente de conflitos** · **contrato de relatório de worker** ·
  **memória de correções**.
- **Passo 3b** — Intake contínuo: poller intra-execução + watcher ocioso (vê novo trabalho
  a qualquer minuto).
- **Passo 3c** — Modelo de velocidade: pipeline (não barreira), cache de compilação
  compartilhado, verify-once-at-merge, **digest de contexto compartilhado**.
- **Passo 3d** — Roteamento de modelo L0→L4 (determinístico → local → médio → reasoning → pago).
- **Passo 4** — Loop de qualidade · **portão de AC (DoD real)** · **run-verification** ·
  **verificação adversarial por multi-voto** · **portão de análise estática**.
- **Passo 5** — Portões de segurança: varredura de segredos, portão humano para op irreversível,
  **veredito de 4 estados pré-execução**, **atestação composta por segmento**, **config de
  trust-before-load**, **portão de integridade de cadeia de suprimentos**, **transform_guard**.
- **Passo 6** — Entregar + fechar + auto-auditar · **pacote de evidências** · **verificar a
  realidade (nunca confiar no auto-relato)** · **rollback-guard se o merge quebrar a main**.
- **Passo 6b** — Fechar o loop de feedback: CI → corrigir, comentários de revisão → resolver,
  branch-atrasada → reconciliar, **ciclo de vida completo de PR** até estar pronto para merge.
- **Passo 7** — Loop permanente 24/7 (10 eixos): driver durável, matriz de cobertura total,
  estado durável, **governança de custo + kill-switch rígido**, segurança desassistida,
  auto-recuperação + **retry inteligente por classe de falha**, priorização/WIP,
  observabilidade + **auditoria periódica de economia** + **medição por snapshot**,
  autoaperfeiçoamento, coordenação e parada limpa.

### Economia de tokens (incorporada do rtk + caveman)
- Execução terminal-first — nunca simular um comando.
- Tabela de substituição **multiplataforma** (Windows / macOS / Linux): 30+ fatos que o
  terminal responde mais barato que o LLM.
- **Catálogo de redução de saída** como dado: receita por comando, % de economia esperada,
  guarda `skip-if-structured`.
- **Limites por nível de sinal**: `CAP_ERRORS / CAP_WARNINGS / CAP_LIST / CAP_INVENTORY`.
- **Success-collapse** + **dedup-com-contagens** (com uma guarda `unless errors`).
- **Clamping de comandos compostos** — por segmento, seguro a pipe/redirect, fail-open.
- **Camadas de densidade por consumidor** (máquina vs humano); pular conteúdo já denso.
- **Contrato de relatório de worker** — schema conciso com status-token-first para sub-agentes.
- **Baseline de economia honesto** = braço de controle realista, **vinculado a um portão de
  qualidade aprovado** (compressão que reprova no seu portão não rende crédito algum).

### Qualidade e entrega
- Checklist de DoD por critérios de aceitação · run-verification · verificação adversarial ·
  portão de análise estática · certificado de entrega · re-verificação da realidade ·
  rollback automático.

### Segurança
- Varredura de segredos · portão humano para op irreversível · veredito de 4 estados (nunca
  escalar privilégio) · atestação de comandos compostos · trust-before-load · integridade de
  cadeia de suprimentos · blindagem contra prompt-injection · kill-switch rígido de $ para
  execuções desassistidas.

### Autonomia 24/7
- Agendador durável · fila ao vivo + watcher ocioso · journal/estado durável ·
  disjuntores (circuit breakers) · quarentena de dead-letter · autoaperfeiçoamento e
  meta-revisão · reivindicações atômicas multi-instância · sinal de STOP limpo.

---

## 🚀 Instalação & uso

O simplicio-tasks é uma **skill** — uma única pasta que você coloca em qualquer runtime que
carregue skills. Sem dependência, sem binário necessário.

```bash
# Claude Code (project or user skills dir)
git clone https://github.com/wesleysimplicio/simplicio-tasks
cp -r simplicio-tasks/.claude/skills/simplicio-tasks  <your-repo>/.claude/skills/

# then, in your agent:
/simplicio-tasks finish all the open issues
```

Outros runtimes (Codex, Gemini, Copilot, agentes locais) carregam o mesmo
`SKILL.md` — veja [`AGENTS.md`](../AGENTS.md), [`CLAUDE.md`](../CLAUDE.md) e
[`GEMINI.md`](../GEMINI.md) para os pontos de entrada por runtime. Onde um runtime hospedeiro
expõe comandos nativos, ele os vincula automaticamente aos pontos de extensão; caso contrário,
os fallbacks do LLM cobrem **100%** do trabalho.

**Antes de uma execução 24/7 desassistida:** defina um teto de custo (`.orchestrator/loop-budget.json`,
`daily_usd_ceiling > 0`), confirme que a autenticação da fonte é persistente e mantenha ligados
o portão humano para op irreversível + a varredura de segredos. Com `ceiling = 0`, o watcher se
recusa a rodar desassistido (fail-safe).

---

## 📊 Economia de tokens

Toda mensagem termina com uma linha de economia honesta:

```
simplicio-tasks: ~<spent> tokens · baseline ~<control-arm> · saved ~<saved> (<pct>%)
```

O baseline é o **caminho não-orquestrado sensato mais barato** para o mesmo resultado — não
um espantalho verboso — e a economia só é **creditada quando o run-verification e o portão de
critérios de aceitação do item passam**. Compressão crua nunca é contada como sucesso por si só.

---

## 📄 Licença

MIT — veja [LICENSE](../LICENSE). Parte do ecossistema [Simplicio](https://github.com/wesleysimplicio).
