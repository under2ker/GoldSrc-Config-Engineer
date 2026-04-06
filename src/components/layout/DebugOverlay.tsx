import { useEffect } from "react";
import { createPortal } from "react-dom";
import { isTauri } from "@tauri-apps/api/core";
import { X } from "lucide-react";
import pkg from "../../../package.json";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type DebugOverlayProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  pathname: string;
};

function formatBytes(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}

/** Панель отладки (Фаза 4): версия, маршрут, окружение; по F12. */
export function DebugOverlay({ open, onOpenChange, pathname }: DebugOverlayProps) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        onOpenChange(false);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onOpenChange]);

  if (!open) return null;

  const mem = (performance as Performance & { memory?: { usedJSHeapSize: number; totalJSHeapSize: number } })
    .memory;

  const node = (
    <div
      className={cn(
        "pointer-events-auto fixed bottom-4 right-4 z-[200] flex max-w-[min(22rem,calc(100vw-2rem))] flex-col gap-2 rounded-lg border border-border",
        "bg-background/95 p-3 text-xs shadow-xl backdrop-blur-md",
      )}
      role="dialog"
      aria-label="Отладочная панель"
    >
      <div className="flex items-center justify-between gap-2 border-b border-border pb-2">
        <span className="font-semibold text-foreground">Отладка</span>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="size-7 shrink-0"
          onClick={() => onOpenChange(false)}
          aria-label="Закрыть"
        >
          <X className="size-4" />
        </Button>
      </div>
      <dl className="space-y-1.5 font-mono text-[11px] leading-relaxed text-muted-foreground">
        <div>
          <dt className="text-foreground/80">Версия</dt>
          <dd className="break-all text-foreground">{pkg.version}</dd>
        </div>
        <div>
          <dt className="text-foreground/80">Маршрут</dt>
          <dd className="break-all text-foreground">{pathname}</dd>
        </div>
        <div>
          <dt className="text-foreground/80">Окружение</dt>
          <dd className="text-foreground">{isTauri() ? "Tauri" : "Web"}</dd>
        </div>
        {mem ? (
          <div>
            <dt className="text-foreground/80">JS heap (Chrome)</dt>
            <dd className="text-foreground">
              {formatBytes(mem.usedJSHeapSize)} / {formatBytes(mem.totalJSHeapSize)}
            </dd>
          </div>
        ) : null}
        <div>
          <dt className="text-foreground/80">User-Agent</dt>
          <dd className="max-h-16 overflow-y-auto break-all text-[10px] text-foreground/90">
            {navigator.userAgent}
          </dd>
        </div>
      </dl>
      <p className="border-t border-border pt-2 text-[10px] text-muted-foreground">
        F12 — показать/скрыть · Esc — закрыть
      </p>
    </div>
  );

  return createPortal(node, document.body);
}
