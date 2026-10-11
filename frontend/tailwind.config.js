/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          dark: '#0a0d14',
          panel: '#101726',
          card: '#161f36',
          border: '#222f4d',
          accent: '#38bdf8',
          danger: '#f43f5e',
          warning: '#f59e0b',
          safe: '#10b981'
        }
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'threat-flash': 'threatGlow 2s ease-in-out infinite',
      },
      keyframes: {
        threatGlow: {
          '0%, 100%': { boxShadow: '0 0 15px rgba(244, 63, 94, 0.4)' },
          '50%': { boxShadow: '0 0 30px rgba(244, 63, 94, 0.8)' },
        }
      }
    },
  },
  plugins: [],
}
