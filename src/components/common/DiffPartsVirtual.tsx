import type { Change } from "diff";
import { useRef } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import { cn } from "@/lib/utils";

const VIRTUAL_THRESHOLD = 28;

export function diffNeedsVirtualization(parts: Change[]): boolean {
  return parts.length >= VIRTUAL_THRESHOLD;
}

type Props = { parts: Change[] };

/** Виртуализированный список фрагментов diff — для длинных файлов без зависания DOM. */
export function DiffPartsVirtual({ parts }: Props) {
  const parentRef = useRef<HTMLDivElement>(null);
  const virtualizer = useVirtualizer({
    count: parts.length,
    getScrollElement: () => parentRef.current,
    estimateSize: (i) => {
      const lineCount = parts[i]?.value.split("\n").length ?? 1;
      return Math.min(520, 12 + lineCount * 15);
    },
    overscan: 8,
    measureElement:
      typeof document !== "undefined"
        ? (el) => (el instanceof HTMLElement ? el.getBoundingClientRect().height : 0)
        : undefined,
  });

  return (
    <div
      ref={parentRef}
      className="h-[min(28rem,50vh)] overflow-auto rounded-md border border-border bg-muted/15"
    >
      <div
        className="relative w-full font-mono text-xs leading-relaxed"
        style={{ height: virtualizer.getTotalSize() }}
      >
        {virtualizer.getVirtualItems().map((v) => {
          const part = parts[v.index]!;
          return (
            <div
              key={v.key}
              data-index={v.index}
              ref={virtualizer.measureElement}
              className="absolute left-0 top-0 w-full px-3"
              style={{ transform: `translateY(${v.start}px)` }}
            >
              <pre
                className={cn(
                  "mb-1 overflow-x-auto whitespace-pre-wrap break-words rounded px-2 py-1",
                  part.added && "bg-emerald-500/15 text-emerald-900 dark:text-emerald-100",
                  part.removed && "bg-red-500/15 text-red-900 dark:text-red-100",
                  !part.added && !part.removed && "text-foreground/85",
                )}
              >
                {part.value}
              </pre>
            </div>
          );
        })}
      </div>
    </div>
  );
}
