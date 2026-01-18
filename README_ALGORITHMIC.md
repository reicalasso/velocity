# Velocity Algorithmic Core

> **Version 0.2.0** - Complete Algorithmic Implementation

## ⚠️ Bu "Yüksek Seviye Laf" Değil

Gerçekten kodlanabilir, modüler ve ölçeklenebilir bir algoritmik iskelet.

---

## 🎯 Ne Yaptık?

Velocity'nin tüm **algoritmik çekirdeğini** implement ettik:

```
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

Bu pseudocode değil - **çalışan koddur**.

---

## 📦 7 Algoritmik Adım

### 1. Intent Parsing ✅

```python
from velocity import IntentParser

parser = IntentParser()
intent = parser.parse("What is quantum computing?")
# → IntentGraph(goal, type, uncertainty, subgoals)
```

**Dosya**: `velocity/core/intent_parser.py`

### 2. Epistemic Routing ✅

```python
from velocity import EpistemicRouter

router = EpistemicRouter()
strategies = router.route(intent, max_strategies=5)
# → List[SourceStrategy] (skorlanmış, sıralı)
```

**Dosya**: `velocity/core/epistemic_router.py`

### 3. Hypothesis Generation ✅

```python
from velocity import HypothesisGenerator

generator = HypothesisGenerator(max_hypotheses=5)
hypotheses = generator.generate(intent, strategies)
# → List[Hypothesis] (paralel değerlendirilebilir)
```

**Dosya**: `velocity/core/hypothesis_generator.py`

### 4. Network Interrogation Loop ✅

```python
from velocity import ParallelInterrogationEngine

engine = ParallelInterrogationEngine(...)
results = await engine.run_parallel(hypotheses)
# → List[InterrogationResult] (her hipotez için)
```

**Dosya**: `velocity/core/interrogation_loop.py`

### 5. Contradiction Handling ✅

```python
# Automatic state forking
if engine.should_fork(hypothesis):
    forked = generator.fork_hypothesis(hypothesis)
    # Forked hypothesis paralel olarak değerlendirilir
```

**Implementation**: İçinde `velocity_core.py`

### 6. Hypothesis Elimination ✅

```python
from velocity import HypothesisEliminator, EliminationCriteria

eliminator = HypothesisEliminator(criteria)
surviving, eliminated = eliminator.eliminate_weak(hypotheses, results)
# → (surviving, eliminated)
```

**Dosya**: `velocity/core/hypothesis_eliminator.py`

### 7. State Synthesis ✅

```python
from velocity import StateSynthesizer

synthesizer = StateSynthesizer()
final_state = synthesizer.synthesize(surviving, eliminated)
# → SynthesizedState(decision, confidence, evidence, etc.)
```

**Dosya**: `velocity/core/state_synthesizer.py`

---

## 🚀 Tam Sistem

### Main Engine

```python
from velocity import VelocityCore
import asyncio

async def main():
    core = VelocityCore(
        max_hypotheses=5,
        confidence_threshold=0.7,
        max_iterations=10
    )
    
    result = await core.execute("What is quantum computing?")
    
    print(f"Decision: {result['decision']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Uncertainty: {result['uncertainty']}")
    print(f"Evidence: {len(result['evidence'])}")
    print(f"Contradictions: {len(result['contradictions'])}")

asyncio.run(main())
```

**Dosya**: `velocity/core/velocity_core.py`

---

## 📂 Proje Yapısı

```
velocity/
├── ALGORITHMIC_CORE.md          ⭐ Tam algoritmik açıklama
├── IMPLEMENTATION_COMPLETE.md   ⭐ Implementation özeti
├── START_HERE.md                ⭐ Buradan başla
│
├── core/
│   ├── velocity_core.py        ✅ Ana engine (tüm akış)
│   ├── intent_parser.py        ✅ Adım 1
│   ├── epistemic_router.py     ✅ Adım 2
│   ├── hypothesis_generator.py ✅ Adım 3
│   ├── interrogation_loop.py   ✅ Adım 4 + 5
│   ├── hypothesis_eliminator.py✅ Adım 6
│   └── state_synthesizer.py    ✅ Adım 7
│
├── examples/
│   └── algorithmic_core_demo.py ⭐ Tam demo
│
└── tests/
    └── test_algorithmic_core.py ✅ Unit tests
