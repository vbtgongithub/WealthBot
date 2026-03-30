'use client';

import { Component, type ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    if (typeof window !== 'undefined' && process.env.NEXT_PUBLIC_SENTRY_ENABLED === 'true') {
      import('@sentry/react').then((Sentry) => {
        Sentry.captureException(error, { extra: { componentStack: errorInfo.componentStack } });
      }).catch(() => {
        console.error('ErrorBoundary caught:', error);
      });
    } else {
      console.error('ErrorBoundary caught:', error);
    }
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;

      return (
        <div className="flex items-center justify-center min-h-[60vh] p-6">
          <div className="card max-w-md text-center space-y-4">
            <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center mx-auto">
              <AlertTriangle className="w-6 h-6 text-red-400" />
            </div>
            <h2 className="text-lg font-semibold text-text-primary">Something went wrong</h2>
            <p className="text-sm text-text-muted">
              {this.state.error?.message ?? 'An unexpected error occurred.'}
            </p>
            <button onClick={this.handleReset} className="btn-primary inline-flex items-center gap-2">
              <RefreshCw className="w-4 h-4" /> Try Again
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
