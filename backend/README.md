# Demo Therapist - Backend

🎯 **Analyze demo videos for clarity issues and provide actionable feedback with humor**

## 🏗️ Architecture Overview

```
Backend Pipeline:
1. Upload video → TwelveLabs indexing (Person A)
2. Get transcript + timestamps (Person A)
3. Create 10s windows (Person A)
4. Analyze each window with LLM (Person B's tools)
5. Compute signals + risk scores (Person A + Person B helpers)
6. Generate issues with roasts (Person B's tools)
7. Return JSON to frontend (Person C)
```

## 📁 File Structure

```
backend/
├── llm_tools.py              # Person B: All LLM functions (Gemini)
├── signal_helpers.py         # Person B: Local signal computation
├── config.py                 # Configuration management
├── requirements.txt          # Python dependencies
│
├── example_integration.py    # Complete working example
├── test_llm_tools.py        # Test suite
│
├── README.md                # This file
└── README_PERSON_B.md       # Person B detailed docs
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up API Keys

```bash
# Gemini (Person B - Required)
export GEMINI_API_KEY="your-gemini-key-here"

# TwelveLabs (Person A - Required for full pipeline)
export TWELVE_LABS_API_KEY="your-twelvelabs-key-here"
```

Or create a `.env` file:

```bash
GEMINI_API_KEY=your-gemini-key-here
TWELVE_LABS_API_KEY=your-twelvelabs-key-here
```

### 3. Test the Tools

```bash
# Test Person B's LLM tools
python test_llm_tools.py

# Run integration example
python example_integration.py
```

## 👥 Team Responsibilities

### Person A - Backend + TwelveLabs Integration

**Your tasks:**
- FastAPI setup (`main.py`)
- `/upload` and `/analyze` endpoints
- TwelveLabs video indexing
- Transcript retrieval + windowing
- Integrate Person B's LLM tools
- Risk scoring and thresholding
- Return JSON to frontend

**What Person B provides for you:**
```python
from llm_tools import LLMTools
from signal_helpers import SignalHelpers

# Initialize once
llm = LLMTools()

# For each window:
terms = llm.extract_terms(window_text)
claims = llm.classify_claims_evidence(window_text)
role = llm.role_tag(window_text)

# Compute local signals
ramble = SignalHelpers.analyze_ramble(window_text)

