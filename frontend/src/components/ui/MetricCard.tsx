'use client';

import { cn, formatCurrency, formatPercent } from '@/lib/utils';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface MetricCardProps {
  label: string;
  value: number;
  format?: 'currency' | 'percent' | 'number';
  change?: number;
  changeLabel?: string;
  icon?: React.ReactNode;
  className?: string;
}

export function MetricCard({
  label,
  value,
  format = 'currency',
  change,
  changeLabel,
  icon,
  className,
}: MetricCardProps) {
  const formattedValue = (() => {
    switch (format) {
      case 'currency':
        return formatCurrency(value);
      case 'percent':
        return `${value}%`;
      case 'number':
        return value.toLocaleString();
      default:
        return value.toString();
    }
  })();

  const isPositive = change !== undefined && change > 0;
  const isNegative = change !== undefined && change < 0;
  const isNeutral = change === undefined || change === 0;

  const TrendIcon = isPositive ? TrendingUp : isNegative ? TrendingDown : Minus;

  return (
    <div className={cn('card', className)}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-text-secondary mb-1">{label}</p>
          <p className="text-2xl font-bold text-text-primary">{formattedValue}</p>
        </div>
        {icon && (
          <div className="p-2 rounded-lg bg-accent-green/10 text-accent-green">
            {icon}
          </div>
        )}
      </div>

      {change !== undefined && (
        <div className="flex items-center gap-1 mt-2">
          <div
            className={cn(
              'flex items-center gap-1 text-sm font-medium',
              isPositive && 'text-status-success',
              isNegative && 'text-status-error',
              isNeutral && 'text-text-muted'
            )}
          >
            <TrendIcon className="w-4 h-4" />
            <span>{formatPercent(Math.abs(change))}</span>
          </div>
          {changeLabel && (
            <span className="text-xs text-text-muted ml-1">{changeLabel}</span>
          )}
        </div>
      )}
    </div>
  );
}
