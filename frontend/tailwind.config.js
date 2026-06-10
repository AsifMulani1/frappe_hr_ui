import frappeUIPreset from "frappe-ui/tailwind"

export default {
  presets: [frappeUIPreset],
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
    "./node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}",
    "../node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // Brand accent = Frappe HR logo green (#06B58B). The app uses `blue-*`
      // utility classes as its accent throughout, so we remap the blue scale to
      // the brand teal-green — every accent surface (active nav, links, selected
      // rows, accent/info badges, rings) picks up the brand colour in one place.
      // `success` stays the separate `green-*` scale, so no semantic collision.
      colors: {
        blue: {
          50: "#E6FAF4",
          100: "#C2F1E4",
          200: "#8FE6CD",
          300: "#54D6B2",
          400: "#1FC198",
          500: "#06B58B",
          600: "#059377",
          700: "#0A6E57",
          800: "#0C5747",
          900: "#0D483B",
          950: "#04271F",
        },
      },
    },
  },
  plugins: [],
}
