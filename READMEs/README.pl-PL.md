# 🔁 simplicio-tasks — Uniwersalny zapętlony orkiestrator AI

<p align="center">
  <img src="../assets/simplicio-tasks-logo.svg" alt="simplicio-tasks" width="920" />
</p>

<p align="center">
  <a href="https://github.com/wesleysimplicio/simplicio-tasks/stargazers"><img src="https://img.shields.io/github/stars/wesleysimplicio/simplicio-tasks?style=social" alt="Stars"></a>
  <a href="https://github.com/wesleysimplicio/simplicio-tasks"><img src="https://img.shields.io/badge/skill-runtime--agnostic-39FF14" alt="Runtime-agnostic"></a>
  <a href="#-43-punkty-rozszerzeń"><img src="https://img.shields.io/badge/extension%20points-43-00E08A" alt="43 extension points"></a>
  <a href="#-ekonomia-tokenów"><img src="https://img.shields.io/badge/tokens-up%20to%2096%25%20fewer-green" alt="Up to 96% fewer tokens"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License"></a>
</p>

<p align="center">
  <a href="#-tldr">TL;DR</a> ·
  <a href="#-vs-caveman--rtk">vs caveman i rtk</a> ·
  <a href="#-43-punkty-rozszerzeń">43 punkty</a> ·
  <a href="#-wszystko-w-środku">Wszystko w środku</a> ·
  <a href="#-instalacja--użycie">Instalacja</a>
</p>

<p align="center">
  <strong>🌍 Języki:</strong><br>
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
  <strong>🇵🇱 Polski</strong> |
  <a href="README.tr-TR.md">🇹🇷 Türkçe</a> |
  <a href="README.nl-NL.md">🇳🇱 Nederlands</a> |
  <a href="README.hi-IN.md">🇮🇳 हिन्दी</a> |
  <a href="README.ar-SA.md">🇸🇦 العربية</a>
</p>

---

## ⚡ TL;DR

**simplicio-tasks** to pojedynczy, niezależny od środowiska uruchomieniowego **skill**,
który zamienia dowolny mocny LLM (Claude, Codex, Copilot, Gemini, Grok, modele lokalne)
w **autonomiczny zapętlony orkiestrator**. Wskazujesz mu pewien zakres pracy — *„dokończ
wszystkie otwarte zgłoszenia"*, *„opróżnij kolejkę CI"*, *„rozładuj tablicę Jira"* — a on
samodzielnie przeprowadza cały cykl życia:

> **odkryj → zrozum → zdecyduj → działaj → zweryfikuj → popraw → zapisz → powtórz**

Odkrywa pracę z dowolnego źródła, usuwa duplikaty, automatycznie skaluje flotę agentów do
możliwości Twojej maszyny, realizuje każdy element w pętli jakościowej, która **uruchamia
kod (a nie tylko go kompiluje)**, otwiera PR-y, rozwiązuje uwagi z CI/przeglądu, scala
zmiany i nieprzerwanie obserwuje **24/7** w poszukiwaniu nowej pracy — wszystko za bramkami
bezpieczeństwa i twardym wyłącznikiem awaryjnym kosztów.

Niesie ze sobą **43 nazwane punkty rozszerzeń**. Każdy ma awaryjną ścieżkę LLM, która zawsze
działa, a każdy *wiąże się z natywnym poleceniem środowiska hostującego*, gdy takie jest
dostępne — czyniąc dany krok deterministycznym i niemal zerotokenowym. **Skill nie wskazuje
żadnego środowiska uruchomieniowego; to środowisko wykrywa skill.** Ta inwersja jest całą
sztuczką: jeden uniwersalny protokół z opcjonalną natywną szybkością wstrzykniętą pod spód.

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

## 🆚 vs caveman i rtk

