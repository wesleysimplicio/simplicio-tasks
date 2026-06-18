# 🔁 simplicio-tasks — 万能のループ型AIオーケストレーター

<p align="center">
  <img src="../assets/simplicio-tasks-logo.svg" alt="simplicio-tasks" width="920" />
</p>

<p align="center">
  <a href="https://github.com/wesleysimplicio/simplicio-tasks/stargazers"><img src="https://img.shields.io/github/stars/wesleysimplicio/simplicio-tasks?style=social" alt="Stars"></a>
  <a href="https://github.com/wesleysimplicio/simplicio-tasks"><img src="https://img.shields.io/badge/skill-runtime--agnostic-39FF14" alt="Runtime-agnostic"></a>
  <a href="#-43個の拡張ポイント"><img src="https://img.shields.io/badge/extension%20points-43-00E08A" alt="43 extension points"></a>
  <a href="#-トークンエコノミー"><img src="https://img.shields.io/badge/tokens-up%20to%2096%25%20fewer-green" alt="Up to 96% fewer tokens"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License"></a>
</p>

<p align="center">
  <a href="#-tldr">TL;DR</a> ·
  <a href="#-caveman--rtk-との比較">caveman・rtk との比較</a> ·
  <a href="#-43個の拡張ポイント">43個のポイント</a> ·
  <a href="#-すべての内蔵機能">すべての内蔵機能</a> ·
  <a href="#-インストールと使い方">インストール</a>
</p>

<p align="center">
  <strong>🌍 Languages:</strong><br>
  <a href="../README.md">🇬🇧 English</a> |
  <a href="README.pt-BR.md">🇧🇷 Português</a> |
  <a href="README.es-ES.md">🇪🇸 Español</a> |
  <a href="README.fr-FR.md">🇫🇷 Français</a> |
  <a href="README.de-DE.md">🇩🇪 Deutsch</a> |
  <a href="README.it-IT.md">🇮🇹 Italiano</a> |
  🇯🇵 <strong>日本語</strong> |
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

**simplicio-tasks** は、あらゆる高性能LLM（Claude、Codex、Copilot、Gemini、Grok、ローカルモデル）を
**自律的にループするオーケストレーター**へと変える、単一でランタイム非依存の**スキル**です。
作業のまとまり——*「開いているissueを全部片付けて」*、*「CIキューを空にして」*、
*「Jiraボードを消化して」*——を指定すれば、ライフサイクル全体を自力で回します。

> **発見 → 理解 → 決定 → 実行 → 検証 → 修正 → 記録 → 繰り返し**

任意のソースから作業を発見し、重複を排除し、エージェント群をマシンに合わせて自動スケールし、
**コードをコンパイルするだけでなく実際に実行する**品質ループを通して各項目を実装し、PRを開き、
CI／レビューのフィードバックを解消し、マージし、新しい作業がないか**24時間365日**監視し続けます——
そのすべてを安全ゲートと強制的なコストキルスイッチの背後で行います。

これは**43個の名前付き拡張ポイント**を備えています。それぞれに常に動作するLLMフォールバックが用意され、
ホストランタイムにネイティブコマンドが存在する場合は*それにバインドされ*——そのステップを
決定論的かつほぼゼロトークンにします。**スキルはランタイムを名指ししない。ランタイムがスキルを検出する。**
この逆転こそが核心の仕掛けです。1つの汎用プロトコルがあり、その下にオプションでネイティブの高速性を注入できるのです。

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

## 🆚 caveman・rtk との比較