# Generate issues
label_fix = llm.label_and_fix(window_text, signals, terms.terms)
roast = llm.roast_variants(label_fix.label, label_fix.explanation, label_fix.fix)
```

See `example_integration.py` for complete pipeline.

### Person B - LLM Prompts + Signal Helpers

**Your deliverables:** ✅ COMPLETE
- ✅ `llm_tools.py` - All LLM functions
- ✅ `signal_helpers.py` - Local signal computation
- ✅ `config.py` - Configuration
- ✅ `example_integration.py` - Integration example
- ✅ `test_llm_tools.py` - Test suite
- ✅ `README_PERSON_B.md` - Documentation

**Status:** Ready for Person A to integrate!

### Person C - Frontend

**Your needs from backend:**

**Endpoint:** `POST /analyze`

**Request:**
```json
{
  "video_id": "abc123"
}
```

**Response:**
```json
{
  "run_id": "xyz789",
  "video_title": "demo.mp4",
  "clarity_score": 63,
  "clarity_tier": "Wait...what are we building?",
  "segments": [
    {
      "segment_id": 7,
      "start_sec": 70,
      "end_sec": 80,
      "risk": 8.6,
      "severity": "high",
      "signals_triggered": ["concept_spike", "grounding_gap"],
      "label": "Buzzword Overdose",
      "evidence": {
        "transcript_excerpt": "We used Marengo with RAG...",
        "terms": ["Marengo", "RAG", "embeddings"],
        "claims": ["faster", "scalable"],
        "visual_alignment": 0.35
      },
      "fix": "Define Marengo in one sentence before this segment.",
      "tone": {
        "kind": "This part introduces multiple terms quickly. Add a definition of Marengo first.",
        "honest": "You dropped 3 acronyms with zero grounding. Define Marengo before going deeper.",
        "brutal": "Acronym speedrun detected. Judges met Marengo 0 seconds ago—introduce it first."
      }
    }
  ]
}
```

## 🎯 The 6 Signals

### Signal 1: Concept Spike (Buzzword Velocity)
**What:** Too many new technical terms at once  
**LLM Function:** `llm.extract_terms(text)`  
**Helper:** `SignalHelpers.compute_concept_spike_severity()`

### Signal 2: Grounding Gap (Used Before Defined)
**What:** Terms used without definition  
**LLM Function:** `llm.check_term_definition(term, text)`  
**Helper:** `SignalHelpers.compute_grounding_gap_severity()`

### Signal 3: Trust-Me-Bro (Claims Without Evidence)
**What:** Benefits claimed without proof  
**LLM Function:** `llm.classify_claims_evidence(text)`  
**Helper:** `SignalHelpers.compute_tmb_severity()`

### Signal 4: Visual-Verbal Mismatch (Optional)
**What:** Talking about X while showing Y  
**Implementation:** TwelveLabs visual search + LLM alignment check

### Signal 5: Structure Order Violations
**What:** Bad pitch ordering (demo before problem)  
**LLM Function:** `llm.role_tag(text)`  
**Helper:** `SignalHelpers.check_structure_violations()`

### Signal 6: Ramble Ratio
**What:** Too many filler words, low density  
**Helper:** `SignalHelpers.analyze_ramble(text)` (no LLM needed)

## 🔧 Configuration

Edit `config.py` or set environment variables:

```python
# Model selection
GEMINI_MODEL=gemini-1.5-flash  # Fast (default)
# GEMINI_MODEL=gemini-1.5-pro   # Better quality

# Risk threshold
RISK_THRESHOLD=4.0  # Lower = more sensitive

# Signal weights (tune importance)
SIGNAL_WEIGHTS = {
    "concept_spike": 1.0,
    "grounding_gap": 1.3,
    "tmb": 1.2,
    "visual_mismatch": 1.5,
    "structure_order": 1.4,
    "ramble_ratio": 0.8
}
```

## 📊 Data Flow

```
1. Video Upload (Person A)
   └→ POST /upload → video_id

2. TwelveLabs Processing (Person A)
   ├→ Index video
   ├→ Get transcript + timestamps
   └→ Create 10s windows

