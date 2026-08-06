/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        vwblue: '#0b1c3f',
        primary: '#3f6ad8',
        accent: '#30c5d2',
        success: '#3ac47d',
        warning: '#f7b82f',
        danger: '#d92550',
      },
      fontFamily: {
        sans: ['Inter', 'Plus Jakarta Sans', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
