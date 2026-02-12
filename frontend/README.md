# Aura.fi Frontend

A modern, production-ready financial dashboard built with Next.js 14, TypeScript, and Tailwind CSS.

## Features

- **Dashboard**: Real-time net worth tracking, spending analytics, and financial forecasting
- **Transactions**: Full transaction history with filtering, search, and categorization
- **Budgets**: Visual budget tracking with progress indicators and category breakdown
- **Investments**: Portfolio performance charts, holdings overview, and market data
- **AI Assistant**: Integrated AI-powered financial assistant (Aura)

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create environment file:
   ```bash
   cp .env.local.example .env.local
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Dashboard (home)
│   │   ├── transactions/       # Transactions page
│   │   ├── budgets/            # Budgets page
│   │   └── investments/        # Investments page
│   ├── components/
│   │   ├── assistant/          # AI Assistant component
│   │   ├── charts/             # Chart components (Recharts)
│   │   ├── layout/             # Layout components (Sidebar, Header)
│   │   ├── providers/          # React context providers
│   │   └── ui/                 # Reusable UI components
│   ├── hooks/                  # Custom React hooks
│   ├── lib/                    # Utility functions & API client
│   ├── stores/                 # Zustand state stores
│   ├── styles/                 # Global CSS & Tailwind config
│   └── types/                  # TypeScript type definitions
├── public/                     # Static assets
├── tailwind.config.js          # Tailwind configuration
├── tsconfig.json               # TypeScript configuration
└── package.json
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## Design System

### Colors

The app uses a dark theme with the following color palette:

- **Background**: `#0a0f1a` (primary), `#0f1629` (secondary), `#141b2d` (card)
- **Accent**: `#22c55e` (green), `#4ade80` (light green)
- **Text**: `#ffffff` (primary), `#94a3b8` (secondary), `#64748b` (muted)

### Components

All components are built with accessibility and responsiveness in mind:

- `MetricCard` - Display key metrics with optional trend indicators
- `ProgressBar` - Visual progress indicator with customizable colors
- `CategoryBadge` - Transaction category labels with icons
- `StatusBadge` - Transaction status indicators
- `TimeRangeSelector` - Chart time range filter
- `AuraAssistant` - AI assistant chat interface

## API Integration

The frontend is designed to work with the WealthBot FastAPI backend. Configure the API URL in `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Deployment

### Vercel (Recommended)

```bash
npm run build
vercel deploy
```

### Docker

```bash
docker build -t aura-fi-frontend .
docker run -p 3000:3000 aura-fi-frontend
```

## License

MIT