simplicio-tasks powstał **po dogłębnym przestudiowaniu** dwóch najlepszych narzędzi do
oszczędzania tokenów na GitHubie — [**caveman**](https://github.com/JuliusBrussee/caveman)
(74k★, *kompresja rozmowy*) i [**rtk**](https://github.com/rtk-ai/rtk) (63k★, *kompresja
poleceń*). Łączy to, co najlepsze z **obu**, w pełnoprawnego orkiestratora. Tamte redukują
tokeny; simplicio-tasks **wykonuje pracę** i przy tym redukuje tokeny.

| | 🪨 **caveman** | ⚙️ **rtk** | 🔁 **simplicio-tasks** |
|---|---|---|---|
| **Czym jest** | Skill dla Claude Code | Proxy CLI w Rust | Skill niezależny od środowiska |
| **Główna idea** | Mów zwięźlej (odrzuć wypełniacze) | Redukuj wyjście poleceń deweloperskich | **Orkiestruj całą pracę** |
| **Zakres** | Prozaiczne wyjście LLM | Wyjście poleceń powłoki | Pełny cykl życia pracy, od początku do końca |
| **Oszczędność tokenów** | ~65% na odpowiedziach | 60–90% na poleceniach | Oba — katalog + limity + przycinanie |
| **Wykonuje pracę?** | ❌ tylko formatowanie | ❌ tylko proxy | ✅ odkryj→zrealizuj→scal→zamknij |
| **Wielokrokowa autonomia** | ❌ | ❌ | ✅ ciągła pula pracowników |
| **Bramki jakości** | — | — | ✅ bramka AC · weryfikacja przez uruchomienie · weryfikacja adwersarialna · bramka dostarczenia |
| **Bezpieczeństwo** | — | semgrep, zastrzeżenia | ✅ werdykt 4-stanowy · atestacja · skan sekretów · bramka ludzka · wyłącznik awaryjny |
| **Pętla 24/7** | ❌ | ❌ | ✅ trwały obserwator, samonaprawiający się |
| **Wiązanie ze środowiskiem** | Claude/Codex/Gemini | dowolne (proxy PATH) | **dowolne** (43 punkty rozszerzeń) |
| **Co zaczerpnęliśmy** | zwięzłe raporty pracowników, poziomy gęstości, ochrona przed parafrazowaniem, uczciwa linia bazowa | katalog redukcji per polecenie, limity warstwowane sygnałem, przycinanie złożone, fail-open, werdykt 4-stanowy | — |
| **Co pominęliśmy** | upuszczanie słów na poziomie gramatyki (pogarsza jakość kodu) | rejestry per język (specyficzne dla środowiska) | — |

> **Świadomie odrzuciliśmy** caveman-owe „mów-jak-jaskiniowiec" upuszczanie słów — zwięzła
> *proza* jest w porządku, ale kaleczenie gramatyki pogarsza kod i potwierdzenia. Zachowaliśmy
> *dyscyplinę* (nigdy nie parafrazuj kodu/URL-i/ścieżek), a nie sztuczkę.

<p align="center">
  <img src="../assets/architecture.svg" alt="architecture" width="900" />
</p>

---

## 🧩 43 punkty rozszerzeń

Każdy krok pracy odbywa się w **nazwanym punkcie rozszerzenia**. Jeśli środowisko hostujące
udostępnia natywną zdolność, następuje **wiązanie** (deterministyczne, niemal zerotokenowe).
W przeciwnym razie LLM realizuje **ścieżkę awaryjną** standardowymi narzędziami (powłoka, git,
gh, edycja plików, sieć). Skill zależy od abstrakcji, nigdy od konkretnego środowiska.

### Orkiestracja i skala
| Punkt | Co robi |
|---|---|
| `orient` | Skompresowana mapa repozytorium/pracy |
| `normalize` | Element pracy → schemat kanoniczny |
| `intake` | Pobranie pracy z linku do sprintu/tablicy |
| `source_adapter` | Jednolity łącznik źródła (list/get/claim/update/attach/close) |
| `autoscale` | Bezpieczny rozmiar floty na podstawie profilu maszyny |
| `plan` / `decide` | Wsparcie planowania i decyzji |
| `execute` | Lokalne rozproszenie agentów dla pracy masowej/mechanicznej |
| `issue_factory` | Pełna pętla: discover→claim→implement→PR |
| `claim` | Atomowe, bezpieczne między sesjami przejęcie elementu pracy |
| `worktree` | Izolowany checkout dla każdego elementu |
| `dependency_graph` | Wznawialne uporządkowanie DAG między elementami |
| `durable_workflow` | Potok per element jako wznawialna maszyna stanów faz |
| `work_queue` | Trwała kolejka priorytetowa z automatycznym ponawianiem + blokadą zapisu |
| `resource_governor` | Dynamiczne dławienie w trakcie pętli + pułapy warstwy maszyny |
| `model_route` | Najtańszy realny substrat na podzadanie (L0→zdalny) |
| `model_preflight` | Sondowanie używalnego modelu przed routingiem generacji |

### Edycja, jakość i dowody
| Punkt | Co robi |
|---|---|
| `deterministic_edit` | Mechaniczne, zerotokenowe zastosowanie podjętej zmiany |
| `diagnostics` | Parsowanie wyjścia budowania/testów → ustrukturyzowane błędy → iteracja |
| `toolchain_detect` | Wykrycie rzeczywistego stosu build/lint/typecheck/test repozytorium |
| `validate` / `smoke` | Weryfikacja przez uruchomienie: „działa, a nie tylko kompiluje się" |
| `delivery_gate` | DoD: sprawdzenie AC + regresja + przegląd diffu + certyfikat |
| `endpoint_compare` | Rozjazd Web↔API↔agent → elementy do uzupełnienia |
| `web_verify` | Sterowanie prawdziwą przeglądarką, by udowodnić, że zmiana UI działa |
| `pr` / `evidence` | Otwarcie/aktualizacja PR + weryfikowalny rejestr dowodów |
| `retry` | Sklasyfikowane ponawianie + odczekanie wg klasy awarii |
| `reuse_precedent` | Dopasowanie wcześniej rozwiązanego przebiegu → ponowne użycie, nie regeneracja |
| `trajectory` | Rejestracja wyniku przebiegu na potrzeby samodoskonalenia |
| `learn` | Uczenie się z przebiegu — aktualizacja precedensów/pamięci |
| `status` | Dashboard obserwowalności na żywo |
| `capability_rank` | Ranking, który skill/narzędzie pasuje do podzadania |

### Tokeny, kontekst i bezpieczeństwo
| Punkt | Co robi |
|---|---|
| `recall` | Wcześniejsze decyzje / precedensy |
| `compress` | Kompresja kontekstu / przycinanie wyjścia |
| `prompt_budget` | Koperta promptu z budżetem tokenów + cache fragmentów |
| `shell_exec` | Przycięte wykonanie powłoki (ustrukturyzowane, ograniczone) |
| `transform_guard` | Sprawdzenie, czy kompakcja zachowała każdy token kodu/URL/ścieżki/wersji |
| `action_gate` | Klasyfikacja ryzyka każdej mutacji (safe/auto/ask) przed jej wykonaniem |
| `security` | Skan łańcucha dostaw / sekretów |
| `human_gate` | Asynchroniczny kanał zatwierdzeń przez człowieka |
| `notify` | Wypchnięcie postępu/blokera/podsumowania + odbiór zatwierdzeń |
| `checkpoint_restore` | Zrzut stanu przed ryzykowną partią; przywrócenie przy awarii |
| `watcher` | Trwały harmonogram / poller (przetrwa restart) |
| `savings_ledger` | Śledzenie rzeczywistego zużycia tokenów na sesję |
| `web_research` | Pobranie aktualnej wiedzy zewnętrznej, bramkowane, z proweniencją |

---

## 📦 Wszystko w środku

Pełen inwentarz tego, co niesie skill — każdy mechanizm, z odniesieniem.

### Pętla (7 kroków + podkroki)
- **Krok 0** — Załaduj kontrakt (kanoniczny protokół).
- **Krok 1** — Tożsamość + tania detekcja środowiska.
- **Krok 1b** — 43 punkty rozszerzeń (wiązanie natywne lub awaryjna ścieżka LLM).
- **Krok 1c** — Bramka ekonomii tokenów: `THINK / NO-THINK`, `INTERNET off by default`,
  `terminal-first execution`, **katalog redukcji wyjścia**, **limity warstwowane sygnałem**,
  **zwinięcie sukcesu + deduplikacja**, **przycinanie poleceń złożonych**, **poziomy gęstości
  routowane wg odbiorcy**, **fail-open**, **auto-klarowność (bezpieczeństwo ważniejsze niż
  zwięzłość)**.
- **Krok 1d** — Pre-flight: budżet wyłącznika awaryjnego, uwierzytelnienie źródła, uzbrojenie
  obserwatora.
- **Krok 2** — Odkrycie + normalizacja elementów pracy (dowolny adapter źródła).
- **Krok 2b** — Głęboki intake: odczyt pełnej treści + komentarzy, wyodrębnienie **kryteriów
  akceptacji**, **orientacja w bazie kodu**, **tryb odczytu tylko sygnatur**, zbudowanie planu.
- **Krok 2c** — DAG zależności + harmonogramowanie topologiczne.
- **Krok 3** — Router dwuścieżkowy: ciągła pula pracowników **fast-path** vs **heavy-path** ·
  **izolacja świadoma konfliktów** · **kontrakt raportu pracownika** · **pamięć poprawek**.
- **Krok 3b** — Ciągły intake: poller wewnątrz przebiegu + obserwator bezczynności (zobacz nową
  pracę w każdej minucie).
- **Krok 3c** — Model szybkości: potok (nie bariera), współdzielony cache kompilacji,
  weryfikacja-raz-przy-scaleniu, **współdzielony skrót kontekstu**.
- **Krok 3d** — Routing modeli L0→L4 (deterministyczny → lokalny → średni → rozumujący → płatny).
- **Krok 4** — Pętla jakości · **bramka AC (prawdziwe DoD)** · **weryfikacja przez uruchomienie** ·
  **adwersarialna weryfikacja wielogłosowa** · **bramka analizy statycznej**.
- **Krok 5** — Bramki bezpieczeństwa: skan sekretów, bramka ludzka dla operacji nieodwracalnych,
  **werdykt 4-stanowy przed wykonaniem**, **atestacja złożona per segment**, **konfiguracja
  zaufaj-przed-załadowaniem**, **bramka integralności łańcucha dostaw**, **transform_guard**.
- **Krok 6** — Dostarczenie + zamknięcie + autoaudyt · **pakiet dowodów** · **weryfikacja
  rzeczywistości (nigdy nie ufaj autoraportowi)** · **strażnik wycofania, jeśli scalenie psuje
  main**.
- **Krok 6b** — Zamknięcie pętli sprzężenia zwrotnego: CI → naprawa, komentarze przeglądu →
  rozwiązanie, gałąź-w-tyle → uzgodnienie, pełny **cykl życia PR** aż do gotowości do scalenia.
- **Krok 7** — Stała pętla 24/7 (10 osi): trwały sterownik, macierz pełnego pokrycia, trwały stan,
  **zarządzanie kosztami + twardy wyłącznik awaryjny**, bezpieczeństwo bez nadzoru, samonaprawa +
  **inteligentne ponawianie wg klasy awarii**, priorytetyzacja/WIP, obserwowalność + **okresowy
  audyt oszczędności** + **pomiar zrzutu**, samodoskonalenie, koordynacja i czyste zatrzymanie.

### Ekonomia tokenów (złożona z rtk + caveman)
- Wykonanie terminal-first — nigdy nie symuluj polecenia.
- **Wieloplatformowa** tablica podstawień (Windows / macOS / Linux): 30+ faktów, na które
  terminal odpowiada taniej niż LLM.
- **Katalog redukcji wyjścia** jako dane: przepis per polecenie, oczekiwane oszczędności %,
  ochrona `skip-if-structured`.
- **Limity warstwowane sygnałem**: `CAP_ERRORS / CAP_WARNINGS / CAP_LIST / CAP_INVENTORY`.
- **Zwinięcie sukcesu** + **deduplikacja-z-liczbami** (z ochroną `unless errors`).
- **Przycinanie poleceń złożonych** — per segment, bezpieczne dla potoków/przekierowań, fail-open.
- **Poziomy gęstości wg odbiorcy** (maszyna vs człowiek); pomijanie już gęstej treści.
- **Kontrakt raportu pracownika** — zwięzły schemat status-token-first dla podagentów.
- **Uczciwa linia bazowa oszczędności** = realistyczne ramię kontrolne, **powiązane z przejściem
  bramki jakości** (kompresja, która nie przejdzie swojej bramki, zdobywa zero punktów).

### Jakość i dostarczenie
- Lista kontrolna DoD kryteriów akceptacji · weryfikacja przez uruchomienie · weryfikacja
  adwersarialna · bramka analizy statycznej · certyfikat dostarczenia · ponowna weryfikacja
  rzeczywistości · automatyczne wycofanie.

### Bezpieczeństwo
- Skan sekretów · bramka ludzka dla operacji nieodwracalnych · werdykt 4-stanowy (nigdy nie
  eskaluj uprawnień) · atestacja poleceń złożonych · zaufaj-przed-załadowaniem · integralność
  łańcucha dostaw · utwardzenie przeciw wstrzykiwaniu promptów · twardy wyłącznik awaryjny $ dla
  przebiegów bez nadzoru.

### Autonomia 24/7
- Trwały harmonogram · kolejka na żywo + obserwator bezczynności · trwały dziennik/stan ·
  bezpieczniki obwodowe · kwarantanna dead-letter · samodoskonalenie i metaprzegląd ·
  atomowe przejęcia wielu instancji · czysty sygnał STOP.

---

## 🚀 Instalacja i użycie

simplicio-tasks to **skill** — pojedynczy folder, który wrzucasz do dowolnego środowiska
uruchomieniowego ładującego skille. Bez zależności, bez wymaganego binarki.

```bash
# Claude Code (project or user skills dir)
git clone https://github.com/wesleysimplicio/simplicio-tasks
cp -r simplicio-tasks/.claude/skills/simplicio-tasks  <your-repo>/.claude/skills/

# then, in your agent:
/simplicio-tasks finish all the open issues
```

Inne środowiska (Codex, Gemini, Copilot, agenci lokalni) ładują ten sam `SKILL.md` — zobacz
[`AGENTS.md`](../AGENTS.md), [`CLAUDE.md`](../CLAUDE.md) i [`GEMINI.md`](../GEMINI.md), by poznać
punkty wejścia dla poszczególnych środowisk. Tam, gdzie środowisko hostujące udostępnia natywne
polecenia, automatycznie wiąże je z punktami rozszerzeń; w przeciwnym razie ścieżki awaryjne LLM
pokrywają **100%** pracy.

**Przed przebiegiem 24/7 bez nadzoru:** ustaw pułap kosztów (`.orchestrator/loop-budget.json`,
`daily_usd_ceiling > 0`), potwierdź, że uwierzytelnienie źródła jest trwałe, i pozostaw włączone
bramkę ludzką dla operacji nieodwracalnych + skan sekretów. Przy `ceiling = 0` obserwator
odmawia działania bez nadzoru (fail-safe).

---

## 📊 Ekonomia tokenów

Każda wiadomość kończy się uczciwą linią oszczędności:

```
simplicio-tasks: ~<spent> tokens · baseline ~<control-arm> · saved ~<saved> (<pct>%)
```

Linia bazowa to **najtańsza rozsądna ścieżka bez orkiestracji** do tego samego rezultatu — a nie
rozwlekły chochoł — a oszczędności są **zaliczane tylko wtedy, gdy weryfikacja przez uruchomienie
i bramka kryteriów akceptacji danego elementu przejdą**. Sama surowa kompresja nigdy nie jest
liczona jako sukces.

---

## 📄 Licencja

MIT — zobacz [LICENSE](../LICENSE). Część ekosystemu [Simplicio](https://github.com/wesleysimplicio).
