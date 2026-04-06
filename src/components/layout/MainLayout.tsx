import { Suspense, useEffect, useState } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { getCurrentWindow } from "@tauri-apps/api/window";
import { isTauri } from "@tauri-apps/api/core";
import { AppCommandPalette } from "@/components/layout/AppCommandPalette";
import { AppErrorBoundary } from "@/components/layout/AppErrorBoundary";
import { Header } from "@/components/layout/Header";
import { KeyboardShortcutsDialog } from "@/components/layout/KeyboardShortcutsDialog";
import { PageLoading } from "@/components/layout/PageLoading";
import { Sidebar } from "@/components/layout/Sidebar";
import { SplashScreen } from "@/components/layout/SplashScreen";
import { TitleBar } from "@/components/layout/TitleBar";
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuSeparator,
  ContextMenuTrigger,
} from "@/components/ui/context-menu";
import { readAliasPrefs, writeAliasPrefs } from "@/lib/aliasPrefs";
import { logApp } from "@/lib/appLogger";
import { GCE_OPEN_HELP } from "@/lib/uiEvents";
import { useConfigStore } from "@/stores/configStore";
import { useProfileStore } from "@/stores/profileStore";

const titles: Record<string, string> = {
  "/dashboard": "Главная",
  "/quick-setup": "Быстрая настройка",
  "/modes": "Режимы",
  "/presets": "Про-пресеты",
  "/crosshair": "Прицел",
  "/sensitivity": "Чувствительность мыши",
  "/compare": "Сравнение конфигов",
  "/export": "Экспорт",
  "/import": "Импорт",
  "/launch-options": "Параметры запуска",
  "/preview": "Просмотр",
  "/diagnostics": "Диагностика",
  "/settings": "Настройки",
  "/profiles": "Профили",
  "/aliases": "Алиасы",
};

/** Подзаголовок шапки (visual set §3.2.1) — кратко о назначении раздела. */
const pageSubtitles: Partial<Record<string, string>> = {
  "/dashboard": "Обзор, быстрые действия и недавние .cfg",
  "/quick-setup": "Мастер: режим, пресет, генерация и сохранение",
  "/modes": "Каталог режимов и генерация одного .cfg",
  "/presets": "Про-пресеты по командам и ролям",
  "/crosshair": "Превью прицела и ориентиры для CVAR",
  "/sensitivity": "См на 360° и индекс для сравнения с другими конфигами",
  "/compare": "Построчное сравнение двух текстов конфигов",
  "/export": "Один файл или модульный набор в папку",
  "/import": "Разбор .cfg и черновик для редактора",
  "/launch-options": "Параметры запуска Steam / hl.exe",
  "/preview": "Подсветка синтаксиса, текст не уходит в сеть",
  "/diagnostics": "Проверка окружения и журнал сессии",
  "/settings": "Тема, язык, данные приложения и папка игры",
  "/profiles": "Локальные профили и история снимков конфигурации",
  "/aliases": "Пресеты алиасов и генерация aliases.cfg",
};