```

---

## 🧪 Çalıştır

### Demo

```bash
cd velocity
python examples/algorithmic_core_demo.py
```

**Seçenekler**:
1. Full execution - Tüm akış
2. Step-by-step - Her adım ayrı
3. Both - İkisi birden

### Tests

```bash
pytest tests/test_algorithmic_core.py -v
```

---

## 📊 Özellikler

### ✅ Modüler

Her adım bağımsız modül:
- Ayrı test edilebilir
- Ayrı geliştirilebilir
- Değiştirilebilir

### ✅ Algoritmik

"Laf" değil kod:
- Her adım net algoritma
- Input/output tanımlı
- Pseudocode → Real code

### ✅ Paralel

GPU ve async kullanımı:
- Hypothesis evaluation paralel
- Network queries paralel
- State forking paralel

### ✅ State-Driven

Token değil state:
- Cognitive state tracking
- Uncertainty explicit
- Contradictions tracked
- Confidence calibrated

### ✅ Transparent

İzlenebilir:
- Full logging
- Decision rationale
- Source attribution
- Process metadata

---

## 💡 Kritik Fark

### LLM

**Soru**: "Bu soruya cevap üret"
**Yaklaşım**: En olası token dizisi
**Sonuç**: Kendinden emin, kaynak yok

### Velocity

**Soru**: "Bu soruya cevap üretilebilir mi?"
**Yaklaşım**: Hipotez uzayını değerlendir
**Sonuç**: Dikkatli, epistemik olarak sağlam

---

## 📖 Dokümantasyon

### Algoritmik Dokümanlar

1. **ALGORITHMIC_CORE.md** - Tam algoritmik açıklama
2. **IMPLEMENTATION_COMPLETE.md** - Implementation özeti
3. Her modül kendi docstring'leri

### Felsefe Dokümanları

1. **PARADIGM.md** - Velocity paradigması (Turkish)
2. **PHILOSOPHY.md** - Derin felsefi temel
3. **COMPARISON.md** - Velocity vs Traditional AI

---

## 🎓 Öğrenme Yolu

### 1. Felsefe (30 dk)

- `PARADIGM.md` oku
- `PHILOSOPHY.md` oku
- Konsepti anla

### 2. Algoritma (1 saat)

- `ALGORITHMIC_CORE.md` oku
- Her adımı anla
- Pseudocode'u gör

### 3. Kod (2 saat)

- `examples/algorithmic_core_demo.py` çalıştır
- Her modülün kodunu oku
- Test'leri çalıştır

### 4. Geliştir (∞)

- Kendi modülünü ekle
- Custom source ekle
- Paper yaz!

---

## 🔬 Epistemik Üstünlük

Velocity'nin üstünlüğü:

1. **Uncertainty explicit** - Bilmediğini bilir
2. **Contradictions tracked** - Çelişkileri saklamaz
3. **Sources attributed** - Her iddia kaynaklı
4. **Confidence calibrated** - Güven skoru doğru
5. **Alternatives shown** - Tek cevap değil, olasılık uzayı

---

## 📈 Metrikler

### Implementation

- **7 core modules** - Tamamlandı ✅
- **~2000+ LOC** - Core only
- **Complete tests** - Her modül için
- **Full documentation** - Her adım

### Functionality

- **6 decision types** - Factual, comparative, predictive, etc.
- **10 source types** - Epistemik kaynak çeşitliliği
- **Unlimited hypotheses** - Paralel değerlendirme
- **Dynamic queries** - State-driven loop
- **Multi-criteria elimination** - Doğal seleksiyon

---

## 🎯 Next Steps

### Kullan

```bash
python examples/algorithmic_core_demo.py
```

### Öğren

```bash
# Dok okcu
cat ALGORITHMIC_CORE.md

# Kodu incele
ls velocity/core/
```

### Geliştir

```python
# Custom modül ekle
from velocity.core.epistemic_router import EpistemicRouter

class MyRouter(EpistemicRouter):
    def custom_routing_logic(self):
        # Your logic here
        pass
```

---

## 🏆 Status

**Velocity Algorithmic Core: COMPLETE ✅**

- ✅ 7 adım implement edildi
- ✅ Her adım test edildi
- ✅ Tam dokümantasyon
- ✅ Çalışan demo
- ✅ Production-ready structure

---

## 🎉 Sonuç

Velocity artık sadece bir konsept değil.

**Çalışan, modüler, ölçeklenebilir bir sistem.**

> "Yüksek seviye laf" değil.
> Algoritmik iskelet.

**Welcome to the real Velocity.**

---

## 📞 Quick Links

- **Start Here**: `START_HERE.md`
- **Algorithm Docs**: `ALGORITHMIC_CORE.md`
- **Implementation**: `IMPLEMENTATION_COMPLETE.md`
- **Philosophy**: `PARADIGM.md`, `PHILOSOPHY.md`
- **Demo**: `examples/algorithmic_core_demo.py`
- **Tests**: `tests/test_algorithmic_core.py`

---

*Intelligence lives in the speed of interrogation, not in the size of memory.*

**Velocity 0.2.0 - Algorithmic Core**
