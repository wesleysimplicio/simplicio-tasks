# 🔁 simplicio-tasks — 범용 반복 루프 AI 오케스트레이터

<p align="center">
  <img src="../assets/simplicio-tasks-logo.svg" alt="simplicio-tasks" width="920" />
</p>

<p align="center">
  <a href="https://github.com/wesleysimplicio/simplicio-tasks/stargazers"><img src="https://img.shields.io/github/stars/wesleysimplicio/simplicio-tasks?style=social" alt="Stars"></a>
  <a href="https://github.com/wesleysimplicio/simplicio-tasks"><img src="https://img.shields.io/badge/skill-runtime--agnostic-39FF14" alt="Runtime-agnostic"></a>
  <a href="#-43개의-확장-지점"><img src="https://img.shields.io/badge/extension%20points-43-00E08A" alt="43 extension points"></a>
  <a href="#-토큰-경제"><img src="https://img.shields.io/badge/tokens-up%20to%2096%25%20fewer-green" alt="Up to 96% fewer tokens"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License"></a>
</p>

<p align="center">
  <a href="#-tldr">요약</a> ·
  <a href="#-caveman--rtk와의-비교">caveman & rtk와의 비교</a> ·
  <a href="#-43개의-확장-지점">43개 지점</a> ·
  <a href="#-내부에-담긴-모든-것">내부에 담긴 모든 것</a> ·
  <a href="#-설치--사용">설치</a>
</p>

<p align="center">
  <strong>🌍 Languages:</strong><br>
  <a href="../README.md">🇬🇧 English</a> |
  <a href="README.pt-BR.md">🇧🇷 Português</a> |
  <a href="README.es-ES.md">🇪🇸 Español</a> |
  <a href="README.fr-FR.md">🇫🇷 Français</a> |
  <a href="README.de-DE.md">🇩🇪 Deutsch</a> |
  <a href="README.it-IT.md">🇮🇹 Italiano</a> |
  <a href="README.ja-JP.md">🇯🇵 日本語</a> |
  <strong>🇰🇷 한국어</strong> |
  <a href="README.zh-CN.md">🇨🇳 简体中文</a> |
  <a href="README.ru-RU.md">🇷🇺 Русский</a> |
  <a href="README.pl-PL.md">🇵🇱 Polski</a> |
  <a href="README.tr-TR.md">🇹🇷 Türkçe</a> |
  <a href="README.nl-NL.md">🇳🇱 Nederlands</a> |
  <a href="README.hi-IN.md">🇮🇳 हिन्दी</a> |
  <a href="README.ar-SA.md">🇸🇦 العربية</a>
</p>

---

## ⚡ 요약

**simplicio-tasks**는 강력한 LLM(Claude, Codex, Copilot, Gemini, Grok, 로컬 모델)을
**자율 반복 루프 오케스트레이터**로 바꿔 주는, 런타임에 종속되지 않는 단일 **스킬**입니다.
처리할 작업 더미 — *"열린 이슈를 전부 끝내라"*, *"CI 큐를 비워라"*,
*"Jira 보드를 비워라"* — 를 가리키기만 하면, 전체 생애주기를 스스로 실행합니다.

> **발견 → 이해 → 결정 → 실행 → 검증 → 수정 → 기록 → 반복**

어떤 소스에서든 작업을 발견하고, 중복을 제거하며, 사용자의 머신에 맞춰 에이전트 함대를
자동으로 확장하고, **코드를 단지 컴파일하는 게 아니라 실제로 실행하는** 품질 루프를 통해
각 항목을 구현하며, PR을 열고, CI/리뷰 피드백을 해결하고, 병합한 뒤, 새 작업을 찾아
**24시간 연중무휴**로 계속 감시합니다 — 이 모든 것이 안전 게이트와 강력한 비용
킬 스위치의 통제 아래에서 이뤄집니다.

