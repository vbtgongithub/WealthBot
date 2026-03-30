'use client';

import { cn } from '@/lib/utils';

interface TimeRangeSelectorProps {
  ranges: Array<{ label: string; value: string }>;
  activeRange: string;
  onChange: (range: string) => void;
  className?: string;
}

export function TimeRangeSelector({
  ranges,
  activeRange,
  onChange,
  className,
}: TimeRangeSelectorProps) {
  return (
    <div
      className={cn(
        'inline-flex items-center bg-background-secondary rounded-lg p-1',
        className
      )}
    >
      {ranges.map((range) => (
        <button
          key={range.value}
          onClick={() => onChange(range.value)}
          className={cn(
            'px-3 py-1.5 text-sm font-medium rounded-md transition-colors duration-200',
            activeRange === range.value
              ? 'bg-brand-primary/10 text-brand-primary'
              : 'text-text-muted hover:text-text-secondary'
          )}
        >
          {range.label}
        </button>
      ))}
    </div>
  );
}
