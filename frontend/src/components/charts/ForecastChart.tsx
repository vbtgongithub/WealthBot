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

interface ForecastChartProps {
  data: Array<{
    date: string;
    projected: number;
    actual?: number;
  }>;
  className?: string;
}

export function ForecastChart({ data, className }: ForecastChartProps) {
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background-card border border-border-primary rounded-lg p-3 shadow-lg">
          <p className="text-xs text-text-muted mb-1">{formatDate(label, 'medium')}</p>
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center gap-2">
              <div
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-sm text-text-secondary capitalize">
                {entry.dataKey}:
              </span>
              <span className="text-sm font-medium text-text-primary">
                {formatCurrency(entry.value)}
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className={className}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
        >
          <defs>
            <linearGradient id="projectedGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="actualGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
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
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="projected"
            stroke="#22c55e"
            strokeWidth={2}
            fill="url(#projectedGradient)"
          />
          <Area
            type="monotone"
            dataKey="actual"
            stroke="#3b82f6"
            strokeWidth={2}
            fill="url(#actualGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
