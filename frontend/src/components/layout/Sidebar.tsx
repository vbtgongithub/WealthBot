'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Gauge,
  ArrowLeftRight,
  BarChart3,
  Settings,
  LogOut,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface NavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
}

const navItems: NavItem[] = [
  { label: 'Home', href: '/', icon: Gauge },
  { label: 'Transactions', href: '/transactions', icon: ArrowLeftRight },
  { label: 'Analytics', href: '/budgets', icon: BarChart3 },
  { label: 'Settings', href: '/investments', icon: Settings },
];

interface SidebarProps {
  user?: {
    name: string;
    plan: string;
    avatar?: string;
  };
}

export function Sidebar({ user }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-background-secondary border-r border-border-primary flex flex-col z-50">
      {/* Logo */}
      <div className="p-6">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-accent-green flex items-center justify-center">
            <span className="text-white font-bold text-sm">W</span>
          </div>
          <span className="text-xl font-semibold text-text-primary">WealthBot</span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-2">
        <ul className="space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;

            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    'flex items-center gap-3 px-4 py-3 rounded-lg transition-colors duration-200',
                    isActive
                      ? 'bg-accent-green/10 text-accent-green'
                      : 'text-text-secondary hover:bg-background-hover hover:text-text-primary'
                  )}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* User Section */}
      <div className="p-4 border-t border-border-primary">
        <div className="flex items-center gap-3 p-2">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-accent-green to-accent-green-dark flex items-center justify-center">
            {user?.avatar ? (
              <img
                src={user.avatar}
                alt={user?.name || 'User'}
                className="w-full h-full rounded-full object-cover"
              />
            ) : (
              <span className="text-white font-semibold">
                {user?.name?.charAt(0) || 'A'}
              </span>
            )}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-text-primary truncate">
              {user?.name || 'Arjun'}
            </p>
            <p className="text-xs text-text-muted flex items-center gap-1">
              <Settings className="w-3 h-3" />
              {user?.plan || 'Student'}
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}
