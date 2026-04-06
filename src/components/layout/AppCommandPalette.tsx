import type { ElementType } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "cmdk";
import {
  Crosshair,
  Download,
  Gauge,
  GitCompare,
  History,
  Home,
  HelpCircle,
  Library,
  Braces,
  Image,
  FileCode,
  Calculator,
  Rocket,
  Search,
  Settings,
  Stethoscope,
  Upload,
  Users,
} from "lucide-react";
import { CFG_CLIPBOARD_SNIPPETS } from "@/lib/cfgClipboardSnippets";
import { clearRecentConfigs } from "@/lib/recentConfigs";
import { useCatalogStore } from "@/stores/catalogStore";

const ROUTES: {
  to: string;
  label: string;
  keywords?: string[];
  icon: ElementType;
}[] = [
  {
    to: "/dashboard",
    label: "Главная",
    keywords: [
      "home",
      "дашборд",
      "shift h",
      "главная страница",
      "готовность",
      "заполненность",
      "прогресс конфига",
      "completeness",
    ],
    icon: Home,
  },
  {
    to: "/quick-setup",
    label: "Быстрая настройка",
    keywords: ["wizard", "мастер", "shift q", "quick"],
    icon: Gauge,
  },
  {
    to: "/modes",
    label: "Режимы",
    keywords: ["modes", "shift m", "игровые режимы"],
    icon: Users,
  },
  {
    to: "/presets",
    label: "Про-пресеты",
    keywords: ["preset", "про", "shift b", "pro preset"],
    icon: Image,
  },
  {
    to: "/crosshair",
    label: "Прицел",
    keywords: ["cross", "crosshair", "shift x", "прицел"],
    icon: Crosshair,
  },
  {
    to: "/sensitivity",
    label: "Чувствительность мыши",
    keywords: ["sens", "dpi", "мышь", "cm", "360", "shift t"],
    icon: Calculator,
  },
  {
    to: "/launch-options",
    label: "Параметры запуска",
    keywords: ["steam", "hl.exe", "запуск", "launch", "noforce", "freq"],
    icon: Rocket,
  },
  {
    to: "/compare",
    label: "Сравнение конфигов",
    keywords: ["diff", "сравнить", "отличия", "shift g", "compare"],
    icon: GitCompare,
  },
  { to: "/export", label: "Экспорт", keywords: ["save", "cfg"], icon: Download },
  { to: "/import", label: "Импорт", keywords: ["open", "cfg", "drop"], icon: Upload },
  {
    to: "/profiles",
    label: "Профили",
    keywords: [
      "profile",
      "sqlite",
      "сохранить",
      "история",
      "history",
      "снимок",
      "копия",
      "shift",
      "ctrl shift p",
    ],
    icon: Library,
  },
  {
    to: "/aliases",
    label: "Алиасы",
    keywords: ["alias", "алиас", "скрипт"],
    icon: Braces,
  },
  { to: "/preview", label: "Просмотр", keywords: ["highlight"], icon: FileCode },
  {
    to: "/diagnostics",
    label: "Диагностика",
    keywords: ["health", "check", "sqlite", "база", "путь", "paths", "diag", "shift d", "стетоскоп"],
    icon: Stethoscope,
  },
  {
    to: "/settings",
    label: "Настройки",
    keywords: ["theme", "тема", "preferences", "gear", "shift s", "параметры приложения"],
    icon: Settings,
  },
];

type AppCommandPaletteProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onOpenHelp: () => void;
};

