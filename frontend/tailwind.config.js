/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: "#070B14",
          surface: "#0B1220",
          card: "#101A2B",
          border: "#1D2B40",
          cyan: "#39D5FF",
          blue: "#5B8CFF",
          green: "#35E6A1",
          amber: "#FFBF69",
          red: "#FF4D67",
          text: "#E7EEF8",
          muted: "#8291A8",
        }
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["JetBrains Mono", "SFMono-Regular", "Menlo", "Monaco", "Consolas", "Courier New", "monospace"],
      },
      boxShadow: {
        'cyan-glow': '0 0 15px -3px rgba(57, 213, 255, 0.25)',
        'red-glow': '0 0 15px -3px rgba(255, 77, 103, 0.35)',
        'amber-glow': '0 0 15px -3px rgba(255, 191, 105, 0.25)',
        'panel': '0 4px 20px -2px rgba(0, 0, 0, 0.5)',
      },
      animation: {
        'radar-sweep': 'radar 4s linear infinite',
        'pulse-subtle': 'pulseSubtle 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'scanline': 'scanline 8s linear infinite',
      },
      keyframes: {
        radar: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        pulseSubtle: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.6' },
        },
        scanline: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        }
      }
    },
  },
  plugins: [],
}
