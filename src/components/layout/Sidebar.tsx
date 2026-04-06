import type { ElementType } from "react";
import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import {
  Activity,
  Calculator,
  ChevronLeft,
  ChevronRight,
  Crosshair,
  Download,
  Eye,
  GitCompare,
  Home,
  Layers,
  Library,
  Braces,
  Package,
  Rocket,
  Settings,
  Upload,
  Wrench,
  Zap,
} from "lucide-react";
import { interpolate, useI18n } from "@/lib/i18n";
import { loadRecentConfigs, type RecentConfigEntry } from "@/lib/recentConfigs";
import { GCE_RECENT_UPDATED } from "@/lib/uiEvents";
import { useAppStore } from "@/stores/appStore";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  sidebarBrandMetaClass,
  sidebarNavGroupLabelClass,
  sidebarRecentNameClass,
  sidebarStatusOverlineClass,
} from "@/lib/layoutTokens";
import { cn } from "@/lib/utils";

type NavItem = { to: string; icon: ElementType };

function navKeyFromPath(to: string): string {
  return to.replace(/^\//, "") || "dashboard";
}

/** Иконки и группы в духе референс-макета сайдбара. */
const primary: NavItem[] = [
  { to: "/dashboard", icon: Home },
  { to: "/quick-setup", icon: Zap },
  { to: "/modes", icon: Layers },
  { to: "/presets", icon: Package },
];

const tools: NavItem[] = [
  { to: "/crosshair", icon: Crosshair },
  { to: "/sensitivity", icon: Calculator },
  { to: "/launch-options", icon: Rocket },
  { to: "/compare", icon: GitCompare },
  { to: "/export", icon: Download },
  { to: "/import", icon: Upload },
  { to: "/profiles", icon: Library },
  { to: "/aliases", icon: Braces },
  { to: "/preview", icon: Eye },
  { to: "/diagnostics", icon: Activity },
];

function NavButton({ item, collapsed }: { item: NavItem; collapsed: boolean }) {
  const { t } = useI18n();
  const label = t(`nav.${navKeyFromPath(item.to)}`);
  const Icon = item.icon;
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <NavLink
          to={item.to}
          title={label}
          aria-label={collapsed ? label : undefined}
          className={({ isActive }) =>
            collapsed
              ? cn(
                  "flex h-10 w-full items-center justify-center rounded-lg p-0 text-sm font-medium tracking-tight transition-colors",
                  isActive
                    ? "bg-sidebar-accent/90 text-sidebar-accent-foreground shadow-sm"
                    : "text-sidebar-foreground/90 hover:bg-sidebar-accent/55 hover:text-sidebar-accent-foreground",
                )
              : cn(
                  "group flex items-center gap-3 rounded-lg py-2 text-sm font-medium tracking-tight transition-colors",
                  "border-l-2 border-transparent pl-2 pr-3",
                  isActive
                    ? "border-l-sidebar-primary bg-sidebar-accent/90 text-sidebar-accent-foreground shadow-sm"
                    : "text-sidebar-foreground/90 hover:border-l-sidebar-border hover:bg-sidebar-accent/55 hover:text-sidebar-accent-foreground",
                )
          }
        >
          <Icon
            className="pointer-events-none size-[18px] shrink-0 opacity-90"
            strokeWidth={1.75}
            aria-hidden
          />
          {collapsed ? null : <span className="truncate">{label}</span>}
        </NavLink>
      </TooltipTrigger>
      <TooltipContent side="right" sideOffset={6}>
        {label}
      </TooltipContent>
    </Tooltip>
  );
}

/** В узком режиме без Radix ScrollArea — иначе полоса прокрутки съедает ширину и «центр» иконок смещается влево. */
function SidebarNavScrollInner({ collapsed }: { collapsed: boolean }) {
  const { t } = useI18n();
  return (
    <div className={cn(collapsed ? "px-1.5 py-2" : "px-2 py-3")}>
      <p
        className={cn(
          sidebarNavGroupLabelClass,
          collapsed && "sr-only",
        )}
      >
        {t("sidebar.sections")}
      </p>
      <nav className="flex w-full flex-col gap-0.5">
        {primary.map((item) => (
          <NavButton key={item.to} item={item} collapsed={collapsed} />
        ))}
      </nav>

      <Separator className={cn("bg-sidebar-border/80", collapsed ? "my-2.5" : "my-4")} />

      <p
        className={cn(
          sidebarNavGroupLabelClass,
          collapsed && "sr-only",
        )}
      >
        {t("sidebar.tools")}
      </p>
      <nav className="flex w-full flex-col gap-0.5">
        {tools.map((item) => (
          <NavButton key={item.to} item={item} collapsed={collapsed} />
        ))}
      </nav>
    </div>
  );
}

