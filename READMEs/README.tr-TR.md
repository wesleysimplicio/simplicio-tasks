# 🔁 simplicio-tasks — Evrensel Döngülü Yapay Zeka Orkestratörü

<p align="center">
  <img src="../assets/simplicio-tasks-logo.svg" alt="simplicio-tasks" width="920" />
</p>

<p align="center">
  <a href="https://github.com/wesleysimplicio/simplicio-tasks/stargazers"><img src="https://img.shields.io/github/stars/wesleysimplicio/simplicio-tasks?style=social" alt="Stars"></a>
  <a href="https://github.com/wesleysimplicio/simplicio-tasks"><img src="https://img.shields.io/badge/skill-runtime--agnostic-39FF14" alt="Runtime-agnostic"></a>
  <a href="#-43-genişletme-noktası"><img src="https://img.shields.io/badge/extension%20points-43-00E08A" alt="43 extension points"></a>
  <a href="#-token-ekonomisi"><img src="https://img.shields.io/badge/tokens-up%20to%2096%25%20fewer-green" alt="Up to 96% fewer tokens"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License"></a>
</p>

<p align="center">
  <a href="#-tldr">TL;DR</a> ·
  <a href="#-caveman--rtk-ile-karşılaştırma">caveman & rtk ile karşılaştırma</a> ·
  <a href="#-43-genişletme-noktası">43 Nokta</a> ·
  <a href="#-içindeki-her-şey">İçindeki Her Şey</a> ·
  <a href="#-kurulum--kullanım">Kurulum</a>
</p>

<p align="center">
  <strong>🌍 Diller:</strong><br>
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
  <strong>🇹🇷 Türkçe</strong> |
  <a href="README.nl-NL.md">🇳🇱 Nederlands</a> |
  <a href="README.hi-IN.md">🇮🇳 हिन्दी</a> |
  <a href="README.ar-SA.md">🇸🇦 العربية</a>
</p>

---

## ⚡ TL;DR

**simplicio-tasks**, güçlü herhangi bir LLM'i (Claude, Codex, Copilot, Gemini, Grok,
yerel modeller) **otonom, döngülü bir orkestratöre** dönüştüren, runtime'dan bağımsız,
tek bir **skill**'dir. Onu bir iş yığınına yönlendirirsiniz — *"tüm açık issue'ları
bitir"*, *"CI kuyruğunu boşalt"*, *"Jira board'unu temizle"* — ve tüm yaşam döngüsünü
kendi başına yürütür:

> **keşfet → anla → karar ver → uygula → doğrula → düzelt → kaydet → tekrarla**

İşi herhangi bir kaynaktan keşfeder, yinelenenleri ayıklar, makinenize göre bir ajan
filosunu otomatik ölçeklendirir, her bir öğeyi **kodu (sadece derlemekle kalmayıp)
çalıştıran** bir kalite döngüsüyle uygular, PR'lar açar, CI/inceleme geri bildirimlerini
çözer, birleştirir ve yeni iş için **7/24** izlemeyi sürdürür — hepsi güvenlik kapılarının
ve sıkı bir maliyet acil durdurma anahtarının arkasında.

Üzerinde **43 adlandırılmış genişletme noktası** taşır. Her birinin daima çalışan bir
LLM yedeği vardır ve her biri, mevcut olduğunda *bir host runtime'ın yerel komutuna
bağlanır* — bu da adımı deterministik ve token'a neredeyse sıfır maliyetli hale getirir.
**Skill hiçbir runtime'ı adlandırmaz; runtime skill'i algılar.** İşin tüm püf noktası bu
tersine çevirmedir: tek bir evrensel protokol, altına enjekte edilen isteğe bağlı yerel
hızla birlikte.

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

## 🆚 caveman & rtk ile karşılaştırma

