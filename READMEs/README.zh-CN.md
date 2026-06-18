# 🔁 simplicio-tasks —— 通用循环式 AI 编排器

<p align="center">
  <img src="../assets/simplicio-tasks-logo.svg" alt="simplicio-tasks" width="920" />
</p>

<p align="center">
  <a href="https://github.com/wesleysimplicio/simplicio-tasks/stargazers"><img src="https://img.shields.io/github/stars/wesleysimplicio/simplicio-tasks?style=social" alt="Stars"></a>
  <a href="https://github.com/wesleysimplicio/simplicio-tasks"><img src="https://img.shields.io/badge/skill-runtime--agnostic-39FF14" alt="Runtime-agnostic"></a>
  <a href="#-43-个扩展点"><img src="https://img.shields.io/badge/extension%20points-43-00E08A" alt="43 extension points"></a>
  <a href="#-token-经济"><img src="https://img.shields.io/badge/tokens-up%20to%2096%25%20fewer-green" alt="Up to 96% fewer tokens"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License"></a>
</p>

<p align="center">
  <a href="#-tldr">摘要</a> ·
  <a href="#-对比-caveman--rtk">对比 caveman 与 rtk</a> ·
  <a href="#-43-个扩展点">43 个扩展点</a> ·
  <a href="#-内含的一切">内含的一切</a> ·
  <a href="#-安装与使用">安装</a>
</p>

<p align="center">
  <strong>🌍 语言：</strong><br>
  <a href="../README.md">🇬🇧 English</a> |
  <a href="README.pt-BR.md">🇧🇷 Português</a> |
  <a href="README.es-ES.md">🇪🇸 Español</a> |
  <a href="README.fr-FR.md">🇫🇷 Français</a> |
  <a href="README.de-DE.md">🇩🇪 Deutsch</a> |
  <a href="README.it-IT.md">🇮🇹 Italiano</a> |
  <a href="README.ja-JP.md">🇯🇵 日本語</a> |
  <a href="README.ko-KR.md">🇰🇷 한국어</a> |
  <strong>🇨🇳 简体中文</strong> |
  <a href="README.ru-RU.md">🇷🇺 Русский</a> |
  <a href="README.pl-PL.md">🇵🇱 Polski</a> |
  <a href="README.tr-TR.md">🇹🇷 Türkçe</a> |
  <a href="README.nl-NL.md">🇳🇱 Nederlands</a> |
  <a href="README.hi-IN.md">🇮🇳 हिन्दी</a> |
  <a href="README.ar-SA.md">🇸🇦 العربية</a>
</p>

---

## ⚡ TL;DR

**simplicio-tasks** 是一个单一的、与运行时无关的 **skill（技能）**，它能把任何强大的 LLM
（Claude、Codex、Copilot、Gemini、Grok、本地模型）变成一个**自主的循环式编排器**。
你只需把它指向一批工作 —— *“完成所有未关闭的 issue”*、
*“清空 CI 队列”*、*“清干净 Jira 看板”* —— 它就会自行运转完整的生命周期：

> **发现 → 理解 → 决策 → 行动 → 验证 → 纠正 → 记录 → 重复**

它会从任意来源发现工作、去重、按你的机器自动伸缩一支智能体队伍，
通过一个**真正运行代码（而不仅仅是编译）**的质量循环来实现每一项工作，
开 PR、处理 CI/评审反馈、合并，并持续 **7×24** 监视新工作 ——
这一切都在安全门控和一个硬性成本急停开关的背后进行。

它携带 **43 个具名扩展点**。每个扩展点都有一个始终可用的 LLM 兜底实现，
并且当宿主运行时存在原生命令时，每个扩展点都会*绑定到该运行时的原生命令* —— 让这一步骤变得确定性且接近零 token。
**skill 不指名任何运行时；是运行时来探测 skill。** 这种反转正是整个诀窍所在：
一套通用协议，底层可选地注入原生速度。

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

## 🆚 对比 caveman 与 rtk

