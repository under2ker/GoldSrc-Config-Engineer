import { useNavigate } from "react-router-dom";
import {
  Braces,
  Calculator,
  Crosshair,
  Download,
  FileUp,
  GitCompare,
  Rocket,
  Settings,
  Zap,
} from "lucide-react";
import { pageCaptionClass, pageSectionTitleClass } from "@/lib/layoutTokens";
import { cn } from "@/lib/utils";

type ActionDef = {
  key: string;
  title: string;
  description: string;
  icon: typeof Zap;
  iconClass: string;
  ringClass: string;
  onActivate: () => void;
};

export function DashboardQuickActions(props: { onGoToGenerate: () => void }) {
  const navigate = useNavigate();
  const { onGoToGenerate } = props;

  const actions: ActionDef[] = [
    {
      key: "generate",
      title: "Быстрая генерация",
      description: "Режим и кнопка «Сгенерировать .cfg»",
      icon: Zap,
      iconClass: "text-amber-600 dark:text-amber-400",
      ringClass: "border-amber-500/30 bg-amber-500/10",
      onActivate: onGoToGenerate,
    },
    {
      key: "wizard",
      title: "Быстрая настройка",
      description: "Пошаговый мастер конфигурации",
      icon: Settings,
      iconClass: "text-violet-600 dark:text-violet-400",
      ringClass: "border-violet-500/30 bg-violet-500/10",
      onActivate: () => navigate("/quick-setup"),
    },
    {
      key: "import",
      title: "Импорт конфига",
      description: "Загрузить существующий .cfg",
      icon: FileUp,
      iconClass: "text-cyan-600 dark:text-cyan-400",
      ringClass: "border-cyan-500/30 bg-cyan-500/10",
      onActivate: () => navigate("/import"),
    },
    {
      key: "aliases",
      title: "Алиасы",
      description: "Пресеты скриптов (+jumpthrow, циклы, KZ)",
      icon: Braces,
      iconClass: "text-sky-600 dark:text-sky-400",
      ringClass: "border-sky-500/30 bg-sky-500/10",
      onActivate: () => navigate("/aliases"),
    },
    {
      key: "crosshair",
      title: "Настройка прицела",
      description: "Визуальный редактор прицела",
      icon: Crosshair,
      iconClass: "text-emerald-600 dark:text-emerald-400",
      ringClass: "border-emerald-500/30 bg-emerald-500/10",
      onActivate: () => navigate("/crosshair"),
    },
    {
      key: "sensitivity",
      title: "Чувствительность мыши",
      description: "Оценка см/360° и сравнение с другими конфигами",
      icon: Calculator,
      iconClass: "text-lime-600 dark:text-lime-400",
      ringClass: "border-lime-500/30 bg-lime-500/10",
      onActivate: () => navigate("/sensitivity"),
    },
    {
      key: "launch",
      title: "Параметры запуска",
      description: "Строка запуска для Steam (CS 1.6)",
      icon: Rocket,
      iconClass: "text-orange-600 dark:text-orange-400",
      ringClass: "border-orange-500/30 bg-orange-500/10",
      onActivate: () => navigate("/launch-options"),
    },
    {
      key: "compare",
      title: "Сравнение",
      description: "Сравнить два конфига",
      icon: GitCompare,
      iconClass: "text-pink-600 dark:text-pink-400",
      ringClass: "border-pink-500/30 bg-pink-500/10",
      onActivate: () => navigate("/compare"),
    },
    {
      key: "export",
      title: "Экспорт",
      description: "Сохранить конфиг в файл",
      icon: Download,
      iconClass: "text-blue-600 dark:text-blue-400",
      ringClass: "border-blue-500/30 bg-blue-500/10",
      onActivate: () => navigate("/export"),
    },
  ];

  return (
    <section className="space-y-4">
      <h2 className={pageSectionTitleClass}>
        Быстрые действия
      </h2>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {actions.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.key}
              type="button"
              onClick={item.onActivate}
              className={cn(
                "group flex w-full items-center gap-4 rounded-xl border border-border/80 bg-card/50 p-4 text-left shadow-sm transition-all",
                "motion-safe:hover:-translate-y-0.5 motion-safe:hover:shadow-md",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background",
              )}
            >
              <div
                className={cn(
                  "flex size-12 shrink-0 items-center justify-center rounded-xl border transition-colors",
                  item.ringClass,
                )}
              >
                <Icon className={cn("size-6", item.iconClass)} strokeWidth={1.75} aria-hidden />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-sm font-semibold text-foreground">{item.title}</h3>
                <p className={cn(pageCaptionClass, "mt-0.5 leading-snug")}>
                  {item.description}
                </p>
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}
