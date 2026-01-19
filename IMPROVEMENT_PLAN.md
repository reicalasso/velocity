# Velocity Answer Quality Improvement Plan

## Goal
Make Velocity answers as readable and natural as ChatGPT/Claude, without using LLMs.

---

## Current Problems

### 1. Word Concatenation
**Problem:**
```
Quantumcomputingisan emergent field...
AnkaraÜniversitesi (AÜ),Ankara'da yer alan...
```

**Root Cause:**
- NLP summarization removes whitespace during sentence extraction
- BeautifulSoup text extraction concatenates words
- No post-processing to fix spacing

### 2. Unnatural Flow
**Problem:**
- Sentences are just concatenated
- No transition words
- No paragraph structure
- Technical, not conversational

### 3. Formatting Issues
**Problem:**
- No proper punctuation spacing
- Numbers and text merged
- Special characters break flow

---

## Solution: 3-Phase Approach

### Phase 1: Fix NLP Processing (URGENT)

**File:** `velocity/network/web_search.py` - `NLPProcessor`

**Changes:**

1. **Better Text Extraction**
```python
def _clean_html_text(self, html_text: str) -> str:
    """
    Extract clean text from HTML with proper spacing
    """
    # Add space after common HTML elements
    html_text = re.sub(r'(<br>|<br/>|</p>|</div>|</li>)', ' ', html_text)
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_text, 'html.parser')
    
    # Get text with separator to preserve word boundaries
    text = soup.get_text(separator=' ', strip=True)
    
    # Fix multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text
```

2. **Better Sentence Splitting**
```python
def extractive_summarize(self, text: str, num_sentences: int = 3) -> str:
    """
    Extractive summarization with proper spacing
    """
    # Clean text first
    text = self._clean_text_spacing(text)
    
    # Split sentences (preserve spacing)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    # ... TF-IDF scoring ...
    
    # Join with proper spacing and punctuation
    summary = '. '.join(top_sentences)
    
    # Ensure ends with period
    if not summary.endswith('.'):
        summary += '.'
    
    return summary

def _clean_text_spacing(self, text: str) -> str:
    """Fix common spacing issues"""
    # Fix concatenated words (heuristic)
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # camelCase
    text = re.sub(r'([a-z])(\d)', r'\1 \2', text)     # word2number
    text = re.sub(r'(\d)([a-z])', r'\1 \2', text)     # number2word
    
    # Fix punctuation spacing
    text = re.sub(r'\s*([,;:!?])\s*', r'\1 ', text)
    text = re.sub(r'\s*\.\s*', '. ', text)
    
    # Fix multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()
```

3. **Natural Language Post-Processing**
```python
def naturalize_answer(self, text: str) -> str:
    """
    Make answer more natural and readable
    """
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Add transitions between sentences (simple heuristic)
    natural_sentences = []
    for i, sent in enumerate(sentences):
        if i > 0 and len(sent) > 30:
            # Add occasional transitions
            transitions = ['Additionally, ', 'Furthermore, ', 'Moreover, ', '']
            # Use empty most of the time for natural flow
            transition = transitions[i % 4] if i % 3 == 0 else ''
            sent = transition + sent
        
        natural_sentences.append(sent)
    
    # Join into paragraphs (3 sentences each)
    paragraphs = []
    for i in range(0, len(natural_sentences), 3):
        para = ' '.join(natural_sentences[i:i+3])
        paragraphs.append(para)
    
    return '\n\n'.join(paragraphs)
```

---

### Phase 2: Answer Synthesis Enhancement

**File:** `velocity/core/state_synthesizer.py`

**Changes:**

```python
def _determine_decision(self, hypotheses: List[Hypothesis]) -> str:
    """
    Generate natural, ChatGPT-like answer
    """
    # Collect evidence
    all_content = self._collect_all_evidence(hypotheses)
    
    if not all_content:
        return "I couldn't find enough information to answer your question."
    
    # Combine content
    combined_text = ' '.join(all_content)
    
    # Clean and normalize
    combined_text = self._clean_and_normalize(combined_text)
    
    # Extractive summarization (4-5 sentences)
    from velocity.network.web_search import NLPProcessor
    nlp = NLPProcessor()
    summary = nlp.extractive_summarize(combined_text, num_sentences=5)
    
    # Naturalize (make ChatGPT-like)
    natural_answer = nlp.naturalize_answer(summary)
    
    # Add source attribution (subtle)
    source_note = self._format_sources(hypotheses)
    
    return f"{natural_answer}\n\n{source_note}"

def _clean_and_normalize(self, text: str) -> str:
    """Clean text before summarization"""
    # Remove URLs
    text = re.sub(r'http[s]?://\S+', '', text)
    
    # Remove reference markers [1], [2], etc.
    text = re.sub(r'\[\d+\]', '', text)
    
    # Fix spacing
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    text = re.sub(r'\s+', ' ', text)
    
    # Remove very short fragments
    sentences = text.split('.')
    sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
    
    return '. '.join(sentences)

def _format_sources(self, hypotheses: List[Hypothesis]) -> str:
    """Format source attribution naturally"""
    sources = set()
    for h in hypotheses:
        for src in h.state.sources_accessed[:3]:
            if '://' in src:
                domain = src.split('://')[1].split('/')[0]
                sources.add(domain)
    
    if not sources:
        return ""
    
    source_list = ', '.join(list(sources)[:3])
    return f"_Sources: {source_list}_"
```

---

### Phase 3: Output Formatting

**File:** `interactive_velocity.py`

**Changes:**

```python
async def ask_velocity(question: str, core: VelocityCore) -> dict:
    """Ask Velocity with natural output"""
    
    result = await core.execute(question)
    
    # Display answer naturally
    print("\n" + "="*70)
    decision = result['decision']
    
    # Word wrap for readability (70 chars)
    import textwrap
    wrapped = textwrap.fill(decision, width=70)
    print(wrapped)
    print()
    
    # Simplified confidence indicator
    confidence = result['confidence']
    if confidence >= 0.7:
        indicator = "High confidence"
    elif confidence >= 0.5:
        indicator = "Moderate confidence"
    else:
        indicator = "Low confidence"
    
    print(f"({indicator})")
    print("="*70)
```

---

## Implementation Order

### Step 1: Fix NLP Processor (30 min)
- Add `_clean_text_spacing()` method
- Fix `extractive_summarize()` spacing
- Add `naturalize_answer()` method

### Step 2: Update State Synthesizer (20 min)
- Integrate new NLP methods
- Add text cleaning
- Better source formatting

### Step 3: Update Output Display (10 min)
- Add text wrapping
- Simplify confidence display
- Better readability

### Step 4: Test (20 min)
- Test Turkish questions
- Test English questions
- Test technical questions
- Compare with ChatGPT quality

---

## Expected Results

**Before:**
```
Quantumcomputingisan emergent field of computer science...
```

**After:**
```
Quantum computing is an emergent field of computer science and 
engineering. It harnesses the unique qualities of quantum mechanics 
to solve problems beyond the ability of classical computers. 
Furthermore, quantum computing holds the promise of solving some 
of our planet's biggest challenges in areas such as environment, 
agriculture, health, and climate.

Sources: wikipedia.org, ibm.com
```

---

## Notes

- No LLM used (pure NLP: TF-IDF, regex, heuristics)
- Fast processing (< 100ms for text cleaning)
- Deterministic (same input → same output)
- CPU-only

---

## Timeline

- **Phase 1**: 30 minutes
- **Phase 2**: 20 minutes  
- **Phase 3**: 10 minutes
- **Testing**: 20 minutes

**Total**: ~1.5 hours

---

**Status**: Ready to implement
