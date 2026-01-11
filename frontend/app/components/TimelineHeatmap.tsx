import { TimelineHeatmap as TimelineHeatmapType } from '../types';

interface Props {
  data: TimelineHeatmapType;
  onSeek?: (seconds: number) => void;
  currentTime?: number;
}

export function TimelineHeatmap({ data, onSeek, currentTime = 0 }: Props) {
  const { values, duration_sec, bin_size_sec } = data;

  return (
    <div className="absolute inset-0 flex gap-px overflow-hidden pointer-events-none z-0">
      {values.map((value, i) => {
        return (
          <div
            key={i}
            className="flex-1"
            style={{
              backgroundColor: `rgba(239, 68, 68, ${value * 0.5})`, // red-500 with reduced opacity
              minWidth: '4px',
            }}
          />
        );
      })}
    </div>
  );
}

function formatTime(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) return '0:00';
  const s = Math.floor(seconds);
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`;
  return `${m}:${String(sec).padStart(2, '0')}`;
}
