/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: 'var(--background)',
        foreground: 'var(--foreground)',
        surface: {
          DEFAULT: 'var(--surface)',
          50: 'var(--surface-50)',
          100: 'var(--surface-100)',
          200: 'var(--surface-200)',
          300: 'var(--surface-300)',
          border: 'var(--border)',
          elevated: 'var(--surface-100)',
        },
        'surface-border': 'var(--border)',
        'surface-elevated': 'var(--surface-100)',
        border: 'var(--border)',
        'border-subtle': 'var(--border-subtle)',
        'border-focus': 'var(--border-focus)',
        obsidian: {
          DEFAULT: '#090d16',
          card: '#0f1422',
          border: '#1e293b',
        },
        accent: {
          DEFAULT: '#18181b',
          foreground: '#ffffff',
          indigo: '#4f46e5',
          emerald: '#10b981',
          amber: '#f59e0b',
          rose: '#ef4444',
          zinc: '#71717a',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
