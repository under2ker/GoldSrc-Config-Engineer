import { ArrowRight, Clock, FileText } from "lucide-react";
import { toast } from "sonner";
import { formatRelativeRu } from "@/lib/formatRelativeRu";
import { pageCaptionClass, pageSectionTitleClass } from "@/lib/layoutTokens";
import type { RecentConfigEntry } from "@/lib/recentConfigs";
import { cn } from "@/lib/utils";

type DashboardRecentConfigsProps = {
  items: RecentConfigEntry[];
};

async function copyPath(path: string): Promise<void> {
  try {
    await navigator.clipboard.writeText(path);
    toast.success("Путь скопирован", { description: path });
  } catch {
    toast.error("Не удалось скопировать путь");
  }
}

export function DashboardRecentConfigs({ items }: DashboardRecentConfigsProps) {
  return (
    <section className="space-y-4">
      <h2 className={cn(pageSectionTitleClass, "flex items-center gap-2")}>
        <Clock className="size-4" strokeWidth={1.75} aria-hidden />
        Недавние конфиги
      </h2>

      {items.length === 0 ? (
        <div
          className={cn(
            "flex flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-border/80 bg-muted/20 px-6 py-12 text-center",
          )}
        >
          <FileText className="size-10 text-muted-foreground/60" strokeWidth={1} aria-hidden />
          <p className="text-sm font-medium text-muted-foreground">Здесь появятся недавние конфиги</p>
          <p className={cn(pageCaptionClass, "max-w-sm")}>
            Сгенерируйте конфиг и сохраните его через «Сохранить как…» или импортируйте файл
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-1">
          {items.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => void copyPath(item.path)}
              className={cn(
                "group flex w-full items-center gap-3 rounded-lg border border-transparent px-4 py-3 text-left transition-colors",
                "hover:border-border hover:bg-muted/40",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
              )}
            >
              <FileText
                className="size-[18px] shrink-0 text-primary"
                strokeWidth={1.75}
                aria-hidden
              />
              <div className="min-w-0 flex-1">
                <span className="block truncate text-sm font-medium text-foreground">
                  {item.name}
                </span>
                <span className="block truncate text-xs text-muted-foreground">
                  {item.modeLabel} · {formatRelativeRu(item.savedAt)}
                </span>
              </div>
              <ArrowRight
                className="size-4 shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100"
                strokeWidth={1.75}
                aria-hidden
              />
            </button>
          ))}
        </div>
      )}
    </section>
  );
}
