import { useEffect, useState } from "react";
import { isTauri } from "@tauri-apps/api/core";
import { Wrench } from "lucide-react";
import pkg from "../../../package.json";
import { cn } from "@/lib/utils";

/**
 * Короткий заставочный кадр при старте настольного приложения (visual set §10 Ph.3 splash).
 * В браузере не показывается.
 */
export function SplashScreen() {
  const [mounted, setMounted] = useState(() => isTauri());
  const [opaque, setOpaque] = useState(true);

  useEffect(() => {
    if (!isTauri()) {
      return;
    }
    if (typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setMounted(false);
      return;
    }
    const fade = window.setTimeout(() => setOpaque(false), 560);
    const remove = window.setTimeout(() => setMounted(false), 880);
    return () => {
      window.clearTimeout(fade);
      window.clearTimeout(remove);
    };
  }, []);

  if (!mounted) {
    return null;
  }

  return (
    <div
      className={cn(
        "fixed inset-0 z-[300] flex flex-col items-center justify-center gap-4 bg-gradient-to-b from-background via-background to-primary/[0.06] transition-opacity duration-300 ease-out",
        opaque ? "opacity-100" : "pointer-events-none opacity-0",
      )}
      role="status"
      aria-live="polite"
      aria-label="Загрузка приложения"
    >
      <div className="flex size-14 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-lg">
        <Wrench className="size-8" strokeWidth={2} aria-hidden />
      </div>
      <div className="text-center">
        <p className="text-lg font-semibold tracking-tight text-foreground">GoldSrc Config Engineer</p>
        <p className="mt-1 text-sm text-muted-foreground">v{pkg.version}</p>
      </div>
    </div>
  );
}
