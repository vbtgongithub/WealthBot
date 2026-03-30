'use client';

import { useMemo, useState } from 'react';
import { Send, MoreHorizontal, Bot, Loader2, X } from 'lucide-react';
import { useAIChat } from '@/hooks';
import { cn } from '@/lib/utils';
import type { AssistantMessage, AssistantAction } from '@/types';

interface AuraAssistantProps {
  messages: AssistantMessage[];
  onSendMessage?: (message: string) => void;
  onClose?: () => void;
  placeholder?: string;
  className?: string;
}

function MessageBubble({
  message,
  onAction,
}: {
  message: AssistantMessage;
  onAction?: (action: AssistantAction) => void;
}) {
  const getTypeStyles = (type: AssistantMessage['type']) => {
    switch (type) {
      case 'alert':
        return 'border-l-2 border-l-status-warning';
      case 'suggestion':
        return 'border-l-2 border-l-brand-primary';
      case 'question':
        return 'border-l-2 border-l-status-info';
      default:
        return '';
    }
  };

  return (
    <div className="flex gap-3 animate-slide-up">
      <div className="w-8 h-8 rounded-full bg-brand-primary/20 flex items-center justify-center flex-shrink-0">
        <Bot className="w-4 h-4 text-brand-primary" />
      </div>
      <div className="flex-1 space-y-3">
        <div
          className={cn(
            'bg-background-secondary rounded-lg p-3 text-sm text-text-secondary',
            getTypeStyles(message.type)
          )}
        >
          {message.content}
          
          {/* Highlight data if present */}
          {message.data?.highlight ? (
            <div className="mt-2 p-2 bg-background-hover rounded-md">
              {message.data.icon ? (
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-semantic-success">{String(message.data.icon)}</span>
                </div>
              ) : null}
              <p className="text-xs text-text-muted">{String(message.data.label)}</p>
              <p className="text-lg font-semibold text-semantic-success">
                {String(message.data.value)}
              </p>
            </div>
          ) : null}
        </div>

        {/* Action Buttons */}
        {message.actions && message.actions.length > 0 && (
          <div className="flex gap-2">
            {message.actions.map((action, index) => (
              <button
                key={index}
                onClick={() => onAction?.(action)}
                className={cn(
                  'px-4 py-2 text-sm font-medium rounded-lg transition-colors duration-200',
                  action.variant === 'primary'
                    ? 'bg-brand-primary hover:bg-brand-primary-dark text-white'
                    : 'bg-background-hover hover:bg-border-primary text-text-primary'
                )}
              >
                {action.label}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export function AuraAssistant({
  messages,
  onSendMessage,
  onClose,
  placeholder = 'Ask Aura about your finances...',
  className,
}: AuraAssistantProps) {
  const [inputValue, setInputValue] = useState('');
  const [localReplies, setLocalReplies] = useState<AssistantMessage[]>([]);
  const aiChat = useAIChat();

  const combinedMessages = useMemo(
    () => [...messages, ...localReplies],
    [localReplies, messages]
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const prompt = inputValue.trim();
    if (!prompt) return;

    onSendMessage?.(prompt);
    setInputValue('');

    try {
      const result = await aiChat.mutateAsync(prompt);
      setLocalReplies((prev) => [
        ...prev,
        {
          id: `ai-${Date.now()}`,
          type: 'suggestion',
          content: result.reply,
          timestamp: new Date().toISOString(),
          actions: result.suggestions.slice(0, 2).map((item) => ({
            label: item,
            variant: 'secondary',
          })),
          data: {
            label: 'Confidence',
            value: `${Math.round(result.confidence * 100)}%`,
            highlight: true,
          },
        },
      ]);
    } catch {
      setLocalReplies((prev) => [
        ...prev,
        {
          id: `ai-error-${Date.now()}`,
          type: 'alert',
          content: 'I could not process that right now. Please try again in a moment.',
          timestamp: new Date().toISOString(),
        },
      ]);
    }
  };

  const handleAction = (action: AssistantAction) => {
    action.onClick?.();
  };

  return (
    <aside
      className={cn(
        'w-80 max-w-[100vw] bg-background-secondary/90 backdrop-blur-xl border-l border-border-primary h-full flex flex-col',
        className
      )}
    >
      {/* Header */}
      <div className="p-4 border-b border-border-primary flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-brand-primary to-brand-primary-dark flex items-center justify-center">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-text-primary">Aura Assistant</h3>
            <div className="flex items-center gap-1">
              <span className="w-2 h-2 bg-brand-primary rounded-full animate-pulse" />
              <span className="text-xs text-text-muted">Active</span>
            </div>
          </div>
        </div>
        <button className="p-1 hover:bg-background-hover rounded-lg transition-colors">
          <MoreHorizontal className="w-5 h-5 text-text-muted" />
        </button>
        {onClose && (
          <button
            onClick={onClose}
            aria-label="Close assistant panel"
            className="p-1 hover:bg-background-hover rounded-lg transition-colors xl:hidden"
          >
            <X className="w-5 h-5 text-text-muted" />
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4" role="log" aria-label="Aura assistant messages">
        {combinedMessages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            onAction={handleAction}
          />
        ))}
      </div>

      {/* Input */}
      <form
        onSubmit={handleSubmit}
        className="p-4 border-t border-border-primary"
      >
        <div className="flex items-center gap-2 bg-background-card rounded-lg border border-border-primary px-3 py-2 focus-within:border-brand-primary transition-colors">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={placeholder}
            className="flex-1 bg-transparent text-sm text-text-primary placeholder-text-muted focus:outline-none"
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || aiChat.isPending}
            aria-label="Send message"
            className="p-2.5 min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg bg-brand-primary/20 text-brand-primary hover:bg-brand-primary/30 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {aiChat.isPending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </div>
      </form>
    </aside>
  );
}
