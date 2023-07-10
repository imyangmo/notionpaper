/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx,astro}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx,astro}",
    "./components/**/*.{js,ts,jsx,tsx,mdx,astro}",

    // Or if using `src` directory:
    "./src/**/*.{js,ts,jsx,tsx,mdx,astro}",
  ],
  theme: {
    extend: {},
  },
  plugins: [require("daisyui"), require('@tailwindcss/typography')],
}

