export type SignalBreakdownItem = {
  signal: string;
  weight: number;
  percent: number;
  segments: number;
};

export type SignalBreakdown = {
  mode: string;
  total_weight: number;
  items: SignalBreakdownItem[];
};

export type TimelineHeatmapPeak = {
  t: number;
  value: number;
  segment_id: number;
};

export type TimelineHeatmap = {
  bin_size_sec: number;
  duration_sec: number;
  values: number[];
  peaks: TimelineHeatmapPeak[];
};
