'use client';

import { cn, getCategoryColor, getCategoryLabel } from '@/lib/utils';
import {
  Utensils,
  DollarSign,
  ShoppingBag,
  Car,
  Coffee,
  ShoppingCart,
  Music,
  MoreHorizontal,
} from 'lucide-react';
import type { TransactionCategory } from '@/types';

interface CategoryBadgeProps {
  category: TransactionCategory;
  showIcon?: boolean;
  size?: 'sm' | 'md';
  className?: string;
}

const categoryIcons: Record<TransactionCategory, React.ComponentType<{ className?: string }>> = {
  'Food': Utensils,
  'Income': DollarSign,
  'Shopping': ShoppingBag,
  'Travel': Car,
  'Coffee': Coffee,
  'Groceries': ShoppingCart,
  'Entertainment': Music,
  'Other': MoreHorizontal,
};

export function CategoryBadge({
  category,
  showIcon = true,
  size = 'md',
  className,
}: CategoryBadgeProps) {
  const Icon = categoryIcons[category] || categoryIcons.Other;
  const color = getCategoryColor(category);
  const label = getCategoryLabel(category);

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs gap-1',
    md: 'px-3 py-1 text-sm gap-1.5',
  };

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full font-medium',
        sizeClasses[size],
        className
      )}
      style={{
        backgroundColor: `${color}20`,
        color: color,
      }}
    >
      {showIcon && <Icon className={iconSizes[size]} />}
      {label}
    </span>
  );
}
