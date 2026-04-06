import { Fragment } from "react";
import { cn } from "@/lib/utils";

function LineHighlight({ text }: { text: string }) {
  const idx = text.indexOf("//");
  if (idx !== -1) {
    return (
      <>
        <KeywordSpan s={text.slice(0, idx)} />
        <span className="text-emerald-700 dark:text-emerald-400">{text.slice(idx)}</span>
      </>
    );
  }
  return <KeywordSpan s={text} />;
}

function KeywordSpan({ s }: { s: string }) {
  const m = s.match(/^(\s*)(bind|alias|echo|exec|setinfo)(\s+)(.*)$/i);
  if (m) {
    return (
      <>
        {m[1]}
        <span className="font-medium text-sky-700 dark:text-sky-400">{m[2]}</span>
        {m[3]}
        <span className="text-foreground">{m[4]}</span>
      </>
    );
  }
  return <span className="text-foreground">{s}</span>;
}

export type CfgTextPreviewProps = {
  text: string;
  className?: string;
  /** Базовый размер шрифта кода (десктоп: ≥14px для моноширинного тела). */
  fontSizePx?: number;
  /** Нумерация строк — визуально отделяет «редактор» от textarea. */
  showLineNumbers?: boolean;
  /** Если false — длинные строки не переносятся, удобно для широких биндов. */
  breakLongLines?: boolean;
};

/** Подсветка строк .cfg: пропорциональный шрифт только в описаниях снаружи; тело — mono. */
export function CfgTextPreview({
  text,
  className,
  fontSizePx = 14,
  showLineNumbers = false,
  breakLongLines = true,
}: CfgTextPreviewProps) {
  const lines = text.split("\n");
  const fs = `${fontSizePx}px`;

  if (!showLineNumbers) {
    return (
      <pre
        className={cn(
          "m-0 font-mono leading-relaxed text-foreground",
          breakLongLines ? "whitespace-pre-wrap break-words" : "overflow-x-auto whitespace-pre",
          className,
        )}
        style={{ fontSize: fs }}
      >
        {lines.map((line, i) => (
          <Fragment key={`${i}-${line.slice(0, 24)}`}>
            {i > 0 ? "\n" : null}
            <LineHighlight text={line} />
          </Fragment>
        ))}
      </pre>
    );
  }

  return (
    <div
      className={cn(
        "grid w-full max-w-full grid-cols-[minmax(2.25rem,auto)_1fr] gap-x-0 font-mono leading-relaxed",
        className,
      )}
      style={{ fontSize: fs }}
    >
      {lines.map((line, i) => (
        <Fragment key={`${i}-${line.slice(0, 24)}`}>
          <span
            className="select-none border-r border-border/80 py-0.5 pr-2 text-right text-xs text-muted-foreground tabular-nums"
            aria-hidden
          >
            {i + 1}
          </span>
          <span
            className={cn(
              "min-w-0 border-b border-transparent py-0.5 pl-3 text-foreground last:border-b-0",
              breakLongLines ? "whitespace-pre-wrap break-words" : "overflow-x-auto whitespace-pre",
            )}
          >
            <LineHighlight text={line} />
          </span>
        </Fragment>
      ))}
    </div>
  );
}
