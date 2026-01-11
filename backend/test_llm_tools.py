"""
Quick Test Script for LLM Tools
Run this to verify everything works before integration
"""

import os
import sys
from typing import Dict, List


def check_dependencies():
    """Check if all required packages are installed"""
    print("🔍 Checking dependencies...")
    
    required = [
        "google.generativeai",
        "dotenv",
        "dataclasses"
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing.append(package)
    
    if missing:
        print("\n⚠️  Missing packages. Install with:")
        print("  pip install -r requirements.txt")
        return False
    
    print()
    return True


def check_api_key():
    """Check if Gemini API key is set"""
    print("🔑 Checking API key...")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        print("  ❌ GEMINI_API_KEY not found")
        print("\n⚠️  Set your API key:")
        print('  export GEMINI_API_KEY="your-key-here"')
        print("  Or create a .env file")
        print("\n  Get key from: https://makersuite.google.com/app/apikey")
        return False
    
    print(f"  ✅ API key found ({api_key[:10]}...)")
    print()
    return True


def test_llm_functions():
    """Test all LLM functions with sample data"""
    print("🧪 Testing LLM functions...\n")
    
    try:
        from llm_tools import LLMTools
        from signal_helpers import SignalHelpers
        
        # Initialize
        llm = LLMTools()
        print("✅ LLM Tools initialized\n")
        
        # Test data
        test_texts = [
            {
                "name": "Buzzword heavy",
                "text": "We built this using Marengo with RAG, FAISS embeddings, and LLM integration for real-time processing."
            },
            {
                "name": "Claim without evidence",
                "text": "Our system is 10x faster and more scalable than any competitor. It's the best solution available."
            },
            {
                "name": "Clean explanation",
                "text": "RAG, or Retrieval Augmented Generation, is a technique that combines retrieval with generation. As you can see in this demo, it works well."
            }
        ]
        
        results = []
        
        for i, test in enumerate(test_texts):
            print(f"{'='*60}")
            print(f"Test {i+1}: {test['name']}")
            print(f"{'='*60}")
            print(f"Input: {test['text']}\n")
            
            # Test 1: Extract terms
            print("1️⃣ Extracting terms...")
            terms = llm.extract_terms(test['text'])
            print(f"   Terms: {terms.terms}")
            print(f"   Acronyms: {terms.acronyms}\n")
            
            # Test 2: Claims & Evidence
            print("2️⃣ Detecting claims/evidence...")
            claims = llm.classify_claims_evidence(test['text'])
            print(f"   Claims: {claims.claims}")
            print(f"   Evidence: {claims.evidence}")
            print(f"   Has evidence: {claims.has_evidence}\n")
            
            # Test 3: Role tagging
            print("3️⃣ Tagging role...")
            role = llm.role_tag(test['text'])
            print(f"   Role: {role.role}")
            print(f"   Confidence: {role.confidence:.2f}\n")
            
            # Test 4: Check term definitions
            if terms.terms:
                print("4️⃣ Checking term definitions...")
                for term in terms.terms[:2]:  # Check first 2 terms
                    is_defined = llm.check_term_definition(term, test['text'])
                    status = "✅ Defined" if is_defined else "❌ Not defined"
                    print(f"   '{term}': {status}")
                print()
            
            # Test 5: Local signals (no API call)
            print("5️⃣ Local signal analysis...")
            ramble = SignalHelpers.analyze_ramble(test['text'])
            print(f"   Filler ratio: {ramble.filler_ratio:.2%}")
            print(f"   Ramble severity: {ramble.severity}\n")
            
            results.append({
                "test": test['name'],
                "terms": len(terms.terms),
                "claims": len(claims.claims),
                "has_evidence": claims.has_evidence,
                "role": role.role
            })
            
            print()
        
        # Test 6: Label and fix generation
        print(f"{'='*60}")
        print("Test: Label and Fix Generation")
        print(f"{'='*60}\n")
        
        label_fix = llm.label_and_fix(
            window_text=test_texts[0]['text'],
            triggered_signals=["concept_spike", "grounding_gap"],
            terms=["Marengo", "RAG", "FAISS"]
        )
        
        print(f"Label: {label_fix.label}")
        print(f"Explanation: {label_fix.explanation}")
        print(f"Fix: {label_fix.fix}\n")
        
        # Test 7: Roast variants (with personalized context)
        print("6️⃣ Generating roast variants...\n")
        roast = llm.roast_variants(
            label_fix.label,
            label_fix.explanation,
            label_fix.fix,
            transcript_excerpt=transcript_1,
            signals=["concept_spike", "grounding_gap"]
        )
        
        print(f"😊 Kind: {roast.kind}\n")
        print(f"😐 Honest: {roast.honest}\n")
        print(f"😤 Brutal: {roast.brutal}\n")
        
        # Summary
        print(f"{'='*60}")
        print("Summary")
        print(f"{'='*60}\n")
        
        for result in results:
            print(f"✅ {result['test']}")
            print(f"   Terms: {result['terms']}, Claims: {result['claims']}, Role: {result['role']}")
        
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_signal_helpers():
    """Test local signal helper functions"""
    print("\n" + "="*60)
    print("Testing Signal Helpers (Local - No API)")
    print("="*60 + "\n")
    
    try:
        from signal_helpers import SignalHelpers
        
        # Test ramble detection
        ramble_text = "Um, so like, you know, we basically built this thing, um, like, it's pretty good, you know?"
        result = SignalHelpers.analyze_ramble(ramble_text)
        
        print(f"1️⃣ Ramble Detection:")
        print(f"   Filler ratio: {result.filler_ratio:.2%}")
        print(f"   Severity: {result.severity}\n")
        
        # Test concept spike
        severity = SignalHelpers.compute_concept_spike_severity(5, 2)
        print(f"2️⃣ Concept Spike Severity: {severity}\n")
        
        # Test risk scoring
        severities = {
            "concept_spike": 2,
            "grounding_gap": 1,
            "tmb": 2
        }
        risk = SignalHelpers.compute_risk_score(severities)
        print(f"3️⃣ Risk Score: {risk:.1f}\n")
        
        # Test clarity score
        clarity = SignalHelpers.compute_clarity_score(20, 5)
        tier = SignalHelpers.get_clarity_tier(clarity)
        print(f"4️⃣ Clarity Score: {clarity}/100 ({tier})\n")
        
        # Test structure violations
        role_sequence = [
            (0, "demo"),
            (1, "solution"),
            (2, "problem")
        ]
        severity, violations = SignalHelpers.check_structure_violations(role_sequence)
        print(f"5️⃣ Structure Violations: {len(violations)} found")
        for v in violations:
            print(f"   - {v}")
        print()
        
        print("✅ Signal helpers working correctly!\n")
        return True
        
    except Exception as e:
        print(f"❌ Signal helper tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🎯 Demo Therapist - LLM Tools Test Suite")
    print("="*60 + "\n")
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install requirements.")
        sys.exit(1)
    
    # Step 2: Check API key
    if not check_api_key():
        print("\n❌ API key not configured. Please set GEMINI_API_KEY.")
        sys.exit(1)
    
    # Step 3: Test signal helpers (no API needed)
    if not test_signal_helpers():
        print("\n❌ Signal helper tests failed.")
        sys.exit(1)
    
    # Step 4: Test LLM functions (requires API)
    if not test_llm_functions():
        print("\n❌ LLM function tests failed.")
        sys.exit(1)
    
    # Success!
    print("\n" + "="*60)
    print("🎉 ALL TESTS PASSED!")
    print("="*60)
    print("\n✅ Person B's LLM Tools are ready for integration!")
    print("📖 See example_integration.py for usage examples")
    print("📚 Read README_PERSON_B.md for full documentation")
    print()


if __name__ == "__main__":
    main()
