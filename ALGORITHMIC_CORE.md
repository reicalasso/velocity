# VELOCITY — ALGORİTMİK ÇEKİRDEK

> ⚠️ Bu "yüksek seviye laf" değil; gerçekten kodlanabilir, modüler ve ölçeklenebilir bir algoritmik iskelet.

## Temel Prensip

Bu tek bir algoritma değil, bir **yürütme döngüsü (cognitive loop)**.

## 0️⃣ Girdi Varsayımı

**Velocity şunu alır:**
- Kullanıcı girdisi (doğal dil / API / görev tanımı)
- Sistem hedefi (cevapla, karar ver, öner, üret, planla)

**Çıktı:**
- Cevap + güven aralığı
- veya karar grafı
- veya "karar verilemez" durumu

---

## 1️⃣ INTENT PARSING (Amaç Çıkarımı)

**LLM'ler burada hemen cevap üretir**
**Velocity önce problemi tanımlar**

### Algoritmik Adım

```python
Input → Intent Graph
```

### Çıkarılanlar

- Ana hedef
- Alt hedefler
- Belirsizlik düzeyi
- Bilgi ihtiyacı türü:
  - factual?
  - comparative?
  - predictive?
  - strategic?

### Çıktı

```python
{
  "goal": "...",
  "subgoals": [...],
  "uncertainty": 0.72,
  "decision_type": "comparative"
}
```

### Implementation

`velocity/core/intent_parser.py`

```python
from velocity import IntentParser

parser = IntentParser()
intent = parser.parse("What is quantum computing?")

print(intent.goal)              # Ana hedef
print(intent.decision_type)     # DecisionType.FACTUAL
print(intent.uncertainty)       # 0.35
print(intent.subgoals)          # []
```

---

## 2️⃣ EPISTEMIC ROUTING (Nereye Bakmalıyım?)

**Burada retrieval yok, KARAR var.**

Velocity şu soruyu sorar:
> "Bu problemi çözmek için hangi epistemik alanlara bakmalıyım?"

### Kaynak Tipleri

- Resmi dokümantasyon
- Akademik yayın
- Forumlar
- Canlı sistem verileri
- Sosyal sinyaller
- Kod repoları

### Algoritma

Her kaynak için skor hesaplanır:

```python
EpistemicScore = f(
  trust,
  freshness,
  relevance,
  diversity,
  cost
)
```

**En yüksek skorlu kaynak stratejileri seçilir**

⚠️ Önemli: Tek tek site değil, **strateji** seçilir.

### Implementation

`velocity/core/epistemic_router.py`

```python
from velocity import EpistemicRouter

router = EpistemicRouter()
strategies = router.route(intent, max_strategies=5, budget=10.0)

for strategy in strategies:
    print(f"{strategy.source_type.value}: score={strategy.compute_score():.2f}")
```

---

## 3️⃣ PARALLEL HYPOTHESIS GENERATION (GPU alanı)

**Şimdi iş ciddileşiyor.**

Velocity tek cevap aramaz.
**Hipotez uzayı üretir.**

### Algoritmik Olarak

```python
H = {h1, h2, h3, ..., hn}
```

### Her Hipotez

- Farklı varsayıma dayanır
- Farklı kaynak stratejisi kullanır
- Farklı çözüm yolu dener

### GPU'lar Burada

- Aynı anda n hipotezi yürütür
- Her biri kendi küçük "dünya modeli"ne sahiptir
- **Bu training değil, paralel evaluation**

### Implementation

`velocity/core/hypothesis_generator.py`

```python
from velocity import HypothesisGenerator

generator = HypothesisGenerator(max_hypotheses=5)
hypotheses = generator.generate(intent, strategies)

for h in hypotheses:
    print(f"H{i}: {h.description}")
    print(f"    Assumptions: {h.assumptions}")
    print(f"    Strategy: {h.source_strategy.source_type.value}")
```

---

## 4️⃣ NETWORK INTERROGATION LOOP (Asıl zeka burada)

### Her Hipotez İçin

```python
while confidence < threshold AND budget_not_exceeded:
    source = select_next_source(state)
    evidence = query(source)
    state = update(state, evidence)
    confidence = recompute_confidence(state)
```

### Kritik Noktalar

- `confidence` dinamik
- `budget` (zaman / istek / para) sınırlı
- Sonsuz tarama yok

**Bu döngü:**
- Aramayı
- Karar vermeyi
- Akıl yürütmeyi

**aynı şey haline getirir**

### Implementation

`velocity/core/interrogation_loop.py`