/** Строка состояния в духе visual set §3.1.5: последний сохранённый .cfg из локального списка. */
function SidebarRecentStatus({ collapsed }: { collapsed: boolean }) {
  const { t } = useI18n();
  const [recent, setRecent] = useState<RecentConfigEntry[]>(() => loadRecentConfigs());
  useEffect(() => {
    const sync = () => setRecent(loadRecentConfigs());
    sync();
    window.addEventListener(GCE_RECENT_UPDATED, sync);
    return () => window.removeEventListener(GCE_RECENT_UPDATED, sync);
  }, []);
  const first = recent[0];
  const has = recent.length > 0;
  const tip = has
    ? interpolate(t("sidebar.recentTooltipHas"), { name: first.name })
    : t("sidebar.recentTooltipEmpty");

  if (collapsed) {
    return (
      <Tooltip>
        <TooltipTrigger asChild>
          <div
            className="flex h-10 w-full items-center justify-center rounded-lg"
            role="status"
            aria-label={tip}
          >
            <span
              className={cn(
                "size-2 shrink-0 rounded-full",
                has ? "bg-success" : "bg-muted-foreground/45",
              )}
            />
          </div>
        </TooltipTrigger>
        <TooltipContent side="right" className="max-w-[min(280px,calc(100vw-4rem))] text-xs">
          {tip}
        </TooltipContent>
      </Tooltip>
    );
  }

  return (
    <div className="border-b border-sidebar-border/80 px-2 pb-2.5 pt-0.5">
      <div className="flex items-start gap-2">
        <span
          className={cn(
            "mt-1 size-2 shrink-0 rounded-full",
            has ? "bg-success" : "bg-muted-foreground/45",
          )}
          aria-hidden
        />
        <div className="min-w-0 flex-1">
          <p className={sidebarStatusOverlineClass}>
            {t("sidebar.recentOverline")}
          </p>
          <p
            className={sidebarRecentNameClass}
            title={has ? `${first.name} — ${first.path}` : undefined}
          >
            {has ? first.name : t("sidebar.recentEmpty")}
          </p>
        </div>
      </div>
    </div>
  );
}

