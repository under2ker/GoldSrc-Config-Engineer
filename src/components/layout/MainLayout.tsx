import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { getCurrentWindow } from "@tauri-apps/api/window";
import { isTauri } from "@tauri-apps/api/core";
import { AppCommandPalette } from "@/components/layout/AppCommandPalette";
import { Header } from "@/components/layout/Header";
import { KeyboardShortcutsDialog } from "@/components/layout/KeyboardShortcutsDialog";
import { Sidebar } from "@/components/layout/Sidebar";
import { DebugOverlay } from "@/components/layout/DebugOverlay";
import { PageRouteMotion } from "@/components/layout/PageRouteMotion";
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
import { getLayoutPage, useI18n } from "@/lib/i18n";
import { GCE_OPEN_HELP } from "@/lib/uiEvents";
import { useCatalogStore } from "@/stores/catalogStore";
import { useConfigStore } from "@/stores/configStore";
import { useProfileStore } from "@/stores/profileStore";

export function MainLayout() {
  const loc = useLocation();
  const navigate = useNavigate();
  const { t, locale } = useI18n();
  const page = getLayoutPage(locale, loc.pathname);
  const title = page?.title ?? t("layout.appName");
  const subtitle = page?.subtitle;
  const [commandOpen, setCommandOpen] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);
  const [debugOpen, setDebugOpen] = useState(false);

  useEffect(() => {
    logApp("info", `Раздел: ${loc.pathname}`);
  }, [loc.pathname]);

  /** После фоновой синхронизации каталогов JSON с GitHub — обновить режимы/пресеты в UI. */
  useEffect(() => {
    if (!isTauri()) return;
    let unlisten: (() => void) | undefined;
    void import("@tauri-apps/api/event").then(({ listen }) => {
      void listen("gce-catalog-synced", () => {
        void useCatalogStore.getState().load();
      }).then((fn) => {
        unlisten = fn;
      });
    });
    return () => {
      unlisten?.();
    };
  }, []);

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
          toast.message(t("toast.fullscreen"));
        }
        return;
      }

      if (e.key === "F12") {
        e.preventDefault();
        setDebugOpen((o) => !o);
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
        toast.message(t("toast.exportTitle"), { description: t("toast.exportDesc") });
      }
    };

    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [navigate, t]);

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
        {t("main.skipToContent")}
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
            className="min-h-0 flex-1 scroll-mt-0 overflow-auto p-[var(--space-page,1.5rem)]"
          >
            <PageRouteMotion />
          </main>
            </ContextMenuTrigger>
            <ContextMenuContent className="min-w-[200px]">
              <ContextMenuItem
                onSelect={() => {
                  navigate("/dashboard");
                }}
              >
                {t("contextMenu.home")}
              </ContextMenuItem>
              <ContextMenuItem
                onSelect={() => {
                  navigate("/quick-setup");
                }}
              >
                {t("contextMenu.quickSetup")}
              </ContextMenuItem>
              <ContextMenuItem
                onSelect={() => {
                  navigate("/modes");
                }}
              >
                {t("contextMenu.modes")}
              </ContextMenuItem>
              <ContextMenuItem
                onSelect={() => {
                  navigate("/compare");
                }}
              >
                {t("contextMenu.compare")}
              </ContextMenuItem>
              <ContextMenuItem
                onSelect={() => {
                  navigate("/presets");
                }}
              >
                {t("contextMenu.presets")}
              </ContextMenuItem>
              <ContextMenuItem
                onSelect={() => {
                  navigate("/crosshair");
                }}
              >
                {t("contextMenu.crosshair")}
              </ContextMenuItem>
              <ContextMenuItem
                onSelect={() => {
                  navigate("/sensitivity");
                }}
              >
                {t("contextMenu.sensitivity")}
              </ContextMenuItem>
              <ContextMenuItem
                onSelect={() => {
                  navigate("/export");
                }}
              >
                {t("contextMenu.export")}
              </ContextMenuItem>
              <ContextMenuItem
                onSelect={() => {
                  navigate("/import");
                }}
              >
                {t("contextMenu.import")}
              </ContextMenuItem>
              <ContextMenuItem
                onSelect={() => {
                  navigate("/launch-options");
                }}
              >
                {t("contextMenu.launchOptions")}
              </ContextMenuItem>
              <ContextMenuItem
                onSelect={() => {
                  navigate("/settings");
                }}
              >
                {t("contextMenu.settings")}
              </ContextMenuItem>
              <ContextMenuSeparator />
              <ContextMenuItem
                onSelect={() => {
                  setCommandOpen(true);
                }}
              >
                {t("contextMenu.commandPalette")}
              </ContextMenuItem>
              <ContextMenuItem
                onSelect={() => {
                  setHelpOpen(true);
                }}
              >
                {t("contextMenu.help")}
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
      <DebugOverlay open={debugOpen} onOpenChange={setDebugOpen} pathname={loc.pathname} />
      <SplashScreen />
    </div>
  );
}
