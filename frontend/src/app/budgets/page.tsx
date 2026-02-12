'use client';

import { useState } from 'react';
import { MainLayout, Header } from '@/components/layout';
import { AlertTriangle, TrendingUp, TrendingDown } from 'lucide-react';
import {
  SUBSCRIPTIONS,
  SPENDING_STATS,
  VELOCITY_THIS_MONTH,
  VELOCITY_LAST_MONTH,
} from '@/constants/data';
import { formatCurrency } from '@/lib/utils';
import type { AssistantMessage } from '@/types';
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

// Merge velocity data for the chart
const velocityData = VELOCITY_THIS_MONTH.map((item, i) => ({
  week: item.week,
  thisMonth: item.amount,
  lastMonth: VELOCITY_LAST_MONTH[i]?.amount ?? 0,
}));

// Find the biggest "unnecessary" spend (highest thisMonth that increased vs lastMonth)
const ouchCategory = [...SPENDING_STATS]
  .filter((s) => s.thisMonth > s.lastMonth)
  .sort((a, b) => b.thisMonth - a.thisMonth)[0];

const initialMessages: AssistantMessage[] = [
  {
    id: '1',
    type: 'alert',
    content: `Your ${ouchCategory?.category} spending jumped ${Math.round(
      ((ouchCategory?.thisMonth - ouchCategory?.lastMonth) / ouchCategory?.lastMonth) * 100
    )}% this month. Want me to find where the money went?`,
    timestamp: new Date().toISOString(),
    actions: [{ label: 'Show breakdown', variant: 'primary' }],
  },
];

export default function AnalyticsPage() {
  const [messages, setMessages] = useState<AssistantMessage[]>(initialMessages);

  const handleSendMessage = (message: string) => {
    const newMessage: AssistantMessage = {
      id: Date.now().toString(),
      type: 'question',
      content: message,
      timestamp: new Date().toISOString(),
    };
    setMessages([...messages, newMessage]);
  };

  const totalSubs = SUBSCRIPTIONS.reduce((sum, s) => sum + s.amount, 0);

  return (
    <MainLayout
      assistantMessages={messages}
      onAssistantMessage={handleSendMessage}
      assistantPlaceholder="Ask about spending patterns..."
    >
      <Header
        title="Leakage Hunter"
        subtitle="Find where your money silently disappears"
      />

      {/* ------------------------------------------------------------------ */}
      {/* Subscription Radar                                                 */}
      {/* Highlights recurring payments so they don't go unnoticed           */}
      {/* ------------------------------------------------------------------ */}
      <div className="card mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-text-primary">
              📡 Subscription Radar
            </h3>
            <p className="text-xs text-text-muted mt-0.5">
              {formatCurrency(totalSubs)}/mo across {SUBSCRIPTIONS.length} services
            </p>
          </div>
          <span className="text-xs text-status-warning bg-status-warning/10 px-2 py-1 rounded-full">
            {SUBSCRIPTIONS.filter((s) => parseInt(s.nextDue) <= 5).length} due soon
          </span>
        </div>

        <div className="space-y-3">
          {SUBSCRIPTIONS.map((sub) => {
            const isDueSoon = parseInt(sub.nextDue) <= 5;
            return (
              <div
                key={sub.id}
                className="flex items-center gap-3 p-3 rounded-lg bg-background-secondary border border-border-primary"
              >
                <span className="text-xl">{sub.icon}</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-text-primary">{sub.name}</p>
                  <p className="text-xs text-text-muted">
                    {formatCurrency(sub.amount)} · {sub.frequency}
                  </p>
                </div>
                <span
                  className={`text-xs px-2 py-1 rounded-full font-medium ${
                    isDueSoon
                      ? 'bg-status-warning/15 text-status-warning'
                      : 'bg-background-hover text-text-muted'
                  }`}
                >
                  Due in {sub.nextDue}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* Spending Velocity — line chart comparing this vs last month        */}
      {/* ------------------------------------------------------------------ */}
      <div className="card mb-6">
        <div className="mb-4">
          <h3 className="text-sm font-semibold text-text-primary">
            ⚡ Spending Velocity
          </h3>
          <p className="text-xs text-text-muted mt-0.5">
            This month vs last month (cumulative weekly spend)
          </p>
        </div>

        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={velocityData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="week" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#141b2d',
                  border: '1px solid #1e293b',
                  borderRadius: '8px',
                  color: '#fff',
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
        </div>
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* The "Ouch" Metric — biggest unnecessary expense                    */}
      {/* ------------------------------------------------------------------ */}
      {ouchCategory && (
        <div className="card border-status-warning/30 mb-6">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-xl bg-status-warning/10 text-2xl">
              <AlertTriangle className="w-6 h-6 text-status-warning" />
            </div>
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-status-warning mb-1">
                💸 The &quot;Ouch&quot; of the Month
              </h3>
              <p className="text-lg font-bold text-text-primary">
                You spent {formatCurrency(ouchCategory.thisMonth)} on {ouchCategory.category}
              </p>
              <p className="text-sm text-text-muted mt-1">
                That&apos;s{' '}
                <span className="text-status-warning font-semibold">
                  {formatCurrency(ouchCategory.thisMonth - ouchCategory.lastMonth)} more
                </span>{' '}
                than last month ({formatCurrency(ouchCategory.lastMonth)})
              </p>
            </div>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------------ */}
      {/* Category Breakdown — spend comparison cards                        */}
      {/* ------------------------------------------------------------------ */}
      <div className="card">
        <h3 className="text-sm font-semibold text-text-primary mb-4">
          Category Breakdown
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {SPENDING_STATS.map((stat) => {
            const diff = stat.thisMonth - stat.lastMonth;
            const isUp = diff > 0;
            return (
              <div
                key={stat.category}
                className="flex items-center gap-3 p-3 rounded-lg bg-background-secondary border border-border-primary"
              >
                <span className="text-xl">{stat.icon}</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-text-primary">{stat.category}</p>
                  <p className="text-xs text-text-muted">
                    {formatCurrency(stat.thisMonth)} this month
                  </p>
                </div>
                <div className={`flex items-center gap-1 text-xs font-medium ${isUp ? 'text-status-error' : 'text-accent-green'}`}>
                  {isUp ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
                  {isUp ? '+' : ''}{formatCurrency(Math.abs(diff))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </MainLayout>
  );
}
