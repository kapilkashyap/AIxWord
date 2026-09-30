/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Crossword-specific colors
        'cell-empty': '#ffffff',
        'cell-blocked': '#000000',
        'cell-selected': '#ffeb3b',
        'cell-active-word': '#fff9c4',
        'cell-completed': '#c8e6c9',
        'cell-error': '#ffcdd2',
        'cell-border': '#000000',
        'clue-active': '#1976d2',
        'clue-hover': '#e3f2fd',
      },
      spacing: {
        'cell': '3rem',
      },
      fontFamily: {
        'mono': ['Courier New', 'monospace'],
      },
    },
  },
  plugins: [],
};