simplicio-tasks, GitHub'daki en iyi iki token-tasarrufçusunu **derinlemesine
inceledikten sonra** geliştirildi — [**caveman**](https://github.com/JuliusBrussee/caveman)
(74k★, *konuşmayı sıkıştır*) ve [**rtk**](https://github.com/rtk-ai/rtk) (63k★,
*komutları sıkıştır*). **İkisinin de** en iyilerini eksiksiz bir orkestratörde birleştirir.
Onlar token azaltır; simplicio-tasks **işi yapar** ve bunu yaparken token'ı azaltır.

| | 🪨 **caveman** | ⚙️ **rtk** | 🔁 **simplicio-tasks** |
|---|---|---|---|
| **Nedir** | Claude Code skill'i | Rust CLI proxy | Runtime'dan bağımsız skill |
| **Temel fikir** | Daha öz konuş (gereksizleri at) | Geliştirme komutu çıktısını azalt | **Tüm işi orkestre et** |
| **Kapsam** | LLM düzyazı çıktısı | Shell komutu çıktısı | Tam iş yaşam döngüsü, baştan sona |
| **Token tasarrufu** | Yanıtlarda ~%65 | Komutlarda %60–90 | Her ikisi de — katalog + tavanlar + kırpma |
| **İşi yapar mı?** | ❌ yalnızca biçimlendirme | ❌ yalnızca proxy | ✅ keşfet→uygula→birleştir→kapat |
| **Çok adımlı otonomi** | ❌ | ❌ | ✅ sürekli işçi havuzu |
| **Kalite kapıları** | — | — | ✅ AC kapısı · çalıştırma-doğrulaması · çekişmeli doğrulama · teslimat kapısı |
| **Güvenlik** | — | semgrep, sorumluluk reddi | ✅ 4 durumlu karar · tasdik · gizli-tarama · insan kapısı · acil durdurma |
| **7/24 döngü** | ❌ | ❌ | ✅ dayanıklı watcher, kendini onaran |
| **Runtime bağlama** | Claude/Codex/Gemini | herhangi biri (PATH proxy) | **herhangi biri** (43 genişletme noktası) |
| **Aldıklarımız** | öz işçi raporları, yoğunluk kademeleri, asla-yeniden-ifade-etme koruması, dürüst baz çizgi | komut başına azaltma kataloğu, sinyal-kademeli tavanlar, bileşik-kırpma, fail-open, 4 durumlu karar | — |
| **Bıraktıklarımız** | dilbilgisi kelime-atma (kod kalitesini düşürür) | dil başına kayıtlar (runtime'a özgü) | — |

> caveman'in "mağara adamı gibi konuş" kelime-atma yaklaşımını bilinçli olarak
> **reddettik** — öz *düzyazı* sorun değil, ancak dilbilgisini bozmak kodu ve
> onayları kötüleştirir. *Disiplini* koruduk (kodu/URL'leri/yolları asla yeniden
> ifade etme), numarayı değil.

<p align="center">
  <img src="../assets/architecture.svg" alt="architecture" width="900" />
</p>

---

## 🧩 43 genişletme noktası

İşin her adımı **adlandırılmış bir genişletme noktasında** gerçekleşir. Bir host
runtime yerel bir yetenek sunarsa ona **bağlanır** (deterministik, token'a neredeyse
sıfır maliyet). Aksi halde LLM, standart araçlarla (shell, git, gh, dosya düzenleme,
web) **yedeği** yürütür. Skill, soyutlamaya bağımlıdır, asla belirli bir runtime'a değil.

### Orkestrasyon & ölçek
| Nokta | Ne yapar |
|---|---|
| `orient` | Sıkıştırılmış repo/iş haritası |
| `normalize` | İş-öğesi → kanonik şema |
| `intake` | Bir sprint/board bağlantısından iş alımı |
| `source_adapter` | Tek tip kaynak bağlayıcısı (list/get/claim/update/attach/close) |
| `autoscale` | Makine profilinden güvenli filo boyutu |
| `plan` / `decide` | Plan & karar desteği |
| `execute` | Toplu/mekanik iş için yerel ajan dağıtımı |
| `issue_factory` | Tam döngü: discover→claim→implement→PR |
| `claim` | Atomik, oturumlar arası güvenli iş-öğesi sahiplenme |
| `worktree` | Öğe başına izole checkout |
| `dependency_graph` | Öğeler arası devam ettirilebilir DAG sıralaması |
| `durable_workflow` | Öğe başına pipeline, devam ettirilebilir faz durum makinesi olarak |
| `work_queue` | Otomatik-yeniden-deneme + yazma-kilidi ile dayanıklı öncelik kuyruğu |
| `resource_governor` | Döngü-ortası dinamik kısıtlama + makine-kademe tavanları |
| `model_route` | Alt-görev başına en ucuz uygulanabilir altyapı (L0→remote) |
| `model_preflight` | Üretimi yönlendirmeden önce kullanılabilir bir modeli yokla |

### Düzenleme, kalite & kanıt
| Nokta | Ne yapar |
|---|---|
| `deterministic_edit` | Kararlaştırılmış bir değişikliğin mekanik, sıfır-token uygulanması |
| `diagnostics` | Build/test çıktısını ayrıştır → yapılandırılmış hatalar → yinele |
| `toolchain_detect` | Repo'nun gerçek build/lint/typecheck/test yığınını algıla |
| `validate` / `smoke` | Çalıştırma-doğrulaması: "sadece derlenmez, çalışır" |
| `delivery_gate` | DoD: AC kontrolü + gerileme + diff incelemesi + sertifika |
| `endpoint_compare` | Web↔API↔ajan sapması → takip öğeleri |
| `web_verify` | Bir UI değişikliğinin çalıştığını kanıtlamak için gerçek bir tarayıcıyı sür |
| `pr` / `evidence` | PR açma/güncelleme + doğrulanabilir kanıt defteri |
| `retry` | Hata sınıfına göre sınıflandırılmış yeniden-deneme+geri-çekilme |
| `reuse_precedent` | Önceden çözülmüş bir koşuyu eşleştir → yeniden üretme, yeniden kullan |
| `trajectory` | Kendini iyileştirme için koşu sonucunu kaydet |
| `learn` | Bir koşudan öğren — emsalleri/belleği güncelle |
| `status` | Canlı gözlemlenebilirlik panosu |
| `capability_rank` | Bir alt-göreve hangi skill/aracın uyduğunu sırala |

### Token'lar, bağlam & güvenlik
| Nokta | Ne yapar |
|---|---|
| `recall` | Önceki kararlar / emsaller |
| `compress` | Bağlam sıkıştırma / çıktı kırpma |
| `prompt_budget` | Token-bütçeli prompt zarfı + fragment önbelleği |
| `shell_exec` | Kırpılmış shell yürütme (yapılandırılmış, sınırlı) |
| `transform_guard` | Bir sıkıştırmanın her kod/URL/yol/sürüm token'ını koruduğunu doğrula |
| `action_gate` | Çalışmadan önce her mutasyonu risk-sınıflandır (safe/auto/ask) |
| `security` | Tedarik zinciri / gizli tarama |
| `human_gate` | Asenkron insan onay kanalı |
| `notify` | İlerleme/engel/özet gönder + onayları al |
| `checkpoint_restore` | Riskli bir partiden önce durumu anlık görüntüle; hatada geri yükle |
| `watcher` | Dayanıklı zamanlayıcı / yoklayıcı (yeniden başlatmaya dayanır) |
| `savings_ledger` | Oturum başına gerçek token-harcaması takibi |
| `web_research` | Güncel dış bilgiyi getir, kapılı, kaynak gösterimi ile |

---

## 📦 İçindeki her şey

Skill'in taşıdığı her şeyin tam bir envanteri — her mekanizma, kaynak gösterilerek.

### Döngü (7 adım + alt-adımlar)
- **Adım 0** — Sözleşmeyi yükle (kanonik protokol).
- **Adım 1** — Kimlik + ucuz ortam algılama.
- **Adım 1b** — 43 genişletme noktası (yerele bağlan veya LLM-yedek).
- **Adım 1c** — Token-ekonomisi kapısı: `THINK / NO-THINK`, `INTERNET off by default`,
  `terminal-first execution`, **çıktı-azaltma kataloğu**, **sinyal-kademeli tavanlar**,
  **başarı-toplama + dedup**, **bileşik-komut kırpma**, **tüketiciye-yönlendirilmiş
  yoğunluk kademeleri**, **fail-open**, **otomatik-netlik (güvenlik özlüğü geçersiz kılar)**.
- **Adım 1d** — Pre-flight: acil durdurma bütçesi, kaynak kimlik doğrulaması, watcher'ı kur.
- **Adım 2** — İş-öğelerini keşfet + normalleştir (herhangi bir kaynak adaptörü).
- **Adım 2b** — Derin alım: tam gövdeyi + yorumları oku, **kabul kriterlerini** çıkar,
  **kod tabanına yönel**, **yalnızca-imza okuma modu**, bir plan oluştur.
- **Adım 2c** — Bağımlılık DAG'ı + topolojik zamanlama.
- **Adım 3** — Çift-yollu yönlendirici: **hızlı-yol** vs **ağır-yol** sürekli işçi
  havuzu · **çakışma-farkında izolasyon** · **işçi rapor sözleşmesi** · **düzeltme
  belleği**.
- **Adım 3b** — Sürekli alım: koşu-içi yoklayıcı + boşta watcher (her an yeni iş gör).
- **Adım 3c** — Hız modeli: pipeline (bariyer değil), paylaşılan derleme önbelleği,
  birleştirmede-bir-kez-doğrula, **paylaşılan bağlam özeti**.
- **Adım 3d** — Model yönlendirme L0→L4 (deterministik → yerel → orta → akıl yürütme → ücretli).
- **Adım 4** — Kalite döngüsü · **AC kapısı (gerçek DoD)** · **çalıştırma-doğrulaması** ·
  **çekişmeli çoklu-oy doğrulama** · **statik-analiz kapısı**.
- **Adım 5** — Güvenlik kapıları: gizli-tarama, geri-alınamaz-işlem insan kapısı, **4 durumlu
  yürütme-öncesi karar**, **segment-başına bileşik tasdik**, **yüklemeden-önce-güven
  yapılandırması**, **tedarik-zinciri bütünlük kapısı**, **transform_guard**.
- **Adım 6** — Teslim et + kapat + öz-denetim · **kanıt paketi** · **gerçekliği doğrula
  (öz-rapora asla güvenme)** · **birleştirme main'i bozarsa geri-alma-koruması**.
- **Adım 6b** — Geri bildirim döngüsünü kapat: CI → düzelt, inceleme yorumları → çöz,
  dal-geride → uzlaştır, birleştirmeye-hazır olana kadar tam **PR yaşam döngüsü**.
- **Adım 7** — 7/24 sürekli döngü (10 eksen): dayanıklı sürücü, tam kapsam matrisi,
  dayanıklı durum, **maliyet yönetişimi + sıkı acil durdurma anahtarı**, gözetimsiz güvenlik,
  kendini-onarma + **hata sınıfına göre akıllı yeniden-deneme**, önceliklendirme/WIP,
  gözlemlenebilirlik + **periyodik tasarruf denetimi** + **anlık görüntü ölçümü**,
  kendini-iyileştirme, koordinasyon & temiz durdurma.

### Token ekonomisi (rtk + caveman'den katlanarak alındı)
- Terminal-öncelikli yürütme — bir komutu asla simüle etme.
- **Platformlar-arası** ikame tablosu (Windows / macOS / Linux): terminalin LLM'den
  daha ucuza yanıtladığı 30+ olgu.
- Veri olarak **çıktı-azaltma kataloğu**: komut başına tarif, beklenen-tasarruf %,
  `skip-if-structured` koruması.
- **Sinyal-kademeli tavanlar**: `CAP_ERRORS / CAP_WARNINGS / CAP_LIST / CAP_INVENTORY`.
- **Başarı-toplama** + **sayılarla-dedup** (bir `unless errors` koruması ile).
- **Bileşik-komut kırpma** — segment-başına, pipe/yönlendirme-güvenli, fail-open.
- **Tüketiciye göre yoğunluk kademeleri** (makine vs insan); zaten-yoğun içeriği atla.
- **İşçi rapor sözleşmesi** — alt-ajanlar için durum-token-önce öz şema.
- **Dürüst tasarruf baz çizgisi** = gerçekçi kontrol kolu, **geçen bir kalite kapısına
  bağlı** (kapısını geçemeyen sıkıştırma sıfır kredi kazanır).

### Kalite & teslimat
- Kabul-kriterleri DoD kontrol listesi · çalıştırma-doğrulaması · çekişmeli doğrulama ·
  statik-analiz kapısı · teslimat sertifikası · gerçeklik yeniden-doğrulaması ·
  otomatik geri-alma.

### Güvenlik
- Gizli-tarama · geri-alınamaz-işlem insan kapısı · 4 durumlu karar (asla ayrıcalık
  yükseltme) · bileşik-komut tasdiği · yüklemeden-önce-güven · tedarik-zinciri
  bütünlüğü · prompt-injection sertleştirme · gözetimsiz koşular için sıkı $ acil durdurma anahtarı.

### 7/24 otonomi
- Dayanıklı zamanlayıcı · canlı kuyruk + boşta watcher · dayanıklı günlük/durum ·
  devre kesiciler · ölü-mektup karantinası · kendini-iyileştirme & meta-inceleme ·
  çoklu-örnek atomik sahiplenmeler · temiz STOP sinyali.

---

## 🚀 Kurulum & kullanım

simplicio-tasks bir **skill**'dir — skill yükleyen herhangi bir runtime'a bıraktığınız
tek bir klasör. Bağımlılık yok, binary gerektirmez.

```bash
# Claude Code (project or user skills dir)
git clone https://github.com/wesleysimplicio/simplicio-tasks
cp -r simplicio-tasks/.claude/skills/simplicio-tasks  <your-repo>/.claude/skills/

# then, in your agent:
/simplicio-tasks finish all the open issues
```

Diğer runtime'lar (Codex, Gemini, Copilot, yerel ajanlar) aynı `SKILL.md`'yi yükler —
runtime başına giriş noktaları için [`AGENTS.md`](../AGENTS.md), [`CLAUDE.md`](../CLAUDE.md)
ve [`GEMINI.md`](../GEMINI.md)'ye bakın. Bir host runtime yerel komutlar sunduğunda,
bunları otomatik olarak genişletme noktalarına bağlar; aksi halde LLM yedekleri işin
**%100**'ünü kapsar.

**Gözetimsiz bir 7/24 koşusundan önce:** bir maliyet tavanı belirleyin
(`.orchestrator/loop-budget.json`, `daily_usd_ceiling > 0`), kaynak kimlik doğrulamasının
kalıcı olduğunu onaylayın ve geri-alınamaz-işlem insan kapısını + gizli-taramayı açık
tutun. `ceiling = 0` ile watcher gözetimsiz çalışmayı reddeder (fail-safe).

---

## 📊 Token ekonomisi

Her mesaj dürüst bir tasarruf satırıyla biter:

```
simplicio-tasks: ~<spent> tokens · baseline ~<control-arm> · saved ~<saved> (<pct>%)
```

Baz çizgi, aynı sonuca giden **en ucuz makul orkestrasyonsuz yoldur** — abartılı bir
korkuluk değil — ve tasarruflar **yalnızca öğenin çalıştırma-doğrulaması ve kabul-kriterleri
kapısı geçtiğinde kredilendirilir**. Ham sıkıştırma tek başına asla başarı olarak sayılmaz.

---

## 📄 Lisans

MIT — bkz. [LICENSE](../LICENSE). [Simplicio](https://github.com/wesleysimplicio)
ekosisteminin bir parçasıdır.