```python
from velocity import ParallelInterrogationEngine

engine = ParallelInterrogationEngine(
    interrogator=network_interrogator,
    confidence_threshold=0.7,
    max_iterations=10,
    budget_per_hypothesis=5.0
)

results = await engine.run_parallel(hypotheses)

for result in results:
    print(f"H: {result.hypothesis.id[:8]}")
    print(f"   Confidence: {result.final_confidence:.2f}")
    print(f"   Iterations: {result.iterations}")
    print(f"   Converged: {result.converged}")
```

---

## 5️⃣ CONTRADICTION HANDLING (Çelişki bastırılmaz)

### Yeni Bilgi Geldiğinde

```python
if contradicts(state):
    fork_state()
    track_both()
```

### Yani

- Çelişki varsa state çatallanır
- Biri elenene kadar ikisi de yaşar
- GPU paralelliği burada gerçek anlamda işe yarar

### LLM'lerin Aksine

**LLM:** "En olası"yı seçer
**Velocity:** Olasılık uzayını daraltır

### Implementation

```python
# State forking
if engine.should_fork(hypothesis):
    forked = generator.fork_hypothesis(hypothesis)
    hypotheses.append(forked)
    
    # Re-run forked hypothesis
    fork_results = await engine.run_parallel([forked])
```

---

## 6️⃣ HYPOTHESIS ELIMINATION (Doğal seleksiyon)

### Zamanla

```python
for h in hypotheses:
    if confidence(h) < min_conf OR cost(h) too_high:
        eliminate(h)
```

### Geriye

- 1 güçlü hipotez
- veya
- Birkaç dengeli aday

kalır.

### Implementation

`velocity/core/hypothesis_eliminator.py`

```python
from velocity import HypothesisEliminator, EliminationCriteria

criteria = EliminationCriteria(
    min_confidence=0.3,
    max_cost=10.0,
    min_evidence=2
)

eliminator = HypothesisEliminator(criteria)
surviving, eliminated = eliminator.eliminate_weak(hypotheses, results)

print(f"Surviving: {len(surviving)}")
print(f"Eliminated: {len(eliminated)}")

for h in eliminated:
    print(f"  {h.id[:8]}: {h.elimination_reason}")
```

---

## 7️⃣ STATE SYNTHESIS (Karar oluşumu)

### Kalan Hipotezler Birleştirilir

```python
FinalState = aggregate(states)
```

### Bu State Şunları İçerir

- Karar
- Dayanaklar
- Belirsizlik
- Alternatifler
- Güven aralığı

**Bu nokta:**
- Model cevabı değil
- **Hesaplanmış sonuçtur**

### Implementation

`velocity/core/state_synthesizer.py`

```python
from velocity import StateSynthesizer

synthesizer = StateSynthesizer()
final_state = synthesizer.synthesize(surviving, eliminated)

print(f"Decision: {final_state.decision}")
print(f"Confidence: {final_state.confidence:.2%}")
print(f"Interval: {final_state.confidence_interval}")
print(f"Uncertainty: {final_state.uncertainty_level}")
print(f"Evidence: {len(final_state.evidence_summary)}")
print(f"Contradictions: {len(final_state.contradictions)}")
print(f"Alternatives: {len(final_state.alternatives)}")
```

---

## 8️⃣ OUTPUT LAYER (LLM opsiyonel)

### Eğer

- İnsanla konuşulacaksa → LLM
- Kod üretilecekse → LLM
- API cevabıysa → Direkt JSON

### Ama Şunu Tekrar Net Söyleyeyim

**Bu katman sökülse bile sistem çalışır.**

---

## 9️⃣ Pseudocode ile TAM AKIŞ

```python
intent = parse_intent(input)

routes = epistemic_routing(intent)

hypotheses = generate_hypotheses(routes)

parallel_for h in hypotheses:
    while not done(h):
        evidence = interrogate_network(h.state)
        h.state = update_state(h.state, evidence)

hypotheses = eliminate_weak(hypotheses)

final_state = synthesize(hypotheses)

output = render(final_state)
```

---

## 🔴 Çok Kritik Fark (Burayı Kaçırma)

### LLM

```
"Bu soruya cevap üret"
```

### Velocity

```
"Bu soruya cevap üretilebilir mi?"
```

### Bu Yüzden Velocity

- ✓ Daha az konuşur
- ✓ Daha çok hesaplar
- ✓ Daha az emin görünür
- ✓ Ama epistemik olarak daha sağlamdır

---

## 🚀 Tam Çalışan Implementasyon

### Tüm Akışı Çalıştır