simplicio-tasks 是在**深入研究**了 GitHub 上两个最出色的 token 节省工具之后构建的 ——
[**caveman**](https://github.com/JuliusBrussee/caveman)（74k★，*压缩对话*）
与 [**rtk**](https://github.com/rtk-ai/rtk)（63k★，*压缩命令*）。
它把**两者**的精华融入一个完整的编排器。它们减少 token；
而 simplicio-tasks **完成工作**，并在完成工作的同时减少 token。

| | 🪨 **caveman** | ⚙️ **rtk** | 🔁 **simplicio-tasks** |
|---|---|---|---|
| **它是什么** | Claude Code skill | Rust CLI 代理 | 与运行时无关的 skill |
| **核心理念** | 说话更精简（去掉冗词） | 缩减开发命令的输出 | **编排整个任务** |
| **作用范围** | LLM 的散文输出 | Shell 命令输出 | 端到端的完整工作生命周期 |
| **Token 节省** | 回复约 65% | 命令 60–90% | 两者兼得 —— 目录 + 上限 + 钳制 |
| **会完成工作吗？** | ❌ 仅格式化 | ❌ 仅代理 | ✅ 发现→实现→合并→关闭 |
| **多步自主** | ❌ | ❌ | ✅ 持续运行的工作池 |
| **质量门控** | — | — | ✅ AC 门控 · 运行验证 · 对抗式验证 · 交付门控 |
| **安全** | — | semgrep、免责声明 | ✅ 四态裁决 · 证明 · 密钥扫描 · 人工门控 · 急停开关 |
| **7×24 循环** | ❌ | ❌ | ✅ 持久化看守者，自愈 |
| **运行时绑定** | Claude/Codex/Gemini | 任意（PATH 代理） | **任意**（43 个扩展点） |
| **我们采纳了什么** | 精简的工作报告、密度分级、绝不改写护栏、诚实基线 | 逐命令的缩减目录、信号分级上限、复合钳制、fail-open、四态裁决 | — |
| **我们舍弃了什么** | 语法层面的丢词（会降低代码质量） | 逐语言注册表（特定于运行时） | — |

> 我们**有意拒绝**了 caveman 那种“像穴居人一样说话”的丢词做法 —— 精简的*散文*没问题，
> 但破坏语法会降低代码与确认信息的质量。我们保留的是那份*纪律*
> （绝不改写代码/URL/路径），而非那个噱头。

<p align="center">
  <img src="../assets/architecture.svg" alt="architecture" width="900" />
</p>

---

## 🧩 43 个扩展点

每一步工作都发生在一个**具名扩展点**上。如果宿主运行时暴露了某项原生能力，
该扩展点就会**绑定**（确定性、接近零 token）。否则 LLM 会用标准工具
（shell、git、gh、文件编辑、web）执行**兜底实现**。skill 依赖的是抽象，而绝不依赖某个具体的运行时。

### 编排与伸缩
| 扩展点 | 它做什么 |
|---|---|
| `orient` | 压缩后的仓库/工作地图 |
| `normalize` | 工作项 → 规范化 schema |
| `intake` | 从 sprint/看板链接摄入工作 |
| `source_adapter` | 统一的来源连接器（list/get/claim/update/attach/close） |
| `autoscale` | 根据机器画像得出安全的队伍规模 |
| `plan` / `decide` | 规划与决策支持 |
| `execute` | 针对批量/机械性工作的本地智能体扇出 |
| `issue_factory` | 完整循环：发现→认领→实现→PR |
| `claim` | 原子的、跨会话安全的工作项认领 |
| `worktree` | 每项工作隔离的检出 |
| `dependency_graph` | 工作项之间可恢复的 DAG 排序 |
| `durable_workflow` | 把每项工作的流水线作为可恢复的阶段状态机 |
| `work_queue` | 带自动重试 + 写锁的持久化优先级队列 |
| `resource_governor` | 循环中途的动态限流 + 机器分级上限 |
| `model_route` | 为每个子任务选择最便宜可行的底座（L0→远程） |
| `model_preflight` | 在路由生成前探测一个可用的模型 |

### 编辑、质量与证据
| 扩展点 | 它做什么 |
|---|---|
| `deterministic_edit` | 对已决策的更改进行机械的、零 token 的应用 |
| `diagnostics` | 解析构建/测试输出 → 结构化错误 → 迭代 |
| `toolchain_detect` | 探测仓库真实的构建/lint/类型检查/测试栈 |
| `validate` / `smoke` | 运行验证：“能跑，而不仅仅是能编译” |
| `delivery_gate` | DoD：AC 检查 + 回归 + diff 评审 + 证书 |
| `endpoint_compare` | Web↔API↔智能体的漂移 → 生成后续工作项 |
| `web_verify` | 驱动真实浏览器以证明 UI 更改有效 |
| `pr` / `evidence` | PR 打开/更新 + 可验证的证据账本 |
| `retry` | 按失败类别分类的重试 + 退避 |
| `reuse_precedent` | 匹配先前已解决的运行 → 复用，而非重新生成 |
| `trajectory` | 记录运行结果用于自我改进 |
| `learn` | 从一次运行中学习 —— 更新先例/记忆 |
| `status` | 实时可观测性仪表盘 |
| `capability_rank` | 评估哪个 skill/工具最适合某个子任务 |

### Token、上下文与安全
| 扩展点 | 它做什么 |
|---|---|
| `recall` | 先前的决策 / 先例 |
| `compress` | 上下文压缩 / 输出钳制 |
| `prompt_budget` | 受 token 预算约束的提示封套 + 片段缓存 |
| `shell_exec` | 受钳制的 shell 执行（结构化、有界） |
| `transform_guard` | 验证一次压缩是否保留了每一个代码/URL/路径/版本 token |
| `action_gate` | 在每个变更运行前对其风险分级（safe/auto/ask） |
| `security` | 供应链 / 密钥扫描 |
| `human_gate` | 异步的人工审批通道 |
| `notify` | 推送进度/阻塞/摘要 + 接收审批 |
| `checkpoint_restore` | 在有风险的批处理前快照状态；失败时恢复 |
| `watcher` | 持久化调度器 / 轮询器（可在重启后存活） |
| `savings_ledger` | 按会话追踪真实的 token 花费 |
| `web_research` | 受门控地获取当前外部知识，带溯源 |

---

## 📦 内含的一切

skill 所携带内容的完整清单 —— 每一项机制，皆有出处。

### 循环（7 个步骤 + 子步骤）
- **步骤 0** —— 加载契约（规范协议）。
- **步骤 1** —— 身份识别 + 廉价的环境探测。
- **步骤 1b** —— 43 个扩展点（绑定原生或 LLM 兜底）。
- **步骤 1c** —— Token 经济门控：`THINK / NO-THINK`、`INTERNET off by default`、
  `terminal-first execution`、**输出缩减目录**、**信号分级上限**、
  **成功折叠 + 去重**、**复合命令钳制**、**按消费者路由的密度分级**、
  **fail-open**、**自动清晰度（安全性优先于简洁性）**。
- **步骤 1d** —— 预检：急停开关预算、来源鉴权、武装看守者。
- **步骤 2** —— 发现 + 规范化工作项（任意来源适配器）。
- **步骤 2b** —— 深度摄入：阅读完整正文 + 评论，提取**验收标准**、
  **定位代码库**、**仅签名阅读模式**，并构建计划。
- **步骤 2c** —— 依赖 DAG + 拓扑调度。
- **步骤 3** —— 双路径路由器：**快路径** vs **重路径**的持续工作池 ·
  **冲突感知隔离** · **工作报告契约** · **纠正记忆**。
- **步骤 3b** —— 持续摄入：运行内轮询器 + 空闲看守者（任意时刻都能看到新工作）。
- **步骤 3c** —— 速度模型：流水线（而非屏障）、共享编译缓存、
  合并时一次性验证、**共享上下文摘要**。
- **步骤 3d** —— 模型路由 L0→L4（确定性 → 本地 → 中端 → 推理 → 付费）。
- **步骤 4** —— 质量循环 · **AC 门控（真正的 DoD）** · **运行验证** ·
  **对抗式多票验证** · **静态分析门控**。
- **步骤 5** —— 安全门控：密钥扫描、不可逆操作人工门控、**四态执行前裁决**、
  **逐段复合证明**、**先信任后加载的配置**、**供应链完整性门控**、**transform_guard**。
- **步骤 6** —— 交付 + 关闭 + 自审 · **证据包** · **核实现实（绝不轻信自我报告）** ·
  **若合并破坏 main 则回滚保护**。
- **步骤 6b** —— 闭合反馈环：CI → 修复，评审评论 → 解决，
  分支落后 → 协调，完整的 **PR 生命周期**直至可合并。
- **步骤 7** —— 7×24 常驻循环（10 个维度）：持久化驱动器、全覆盖矩阵、
  持久化状态、**成本治理 + 硬性急停开关**、无人值守安全、
  自愈 + **按失败类别的智能重试**、优先级/WIP、
  可观测性 + **周期性节省审计** + **快照度量**、
  自我改进、协调与干净停止。

### Token 经济（由 rtk + caveman 融合而来）
- 终端优先执行 —— 绝不模拟命令。
- **跨平台**替换表（Windows / macOS / Linux）：30+ 个由终端回答比 LLM 更便宜的事实。
- 以数据形式呈现的**输出缩减目录**：逐命令的配方、预期节省 %、`skip-if-structured` 护栏。
- **信号分级上限**：`CAP_ERRORS / CAP_WARNINGS / CAP_LIST / CAP_INVENTORY`。
- **成功折叠** + **带计数去重**（带 `unless errors` 护栏）。
- **复合命令钳制** —— 逐段、对管道/重定向安全、fail-open。
- **按消费者的密度分级**（机器 vs 人类）；跳过已经很密集的内容。
- **工作报告契约** —— 面向子智能体的“状态 token 优先”精简 schema。
- **诚实的节省基线** = 现实的对照组，**绑定到一个通过的质量门控**
  （未能通过其门控的压缩得零分）。

### 质量与交付
- 验收标准 DoD 清单 · 运行验证 · 对抗式验证 ·
  静态分析门控 · 交付证书 · 现实复验 · 自动回滚。

### 安全
- 密钥扫描 · 不可逆操作人工门控 · 四态裁决（绝不提升权限） ·
  复合命令证明 · 先信任后加载 · 供应链完整性 ·
  提示注入加固 · 面向无人值守运行的硬性 $ 急停开关。

### 7×24 自主
- 持久化调度器 · 实时队列 + 空闲看守者 · 持久化日志/状态 ·
  熔断器 · 死信隔离 · 自我改进与元评审 ·
  多实例原子认领 · 干净的 STOP 信号。

---

## 🚀 安装与使用

simplicio-tasks 是一个 **skill** —— 一个单独的文件夹，你把它丢进任何能加载 skill 的运行时即可。
无依赖，无需二进制文件。

```bash
# Claude Code (project or user skills dir)
git clone https://github.com/wesleysimplicio/simplicio-tasks
cp -r simplicio-tasks/.claude/skills/simplicio-tasks  <your-repo>/.claude/skills/

# then, in your agent:
/simplicio-tasks finish all the open issues
```

其他运行时（Codex、Gemini、Copilot、本地智能体）加载同一个
`SKILL.md` —— 各运行时的入口点请参见 [`AGENTS.md`](../AGENTS.md)、[`CLAUDE.md`](../CLAUDE.md) 和
[`GEMINI.md`](../GEMINI.md)。当宿主运行时暴露了原生命令时，
它会自动把这些命令绑定到扩展点；否则 LLM 兜底实现会覆盖 **100%** 的工作。

**在无人值守的 7×24 运行之前：** 设定一个成本上限（`.orchestrator/loop-budget.json`，
`daily_usd_ceiling > 0`），确认来源鉴权是持久化的，并保持不可逆操作人工门控 + 密钥扫描处于开启状态。
当 `ceiling = 0` 时，看守者会拒绝无人值守运行（fail-safe）。

---

## 📊 Token 经济

每条消息都以一行诚实的节省汇总结尾：

```
simplicio-tasks: ~<spent> tokens · baseline ~<control-arm> · saved ~<saved> (<pct>%)
```

基线是达到相同结果的**最便宜的合理非编排路径** ——
而非一个冗长的稻草人 —— 并且节省**仅在该工作项的运行验证与验收标准门控通过时才计入**。
原始压缩本身绝不被计为成功。

---

## 📄 许可证

MIT —— 参见 [LICENSE](../LICENSE)。本项目是 [Simplicio](https://github.com/wesleysimplicio) 生态系统的一部分。