simplicio-tasks は、GitHub上で最も優れた2つのトークン節約ツール——
[**caveman**](https://github.com/JuliusBrussee/caveman)（74k★、*会話を圧縮する*）と
[**rtk**](https://github.com/rtk-ai/rtk)（63k★、*コマンドを圧縮する*）——を
**深く研究したうえで**構築されました。両者の長所を完全なオーケストレーターへと統合しています。
両者はトークンを削減しますが、simplicio-tasks は**実際に作業を行い**、その過程でトークンを削減します。

| | 🪨 **caveman** | ⚙️ **rtk** | 🔁 **simplicio-tasks** |
|---|---|---|---|
| **正体** | Claude Codeのスキル | Rust製CLIプロキシ | ランタイム非依存のスキル |
| **中核アイデア** | より簡潔に話す（無駄を削る） | 開発コマンドの出力を削減 | **作業全体をオーケストレーションする** |
| **対象範囲** | LLMの散文出力 | シェルコマンドの出力 | 作業ライフサイクル全体、端から端まで |
| **トークン節約** | 返信で約65% | コマンドで60〜90% | 両方——カタログ＋上限＋クランプ |
| **作業を行うか？** | ❌ 整形のみ | ❌ プロキシのみ | ✅ 発見→実装→マージ→クローズ |
| **多段階の自律性** | ❌ | ❌ | ✅ 継続的なワーカープール |
| **品質ゲート** | — | — | ✅ ACゲート・実行検証・敵対的検証・デリバリーゲート |
| **安全性** | — | semgrep、免責事項 | ✅ 4状態判定・証明・シークレットスキャン・人間ゲート・キルスイッチ |
| **24/7ループ** | ❌ | ❌ | ✅ 耐障害性のあるwatcher、自己修復 |
| **ランタイムバインディング** | Claude/Codex/Gemini | 任意（PATHプロキシ） | **任意**（43個の拡張ポイント） |
| **取り入れたもの** | 簡潔なワーカーレポート、密度ティア、決して言い換えないガード、誠実なベースライン | コマンド別の削減カタログ、シグナル階層化された上限、複合クランプ、フェイルオープン、4状態判定 | — |
| **取り入れなかったもの** | 文法的な単語の省略（コード品質を低下させる） | 言語別レジストリ（ランタイム固有） | — |

> 私たちは caveman の「原始人のように話す」単語省略を**意図的に拒否**しました——簡潔な
> *散文*は問題ありませんが、文法を壊すとコードや確認応答の品質が下がります。私たちは
> *規律*（コード／URL／パスを決して言い換えない）を残し、こけおどしは捨てました。

<p align="center">
  <img src="../assets/architecture.svg" alt="architecture" width="900" />
</p>

---

## 🧩 43個の拡張ポイント

作業のすべてのステップは**名前付きの拡張ポイント**で行われます。ホストランタイムがネイティブ機能を
公開していれば、それに**バインド**されます（決定論的、ほぼゼロトークン）。そうでなければ、LLMが標準ツール
（シェル、git、gh、ファイル編集、Web）で**フォールバック**を実行します。スキルは抽象に依存し、
特定のランタイムに依存することは決してありません。

### オーケストレーションとスケール
| ポイント | 役割 |
|---|---|
| `orient` | 圧縮されたリポジトリ／作業マップ |
| `normalize` | 作業項目 → 正規スキーマ |
| `intake` | スプリント／ボードのリンクから作業を取り込む |
| `source_adapter` | 統一的なソースコネクタ（list/get/claim/update/attach/close） |
| `autoscale` | マシンプロファイルから安全な群規模を算出 |
| `plan` / `decide` | 計画と意思決定の支援 |
| `execute` | 大量／機械的な作業のためのローカルエージェントのファンアウト |
| `issue_factory` | フルループ：発見→クレーム→実装→PR |
| `claim` | アトミックでセッション間でも安全な作業項目のクレーム |
| `worktree` | 項目ごとに隔離されたチェックアウト |
| `dependency_graph` | 項目間の再開可能なDAG順序付け |
| `durable_workflow` | 項目ごとのパイプラインを再開可能なフェーズ状態機械として |
| `work_queue` | 自動リトライ＋書き込みロック付きの耐障害性優先度キュー |
| `resource_governor` | ループ中の動的スロットリング＋マシンティアの上限 |
| `model_route` | サブタスクごとに最も安価で実用的な基盤（L0→リモート） |
| `model_preflight` | 生成をルーティングする前に使用可能なモデルをプローブ |

### 編集、品質、エビデンス
| ポイント | 役割 |
|---|---|
| `deterministic_edit` | 決定済みの変更を機械的・ゼロトークンで適用 |
| `diagnostics` | ビルド／テスト出力を解析 → 構造化エラー → 反復 |
| `toolchain_detect` | リポジトリの実際のビルド／lint／型チェック／テストスタックを検出 |
| `validate` / `smoke` | 実行検証：「コンパイルだけでなく動作する」 |
| `delivery_gate` | DoD：ACチェック＋リグレッション＋差分レビュー＋証明書 |
| `endpoint_compare` | Web↔API↔エージェントのずれ → フォローアップ項目 |
| `web_verify` | 実ブラウザを操作してUI変更が動作することを証明 |
| `pr` / `evidence` | PRの作成／更新＋検証可能なエビデンス台帳 |
| `retry` | 失敗クラス別に分類されたリトライ＋バックオフ |
| `reuse_precedent` | 過去の解決済み実行をマッチ → 再生成せず再利用 |
| `trajectory` | 自己改善のために実行結果を記録 |
| `learn` | 実行から学習 — 前例／メモリを更新 |
| `status` | ライブな可観測性ダッシュボード |
| `capability_rank` | どのスキル／ツールがサブタスクに適合するかをランク付け |

### トークン、コンテキスト、安全性
| ポイント | 役割 |
|---|---|
| `recall` | 過去の決定／前例 |
| `compress` | コンテキスト圧縮／出力クランプ |
| `prompt_budget` | トークン予算化されたプロンプトエンベロープ＋フラグメントキャッシュ |
| `shell_exec` | クランプされたシェル実行（構造化、境界付き） |
| `transform_guard` | 圧縮があらゆるコード／URL／パス／バージョントークンを保持したか検証 |
| `action_gate` | 実行前にあらゆる変更をリスク分類（safe/auto/ask） |
| `security` | サプライチェーン／シークレットスキャン |
| `human_gate` | 非同期の人間承認チャネル |
| `notify` | 進捗／ブロッカー／ダイジェストをプッシュ＋承認を受信 |
| `checkpoint_restore` | リスクのあるバッチ前に状態をスナップショット、失敗時に復元 |
| `watcher` | 耐障害性のあるスケジューラ／ポーラー（再起動を生き延びる） |
| `savings_ledger` | セッションごとの実トークン消費の追跡 |
| `web_research` | 来歴付きで、ゲートを通して最新の外部知識を取得 |

---

## 📦 すべての内蔵機能

スキルが備えるものの完全な一覧——あらゆるメカニズムを出典付きで。

### ループ（7ステップ＋サブステップ）
- **ステップ0** — 契約（正規プロトコル）の読み込み。
- **ステップ1** — アイデンティティ＋安価な環境検出。
- **ステップ1b** — 43個の拡張ポイント（ネイティブにバインド、またはLLMフォールバック）。
- **ステップ1c** — トークンエコノミーゲート：`THINK / NO-THINK`、`INTERNET off by default`、
  `terminal-first execution`、**出力削減カタログ**、**シグナル階層化された上限**、
  **成功の集約＋重複排除**、**複合コマンドのクランプ**、**消費者にルーティングされた
  密度ティア**、**フェイルオープン**、**自動明瞭化（安全性が簡潔さに優先）**。
- **ステップ1d** — プレフライト：キルスイッチ予算、ソース認証、watcherの起動。
- **ステップ2** — 作業項目の発見＋正規化（任意のソースアダプタ）。
- **ステップ2b** — 深い取り込み：本文＋コメントの完全な読み込み、**受け入れ基準**の抽出、
  **コードベースのオリエンテーション**、**シグネチャのみ読み込みモード**、計画の構築。
- **ステップ2c** — 依存DAG＋トポロジカルスケジューリング。
- **ステップ3** — デュアルパスルーター：**ファストパス** 対 **ヘビーパス** の継続的ワーカー
  プール・**競合を意識した隔離**・**ワーカーレポート契約**・**修正の
  メモリ**。
- **ステップ3b** — 継続的な取り込み：実行中のポーラー＋アイドルwatcher（いつでも新しい作業を
  検出）。
- **ステップ3c** — 速度モデル：パイプライン（バリアではない）、共有コンパイルキャッシュ、
  マージ時の一回検証、**共有コンテキストダイジェスト**。
- **ステップ3d** — モデルルーティング L0→L4（決定論的 → ローカル → 中位 → 推論 → 有料）。
- **ステップ4** — 品質ループ・**ACゲート（真のDoD）**・**実行検証**・
  **敵対的マルチ投票検証**・**静的解析ゲート**。
- **ステップ5** — 安全ゲート：シークレットスキャン、不可逆操作の人間ゲート、**4状態の
  実行前判定**、**セグメントごとの複合証明**、**読み込み前の信頼確認による
  設定**、**サプライチェーン完全性ゲート**、**transform_guard**。
- **ステップ6** — デリバリー＋クローズ＋自己監査・**エビデンスパッケージ**・**現実を
  検証する（自己申告を決して信頼しない）**・**マージがmainを壊した場合のロールバックガード**。
- **ステップ6b** — フィードバックループを閉じる：CI → 修正、レビューコメント → 解消、
  ブランチの遅延 → 調整、マージ準備が整うまでの完全な**PRライフサイクル**。
- **ステップ7** — 24時間365日の常駐ループ（10の軸）：耐障害性のあるドライバー、全体カバレッジ行列、
  耐障害性のある状態、**コストガバナンス＋強制キルスイッチ**、無人時の安全性、
  自己修復＋**失敗クラス別の知的リトライ**、優先順位付け／WIP、
  可観測性＋**定期的な節約監査**＋**スナップショット計測**、
  自己改善、協調とクリーンな停止。

### トークンエコノミー（rtk＋cavemanから統合）
- ターミナル優先の実行 — コマンドを決してシミュレートしない。
- **クロスプラットフォーム**な置換テーブル（Windows / macOS / Linux）：ターミナルがLLMより
  安価に答えられる30以上の事実。
- データとしての**出力削減カタログ**：コマンドごとのレシピ、期待される節約率%、
  `skip-if-structured`ガード。
- **シグナル階層化された上限**：`CAP_ERRORS / CAP_WARNINGS / CAP_LIST / CAP_INVENTORY`。
- **成功の集約**＋**カウント付き重複排除**（`unless errors`ガード付き）。
- **複合コマンドのクランプ** — セグメントごと、パイプ／リダイレクト安全、フェイルオープン。
- **消費者別の密度ティア**（機械 対 人間）；すでに高密度の内容はスキップ。
- **ワーカーレポート契約** — サブエージェント向けのステータストークン優先の簡潔なスキーマ。
- **誠実な節約ベースライン** = 現実的な対照群、**合格した品質ゲートに紐づけられる**
  （ゲートに不合格な圧縮は加点ゼロ）。

### 品質とデリバリー
- 受け入れ基準のDoDチェックリスト・実行検証・敵対的検証・
  静的解析ゲート・デリバリー証明書・現実の再検証・
  自動ロールバック。

### 安全性
- シークレットスキャン・不可逆操作の人間ゲート・4状態判定（権限を決して昇格させない）・
  複合コマンドの証明・読み込み前の信頼確認・サプライチェーン
  完全性・プロンプトインジェクション対策・無人実行向けの強制的な$キルスイッチ。

### 24/7の自律性
- 耐障害性のあるスケジューラ・ライブキュー＋アイドルwatcher・耐障害性のあるジャーナル／状態・
  サーキットブレーカー・デッドレター隔離・自己改善＆メタレビュー・
  マルチインスタンスのアトミッククレーム・クリーンなSTOPシグナル。

---

## 🚀 インストールと使い方

simplicio-tasks は**スキル**です——スキルを読み込む任意のランタイムにドロップする単一のフォルダ。
依存関係もバイナリも不要です。

```bash
# Claude Code (project or user skills dir)
git clone https://github.com/wesleysimplicio/simplicio-tasks
cp -r simplicio-tasks/.claude/skills/simplicio-tasks  <your-repo>/.claude/skills/

# then, in your agent:
/simplicio-tasks finish all the open issues
```

他のランタイム（Codex、Gemini、Copilot、ローカルエージェント）は同じ
`SKILL.md` を読み込みます——ランタイムごとのエントリーポイントについては
[`AGENTS.md`](../AGENTS.md)、[`CLAUDE.md`](../CLAUDE.md)、[`GEMINI.md`](../GEMINI.md) を参照してください。
ホストランタイムがネイティブコマンドを公開している場合は、それらを拡張ポイントに自動バインドします。
そうでなければ、LLMフォールバックが作業の**100%**をカバーします。

**無人の24/7実行の前に：** コスト上限を設定し（`.orchestrator/loop-budget.json`、
`daily_usd_ceiling > 0`）、ソース認証が永続的であることを確認し、不可逆操作の人間ゲート＋
シークレットスキャンを有効にしておいてください。`ceiling = 0` の場合、watcherは無人での
実行を拒否します（フェイルセーフ）。

---

## 📊 トークンエコノミー

すべてのメッセージは誠実な節約ラインで終わります：

```
simplicio-tasks: ~<spent> tokens · baseline ~<control-arm> · saved ~<saved> (<pct>%)
```

ベースラインは、同じ結果に至る**最も安価で妥当な非オーケストレーション経路**であり——
冗長なわら人形ではありません——節約は**項目の実行検証と受け入れ基準ゲートが合格した場合にのみ
加点されます**。生の圧縮それ自体が成功として数えられることは決してありません。

---

## 📄 ライセンス

MIT — [LICENSE](../LICENSE) を参照してください。[Simplicio](https://github.com/wesleysimplicio) エコシステムの一部です。
