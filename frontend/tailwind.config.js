/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        indigo: {
          50: '#f0f4ff',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
        },
        purple: {
          500: '#a855f7',
          600: '#9333ea',
          700: '#7e22ce',
        },
        pink: {
          500: '#ec4899',
          600: '#db2777',
        },
      },
    },
  },
  plugins: [],
}