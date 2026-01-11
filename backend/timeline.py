from typing import List, Dict, Any
import math

def build_timeline_heatmap(segments: List[Dict[str, Any]], duration_sec: float = None, bin_size_sec: float = 1.0) -> Dict[str, Any]:
    """
    Build a timeline heatmap from analysis segments.
    
    Args:
        segments: List of segments with start_sec, end_sec, and risk
        duration_sec: Total video duration (optional, will use last segment end if not provided)
        bin_size_sec: Size of each time bin in seconds (default: 1s)
        
    Returns:
        Dict with:
        - bin_size_sec: Size of each time bin
        - duration_sec: Total duration
        - values: List of intensity values (0-1) for each bin
        - peaks: List of peak points (high intensity regions)
    """
    # Get duration from segments if not provided
    if not duration_sec:
        duration_sec = max(seg.end_sec for seg in segments) if segments else 0
        
    # Calculate number of bins
    num_bins = math.ceil(duration_sec / bin_size_sec)
    
    # Initialize bins
    values = [0.0] * num_bins
    
    # Find max risk for normalization
    max_risk = max((seg.risk for seg in segments), default=10.0)
    
    # Fill bins based on segment overlaps
    for seg in segments:
        # Convert risk to intensity (0-1)
        intensity = seg.risk / max_risk
        
        # Calculate which bins this segment affects
        start_bin = math.floor(seg.start_sec / bin_size_sec)
        end_bin = math.ceil(seg.end_sec / bin_size_sec)
        
        # Clamp to valid bin range
        start_bin = max(0, min(start_bin, num_bins - 1))
        end_bin = max(0, min(end_bin, num_bins))
        
        # Fill affected bins with max intensity
        for bin_idx in range(start_bin, end_bin):
            values[bin_idx] = max(values[bin_idx], intensity)
    
    # Optional: Apply smoothing (rolling mean of 3)
    smoothed = values.copy()
    for i in range(1, len(values) - 1):
        smoothed[i] = (values[i-1] + values[i] + values[i+1]) / 3
    values = smoothed
    
    # Find peaks (local maxima)
    peaks = []
    for i in range(len(values)):
        is_peak = True
        for j in range(max(0, i-1), min(len(values), i+2)):
            if j != i and values[j] > values[i]:
                is_peak = False
                break
                
        if is_peak and values[i] > 0.5:  # Only include significant peaks
            # Find which segment(s) contributed to this peak
            time = i * bin_size_sec
            relevant_segments = [
                seg.segment_id for seg in segments
                if seg.start_sec <= time <= seg.end_sec
            ]
            if relevant_segments:
                peaks.append({
                    "t": i,
                    "value": values[i],
                    "segment_id": relevant_segments[0]  # Use first overlapping segment
                })
    
    return {
        "bin_size_sec": bin_size_sec,
        "duration_sec": duration_sec,
        "values": [round(v, 3) for v in values],  # Round for cleaner JSON
        "peaks": sorted(peaks, key=lambda x: x["value"], reverse=True)[:5]  # Top 5 peaks
    }
