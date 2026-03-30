'use client';

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { formatCurrency } from '@/lib/utils';

interface BudgetDonutChartProps {
  data: Array<{
    name: string;
    value: number;
    color: string;
  }>;
  className?: string;
}

function DonutTooltip({ active, payload }: any) {
  if (active && payload && payload.length) {
    const item = payload[0].payload;
    const total = payload[0].payload._total as number;
    const percentage = ((item.value / total) * 100).toFixed(1);
    return (
      <div className="bg-background-card/80 backdrop-blur-[12px] border border-border-primary rounded-lg px-3 py-2 shadow-lg">
        <p className="text-sm font-medium text-text-primary">{item.name}</p>
        <p className="text-xs text-text-muted">
          {formatCurrency(item.value)} ({percentage}%)
        </p>
      </div>
    );
  }
  return null;
}

export function BudgetDonutChart({ data, className }: BudgetDonutChartProps) {
  const total = data.reduce((sum, item) => sum + item.value, 0);
  const dataWithTotal = data.map((d) => ({ ...d, _total: total }));

  return (
    <div className={className}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={dataWithTotal}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={2}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip content={<DonutTooltip />} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
