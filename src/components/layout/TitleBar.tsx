import { getCurrentWindow } from "@tauri-apps/api/window";
import { isTauri } from "@tauri-apps/api/core";
import { Minus, Square, X } from "lucide-react";
import { Button } from "@/components/ui/button";

/** Панель управления окном при `decorations: false` (Tauri). В браузере не рендерится. */
export function TitleBar() {
  if (!isTauri()) {
    return null;
  }

  const w = getCurrentWindow();

  return (
    <header className="flex h-9 shrink-0 select-none items-stretch border-b border-sidebar-border bg-sidebar text-sidebar-foreground">
      <div
        className="flex min-w-0 flex-1 items-center px-3"
        data-tauri-drag-region
        role="presentation"
      >
        <span className="truncate text-xs font-medium text-muted-foreground">
          GoldSrc Config Engineer
        </span>
      </div>
      <div
        className="flex shrink-0 items-stretch"
        onMouseDown={(e) => e.stopPropagation()}
      >
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="h-full w-10 rounded-none hover:bg-sidebar-accent"
          onClick={() => void w.minimize().catch(console.error)}
          aria-label="Свернуть"
        >
          <Minus className="size-3.5" />
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="h-full w-10 rounded-none hover:bg-sidebar-accent"
          onClick={() => void w.toggleMaximize().catch(console.error)}
          aria-label="Развернуть"
        >
          <Square className="size-3" />
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="h-full w-10 rounded-none hover:bg-destructive/90 hover:text-destructive-foreground"
          onClick={() => void w.close().catch(console.error)}
          aria-label="Закрыть"
        >
          <X className="size-3.5" />
        </Button>
      </div>
    </header>
  );
}
