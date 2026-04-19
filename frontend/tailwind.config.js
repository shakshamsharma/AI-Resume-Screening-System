/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['DM Sans', 'sans-serif'],
        display: ['Syne', 'sans-serif'],
      },
      colors: {
        accent: {
          DEFAULT: '#1E4FD8',
          light: '#EEF2FF',
          hover: '#1840B5',
        },
        surface: {
          DEFAULT: '#FFFFFF',
          secondary: '#F2F1EE',
          tertiary: '#F8F7F4',
        },
        border: {
          DEFAULT: '#E4E3DF',
          strong: '#C8C7C3',
        },
        muted: '#7A7974',
      },
      boxShadow: {
        card: '0 1px 4px rgba(0,0,0,0.06)',
        dropdown: '0 4px 16px rgba(0,0,0,0.10)',
      },
    },
  },
  plugins: [],
}
