import type { Metadata, Viewport } from 'next';
import '@/styles/globals.css';

export const metadata: Metadata = {
  title: 'WealthBot - Predictive Personal Finance for Students',
  description: 'AI-powered Safe-to-Spend predictions, smart transaction categorization, and spending analytics built for Indian students.',
  keywords: ['finance', 'safe-to-spend', 'students', 'AI', 'personal finance', 'India', 'UPI'],
  authors: [{ name: 'WealthBot Team' }],
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#0a0f1a',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-background-primary antialiased">
        {children}
      </body>
    </html>
  );
}
