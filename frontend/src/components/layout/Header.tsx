'use client';

import { Bell, Plus } from 'lucide-react';
import { cn } from '@/lib/utils';

interface HeaderProps {
  title: string;
  subtitle?: string;
  userName?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export function Header({ title, subtitle, userName, action }: HeaderProps) {
  return (
    <header className="flex items-center justify-between mb-8">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">
          {title}
          {userName && <span>, {userName}</span>}
        </h1>
        {subtitle && (
          <p className="text-text-secondary mt-1">{subtitle}</p>
        )}
      </div>

      <div className="flex items-center gap-4">
        {/* Notification Bell */}
        <button className="relative p-2 rounded-lg bg-background-card hover:bg-background-hover border border-border-primary transition-colors">
          <Bell className="w-5 h-5 text-text-secondary" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-accent-green rounded-full" />
        </button>

        {/* Action Button */}
        {action && (
          <button
            onClick={action.onClick}
            className="btn-primary flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            {action.label}
          </button>
        )}
      </div>
    </header>
  );
}
