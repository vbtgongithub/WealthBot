'use client';

import { useState, useMemo } from 'react';
import { MainLayout, Header } from '@/components/layout';
import { Search, Pencil, Check } from 'lucide-react';
import { useUserStore } from '@/stores/userStore';
import { CATEGORY_CONFIG } from '@/constants/data';
import { formatCurrency, groupByDate } from '@/lib/utils';
import type { AssistantMessage } from '@/types';

const initialMessages: AssistantMessage[] = [
  {
    id: '1',
    type: 'info',
    content: 'Tip: Tap the pencil icon to correct a category if the AI got it wrong — this helps improve predictions!',
    timestamp: new Date().toISOString(),
  },
];

export default function TransactionsPage() {
  const { transactions, updateTransactionCategory, devMode } = useUserStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [messages, setMessages] = useState<AssistantMessage[]>(initialMessages);

  // Filter by search query (merchant, category, or note)
  const filtered = useMemo(() => {
    if (!searchQuery.trim()) return transactions;
    const q = searchQuery.toLowerCase();
    return transactions.filter(
      (tx) =>
        tx.merchant.toLowerCase().includes(q) ||
        tx.category.toLowerCase().includes(q) ||
        tx.note?.toLowerCase().includes(q) ||
        tx.upiApp?.toLowerCase().includes(q)
    );
  }, [transactions, searchQuery]);

  // Group filtered transactions by Today / Yesterday / This Week
  const grouped = useMemo(() => groupByDate(filtered), [filtered]);

  const categoryKeys = Object.keys(CATEGORY_CONFIG);

  const handleSendMessage = (message: string) => {
    const newMessage: AssistantMessage = {
      id: Date.now().toString(),
      type: 'question',
      content: message,
      timestamp: new Date().toISOString(),
    };
    setMessages([...messages, newMessage]);
  };

  return (
    <MainLayout
      assistantMessages={messages}
      onAssistantMessage={handleSendMessage}
      assistantPlaceholder="Search 'Swiggy' or ask about spending..."
    >
      <Header title="Transactions" subtitle="Smart-grouped & AI-categorized" />

      {/* ------------------------------------------------------------------ */}
      {/* Search Bar                                                         */}
      {/* ------------------------------------------------------------------ */}
      <div className="relative mb-6">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-text-muted" />
        <input
          type="text"
          placeholder="Search 'Swiggy' or 'Last Week'..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-12 pr-4 py-3 bg-background-card border border-border-primary rounded-xl text-text-primary placeholder-text-muted focus:outline-none focus:border-accent-green transition-colors"
        />
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* Grouped Transaction List                                           */}
      {/* ------------------------------------------------------------------ */}
      {grouped.length === 0 && (
        <div className="card text-center py-12 text-text-muted">
          No transactions match your search.
        </div>
      )}

      {grouped.map((group) => (
        <div key={group.label} className="mb-6">
          {/* Group header */}
          <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3 px-1">
            {group.label}
          </h3>

          <div className="card p-0 divide-y divide-border-primary overflow-hidden">
            {group.items.map((tx) => {
              const config = CATEGORY_CONFIG[tx.category] || CATEGORY_CONFIG.Other;
              const isEditing = editingId === tx.id;

              return (
                <div
                  key={tx.id}
                  className="flex items-center gap-3 px-4 py-3 hover:bg-background-hover transition-colors"
                >
                  {/* Category icon */}
                  <span
                    className="w-10 h-10 rounded-full flex items-center justify-center text-base shrink-0"
                    style={{ backgroundColor: `${config.color}20` }}
                  >
                    {config.icon}
                  </span>

                  {/* Merchant + meta */}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-text-primary truncate">
                      {tx.merchant}
                    </p>
                    <div className="flex items-center gap-2 mt-0.5">
                      {/* Category pill */}
                      {isEditing ? (
                        <div className="flex gap-1 flex-wrap">
                          {categoryKeys.map((cat) => (
                            <button
                              key={cat}
                              onClick={() => {
                                updateTransactionCategory(tx.id, cat);
                                setEditingId(null);
                              }}
                              className="px-2 py-0.5 text-[10px] rounded-full border border-border-secondary text-text-secondary hover:bg-accent-green/20 hover:text-accent-green transition-colors"
                            >
                              #{cat}
                            </button>
                          ))}
                          <button
                            onClick={() => setEditingId(null)}
                            className="px-1.5 py-0.5 text-[10px] text-text-muted"
                          >
                            <Check className="w-3 h-3" />
                          </button>
                        </div>
                      ) : (
                        <span
                          className="px-2 py-0.5 text-[10px] rounded-full font-medium"
                          style={{
                            backgroundColor: `${config.color}20`,
                            color: config.color,
                          }}
                        >
                          #{tx.category}
                        </span>
                      )}

                      {tx.upiApp && (
                        <span className="text-[10px] text-text-muted">
                          via {tx.upiApp}
                        </span>
                      )}

                      {/* ML confidence badge (dev mode only) */}
                      {devMode && tx.aiConfidence && (
                        <span className="text-[10px] text-text-muted bg-background-secondary px-1.5 py-0.5 rounded">
                          {(tx.aiConfidence * 100).toFixed(0)}% conf
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Amount */}
                  <span
                    className={`text-sm font-semibold shrink-0 ${
                      tx.type === 'credit' ? 'text-accent-green' : 'text-text-primary'
                    }`}
                  >
                    {tx.type === 'credit' ? '+' : '-'}
                    {formatCurrency(tx.amount)}
                  </span>

                  {/* Edit pencil — lets user correct AI categorization */}
                  <button
                    onClick={() => setEditingId(isEditing ? null : tx.id)}
                    className="p-1.5 rounded-lg hover:bg-background-hover text-text-muted hover:text-accent-green transition-colors shrink-0"
                    title="Edit category"
                  >
                    <Pencil className="w-3.5 h-3.5" />
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </MainLayout>
  );
}
