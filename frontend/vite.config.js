import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import frappeui from "frappe-ui/vite"
import path from "path"
import fs from "fs"

// Desktop-first SPA for Frappe HR — served by Frappe at /hr.
// Build wiring mirrors the proven hrms/CRM pattern (assets -> public/frontend,
// html entry copied into www/hr.html). No Ionic / PWA here — this is desktop.
export default defineConfig({
  server: {
    port: 8080,
    proxy: getProxyOptions(),
    allowedHosts: true,
  },
  plugins: [vue(), frappeui()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
  build: {
    outDir: "../frappe_hr_ui/public/frontend",
    emptyOutDir: true,
    target: "es2015",
    commonjsOptions: {
      include: [/tailwind.config.js/, /node_modules/],
    },
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          "frappe-ui": ["frappe-ui"],
        },
      },
    },
  },
  optimizeDeps: {
    include: ["frappe-ui > feather-icons", "showdown", "tailwind.config.js", "engine.io-client"],
  },
})

function getProxyOptions() {
  const config = getCommonSiteConfig()
  const webserver_port = config ? config.webserver_port : 8000
  if (!config) {
    console.log("No common_site_config.json found, using default port 8000")
  }
  return {
    "^/(app|login|api|assets|files|private)": {
      target: `http://127.0.0.1:${webserver_port}`,
      ws: true,
      router: function (req) {
        const site_name = req.headers.host.split(":")[0]
        return `http://${site_name}:${webserver_port}`
      },
    },
  }
}

function getCommonSiteConfig() {
  let currentDir = path.resolve(".")
  while (currentDir !== "/") {
    if (
      fs.existsSync(path.join(currentDir, "sites")) &&
      fs.existsSync(path.join(currentDir, "apps"))
    ) {
      let configPath = path.join(currentDir, "sites", "common_site_config.json")
      if (fs.existsSync(configPath)) {
        return JSON.parse(fs.readFileSync(configPath))
      }
      return null
    }
    currentDir = path.resolve(currentDir, "..")
  }
  return null
}
