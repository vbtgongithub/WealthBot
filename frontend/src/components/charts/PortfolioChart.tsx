'use client';

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import { formatCurrency, formatDate } from '@/lib/utils';

interface PortfolioChartProps {
  data: Array<{
    date: string;
    value: number;
  }>;
  className?: string;
}

function PortfolioTooltip({ active, payload, label }: any) {
  if (active && payload && payload.length) {
    return (
      <div className="bg-background-card/80 backdrop-blur-[12px] border border-border-primary rounded-lg px-3 py-2 shadow-lg">
        <p className="text-xs text-text-muted">
          {formatDate(label, 'medium')}
        </p>
        <p className="text-lg font-semibold text-accent-green">
          {formatCurrency(payload[0].value)}
        </p>
      </div>
    );
  }
  return null;
}

export function PortfolioChart({ data, className }: PortfolioChartProps) {
  return (
    <div className={className}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
        >
          <defs>
            <linearGradient id="portfolioGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#22c55e" stopOpacity={0.4} />
              <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#1e293b"
            vertical={false}
          />
          <XAxis
            dataKey="date"
            tickFormatter={(value) => formatDate(value, 'short')}
            tick={{ fill: '#64748b', fontSize: 12 }}
            axisLine={{ stroke: '#1e293b' }}
            tickLine={false}
          />
          <YAxis
            tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
            tick={{ fill: '#64748b', fontSize: 12 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<PortfolioTooltip />} />
          <Area
            type="monotone"
            dataKey="value"
            stroke="#22c55e"
            strokeWidth={2}
            fill="url(#portfolioGradient)"
            dot={false}
            activeDot={{
              r: 6,
              fill: '#22c55e',
              stroke: '#0f1629',
              strokeWidth: 2,
            }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
