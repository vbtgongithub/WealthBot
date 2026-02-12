'use client';

import { ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import { AuraAssistant } from '@/components/assistant/AuraAssistant';
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
  const user = {
    name: 'Alex Doe',
    plan: 'Pro Plan',
  };

  return (
    <div className="min-h-screen bg-background-primary flex">
      {/* Sidebar */}
      <Sidebar user={user} />

      {/* Main Content */}
      <main className="flex-1 ml-64 mr-80">
        <div className="p-8">{children}</div>
      </main>

      {/* AI Assistant */}
      <div className="fixed right-0 top-0 h-full">
        <AuraAssistant
          messages={assistantMessages}
          onSendMessage={onAssistantMessage}
          placeholder={assistantPlaceholder}
        />
      </div>
    </div>
  );
}
