'use client';

import { cn } from '@/lib/utils';
import { Check, Clock, AlertCircle } from 'lucide-react';

type TransactionStatus = 'cleared' | 'pending' | 'failed';

interface StatusBadgeProps {
  status: TransactionStatus;
  size?: 'sm' | 'md';
  className?: string;
}

const statusConfig: Record<
  TransactionStatus,
  {
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    color: string;
    bgColor: string;
  }
> = {
  cleared: {
    label: 'Cleared',
    icon: Check,
    color: '#22c55e',
    bgColor: 'rgba(34, 197, 94, 0.1)',
  },
  pending: {
    label: 'Pending',
    icon: Clock,
    color: '#f59e0b',
    bgColor: 'rgba(245, 158, 11, 0.1)',
  },
  failed: {
    label: 'Failed',
    icon: AlertCircle,
    color: '#ef4444',
    bgColor: 'rgba(239, 68, 68, 0.1)',
  },
};

export function StatusBadge({ status, size = 'md', className }: StatusBadgeProps) {
  const config = statusConfig[status];
  const Icon = config.icon;

  const sizeClasses = {
    sm: 'text-xs gap-1',
    md: 'text-sm gap-1.5',
  };

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center font-medium',
        sizeClasses[size],
        className
      )}
      style={{ color: config.color }}
    >
      <Icon className={iconSizes[size]} />
      {config.label}
    </span>
  );
}
