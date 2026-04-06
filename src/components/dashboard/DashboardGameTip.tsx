import { Lightbulb } from "lucide-react";
import { useMemo } from "react";
import { pageLeadClass } from "@/lib/layoutTokens";
import { cn } from "@/lib/utils";

const TIPS: string[] = [
  "Положите autoexec.cfg в папку cstrike и добавьте в параметры запуска Steam строку +exec autoexec.cfg.",
  "Перед матчем проверьте rate, cl_updaterate и cl_cmdrate под свой пинг — низкие значения дают «резиновую» стрельбу.",
  "Отключите cl_dynamiccrosshair, если хотите статичный прицел при движении.",
  "Сохраняйте копию рабочего конфига перед экспериментами — так проще откатиться.",
  "Сравнение двух .cfg в приложении помогает найти лишние bind и дубли команд.",
];

export function DashboardGameTip({ className }: { className?: string }) {
  const tip = useMemo(() => {
    const d = new Date();
    const i = (d.getFullYear() + d.getMonth() * 31 + d.getDate()) % TIPS.length;
    return TIPS[i] ?? TIPS[0];
  }, []);

  return (
    <div
      className={cn(
        "flex gap-3 rounded-xl border border-amber-500/25 bg-amber-500/5 px-4 py-3 text-sm text-foreground/90",
        className,
      )}
    >
      <Lightbulb className="mt-0.5 size-5 shrink-0 text-amber-600 dark:text-amber-400" aria-hidden />
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-amber-800/90 dark:text-amber-200/90">
          Совет дня
        </p>
        <p className={cn(pageLeadClass, "mt-1")}>{tip}</p>
      </div>
    </div>
  );
}