export function Sidebar() {
  const { t } = useI18n();
  const collapsed = useAppStore((s) => s.sidebarCollapsed);
  const toggleSidebarCollapsed = useAppStore((s) => s.toggleSidebarCollapsed);
  const settingsLabel = t("nav.settings");

  return (
    <aside
      className={cn(
        "flex min-h-0 shrink-0 flex-col overflow-hidden border-r border-sidebar-border bg-sidebar text-sidebar-foreground shadow-[2px_0_12px_rgba(0,0,0,0.12)] transition-[width] duration-200 ease-out dark:shadow-[2px_0_20px_rgba(0,0,0,0.35)]",
        collapsed ? "w-[3.75rem]" : "w-60",
      )}
    >
      {/* Шапка: синий скруглённый квадрат + белый ключ (как в макете). */}
      <div
        className={cn(
          "shrink-0 border-b border-sidebar-border",
          collapsed ? "flex justify-center px-1.5 py-3" : "px-4 py-4",
        )}
      >
        <div
          className={cn("flex items-center gap-3", collapsed && "w-full justify-center")}
        >
          <div
            className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground shadow-md"
            aria-hidden
          >
            <Wrench className="size-[22px]" strokeWidth={2.2} />
          </div>
          <div className={cn("min-w-0 flex-1", collapsed && "sr-only")}>
            <p className="truncate font-semibold leading-tight tracking-tight text-sidebar-foreground">
              {t("sidebar.brandTitle")}
            </p>
            <p className={sidebarBrandMetaClass}>{t("sidebar.brandMeta")}</p>
          </div>
        </div>
      </div>

      {collapsed ? (
        <div
          className={cn(
            "min-h-0 flex-1 overflow-y-auto overflow-x-hidden overscroll-y-contain",
            /* полоса прокрутки не съедает ширину в узком режиме — иначе «центр» иконок смещается */
            "[scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:h-0 [&::-webkit-scrollbar]:w-0",
          )}
        >
          <SidebarNavScrollInner collapsed />
        </div>
      ) : (
        <ScrollArea className="min-h-0 flex-1">
          <SidebarNavScrollInner collapsed={false} />
        </ScrollArea>
      )}

      {/* Подвал: те же отступы и высота строк, что у навигации выше */}
      <div
        className={cn(
          "shrink-0 border-t border-sidebar-border bg-sidebar/95 backdrop-blur-sm",
          collapsed ? "space-y-0.5 px-1.5 pb-2 pt-2" : "space-y-0.5 p-2 pt-3",
        )}
      >
        <SidebarRecentStatus collapsed={collapsed} />
        <Tooltip>
          <TooltipTrigger asChild>
            <NavLink
              to="/settings"
              title={settingsLabel}
              aria-label={collapsed ? settingsLabel : undefined}
              className={({ isActive }) =>
                collapsed
                  ? cn(
                      "flex h-10 w-full items-center justify-center rounded-lg p-0 text-sm font-medium tracking-tight transition-colors",
                      isActive
                        ? "bg-sidebar-accent/90 text-sidebar-accent-foreground shadow-sm"
                        : "text-sidebar-foreground/90 hover:bg-sidebar-accent/55 hover:text-sidebar-accent-foreground",
                    )
                  : cn(
                      "group flex items-center gap-3 rounded-lg py-2 text-sm font-medium tracking-tight transition-colors",
                      "border-l-2 border-transparent pl-2 pr-3",
                      isActive
                        ? "border-l-sidebar-primary bg-sidebar-accent/90 text-sidebar-accent-foreground shadow-sm"
                        : "text-sidebar-foreground/90 hover:border-l-sidebar-border hover:bg-sidebar-accent/55 hover:text-sidebar-accent-foreground",
                    )
              }
            >
              <Settings
                className="pointer-events-none size-[18px] shrink-0 opacity-90"
                strokeWidth={1.75}
                aria-hidden
              />
              {collapsed ? null : <span className="truncate">{settingsLabel}</span>}
            </NavLink>
          </TooltipTrigger>
          <TooltipContent side="right" sideOffset={6}>
            {settingsLabel}
          </TooltipContent>
        </Tooltip>

        <Tooltip>
          <TooltipTrigger asChild>
            <button
              type="button"
              onClick={toggleSidebarCollapsed}
              className={cn(
                "text-sm font-medium tracking-tight transition-colors",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sidebar-ring/60 focus-visible:ring-offset-2 focus-visible:ring-offset-sidebar",
                collapsed
                  ? cn(
                      "flex h-10 w-full items-center justify-center rounded-lg p-0",
                      "text-sidebar-primary hover:bg-sidebar-accent/40 hover:text-sidebar-primary",
                    )
                  : cn(
                      "flex w-full items-center gap-3 rounded-lg border-l-2 border-transparent py-2 pl-2 pr-3",
                      "text-sidebar-primary hover:bg-sidebar-accent/40 hover:text-sidebar-primary",
                    ),
              )}
              aria-label={collapsed ? t("sidebar.expandPanel") : t("sidebar.collapsePanel")}
            >
              {collapsed ? (
                <ChevronRight
                  className="pointer-events-none size-[18px] shrink-0"
                  strokeWidth={1.75}
                  aria-hidden
                />
              ) : (
                <>
                  <ChevronLeft className="size-[18px] shrink-0 opacity-90" strokeWidth={1.75} aria-hidden />
                  <span className="truncate">{t("sidebar.collapse")}</span>
                </>
              )}
            </button>
          </TooltipTrigger>
          <TooltipContent side="right" sideOffset={6}>
            {collapsed ? t("sidebar.expand") : t("sidebar.collapse")}
          </TooltipContent>
        </Tooltip>
      </div>
    </aside>
  );
}
