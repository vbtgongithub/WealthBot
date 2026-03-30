'use client';

import { ReactNode } from 'react';
import { Menu, Bot } from 'lucide-react';
import { Sidebar } from './Sidebar';
import { AuraAssistant } from '@/components/assistant/AuraAssistant';
import { useCurrentUser } from '@/hooks/useApi';
import { useUserStore } from '@/stores/userStore';
import type { AssistantMessage } from '@/types';

interface MainLayoutProps {
  children: ReactNode;
  assistantMessages?: AssistantMessage[];
  onAssistantMessage?: (message: string) => void;
  assistantPlaceholder?: string;
}

export function MainLayout({
  children,
  assistantMessages = [],
  onAssistantMessage,
  assistantPlaceholder,
}: MainLayoutProps) {
  const { data: currentUser } = useCurrentUser();

  const user = currentUser
    ? {
        name: [currentUser.first_name, currentUser.last_name].filter(Boolean).join(' ') || currentUser.email,
        plan: 'Student',
      }
    : undefined;

  const { toggleSidebar, assistantOpen, setAssistantOpen } = useUserStore();

  return (
    <div className="min-h-screen bg-background-primary flex">
      {/* Skip to content link */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:px-4 focus:py-2 focus:bg-brand-primary focus:text-white focus:rounded-lg"
      >
        Skip to content
      </a>

      {/* Sidebar */}
      <Sidebar user={user} />

      {/* Main Content */}
      <main id="main-content" className="flex-1 lg:ml-64 xl:mr-80">
        {/* Mobile top bar */}
        <div className="sticky top-0 z-30 flex items-center justify-between px-4 py-3 bg-background-primary/80 backdrop-blur-sm border-b border-border-primary lg:hidden">
          <button
            onClick={toggleSidebar}
            aria-label="Toggle sidebar navigation"
            className="p-2 rounded-lg hover:bg-background-hover text-text-secondary"
          >
            <Menu className="w-5 h-5" />
          </button>
          <span className="text-sm font-semibold text-text-primary">WealthBot</span>
          <button
            onClick={() => setAssistantOpen(!assistantOpen)}
            aria-label="Toggle Aura assistant"
            aria-expanded={assistantOpen}
            className="p-2 rounded-lg hover:bg-background-hover text-text-secondary xl:hidden"
          >
            <Bot className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4 sm:p-6 lg:p-8">{children}</div>
      </main>

      {/* AI Assistant — always visible on xl, togglable on smaller screens */}
      <div className={`fixed right-0 top-0 h-full z-40 transition-transform duration-200 ${assistantOpen ? 'translate-x-0' : 'translate-x-[105%] xl:translate-x-0'}`}>
        <AuraAssistant
          messages={assistantMessages}
          onSendMessage={onAssistantMessage}
          placeholder={assistantPlaceholder}
          onClose={() => setAssistantOpen(false)}
        />
      </div>

      {/* Backdrop for assistant on mobile */}
      {assistantOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 xl:hidden"
          onClick={() => setAssistantOpen(false)}
        />
      )}
    </div>
  );
}
