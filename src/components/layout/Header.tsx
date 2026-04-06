import { PanelLeft, Search } from "lucide-react";
import { useAppStore } from "@/stores/appStore";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";

type HeaderProps = {
  title?: string;
  /** Короткая строка под H1 (visual set §3.2.1). */
  subtitle?: string;
  onOpenCommandPalette: () => void;
};

export function Header({ title, subtitle, onOpenCommandPalette }: HeaderProps) {
  const toggleSidebarCollapsed = useAppStore((s) => s.toggleSidebarCollapsed);

  return (
    <header className="sticky top-0 z-30 shrink-0 border-b border-border bg-background/80 backdrop-blur-md supports-[backdrop-filter]:bg-background/60">
      <div
        className={cn(
          "flex items-center gap-2 px-4 py-2 sm:gap-4 sm:px-6",
          subtitle ? "min-h-[3.75rem]" : "min-h-14",
        )}
      >
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className="size-9 shrink-0"
        onClick={toggleSidebarCollapsed}
        aria-label="Свернуть боковую панель"
      >
        <PanelLeft className="size-4" />
      </Button>
      <Separator orientation="vertical" className="hidden h-6 sm:block" />
      <div className="min-w-0 flex-1">
        <h1 className="truncate text-lg font-semibold tracking-tight text-foreground">
          {title ?? "GoldSrc Config Engineer"}
        </h1>
        {subtitle ? (
          <p className="mt-0.5 line-clamp-2 text-xs leading-snug text-muted-foreground sm:text-sm">{subtitle}</p>
        ) : null}
      </div>
      <Button
        type="button"
        variant="outline"
        size="sm"
        className="hidden gap-2 sm:inline-flex"
        onClick={onOpenCommandPalette}
      >
        <Search className="size-3.5" />
        Поиск…
        <kbd className="pointer-events-none ml-1 hidden rounded border bg-muted px-1 font-mono text-[10px] font-medium opacity-80 lg:inline">
          ⌘K
        </kbd>
      </Button>
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className="size-9 shrink-0 sm:hidden"
        onClick={onOpenCommandPalette}
        aria-label="Открыть поиск"
      >
        <Search className="size-4" />
      </Button>
      </div>
      <Breadcrumbs />
    </header>
  );
}
