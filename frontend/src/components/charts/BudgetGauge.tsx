'use client';

import { cn } from '@/lib/utils';

interface BudgetGaugeProps {
  spent: number;
  total: number;
  remaining: number;
  className?: string;
}

export function BudgetGauge({ spent, total, remaining, className }: BudgetGaugeProps) {
  const percentage = Math.min(Math.round((spent / total) * 100), 100);
  const rotation = (percentage / 100) * 180 - 90; // -90 to 90 degrees

  // Determine color based on percentage
  const getColor = () => {
    if (percentage >= 90) return '#ef4444';
    if (percentage >= 75) return '#f59e0b';
    return '#22c55e';
  };

  return (
    <div className={cn('flex flex-col items-center', className)}>
      {/* Gauge */}
      <div className="relative w-40 h-20 overflow-hidden">
        {/* Background arc */}
        <div
          className="absolute inset-0 rounded-t-full border-8 border-background-secondary"
          style={{ borderBottomWidth: 0 }}
        />
        
        {/* Colored arc */}
        <div
          className="absolute inset-0 rounded-t-full border-8 origin-bottom transition-all duration-700"
          style={{
            borderColor: getColor(),
            borderBottomWidth: 0,
            clipPath: `polygon(0 100%, 0 0, ${percentage}% 0, ${percentage}% 100%)`,
          }}
        />

        {/* Needle */}
        <div
          className="absolute bottom-0 left-1/2 w-1 h-16 bg-text-primary rounded-full origin-bottom transition-transform duration-700"
          style={{ transform: `translateX(-50%) rotate(${rotation}deg)` }}
        />

        {/* Center point */}
        <div className="absolute bottom-0 left-1/2 w-4 h-4 bg-background-card border-2 border-text-primary rounded-full transform -translate-x-1/2 translate-y-1/2" />
      </div>

      {/* Labels */}
      <div className="text-center mt-4">
        <div className="text-sm text-text-muted">Spent</div>
        <div className="text-lg font-bold text-text-primary">
          ${spent.toLocaleString()}{' '}
          <span className="text-text-muted font-normal">of ${total.toLocaleString()}</span>
          <span className="text-accent-green ml-1">({percentage}%)</span>
        </div>
        <div className="text-sm text-text-muted mt-1">
          Remaining ${remaining.toLocaleString()}
        </div>
      </div>
    </div>
  );
}