이 스킬은 **43개의 명명된 확장 지점**을 갖추고 있습니다. 각 지점에는 언제나 동작하는 LLM
폴백이 있으며, 호스트 런타임의 네이티브 명령이 존재하면 *각 지점이 거기에 바인딩되어* —
해당 단계를 결정론적이며 거의 토큰을 쓰지 않게 만듭니다. **스킬은 어떤 런타임도 명시하지
않으며, 런타임이 스킬을 감지합니다.** 이 역전이 핵심 비결입니다. 하나의 범용 프로토콜에,
선택적인 네이티브 속도를 그 아래에 주입하는 것이죠.

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

## 🆚 caveman & rtk와의 비교

simplicio-tasks는 GitHub에서 가장 뛰어난 두 토큰 절약 도구 —
[**caveman**](https://github.com/JuliusBrussee/caveman)(별 74k, *대화를 압축*)과
[**rtk**](https://github.com/rtk-ai/rtk)(별 63k, *명령을 압축*) — 를 **깊이 연구한 후**
만들어졌습니다. 둘의 장점을 하나의 완전한 오케스트레이터로 녹여 냈습니다. 두 도구는 토큰을
줄이지만, simplicio-tasks는 **실제로 일을 하면서** 그와 동시에 토큰을 줄입니다.

| | 🪨 **caveman** | ⚙️ **rtk** | 🔁 **simplicio-tasks** |
|---|---|---|---|
| **무엇인가** | Claude Code 스킬 | Rust CLI 프록시 | 런타임 비종속 스킬 |
| **핵심 아이디어** | 더 간결하게 말하기(군더더기 제거) | 개발 명령 출력 축소 | **전체 작업을 오케스트레이션** |
| **범위** | LLM 산문 출력 | 셸 명령 출력 | 작업 생애주기 전체, 처음부터 끝까지 |
| **토큰 절감** | 응답에서 약 65% | 명령에서 60–90% | 둘 다 — 카탈로그 + 상한 + 클램핑 |
| **실제로 일을 하는가?** | ❌ 포매팅만 | ❌ 프록시만 | ✅ 발견→구현→병합→종료 |
| **다단계 자율성** | ❌ | ❌ | ✅ 지속적 워커 풀 |
| **품질 게이트** | — | — | ✅ AC 게이트 · 실행 검증 · 적대적 검증 · 전달 게이트 |
| **안전성** | — | semgrep, 면책 고지 | ✅ 4상태 판정 · 증명 · 시크릿 스캔 · 사람 게이트 · 킬 스위치 |
| **24/7 루프** | ❌ | ❌ | ✅ 내구성 있는 워처, 자가 치유 |
| **런타임 바인딩** | Claude/Codex/Gemini | 모두(PATH 프록시) | **모두**(43개의 확장 지점) |
| **무엇을 가져왔나** | 간결한 워커 보고서, 밀도 등급, 절대-바꿔-쓰지-않는 가드, 정직한 기준선 | 명령별 축소 카탈로그, 신호 등급별 상한, 복합 클램핑, fail-open, 4상태 판정 | — |
| **무엇을 버렸나** | 문법 단어 누락(코드 품질 저하) | 언어별 레지스트리(런타임 종속) | — |

> caveman의 "원시인처럼 말하기" 식 단어 누락은 일부러 **버렸습니다**. 간결한 *산문*은
> 괜찮지만, 문법을 망가뜨리면 코드와 확인 문구의 품질이 떨어지기 때문입니다. 우리는 그
> *원칙*(코드/URL/경로를 절대 바꿔 쓰지 않기)은 가져왔고, 잔재주는 가져오지 않았습니다.

<p align="center">
  <img src="../assets/architecture.svg" alt="architecture" width="900" />
</p>

---

## 🧩 43개의 확장 지점

작업의 모든 단계는 **명명된 확장 지점**에서 일어납니다. 호스트 런타임이 네이티브 기능을
노출하면 거기에 **바인딩**되고(결정론적이며 거의 토큰을 쓰지 않음), 그렇지 않으면 LLM이
표준 도구(셸, git, gh, 파일 편집, 웹)로 **폴백**을 수행합니다. 스킬은 항상 추상화에
의존하며, 특정 런타임에는 절대 의존하지 않습니다.

### 오케스트레이션 & 확장
| 지점 | 하는 일 |
|---|---|
| `orient` | 압축된 저장소/작업 지도 |
| `normalize` | 작업 항목 → 정규 스키마 |
| `intake` | 스프린트/보드 링크에서 작업 수집 |
| `source_adapter` | 통일된 소스 커넥터(list/get/claim/update/attach/close) |
| `autoscale` | 머신 프로파일에 따른 안전한 함대 크기 |
| `plan` / `decide` | 계획 및 의사결정 지원 |
| `execute` | 대량/기계적 작업을 위한 로컬 에이전트 팬아웃 |
| `issue_factory` | 전체 루프: 발견→점유→구현→PR |
| `claim` | 원자적이며 세션 간 안전한 작업 항목 점유 |
| `worktree` | 항목별 격리된 체크아웃 |
| `dependency_graph` | 항목 간 재개 가능한 DAG 순서 결정 |
| `durable_workflow` | 항목별 파이프라인을 재개 가능한 단계 상태 머신으로 |
| `work_queue` | 자동 재시도 + 쓰기 잠금이 있는 내구성 우선순위 큐 |
| `resource_governor` | 루프 도중 동적 스로틀 + 머신 등급 상한 |
| `model_route` | 하위 작업마다 가장 저렴하게 쓸 수 있는 기반(L0→원격) |
| `model_preflight` | 생성을 라우팅하기 전에 쓸 수 있는 모델을 탐색 |

### 편집, 품질 & 증거
| 지점 | 하는 일 |
|---|---|
| `deterministic_edit` | 결정된 변경을 기계적·제로 토큰으로 적용 |
| `diagnostics` | 빌드/테스트 출력 파싱 → 구조화된 오류 → 반복 |
| `toolchain_detect` | 저장소의 실제 빌드/린트/타입체크/테스트 스택 감지 |
| `validate` / `smoke` | 실행 검증: "컴파일만이 아니라 동작한다" |
| `delivery_gate` | DoD: AC 확인 + 회귀 + 디프 리뷰 + 인증서 |
| `endpoint_compare` | 웹↔API↔에이전트 드리프트 → 후속 항목 |
| `web_verify` | 실제 브라우저를 구동해 UI 변경이 동작함을 증명 |
| `pr` / `evidence` | PR 열기/갱신 + 검증 가능한 증거 원장 |
| `retry` | 실패 분류에 따른 재시도+백오프 |
| `reuse_precedent` | 이전에 해결된 실행과 매칭 → 재생성이 아니라 재사용 |
| `trajectory` | 자가 개선을 위한 실행 결과 기록 |
| `learn` | 실행에서 학습 — 선례/메모리 갱신 |
| `status` | 실시간 관측 가능성 대시보드 |
| `capability_rank` | 어떤 스킬/도구가 하위 작업에 맞는지 순위 매김 |

### 토큰, 컨텍스트 & 안전성
| 지점 | 하는 일 |
|---|---|
| `recall` | 이전 결정 / 선례 |
| `compress` | 컨텍스트 압축 / 출력 클램핑 |
| `prompt_budget` | 토큰 예산이 부여된 프롬프트 봉투 + 프래그먼트 캐시 |
| `shell_exec` | 클램핑된 셸 실행(구조화, 경계 설정) |
| `transform_guard` | 압축이 모든 코드/URL/경로/버전 토큰을 보존했는지 검증 |
| `action_gate` | 실행 전에 모든 변경을 위험도 분류(safe/auto/ask) |
| `security` | 공급망 / 시크릿 스캔 |
| `human_gate` | 비동기 사람 승인 채널 |
| `notify` | 진행/차단/요약 푸시 + 승인 수신 |
| `checkpoint_restore` | 위험한 배치 전 상태 스냅샷; 실패 시 복원 |
| `watcher` | 내구성 있는 스케줄러 / 폴러(재부팅에도 살아남음) |
| `savings_ledger` | 세션별 실제 토큰 소비 추적 |
| `web_research` | 출처와 함께 게이트를 거쳐 최신 외부 지식을 가져옴 |

---

## 📦 내부에 담긴 모든 것

스킬이 갖추고 있는 모든 것의 전체 목록 — 모든 메커니즘을 근거와 함께.

### 루프(7단계 + 하위 단계)
- **0단계** — 계약 로드(정규 프로토콜).
- **1단계** — 정체성 + 저렴한 환경 감지.
- **1b단계** — 43개의 확장 지점(네이티브 바인딩 또는 LLM 폴백).
- **1c단계** — 토큰 경제 게이트: `THINK / NO-THINK`, `INTERNET off by default`,
  `terminal-first execution`, **출력 축소 카탈로그**, **신호 등급별 상한**,
  **성공 접기 + 중복 제거**, **복합 명령 클램핑**, **소비자별 라우팅된
  밀도 등급**, **fail-open**, **자동 명료성(안전이 간결함에 우선)**.
- **1d단계** — 사전 점검: 킬 스위치 예산, 소스 인증, 워처 무장.
- **2단계** — 작업 항목 발견 + 정규화(모든 소스 어댑터).
- **2b단계** — 심층 수집: 전체 본문 + 댓글 읽기, **수용 기준** 추출,
  **코드베이스 방향 잡기**, **시그니처 전용 읽기 모드**, 계획 수립.
- **2c단계** — 의존성 DAG + 위상 정렬 스케줄링.
- **3단계** — 이중 경로 라우터: **고속 경로** 대 **고부하 경로** 지속적 워커
  풀 · **충돌 인식 격리** · **워커 보고서 계약** · **수정
  메모리**.
- **3b단계** — 지속적 수집: 실행 내부 폴러 + 유휴 워처(언제든 새 작업을 확인).
- **3c단계** — 속도 모델: 파이프라인(배리어 아님), 공유 컴파일 캐시,
  병합 시점 1회 검증, **공유 컨텍스트 다이제스트**.
- **3d단계** — 모델 라우팅 L0→L4(결정론적 → 로컬 → 중간 → 추론 → 유료).
- **4단계** — 품질 루프 · **AC 게이트(진짜 DoD)** · **실행 검증** ·
  **적대적 다중 투표 검증** · **정적 분석 게이트**.
- **5단계** — 안전 게이트: 시크릿 스캔, 되돌릴 수 없는 작업의 사람 게이트, **4상태
  실행 전 판정**, **세그먼트별 복합 증명**, **로드 전 신뢰
  설정**, **공급망 무결성 게이트**, **transform_guard**.
- **6단계** — 전달 + 종료 + 자가 감사 · **증거 패키지** · **현실 검증
  (자기 보고를 절대 믿지 않음)** · **병합이 main을 깨뜨리면 롤백 가드**.
- **6b단계** — 피드백 루프 닫기: CI → 수정, 리뷰 댓글 → 해결,
  브랜치 뒤처짐 → 조정, 병합 준비가 될 때까지 전체 **PR 생애주기**.
- **7단계** — 24/7 상시 루프(10개 축): 내구성 있는 드라이버, 전체 커버리지 매트릭스,
  내구성 있는 상태, **비용 거버넌스 + 강력한 킬 스위치**, 무인 안전,
  자가 치유 + **실패 분류별 지능형 재시도**, 우선순위/WIP,
  관측 가능성 + **주기적 절감 감사** + **스냅샷 측정**,
  자가 개선, 조정 & 깔끔한 정지.

### 토큰 경제(rtk + caveman에서 녹여 넣음)
- 터미널 우선 실행 — 명령을 절대 시뮬레이션하지 않음.
- **크로스 플랫폼** 치환 테이블(Windows / macOS / Linux): 터미널이 LLM보다
  저렴하게 답하는 30가지 이상의 사실.
- 데이터로서의 **출력 축소 카탈로그**: 명령별 레시피, 예상 절감 %,
  `skip-if-structured` 가드.
- **신호 등급별 상한**: `CAP_ERRORS / CAP_WARNINGS / CAP_LIST / CAP_INVENTORY`.
- **성공 접기** + **개수와 함께 중복 제거**(`unless errors` 가드 포함).
- **복합 명령 클램핑** — 세그먼트별, 파이프/리다이렉트 안전, fail-open.
- **소비자별 밀도 등급**(머신 대 사람); 이미 밀도가 높은 내용은 건너뜀.
- **워커 보고서 계약** — 하위 에이전트용 상태 토큰 우선의 간결한 스키마.
- **정직한 절감 기준선** = 현실적인 대조군, **통과하는 품질 게이트에
  종속**(게이트를 통과하지 못한 압축은 크레딧을 0으로 받음).

### 품질 & 전달
- 수용 기준 DoD 체크리스트 · 실행 검증 · 적대적 검증 ·
  정적 분석 게이트 · 전달 인증서 · 현실 재검증 ·
  자동 롤백.

### 안전성
- 시크릿 스캔 · 되돌릴 수 없는 작업의 사람 게이트 · 4상태 판정(권한을 절대
  상승시키지 않음) · 복합 명령 증명 · 로드 전 신뢰 · 공급망
  무결성 · 프롬프트 인젝션 강화 · 무인 실행을 위한 강력한 $ 킬 스위치.

### 24/7 자율성
- 내구성 있는 스케줄러 · 실시간 큐 + 유휴 워처 · 내구성 있는 저널/상태 ·
  서킷 브레이커 · 데드 레터 격리 · 자가 개선 & 메타 리뷰 ·
  다중 인스턴스 원자적 점유 · 깔끔한 STOP 신호.

---

## 🚀 설치 & 사용

simplicio-tasks는 **스킬**입니다 — 스킬을 로드하는 어떤 런타임에든 넣을 수 있는 단일
폴더죠. 의존성도, 바이너리도 필요 없습니다.

```bash
# Claude Code (project or user skills dir)
git clone https://github.com/wesleysimplicio/simplicio-tasks
cp -r simplicio-tasks/.claude/skills/simplicio-tasks  <your-repo>/.claude/skills/

# then, in your agent:
/simplicio-tasks finish all the open issues
```

다른 런타임(Codex, Gemini, Copilot, 로컬 에이전트)은 동일한 `SKILL.md`를 로드합니다 —
런타임별 진입점은 [`AGENTS.md`](../AGENTS.md), [`CLAUDE.md`](../CLAUDE.md),
[`GEMINI.md`](../GEMINI.md)를 참고하세요. 호스트 런타임이 네이티브 명령을 노출하면
이를 확장 지점에 자동으로 바인딩하고, 그렇지 않으면 LLM 폴백이 작업의 **100%**를
커버합니다.

**무인 24/7 실행 전에:** 비용 상한을 설정하고(`.orchestrator/loop-budget.json`,
`daily_usd_ceiling > 0`), 소스 인증이 지속되는지 확인하며, 되돌릴 수 없는 작업의 사람
게이트 + 시크릿 스캔을 켜 두세요. `ceiling = 0`이면 워처는 무인 실행을 거부합니다(페일
세이프).

---

## 📊 토큰 경제

모든 메시지는 정직한 절감 라인으로 끝납니다:

```
simplicio-tasks: ~<spent> tokens · baseline ~<control-arm> · saved ~<saved> (<pct>%)
```

기준선은 동일한 결과에 이르는 **가장 저렴하고 합리적인 비오케스트레이션 경로**이며 —
장황한 허수아비가 아닙니다 — 절감은 **항목의 실행 검증과 수용 기준 게이트를 통과할
때만** 인정됩니다. 단순 압축만으로는 결코 성공으로 집계되지 않습니다.

---

## 📄 라이선스

MIT — [LICENSE](../LICENSE) 참고. [Simplicio](https://github.com/wesleysimplicio)
생태계의 일부입니다.
