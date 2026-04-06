import { memo, type ReactNode } from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

type CatalogItemCardProps = {
  title: string;
  codeBadge: string;
  description: ReactNode;
  footer: ReactNode;
  /** Опционально: «аватар» (инициалы), visual set — карточки пресетов. */
  avatar?: ReactNode;
  className?: string;
};

/**
 * Единая структура карточки каталога (режим / пресет): иерархия заголовка,
 * нейтральный бэйдж id, вторичная CTA в футере с разделителем.
 */
export const CatalogItemCard = memo(function CatalogItemCard({
  title,
  codeBadge,
  description,
  footer,
  avatar,
  className,
}: CatalogItemCardProps) {
  const headInner = (
    <>
      <div className="flex items-start justify-between gap-2">
        <CardTitle className="text-base font-semibold leading-snug tracking-tight">{title}</CardTitle>
        <Badge
          variant="outline"
          className="shrink-0 border-muted-foreground/30 font-mono text-[10px] tabular-nums text-muted-foreground"
        >
          {codeBadge}
        </Badge>
      </div>
      <CardDescription className="text-sm font-normal leading-relaxed text-muted-foreground">{description}</CardDescription>
    </>
  );

  return (
    <Card className={cn("flex h-full flex-col", className)}>
      <CardHeader className="space-y-1.5 pb-2">
        {avatar ? (
          <div className="flex items-start gap-3">
            <div className="shrink-0 pt-0.5">{avatar}</div>
            <div className="min-w-0 flex-1 space-y-1.5">{headInner}</div>
          </div>
        ) : (
          <div className="space-y-1.5">{headInner}</div>
        )}
      </CardHeader>
      <CardFooter className="mt-auto flex flex-col border-t border-border/80 bg-muted/20 pt-4">
        {footer}
      </CardFooter>
    </Card>
  );
});
