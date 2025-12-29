/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: "#0b1d2c",
        panel: "#13293d",
        accent: "#38bdf8",
      },
    },
  },
  plugins: [],
};

