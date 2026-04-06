import path from "node:path";
import { fileURLToPath } from "node:url";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const rootDir = fileURLToPath(new URL(".", import.meta.url));
// @ts-expect-error Vite injects for Tauri dev host
const host = process.env.TAURI_DEV_HOST;

export default defineConfig(async () => ({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(rootDir, "./src"),
    },
  },
  clearScreen: false,
  server: {
    port: 1420,
    strictPort: true,
    // 127.0.0.1: Tauri на Windows часто опрашивает devUrl раньше, чем успевает IPv6 ::1 — иначе «Waiting for dev server…»
    host: host || "127.0.0.1",
    hmr: host
      ? {
          protocol: "ws",
          host,
          port: 1421,
        }
      : { host: "127.0.0.1" },
    watch: {
      ignored: ["**/src-tauri/**"],
    },
  },
}));
