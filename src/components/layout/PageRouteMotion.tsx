import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { Suspense } from "react";
import { Outlet, useLocation } from "react-router-dom";
import { AppErrorBoundary } from "@/components/layout/AppErrorBoundary";
import { PageLoading } from "@/components/layout/PageLoading";
import { useAppStore } from "@/stores/appStore";

/** Обёртка маршрута: лёгкий fade/slide при смене раздела; уважает «Уменьшить анимации» и `prefers-reduced-motion`. */
export function PageRouteMotion() {
  const loc = useLocation();
  const reduceMotionUser = useAppStore((s) => s.reduceMotion);
  const reduceMotionSystem = useReducedMotion();
  const motionOff = reduceMotionUser || Boolean(reduceMotionSystem);

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={loc.pathname}
        className="min-h-0"
        initial={motionOff ? false : { opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        exit={motionOff ? { opacity: 1, y: 0 } : { opacity: 0, y: -4 }}
        transition={
          motionOff
            ? { duration: 0 }
            : { duration: 0.18, ease: [0.4, 0, 0.2, 1] }
        }
      >
        <Suspense fallback={<PageLoading />}>
          <AppErrorBoundary>
            <Outlet />
          </AppErrorBoundary>
        </Suspense>
      </motion.div>
    </AnimatePresence>
  );
}
