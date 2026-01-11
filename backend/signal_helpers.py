"""
Signal Helpers - Local computations that don't require LLM
Person B's helper functions for signals that can be computed locally

These are lightweight, fast, and don't require API calls.
"""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class RambleResult:
    """Result from ramble/filler analysis"""
    filler_ratio: float
    filler_count: int
    total_words: int
    repeated_phrases: List[str]
    severity: int  # 0, 1, or 2


class SignalHelpers:
    """Helper functions for local signal computation"""
    
    # Common filler words
    FILLER_WORDS = [
        "um", "uh", "like", "you know", "basically", "kind of", 
        "sort of", "actually", "literally", "honestly", "i mean",
        "you see", "right", "okay", "so", "well", "yeah"
    ]
    
    # Claim keywords (for fallback)
    CLAIM_KEYWORDS = [
        "faster", "better", "improved", "reduced", "increased",
        "scalable", "secure", "efficient", "optimized", "enhanced",
        "superior", "best", "revolutionary", "innovative", "cutting-edge",
        "powerful", "robust", "reliable", "seamless"
    ]
    
    # Evidence keywords (for fallback)
    EVIDENCE_KEYWORDS = [
        "graph", "chart", "demo", "show", "see", "benchmark",
        "result", "data", "measured", "tested", "proof", "evidence",
        "screenshot", "here", "this", "as you can see", "look at"
    ]
    
    
    @staticmethod
    def analyze_ramble(text: str, threshold_low: float = 0.03, threshold_high: float = 0.07) -> RambleResult:
        """
        Signal 6: Ramble / Filler Ratio
        
        Detects low-density speaking with too many filler words or repetitions.
        
        Args:
            text: Transcript text
            threshold_low: Low threshold (severity 1)
            threshold_high: High threshold (severity 2)
        
        Returns:
            RambleResult with ratio and severity
        """
        # Tokenize into words
        words = re.findall(r'\b\w+\b', text.lower())
        total_words = len(words)
        
        if total_words == 0:
            return RambleResult(0.0, 0, 0, [], 0)
        
        # Count filler words
        filler_count = sum(1 for word in words if word in SignalHelpers.FILLER_WORDS)
        filler_ratio = filler_count / total_words
        
        # Detect repeated phrases (2-3 word sequences)
        repeated_phrases = SignalHelpers._find_repeated_phrases(words)
        
        # Determine severity
        severity = 0
        if filler_ratio >= threshold_high or len(repeated_phrases) >= 3:
            severity = 2
        elif filler_ratio >= threshold_low or len(repeated_phrases) >= 1:
            severity = 1
        
        return RambleResult(
            filler_ratio=filler_ratio,
            filler_count=filler_count,
            total_words=total_words,
            repeated_phrases=repeated_phrases,
            severity=severity
        )
    
    
    @staticmethod
    def _find_repeated_phrases(words: List[str], window_size: int = 3) -> List[str]:
        """Find repeated 2-3 word phrases"""
        repeated = []
        phrase_counts = {}
        
        # Look for 2-word and 3-word sequences
        for n in [2, 3]:
            for i in range(len(words) - n + 1):
                phrase = " ".join(words[i:i+n])
                phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1
        
        # Return phrases that appear more than once
        repeated = [phrase for phrase, count in phrase_counts.items() if count > 1]
        
        return repeated[:5]  # Limit to top 5
    
    
    @staticmethod
    def compute_concept_spike_severity(
        current_terms: int,
        previous_avg: float,
        threshold_medium: float = 1.5,
        threshold_high: float = 2.5
    ) -> int:
        """
        Signal 1: Concept Spike severity
        
        Args:
            current_terms: Number of terms in current window
            previous_avg: Average number of terms in previous windows
            threshold_medium: Multiplier for severity 1
            threshold_high: Multiplier for severity 2
        
        Returns:
            Severity: 0, 1, or 2
        """
        if previous_avg == 0:
            previous_avg = 1  # Avoid division by zero
        
        ratio = current_terms / previous_avg
        
        if ratio > threshold_high:
            return 2
        elif ratio > threshold_medium:
            return 1
        else:
            return 0
    
    
    @staticmethod
    def compute_grounding_gap_severity(ungrounded_terms: List[str]) -> int:
        """
        Signal 2: Grounding Gap severity
        
        Args:
            ungrounded_terms: List of terms used without definition
        
        Returns:
            Severity: 0, 1, or 2
        """
        count = len(ungrounded_terms)
        
        if count >= 2:
            return 2
        elif count == 1:
            return 1
        else:
            return 0
    
    
    @staticmethod
    def compute_tmb_severity(claims: List[str], evidence: List[str]) -> int:
        """
        Signal 3: Trust-Me-Bro severity
        
        Args:
            claims: List of claims made
            evidence: List of evidence cues
        
        Returns:
            Severity: 0, 1, or 2
        """
        has_claims = len(claims) > 0
        has_evidence = len(evidence) > 0
        
        if not has_claims:
            return 0  # No claims, no problem
        
        if has_evidence:
            # Check if evidence is weak
            if len(evidence) < len(claims):
                return 1  # Claims > evidence (weak)
            return 0  # Good balance
        else:
            return 2  # Claims without evidence
    
    
    @staticmethod
    def check_structure_violations(role_sequence: List[Tuple[int, str]]) -> Tuple[int, List[str]]:
        """
        Signal 5: Structure Order Violations
        
        Checks for bad ordering of pitch segments.
        
        Args:
            role_sequence: List of (window_id, role) tuples
        
        Returns:
            (severity, list of violation descriptions)
        """
        violations = []
        
        # Extract role positions
        role_positions = {}
        for window_id, role in role_sequence:
            if role not in role_positions:
                role_positions[role] = window_id
        
        # Rule 1: Problem should come before solution/demo/metrics
        if "problem" in role_positions:
            problem_pos = role_positions["problem"]
            
            if "solution" in role_positions and role_positions["solution"] < problem_pos:
                violations.append("Solution presented before problem")
            
            if "demo" in role_positions and role_positions["demo"] < problem_pos:
                violations.append("Demo shown before problem explained")
            
            if "metrics" in role_positions and role_positions["metrics"] < problem_pos:
                violations.append("Metrics shown before problem context")
        
        # Rule 2: Demo before problem is critical
        if "demo" in role_positions and "problem" in role_positions:
            if role_positions["demo"] < role_positions["problem"]:
                violations.append("CRITICAL: Demo before problem (instant confusion)")
        
        # Rule 3: Architecture before solution is risky
        if "architecture" in role_positions and "solution" in role_positions:
            if role_positions["architecture"] < role_positions["solution"]:
                violations.append("Architecture details before high-level solution")
        
        # Rule 4: Metrics before baseline/problem
        if "metrics" in role_positions:
            if "problem" not in role_positions and "user_context" not in role_positions:
                violations.append("Metrics without context or baseline")
        
        # Determine severity
        severity = 0
        if len(violations) >= 2:
            severity = 2
        elif len(violations) == 1:
            # Critical violations get severity 2
            if any("CRITICAL" in v or "Demo" in v for v in violations):
                severity = 2
            else:
                severity = 1
        
        return severity, violations
    
    
    @staticmethod
    def compute_risk_score(severities: Dict[str, int], weights: Dict[str, float] = None) -> float:
        """
        Compute overall risk score from signal severities
        
        Args:
            severities: Dict mapping signal name to severity (0, 1, or 2)
            weights: Optional custom weights per signal
        
        Returns:
            Risk score (higher = worse)
        """
        if weights is None:
            # Default weights from spec
            weights = {
                "concept_spike": 1.0,
                "grounding_gap": 1.3,
                "tmb": 1.2,
                "visual_mismatch": 1.5,
                "structure_order": 1.4,
                "ramble_ratio": 0.8
            }
        
        risk = 0.0
        for signal, severity in severities.items():
            weight = weights.get(signal, 1.0)
            risk += weight * severity
        
        return risk
    
    
    @staticmethod
    def compute_clarity_score(
        total_risk: float,
        num_windows: int,
        normalization_factor: float = 8.0
    ) -> int:
        """
        Compute overall clarity score (0-100)
        
        Args:
            total_risk: Sum of all risk scores across windows
            num_windows: Total number of windows
            normalization_factor: Scaling factor (tune for typical videos)
        
        Returns:
            Clarity score (0-100)
        """
        if num_windows == 0:
            return 50  # Default
        
        avg_risk = total_risk / num_windows
        penalty = avg_risk * normalization_factor
        
        clarity = max(0, min(100, 100 - penalty))
        return int(clarity)
    
    
    @staticmethod
    def get_clarity_tier(score: int) -> str:
        """Get tier label for clarity score"""
        if score >= 90:
            return "Judge Whisperer"
        elif score >= 70:
            return "Solid Senior Engineer"
        elif score >= 50:
            return "Wait...what are we building?"
        else:
            return "3AM Red Bull PowerPoint"
    
    
    @staticmethod
    def should_flag_as_issue(
        risk: float,
        severities: Dict[str, int],
        risk_threshold: float = 4.0,
        min_signals: int = 2
    ) -> bool:
        """
        Determine if a window should be flagged as an issue
        
        Args:
            risk: Computed risk score
            severities: Signal severities
            risk_threshold: Minimum risk to flag
            min_signals: Minimum number of signals with severity >= 1
        
        Returns:
            True if should be flagged
        """
        # Rule 1: High risk score
        if risk >= risk_threshold:
            return True
        
        # Rule 2: Multiple signals triggered
        active_signals = sum(1 for s in severities.values() if s >= 1)
        if active_signals >= min_signals:
            return True
        
        return False


