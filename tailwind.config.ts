import type { Config } from "tailwindcss";

export default {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Apple-inspired dark mode palette
        background: "#000000",
        foreground: "#ffffff",
        gray: {
          50: "#f9f9f9",
          100: "#ededed",
          200: "#d3d3d3",
          300: "#b8b8b8",
          400: "#8e8e93",
          500: "#636366",
          600: "#48484a",
          700: "#3a3a3c",
          800: "#2c2c2e",
          900: "#1c1c1e",
        },
        blue: {
          50: "#e7f1ff",
          100: "#d0e3ff",
          200: "#a6cbff",
          300: "#78aeff",
          400: "#4d94ff",
          500: "#007aff",
          600: "#0063cc",
          700: "#004c99",
          800: "#003566",
          900: "#001e33",
        },
      },
      fontFamily: {
        sans: [
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "Helvetica Neue",
          "Arial",
          "sans-serif",
        ],
      },
      animation: {
        "smooth-slide": "slide 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)",
      },
      keyframes: {
        slide: {
          "0%": { transform: "translateX(100%)" },
          "100%": { transform: "translateX(0)" },
        },
      },
      backdropBlur: {
        xs: "2px",
        sm: "4px",
        md: "8px",
        lg: "12px",
        xl: "20px",
      },
      boxShadow: {
        "apple-sm": "0 1px 2px rgba(0, 0, 0, 0.04)",
        "apple-md": "0 4px 12px -2px rgba(0, 0, 0, 0.12)",
        "apple-lg": "0 8px 24px -4px rgba(0, 0, 0, 0.16)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
} satisfies Config;
