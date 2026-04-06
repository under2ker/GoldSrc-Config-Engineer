import { cn } from "@/lib/utils";

/** Две буквы из названия (инициалы или начало строки) — «аватар» без изображений, visual set §10 Ph.3. */
export function initialsFromCatalogTitle(title: string): string {
  const t = title.trim();
  if (!t) {
    return "?";
  }
  const parts = t.split(/\s+/).filter(Boolean);
  if (parts.length >= 2) {
    const a = parts[0]?.[0] ?? "";
    const b = parts[1]?.[0] ?? "";
    return (a + b).toUpperCase();
  }
  return t.slice(0, 2).toUpperCase();
}

type CatalogAvatarProps = {
  title: string;
  className?: string;
};

export function CatalogAvatar({ title, className }: CatalogAvatarProps) {
  const letters = initialsFromCatalogTitle(title);
  return (
    <div
      className={cn(
        "flex size-11 shrink-0 items-center justify-center rounded-full border border-primary/30 bg-gradient-to-br from-primary/20 via-primary/12 to-primary/5 text-[13px] font-bold uppercase leading-none text-primary tabular-nums shadow-sm",
        className,
      )}
      aria-hidden
    >
      {letters}
    </div>
  );
}
