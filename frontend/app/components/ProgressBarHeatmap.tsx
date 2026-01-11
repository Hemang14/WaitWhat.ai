import { TimelineHeatmap as TimelineHeatmapType } from '../types';

interface Props {
  data: TimelineHeatmapType;
  currentTime?: number;
}

export function ProgressBarHeatmap({ data, currentTime = 0 }: Props) {
  const { values } = data;

  return (
    <div className="absolute inset-0 flex gap-0 overflow-hidden pointer-events-none z-0">
      {values.map((value, i) => (
        <div
          key={i}
          className="flex-1"
          style={{
            backgroundColor: `rgba(239, 68, 68, ${value * 0.5})`,
            minWidth: '2px',
          }}
        />
      ))}
    </div>
  );
}
