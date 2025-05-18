import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import wasm from "vite-plugin-wasm";
import topLevelAwait from "vite-plugin-top-level-await";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), wasm(), topLevelAwait()],
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000", // Django server!
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