# Convenience functions for quick use

def quick_ramble_check(text: str) -> RambleResult:
    """Quick check for ramble/filler"""
    return SignalHelpers.analyze_ramble(text)


def quick_risk_score(severities: Dict[str, int]) -> float:
    """Quick risk score calculation"""
    return SignalHelpers.compute_risk_score(severities)


if __name__ == "__main__":
    """Test the helper functions"""
    
    print("🧪 Testing Signal Helpers\n")
    
    # Test 1: Ramble detection
    print("1️⃣ Ramble Detection:")
    text = "Um, so like, you know, we basically, um, built this thing, like, you know what I mean?"
    result = quick_ramble_check(text)
    print(f"   Text: {text}")
    print(f"   Filler ratio: {result.filler_ratio:.2%}")
    print(f"   Filler count: {result.filler_count}/{result.total_words}")
    print(f"   Severity: {result.severity}\n")
    
    # Test 2: Concept spike
    print("2️⃣ Concept Spike:")
    severity = SignalHelpers.compute_concept_spike_severity(current_terms=5, previous_avg=2)
    print(f"   Current: 5 terms, Previous avg: 2 terms")
    print(f"   Severity: {severity}\n")
    
    # Test 3: Risk scoring
    print("3️⃣ Risk Scoring:")
    severities = {
        "concept_spike": 2,
        "grounding_gap": 1,
        "tmb": 0
    }
    risk = quick_risk_score(severities)
    print(f"   Severities: {severities}")
    print(f"   Risk score: {risk:.1f}\n")
    
    # Test 4: Clarity score
    print("4️⃣ Clarity Score:")
    clarity = SignalHelpers.compute_clarity_score(total_risk=25, num_windows=5)
    tier = SignalHelpers.get_clarity_tier(clarity)
    print(f"   Total risk: 25 across 5 windows")
    print(f"   Clarity score: {clarity}/100")
    print(f"   Tier: {tier}\n")
    
    # Test 5: Structure violations
    print("5️⃣ Structure Violations:")
    role_sequence = [
        (0, "demo"),      # BAD: demo first
        (1, "solution"),
        (2, "problem")    # Problem should be first
    ]
    severity, violations = SignalHelpers.check_structure_violations(role_sequence)
    print(f"   Sequence: demo → solution → problem")
    print(f"   Violations: {violations}")
    print(f"   Severity: {severity}\n")
    
    print("✅ All tests completed!")
