import { useEffect, useRef } from "react";

export type CrosshairCanvasProps = {
  /** Полудлина луча от края зазора (логические пиксели canvas). */
  armLength: number;
  /** Зазор от центра до начала линии. */
  gap: number;
  /** Толщина линии. */
  thickness: number;
  /** Обводка тёмным для контраста на светлом фоне. */
  outline: boolean;
  /** Цвет лучей (CSS). */
  color: string;
  /** Цвет фона за сеткой. */
  background: string;
  className?: string;
};

/** Превью прицела в стиле «крест из 4 лучей» (CS-like). */
export function CrosshairCanvas({
  armLength,
  gap,
  thickness,
  outline,
  color,
  background,
  className,
}: CrosshairCanvasProps) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    let raf = 0;
    const paint = () => {
      raf = 0;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;

      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const logicalW = 240;
      const logicalH = 240;
      canvas.style.width = `${logicalW}px`;
      canvas.style.height = `${logicalH}px`;
      canvas.width = Math.floor(logicalW * dpr);
      canvas.height = Math.floor(logicalH * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      ctx.fillStyle = background;
      ctx.fillRect(0, 0, logicalW, logicalH);

      const cx = logicalW / 2;
      const cy = logicalH / 2;

      const drawArm = (dx: number, dy: number) => {
        const x0 = cx + dx * gap;
        const y0 = cy + dy * gap;
        const x1 = cx + dx * (gap + armLength);
        const y1 = cy + dy * (gap + armLength);
        ctx.lineCap = "butt";
        if (outline) {
          ctx.strokeStyle = "rgba(0,0,0,0.85)";
          ctx.lineWidth = thickness + 2;
          ctx.beginPath();
          ctx.moveTo(x0, y0);
          ctx.lineTo(x1, y1);
          ctx.stroke();
        }
        ctx.strokeStyle = color;
        ctx.lineWidth = thickness;
        ctx.beginPath();
        ctx.moveTo(x0, y0);
        ctx.lineTo(x1, y1);
        ctx.stroke();
      };

      drawArm(0, -1);
      drawArm(0, 1);
      drawArm(-1, 0);
      drawArm(1, 0);
    };

    raf = requestAnimationFrame(paint);
    return () => {
      if (raf) {
        cancelAnimationFrame(raf);
      }
    };
  }, [armLength, gap, thickness, outline, color, background]);

  return <canvas ref={ref} className={className} aria-hidden />;
}
