/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#ecfdf5",
          100: "#d1fae5",
          200: "#a7f3d0",
          500: "#10b981",
          600: "#059669", // Primary Action
          700: "#047857", // Hover
          800: "#065f46", // Active
        },
        surface: {
          light: "#FFFFFF",
          secondary: "#F9FAFB",
          dark: "#18181B",
          border: "#E4E4E7",
        },
        content: {
          primary: "#18181B",
          secondary: "#71717A",
          muted: "#A1A1AA",
        },
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
      },
    },
  },
  plugins: [],
};