export function AppCommandPalette({ open, onOpenChange, onOpenHelp }: AppCommandPaletteProps) {
  const navigate = useNavigate();
  const loadCatalog = useCatalogStore((s) => s.load);

  return (
    <CommandDialog
      open={open}
      onOpenChange={onOpenChange}
      label="Команды и переходы"
      contentClassName="overflow-hidden rounded-lg border border-border bg-popover/95 p-0 text-popover-foreground shadow-lg backdrop-blur-md"
      overlayClassName="fixed inset-0 z-[100] bg-black/50 backdrop-blur-md"
    >
      <div className="flex items-center border-b px-3">
        <Search className="mr-2 size-4 shrink-0 opacity-50" aria-hidden />
        <CommandInput
          placeholder="Раздел, справка или CVAR…"
          className="flex h-11 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50"
        />
      </div>
      <CommandList className="max-h-[min(360px,50vh)] overflow-y-auto p-1">
        <CommandEmpty className="py-6 text-center text-sm text-muted-foreground">
          Нет совпадений.
        </CommandEmpty>

        <CommandGroup heading="Данные">
          <CommandItem
            value="обновить каталог режимы пресеты перезагрузить reload список"
            className="flex cursor-pointer items-center gap-2 rounded-sm px-2 py-1.5 text-sm aria-selected:bg-accent aria-selected:text-accent-foreground"
            onSelect={() => {
              void loadCatalog().then(() => {
                toast.success("Список обновлён", { description: "Режимы и про-пресеты" });
                onOpenChange(false);
              });
            }}
          >
            <Gauge className="size-4 shrink-0 opacity-80" />
            Обновить список режимов и пресетов
          </CommandItem>
        </CommandGroup>

        <CommandGroup heading="Справка">
          <CommandItem
            value="справка клавиши горячие help f1"
            className="flex cursor-pointer items-center gap-2 rounded-sm px-2 py-1.5 text-sm aria-selected:bg-accent aria-selected:text-accent-foreground"
            onSelect={() => {
              onOpenHelp();
              onOpenChange(false);
            }}
          >
            <HelpCircle className="size-4 shrink-0 opacity-80" />
            Горячие клавиши (F1)
          </CommandItem>
        </CommandGroup>

        <CommandGroup heading="Недавние .cfg">
          <CommandItem
            value="очистить историю недавние конфиги сброс список главная"
            className="flex cursor-pointer items-center gap-2 rounded-sm px-2 py-1.5 text-sm aria-selected:bg-accent aria-selected:text-accent-foreground"
            onSelect={() => {
              clearRecentConfigs();
              toast.message("Список недавних .cfg очищен");
              onOpenChange(false);
            }}
          >
            <History className="size-4 shrink-0 opacity-80" />
            Очистить «Недавние конфиги» на главной
          </CommandItem>
        </CommandGroup>

        <CommandGroup heading="Перейти">
          {ROUTES.map((r) => {
            const Icon = r.icon;
            return (
              <CommandItem
                key={r.to}
                value={`${r.label} ${r.to} ${r.keywords?.join(" ") ?? ""}`}
                keywords={r.keywords}
                className="flex cursor-pointer items-center gap-2 rounded-sm px-2 py-1.5 text-sm aria-selected:bg-accent aria-selected:text-accent-foreground"
                onSelect={() => {
                  navigate(r.to);
                  onOpenChange(false);
                }}
              >
                <Icon className="size-4 shrink-0 opacity-80" />
                {r.label}
              </CommandItem>
            );
          })}
        </CommandGroup>

        <CommandGroup heading="В буфер обмена">
          {CFG_CLIPBOARD_SNIPPETS.map((s) => (
            <CommandItem
              key={s.id}
              value={`${s.label} ${s.snippet} ${s.keywords?.join(" ") ?? ""}`}
              keywords={s.keywords}
              className="flex cursor-pointer items-center gap-2 rounded-sm px-2 py-1.5 font-mono text-xs aria-selected:bg-accent aria-selected:text-accent-foreground"
              onSelect={() => {
                void navigator.clipboard.writeText(s.snippet).then(
                  () => {
                    toast.success("Скопировано", { description: s.snippet });
                    onOpenChange(false);
                  },
                  () => toast.error("Не удалось скопировать"),
                );
              }}
            >
              {s.label}
            </CommandItem>
          ))}
        </CommandGroup>
      </CommandList>
      <p className="border-t px-3 py-2 text-xs text-muted-foreground">
        <kbd className="rounded border bg-muted px-1 font-mono text-[10px]">Ctrl</kbd>+
        <kbd className="rounded border bg-muted px-1 font-mono text-[10px]">K</kbd> — палитра ·{" "}
        <kbd className="rounded border bg-muted px-1 font-mono text-[10px]">Ctrl</kbd>+
        <kbd className="rounded border bg-muted px-1 font-mono text-[10px]">E</kbd> /{" "}
        <kbd className="rounded border bg-muted px-1 font-mono text-[10px]">I</kbd> — экспорт / импорт ·{" "}
        <kbd className="rounded border bg-muted px-1 font-mono text-[10px]">Ctrl</kbd>+
        <kbd className="rounded border bg-muted px-1 font-mono text-[10px]">S</kbd> — экспорт ·{" "}
        <kbd className="rounded border bg-muted px-1 font-mono text-[10px]">Ctrl</kbd>+
        <kbd className="rounded border bg-muted px-1 font-mono text-[10px]">L</kbd> — запуск Steam
      </p>
    </CommandDialog>
  );
}
