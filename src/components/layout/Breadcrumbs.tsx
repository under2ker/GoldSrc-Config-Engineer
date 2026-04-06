import { Link, useLocation } from "react-router-dom";
import { ChevronRight, Home } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import { pathToBreadcrumbs } from "@/lib/routeMeta";
import { pageCaptionClass } from "@/lib/layoutTokens";
import { cn } from "@/lib/utils";

export function Breadcrumbs({ className }: { className?: string }) {
  const { pathname } = useLocation();
  const { t, locale } = useI18n();
  const crumbs = pathToBreadcrumbs(pathname, locale);
  const isDashboard = pathname === "/dashboard" || pathname === "/";

  /* На главной заголовок страницы уже совпадает с единственным пунктом — дублировать не нужно */
  if (isDashboard) {
    return null;
  }

  return (
    <nav
      aria-label={t("breadcrumbs.aria")}
      className={cn(pageCaptionClass, "flex flex-wrap items-center gap-1 px-4 pb-2 sm:px-6", className)}
    >
      <Link
        to="/dashboard"
        className="inline-flex items-center gap-0.5 rounded-sm text-foreground/80 outline-none ring-offset-background hover:text-primary focus-visible:ring-2 focus-visible:ring-ring"
      >
        <Home className="size-3.5 shrink-0 opacity-70" aria-hidden />
        <span className="sr-only sm:not-sr-only sm:inline">{t("breadcrumbs.home")}</span>
      </Link>
      {crumbs.map((item, i) => {
        const isLast = i === crumbs.length - 1;
        return (
          <span key={item.href} className="inline-flex items-center gap-1">
            <ChevronRight className="size-3.5 shrink-0 opacity-40" aria-hidden />
            {isLast ? (
              <span className="truncate font-medium text-foreground">{item.label}</span>
            ) : (
              <Link
                to={item.href}
                className="truncate rounded-sm outline-none ring-offset-background hover:text-primary focus-visible:ring-2 focus-visible:ring-ring"
              >
                {item.label}
              </Link>
            )}
          </span>
        );
      })}
    </nav>
  );
}
