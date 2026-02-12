/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Aura.fi Dark Theme
        background: {
          primary: '#0a0f1a',
          secondary: '#0f1629',
          card: '#141b2d',
          hover: '#1a2338',
        },
        accent: {
          green: '#22c55e',
          'green-dark': '#16a34a',
          'green-light': '#4ade80',
        },
        text: {
          primary: '#ffffff',
          secondary: '#94a3b8',
          muted: '#64748b',
        },
        border: {
          primary: '#1e293b',
          secondary: '#334155',
        },
        status: {
          success: '#22c55e',
          warning: '#f59e0b',
          error: '#ef4444',
          info: '#3b82f6',
        },
        category: {
          food: '#f59e0b',
          income: '#22c55e',
          shopping: '#ec4899',
          transport: '#22c55e',
          utilities: '#f97316',
          housing: '#ef4444',
          entertainment: '#8b5cf6',
          savings: '#3b82f6',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        card: '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)',
        'card-hover': '0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};