```python
import asyncio
from velocity import VelocityCore

async def main():
    # Core engine'i başlat
    core = VelocityCore(
        max_hypotheses=5,
        confidence_threshold=0.7,
        max_iterations=10,
        budget_per_hypothesis=5.0
    )
    
    # Sorgu
    query = "What is quantum computing?"
    
    # Çalıştır
    result = await core.execute(query)
    
    # Sonuçlar
    print(f"Decision: {result['decision']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Uncertainty: {result['uncertainty']}")
    print(f"Evidence: {len(result['evidence'])} pieces")
    print(f"Contradictions: {len(result['contradictions'])}")
    print(f"Alternatives: {len(result['alternatives'])}")

asyncio.run(main())
```

### Adım Adım

```python
from velocity import (
    IntentParser,
    EpistemicRouter,
    HypothesisGenerator,
    ParallelInterrogationEngine,
    HypothesisEliminator,
    StateSynthesizer
)

# 1. Intent parsing
parser = IntentParser()
intent = parser.parse(query)

# 2. Epistemic routing
router = EpistemicRouter()
strategies = router.route(intent)

# 3. Hypothesis generation
generator = HypothesisGenerator()
hypotheses = generator.generate(intent, strategies)

# 4. Parallel interrogation
engine = ParallelInterrogationEngine(...)
results = await engine.run_parallel(hypotheses)

# 5. Elimination
eliminator = HypothesisEliminator()
surviving, eliminated = eliminator.eliminate_weak(hypotheses, results)

# 6. Synthesis
synthesizer = StateSynthesizer()
final_state = synthesizer.synthesize(surviving, eliminated)
```

---

## 📂 Dosya Yapısı

```
velocity/core/
├── velocity_core.py        # Ana engine (tüm akış)
├── intent_parser.py        # 1. Intent parsing
├── epistemic_router.py     # 2. Epistemic routing
├── hypothesis_generator.py # 3. Hypothesis generation
├── interrogation_loop.py   # 4. Network interrogation
├── hypothesis_eliminator.py# 5. Hypothesis elimination
└── state_synthesizer.py    # 6. State synthesis
```

Her dosya bağımsız bir modüldür ve unit test edilebilir.

---

## 🧪 Çalıştırma

### Demo

```bash
cd velocity
python examples/algorithmic_core_demo.py
```

### Seçenekler

1. **Full execution** - Tüm akışı çalıştır
2. **Step-by-step** - Her adımı ayrı göster
3. **Both** - Her ikisi

---

## 🎯 Temel Özellikler

### ✅ Modüler

Her adım bağımsız bir modül.
Değiştirilebilir, test edilebilir, ölçeklenebilir.

### ✅ Algoritmik

"Yüksek seviye laf" değil, çalışan algoritma.
Her adım net input/output'a sahip.

### ✅ Paralel

GPU'lar hipotez evaluation için kullanılır.
Async/await ile network parallelism.

### ✅ State-Driven

Token bazlı değil, state bazlı ilerleme.
Her state: knowledge, uncertainty, contradictions, confidence.

### ✅ Transparent

Her karar izlenebilir.
Her evidence kaynaklı.
Her çelişki not edilmiş.

---

## 📊 Karşılaştırma

| Özellik | LLM | Velocity |
|---------|-----|----------|
| **Approach** | "Cevap üret" | "Cevap üretilebilir mi?" |
| **Process** | Token generation | Cognitive loop |
| **Knowledge** | In weights | In network |
| **Uncertainty** | Implicit | Explicit |
| **Contradictions** | Hallucinate | Track & fork |
| **Confidence** | Overconfident | Calibrated |
| **Sources** | None | All tracked |
| **GPU Use** | Inference | Hypothesis evaluation |

---

## 🔬 Epistemik Üstünlük

### Velocity Ne Yapar

1. **Soruyu anlar** (intent parsing)
2. **Nereye bakacağına karar verir** (epistemic routing)
3. **Alternatif hipotezler üretir** (hypothesis generation)
4. **Paralel araştırır** (network interrogation)
5. **Çelişkileri takip eder** (contradiction handling)
6. **Zayıf fikirleri eler** (hypothesis elimination)
7. **Sentezler** (state synthesis)

### LLM Ne Yapar

1. "En olası devam tokenini üret"

---

## 💡 核心Insight

```
Traditional AI: "Dünyayı modele sığdır"
Velocity:       "Dünya zaten var, erişimi optimize et"
```

---

## 🚀 Hemen Dene

```bash
# Setup
cd velocity
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Run
python examples/algorithmic_core_demo.py
```

---

## 📝 Sonuç

Bu implementasyon:

- ✅ Gerçek kod (not slides)
- ✅ Modüler yapı
- ✅ Ölçeklenebilir
- ✅ Test edilebilir
- ✅ Production-ready

**Velocity bir "model" değil, bir "cognitive system"dir.**

---

*This is not "high-level talk".*
*This is working, modular, scalable algorithmic skeleton.*

**Welcome to the real Velocity.**