3. Window Analysis (Person A + B)
   For each window:
   ├→ Extract terms (Person B's llm_tools)
   ├→ Check definitions (Person B's llm_tools)
   ├→ Detect claims/evidence (Person B's llm_tools)
   ├→ Tag role (Person B's llm_tools)
   ├→ Analyze ramble (Person B's signal_helpers)
   ├→ Compute risk (Person B's signal_helpers)
   └→ Flag if risk >= threshold

4. Issue Generation (Person B's tools)
   For flagged windows:
   ├→ Generate label + fix (llm_tools)
   └→ Generate roast variants (llm_tools)

5. Response (Person A)
   └→ Return JSON with all issues
```

## 🧪 Testing

### Test LLM Tools Only (Person B)
```bash
python test_llm_tools.py
```

### Test Full Integration (Person A + B)
```bash
python example_integration.py
```

### Test Individual Functions
```python
from llm_tools import LLMTools

llm = LLMTools()

# Test term extraction
terms = llm.extract_terms("We used RAG with FAISS embeddings")
print(terms.terms)  # ['RAG', 'FAISS', 'embeddings']

# Test claims detection
claims = llm.classify_claims_evidence("It's 10x faster")
print(claims.claims)  # ['10x faster']
```

## 📝 Example Integration (Person A)

```python
from llm_tools import LLMTools
from signal_helpers import SignalHelpers

# Initialize
llm = LLMTools()

# Your TwelveLabs code gets windows
windows = get_transcript_windows()  # Your function

issues = []

for window in windows:
    # Person B's tools
    terms = llm.extract_terms(window['text'])
    claims = llm.classify_claims_evidence(window['text'])
    role = llm.role_tag(window['text'])
    ramble = SignalHelpers.analyze_ramble(window['text'])
    
    # Your risk computation
    severities = {
        "concept_spike": 2 if len(terms.terms) > 4 else 0,
        "tmb": SignalHelpers.compute_tmb_severity(claims.claims, claims.evidence),
        "ramble_ratio": ramble.severity
    }
    
    risk = SignalHelpers.compute_risk_score(severities)
    
    # Flag high-risk windows
    if risk >= 4.0:
        # Person B's tools for generation
        label_fix = llm.label_and_fix(
            window['text'],
            list(severities.keys()),
            terms.terms
        )
        
        roast = llm.roast_variants(
            label_fix.label,
            label_fix.explanation,
            label_fix.fix
        )
        
        # Build issue
        issue = {
            "segment_id": window['id'],
            "start_sec": window['start'],
            "end_sec": window['end'],
            "risk": risk,
            "label": label_fix.label,
            "fix": label_fix.fix,
            "tone": {
                "kind": roast.kind,
                "honest": roast.honest,
                "brutal": roast.brutal
            }
        }
        
        issues.append(issue)

return {"segments": issues}
```

See `example_integration.py` for complete code.

## 🐛 Troubleshooting

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "API key not found"
```bash
export GEMINI_API_KEY="your-key"
```

### "Rate limit exceeded"
Add delays between LLM calls:
```python
import time
time.sleep(0.2)
```

### Tests fail
1. Check API key is set
2. Check internet connection
3. Check Gemini API status: https://status.cloud.google.com/

## 🎯 Hackathon Checklist

- ✅ Person B deliverables complete
- ⏳ Person A: FastAPI endpoints
- ⏳ Person A: TwelveLabs integration
- ⏳ Person A: Integrate Person B's tools
- ⏳ Person C: Frontend UI
- ⏳ Deploy and test end-to-end

## 🏆 MLH Prize Eligibility

**Best Use of Gemini:**
- ✅ Term extraction
- ✅ Definition detection
- ✅ Claims/evidence classification
- ✅ Role tagging
- ✅ Label generation
- ✅ Roast text generation

Heavy Gemini usage throughout! 🎉

**Best Use of TwelveLabs:**
- Video indexing
- Transcript with timestamps
- Semantic video search
- Visual context analysis

## 📚 Documentation

- **`README_PERSON_B.md`** - Detailed LLM tools documentation
- **`example_integration.py`** - Complete working example
- **`test_llm_tools.py`** - Test suite with examples

## 🚢 Deployment

### Local (Fastest)
```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload

# Terminal 2: Frontend (Person C)
cd frontend
npm run dev

# Or use ngrok for external access
ngrok http 8000
```

### Production
- **Frontend:** Vercel
- **Backend:** Render (FastAPI)
- **Storage:** Local filesystem or MongoDB Atlas (optional)

## ⚡ Performance Tips

1. **Use Flash model** (default) for speed
2. **Enable fallbacks** for reliability
3. **Batch LLM calls** where possible
4. **Cache results** to avoid re-computation
5. **Add delays** (0.1-0.2s) between API calls

## 🤝 Integration Status

- ✅ **Person B:** COMPLETE - Ready for integration
- ⏳ **Person A:** In progress - Use `example_integration.py` as reference
- ⏳ **Person C:** Waiting for backend endpoints

## 💬 Need Help?

- Person B: Check `README_PERSON_B.md`
- Person A: See `example_integration.py`
- All: Run `python test_llm_tools.py`

---

**Built for Joke Hack 2026** 🎯

Good luck! 🚀
