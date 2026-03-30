'use client';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { formatCurrency } from '@/lib/utils';

interface VelocityDataPoint {
  week: string;
  thisMonth: number;
  lastMonth: number;
}

interface VelocityChartProps {
  data: VelocityDataPoint[];
}

export default function VelocityChart({ data }: VelocityChartProps) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
        <XAxis dataKey="week" stroke="#64748b" fontSize={12} />
        <YAxis stroke="#64748b" fontSize={12} tickFormatter={(v: number) => `₹${(v / 1000).toFixed(0)}k`} />
        <Tooltip
          contentStyle={{
            backgroundColor: 'rgba(20, 27, 45, 0.8)',
            border: '1px solid #1e293b',
            borderRadius: '8px',
            color: '#fff',
            backdropFilter: 'blur(12px)',
          }}
          formatter={(value: number) => [formatCurrency(value), '']}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey="thisMonth"
          name="This Month"
          stroke="#22c55e"
          strokeWidth={2.5}
          dot={{ fill: '#22c55e', r: 4 }}
          activeDot={{ r: 6 }}
        />
        <Line
          type="monotone"
          dataKey="lastMonth"
          name="Last Month"
          stroke="#64748b"
          strokeWidth={2}
          strokeDasharray="5 5"
          dot={{ fill: '#64748b', r: 3 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
