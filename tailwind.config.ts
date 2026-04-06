import type { Config } from "tailwindcss";

/**
 * Tailwind v4: палитра и `@theme inline` — в `src/styles/globals.css`.
 * Здесь — опции сборщика (совместимость с shadcn / явная тёмная тема).
 */
const config = {
  darkMode: "class",
} satisfies Config;

export default config;
