from typing import Dict, Any, List
from collections import defaultdict

KNOWN_SIGNALS = [
    "concept_spike",
    "grounding_gap",
    "tmb",
    "visual_mismatch",
    "structure_order",
    "ramble_ratio",
]

def compute_signal_breakdown(
    segments: List[Dict[str, Any]],
    mode: str = "weighted",   # "weighted" or "count"
) -> Dict[str, Any]:
    """
    Returns donut-ready signal breakdown.

    segments[i] must contain:
      - "risk": number (0..10 recommended)
      - "signals_triggered": list[str]
    """
    if mode not in {"weighted", "count"}:
        mode = "weighted"

    weight_by_signal = defaultdict(float)
    seg_count_by_signal = defaultdict(int)

    for seg in segments:
        # Handle both dict and Pydantic model inputs
        if hasattr(seg, 'dict'):
            seg_dict = seg.dict()
        else:
            seg_dict = seg
            
        signals = seg_dict.get('signals_triggered', []) if isinstance(seg_dict, dict) else seg.signals_triggered
        risk = seg_dict.get('risk', 0) if isinstance(seg_dict, dict) else seg.risk

        # guardrails
        try:
            risk = float(risk)
        except Exception:
            risk = 0.0

        # clamp risk into a stable band (prevents weird spikes)
        risk = max(0.0, min(risk, 10.0))

        # IMPORTANT: avoid double-counting same signal twice within one segment
        unique_signals = list(dict.fromkeys(signals))

        for s in unique_signals:
            if mode == "count":
                weight_by_signal[s] += 1.0
            else:
                weight_by_signal[s] += risk

            seg_count_by_signal[s] += 1

    # ensure known signals exist even if 0 (stable donut legend)
    for s in KNOWN_SIGNALS:
        weight_by_signal.setdefault(s, 0.0)
        seg_count_by_signal.setdefault(s, 0)

    total = sum(weight_by_signal.values())
    items = []

    # keep stable ordering: known signals first, then unknowns
    ordered = KNOWN_SIGNALS + [s for s in weight_by_signal.keys() if s not in KNOWN_SIGNALS]

    for s in ordered:
        w = float(weight_by_signal[s])
        if total > 0:
            pct = (w / total) * 100.0
        else:
            pct = 0.0

        items.append({
            "signal": s,
            "weight": round(w, 2),
            "percent": round(pct, 2),
            "segments": int(seg_count_by_signal[s]),
        })

    # optional: hide zero rows (some UIs prefer this)
    items_nonzero = [it for it in items if it["weight"] > 0]

    return {
        "mode": mode,
        "total_weight": round(total, 2),
        "items": items_nonzero,  # use items if you want to show zeros too
    }