export function MainLayout() {
  const loc = useLocation();
  const navigate = useNavigate();
  const title = titles[loc.pathname] ?? "GoldSrc Config Engineer";
  const subtitle = pageSubtitles[loc.pathname];
  const [commandOpen, setCommandOpen] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);

  useEffect(() => {
    logApp("info", `Раздел: ${loc.pathname}`);
  }, [loc.pathname]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "F1") {
        e.preventDefault();
        setHelpOpen(true);
        return;
      }

      if (e.key === "F11") {
        e.preventDefault();
        if (isTauri()) {
          const w = getCurrentWindow();
          void w.isFullscreen().then((fs) => {
            void w.setFullscreen(!fs);
          });
        } else {
          toast.message("Полноэкранный режим (F11) доступен в программе для Windows / macOS");
        }
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === "a") {
        const target = e.target as HTMLElement | null;
        const tag = target?.tagName ?? "";
        const inField =
          tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || target?.isContentEditable;
        if (!inField) {
          e.preventDefault();
          navigate("/aliases");
        }
        return;
      }

      if (!e.metaKey && !e.ctrlKey) {
        return;
      }

      const k = e.key.toLowerCase();
      const target = e.target as HTMLElement | null;
      const tag = target?.tagName ?? "";
      const inField =
        tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || target?.isContentEditable;
      if (inField && !e.shiftKey && ["e", "i", "s", "l"].includes(k)) {
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.shiftKey && k === "p") {
        if (!inField) {
          e.preventDefault();
          navigate("/profiles");
        }
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.shiftKey && k === "d") {
        if (!inField) {
          e.preventDefault();
          navigate("/diagnostics");
        }
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.shiftKey && k === "s") {
        if (!inField) {
          e.preventDefault();
          navigate("/settings");
        }
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.shiftKey && k === "h") {
        if (!inField) {
          e.preventDefault();
          navigate("/dashboard");
        }
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.shiftKey && k === "q") {
        if (!inField) {
          e.preventDefault();
          navigate("/quick-setup");
        }
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.shiftKey && k === "m") {
        if (!inField) {
          e.preventDefault();
          navigate("/modes");
        }
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.shiftKey && k === "g") {
        if (!inField) {
          e.preventDefault();
          navigate("/compare");
        }
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.shiftKey && k === "b") {
        if (!inField) {
          e.preventDefault();
          navigate("/presets");
        }
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.shiftKey && k === "x") {
        if (!inField) {
          e.preventDefault();
          navigate("/crosshair");
        }
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.shiftKey && k === "t") {
        if (!inField) {
          e.preventDefault();
          navigate("/sensitivity");
        }
        return;
      }

      if (k === "k") {
        e.preventDefault();
        setCommandOpen(true);
        return;
      }
      if (k === "e") {
        e.preventDefault();
        navigate("/export");
        return;
      }
      if (k === "i") {
        e.preventDefault();
        navigate("/import");
        return;
      }
      if (k === "l") {
        e.preventDefault();
        navigate("/launch-options");
        return;
      }
      if (k === "s" && !e.shiftKey) {
        e.preventDefault();
        navigate("/export");
        toast.message("Экспорт .cfg", { description: "Сформируйте файл и нажмите «Сохранить как…»." });
      }
    };

    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [navigate]);

  useEffect(() => {
    const openHelp = () => setHelpOpen(true);
    window.addEventListener(GCE_OPEN_HELP, openHelp);
    return () => window.removeEventListener(GCE_OPEN_HELP, openHelp);
  }, []);

  useEffect(() => {
    if (!isTauri()) return;
    void useProfileStore.getState().refreshProfiles();
  }, []);

  useEffect(() => {
    const saved = readAliasPrefs();
    if (!saved) return;
    useConfigStore.setState({
      ...(saved.aliasPreset != null ? { aliasPreset: saved.aliasPreset } : {}),
      ...(typeof saved.includePractice === "boolean" ? { includePractice: saved.includePractice } : {}),
      ...(saved.aliasEnabled != null ? { aliasEnabled: saved.aliasEnabled } : {}),
    });
  }, []);

  useEffect(() => {
    let prev = "";
    return useConfigStore.subscribe((s) => {
      const snap = JSON.stringify({
        aliasPreset: s.aliasPreset,
        includePractice: s.includePractice,
        aliasEnabled: s.aliasEnabled,
      });
      if (snap === prev) return;
      prev = snap;
      writeAliasPrefs({
        aliasPreset: s.aliasPreset,
        includePractice: s.includePractice,
        aliasEnabled: s.aliasEnabled,
      });
    });
  }, []);

  return (
    <div className="flex h-svh w-full flex-col overflow-hidden bg-background text-foreground">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-3 focus:top-12 focus:z-[80] focus:rounded-md focus:bg-primary focus:px-3 focus:py-2 focus:text-sm focus:font-medium focus:text-primary-foreground focus:shadow-md"
      >
        К основному содержимому
      </a>
      <TitleBar />
      <div className="flex min-h-0 min-w-0 flex-1 overflow-x-auto overflow-y-hidden">
        <div className="flex min-h-0 min-w-[1280px] flex-1 overflow-hidden">
        <Sidebar />
        <div className="flex min-w-0 flex-1 flex-col">
          <Header title={title} subtitle={subtitle} onOpenCommandPalette={() => setCommandOpen(true)} />
          <ContextMenu>
            <ContextMenuTrigger asChild>
          <main
            id="main-content"
            key={loc.pathname}
            className="page-enter min-h-0 flex-1 scroll-mt-0 overflow-auto p-[var(--space-page,1.5rem)]"
          >
            <Suspense fallback={<PageLoading />}>
              <AppErrorBoundary>
                <Outlet />
              </AppErrorBoundary>
            </Suspense>
          </main>
            </ContextMenuTrigger>
            <ContextMenuContent className="min-w-[200px]">
              <ContextMenuItem
                onSelect={() => {
                  navigate("/dashboard");
                }}
              >
                Главная
              </ContextMenuItem>
              <ContextMenuItem
                onSelect={() => {
                  navigate("/quick-setup");
                }}
              >
                Быстрая настройка…
              </ContextMenuItem>
              <ContextMenuItem
                onSelect={() => {
                  navigate("/modes");
                }}
              >
                Режимы…
              </ContextMenuItem>
              <ContextMenuItem
                onSelect={() => {
                  navigate("/compare");
                }}
              >
                Сравнение конфигов…
              </ContextMenuItem>
              <ContextMenuItem
                onSelect={() => {
                  navigate("/presets");
                }}
              >
                Про-пресеты…
              </ContextMenuItem>
              <ContextMenuItem
                onSelect={() => {
                  navigate("/crosshair");
                }}
              >
                Прицел…
              </ContextMenuItem>
              <ContextMenuItem
                onSelect={() => {
                  navigate("/sensitivity");
                }}
              >
                Чувствительность мыши…
              </ContextMenuItem>
              <ContextMenuItem
                onSelect={() => {
                  navigate("/export");
                }}
              >
                Экспорт…
              </ContextMenuItem>
              <ContextMenuItem
                onSelect={() => {
                  navigate("/import");
                }}
              >
                Импорт…
              </ContextMenuItem>
              <ContextMenuItem
                onSelect={() => {
                  navigate("/launch-options");
                }}
              >
                Параметры запуска Steam…
              </ContextMenuItem>
              <ContextMenuItem
                onSelect={() => {
                  navigate("/settings");
                }}
              >
                Настройки…
              </ContextMenuItem>
              <ContextMenuSeparator />
              <ContextMenuItem
                onSelect={() => {
                  setCommandOpen(true);
                }}
              >
                Палитра команд
              </ContextMenuItem>
              <ContextMenuItem
                onSelect={() => {
                  setHelpOpen(true);
                }}
              >
                Справка (F1)
              </ContextMenuItem>
            </ContextMenuContent>
          </ContextMenu>
        </div>
        </div>
      </div>
      <AppCommandPalette
        open={commandOpen}
        onOpenChange={setCommandOpen}
        onOpenHelp={() => {
          setCommandOpen(false);
          setHelpOpen(true);
        }}
      />
      <KeyboardShortcutsDialog open={helpOpen} onOpenChange={setHelpOpen} />
      <SplashScreen />
    </div>
  );
}
