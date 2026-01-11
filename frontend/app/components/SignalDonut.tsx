import { SignalBreakdown, SignalBreakdownItem } from '../types';

const signalNames: { [key: string]: string } = {
  concept_spike: 'Concept Density Spikes',
  grounding_gap: 'Missing Concept Grounding',
  tmb: 'Unsupported Claims Detection',
  structure_order: 'Discourse Structure Violations',
  ramble_ratio: 'Rambling Ratio'
};

export function SignalDonut({ data }: { data: SignalBreakdown }) {
  const total = data.total_weight;
  const items = data.items.sort((a: SignalBreakdownItem, b: SignalBreakdownItem) => b.weight - a.weight);

  return (
    <div className="flex items-start gap-8">
      <div className="relative w-64 h-64">
        <svg viewBox="0 0 100 100" className="transform -rotate-90">
          {items.map((item: SignalBreakdownItem, i: number) => {
            const startAngle = items
              .slice(0, i)
              .reduce((sum: number, it: SignalBreakdownItem) => sum + (it.percent / 100) * 360, 0);
            const angle = (item.percent / 100) * 360;
            const x1 = 50 + 40 * Math.cos((startAngle * Math.PI) / 180);
            const y1 = 50 + 40 * Math.sin((startAngle * Math.PI) / 180);
            const x2 = 50 + 40 * Math.cos(((startAngle + angle) * Math.PI) / 180);
            const y2 = 50 + 40 * Math.sin(((startAngle + angle) * Math.PI) / 180);
            const largeArc = angle > 180 ? 1 : 0;

            return (
              <path
                key={item.signal}
                d={`M 50 50 L ${x1} ${y1} A 40 40 0 ${largeArc} 1 ${x2} ${y2} Z`}
                fill={getSignalColor(item.signal)}
                className="transition-opacity hover:opacity-80"
              />
            );
          })}
        </svg>
      </div>

      <div className="flex flex-col gap-2 py-2">
        {items.map((item: SignalBreakdownItem) => (
          <div key={item.signal} className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full`} style={{ backgroundColor: getSignalColor(item.signal) }} />
            <div className="flex-1">
              <div className="text-sm font-medium text-white">{signalNames[item.signal]}</div>
              <div className="text-xs text-gray-400">
                {item.percent.toFixed(1)}% ({item.segments} segments)
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function getSignalColor(signal: string): string {
  switch (signal) {
    case 'concept_spike':
      return '#FED7D7'; // pastel red
    case 'grounding_gap':
      return '#BFDBFE'; // pastel blue
    case 'tmb':
      return '#C6F6D5'; // pastel green
    case 'structure_order':
      return '#FEF3C7'; // pastel yellow
    case 'ramble_ratio':
      return '#FBCFE8'; // pastel pink
    default:
      return '#E5E7EB'; // light gray
  }
}
