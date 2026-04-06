import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { isTauri } from "@tauri-apps/api/core";
import { toast } from "sonner";
import pkg from "../../package.json";
import { appSettingsGet, appSettingsSet, detectGameInstallation, getAppPathsInfo, ping } from "@/lib/api";
import type { AppPathsInfo } from "@/types/api";
import { HISTORY_MAX_ENTRIES_KEY } from "@/lib/settingsKeys";
import { GLOBAL_KEYBOARD_SHORTCUTS } from "@/lib/keyboardShortcutsMeta";
import { useAppStore } from "@/stores/appStore";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { openPath } from "@tauri-apps/plugin-opener";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { pageCaptionClass, pageLeadClass, pageShellNarrowClass } from "@/lib/layoutTokens";

export function SettingsPage() {
  const [gameBusy, setGameBusy] = useState(false);
  const [gamePath, setGamePath] = useState<string | null>(null);
  const [gameHint, setGameHint] = useState<string | null>(null);

  const theme = useAppStore((s) => s.theme);
  const setTheme = useAppStore((s) => s.setTheme);
  const locale = useAppStore((s) => s.locale);
  const setLocale = useAppStore((s) => s.setLocale);
  const reduceMotion = useAppStore((s) => s.reduceMotion);
  const setReduceMotion = useAppStore((s) => s.setReduceMotion);
  const verboseLog = useAppStore((s) => s.verboseLog);
  const setVerboseLog = useAppStore((s) => s.setVerboseLog);

  const [historyMaxStr, setHistoryMaxStr] = useState("100");
  const [appPaths, setAppPaths] = useState<AppPathsInfo | null>(null);
  const [backendPing, setBackendPing] = useState<string | null>(null);

  useEffect(() => {
    if (!isTauri()) return;
    void appSettingsGet(HISTORY_MAX_ENTRIES_KEY).then((v) => {
      if (v != null && v.trim() !== "") setHistoryMaxStr(v.trim());
    });
  }, []);

  useEffect(() => {
    if (!isTauri()) return;
    void getAppPathsInfo()
      .then((p) => setAppPaths(p))
      .catch(() => setAppPaths(null));
  }, []);

  useEffect(() => {
    if (!isTauri()) return;
    void ping()
      .then((s) => setBackendPing(s))
      .catch(() => setBackendPing(null));
  }, []);

  async function copyPathLine(label: string, path: string) {
    try {
      await navigator.clipboard.writeText(path);
      toast.success("Скопировано", { description: label });
    } catch {
      toast.error("Не удалось скопировать в буфер");
    }
  }

  async function saveHistoryMax() {
    const n = Number.parseInt(historyMaxStr, 10);
    if (Number.isNaN(n) || n < 10 || n > 500) {
      toast.error("Лимит истории", { description: "Введите число от 10 до 500." });
      return;
    }
    await appSettingsSet(HISTORY_MAX_ENTRIES_KEY, String(n));
    toast.success("Сохранено", { description: `Хранится до ${n} снимков.` });
  }

  return (
    <div className={pageShellNarrowClass}>
      <div>
        <p className={pageLeadClass}>
          Внешний вид, язык и справка. Настройки хранятся только на этом устройстве.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Внешний вид</CardTitle>
          <CardDescription>Тёмная или светлая тема оформления.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between gap-4 rounded-lg border p-3">
            <div className="space-y-0.5">
              <Label htmlFor="settings-dark-switch">Тёмная тема</Label>
              <p className={pageCaptionClass}>Быстрый переключатель (дублирует список ниже).</p>
            </div>
            <Switch
              id="settings-dark-switch"
              checked={theme === "dark"}
              onCheckedChange={(on) => setTheme(on ? "dark" : "light")}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="settings-theme">Тема (список)</Label>
            <Select value={theme} onValueChange={(v) => setTheme(v as "dark" | "light")}>
              <SelectTrigger id="settings-theme">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="dark">Тёмная (midnight)</SelectItem>
                <SelectItem value="light">Светлая</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Анимации</CardTitle>
          <CardDescription>
            Отключает вход страницы <code className="text-xs">.page-enter</code> и дополняет системную настройку{" "}
            <span className={pageCaptionClass}>prefers-reduced-motion</span>.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between gap-4 rounded-lg border p-3">
            <div className="space-y-0.5">
              <Label htmlFor="settings-reduce-motion">Уменьшить анимации</Label>
              <p className={pageCaptionClass}>
                Сохраняется на устройстве; при первом запуске учитывается системная настройка уменьшения анимаций.
              </p>
            </div>
            <Switch
              id="settings-reduce-motion"
              checked={reduceMotion}
              onCheckedChange={(on) => setReduceMotion(on)}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Журнал приложения</CardTitle>
          <CardDescription>
            Подробные сообщения в служебный журнал и список последних записей на странице «Диагностика».
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between gap-4 rounded-lg border p-3">
            <div className="space-y-0.5">
              <Label htmlFor="settings-verbose">Подробный журнал (verbose)</Label>
              <p className={pageCaptionClass}>
                Полезно при отладке; в обычной работе оставьте выключенным.
              </p>
            </div>
            <Switch
              id="settings-verbose"
              checked={verboseLog}
              onCheckedChange={(on) => setVerboseLog(on)}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Язык интерфейса</CardTitle>
          <CardDescription>
            Сейчас задаёт атрибут <code className="text-xs">lang</code> у документа; полный i18n — позже.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="settings-locale">Язык</Label>
            <Select value={locale} onValueChange={(v) => setLocale(v as "ru" | "en")}>
              <SelectTrigger id="settings-locale">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ru">Русский</SelectItem>
                <SelectItem value="en">English</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Горячие клавиши</CardTitle>
          <CardDescription>
            Те же сочетания, что в диалоге <span className="font-medium text-foreground">F1</span>.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <table className="w-full text-sm">
              <tbody>
                {GLOBAL_KEYBOARD_SHORTCUTS.map((row) => (
                  <tr key={row.action} className="border-b border-border last:border-0">
                    <td className="max-w-[55%] px-3 py-2 text-muted-foreground">{row.action}</td>
                    <td className="px-3 py-2 text-right font-mono text-xs">{row.keys}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Скриптовые алиасы</CardTitle>
          <CardDescription>
            Каталог из <code className="text-xs">data/aliases.json</code> влияет на блок{" "}
            <code className="text-xs">config/aliases.cfg</code> при экспорте.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button type="button" variant="secondary" asChild>
            <Link to="/aliases">Настроить пресет алиасов</Link>
          </Button>
        </CardContent>
      </Card>

      <Separator />

      {isTauri() ? (
        <Card>
          <CardHeader>
            <CardTitle>История снимков конфига</CardTitle>
            <CardDescription>
              Сколько последних записей хранить в локальной базе (после каждого нового снимка старые удаляются при
              превышении лимита). Диапазон: 10–500.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-3 sm:flex-row sm:items-end">
            <div className="min-w-0 flex-1 space-y-2">
              <Label htmlFor="settings-history-max">Максимум записей</Label>
              <Input
                id="settings-history-max"
                type="number"
                min={10}
                max={500}
                inputMode="numeric"
                value={historyMaxStr}
                onChange={(e) => setHistoryMaxStr(e.target.value)}
                onBlur={() => void saveHistoryMax()}
              />
            </div>
            <Button type="button" variant="secondary" onClick={() => void saveHistoryMax()}>
              Сохранить
            </Button>
          </CardContent>
        </Card>
      ) : null}

      {isTauri() && appPaths ? (
        <Card>
          <CardHeader>
            <CardTitle>Данные приложения</CardTitle>
            <CardDescription>
              Каталог с локальной базой SQLite (профили и история снимков). Подходит для резервной копии или обращения в
              поддержку.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="settings-app-data-dir">Каталог данных</Label>
              <div className="flex flex-col gap-2 lg:flex-row lg:items-start">
                <p
                  id="settings-app-data-dir"
                  className="min-w-0 flex-1 break-all rounded-md border bg-muted/30 px-3 py-2 font-mono text-xs"
                >
                  {appPaths.app_data_dir}
                </p>
                <div className="flex flex-wrap gap-2 shrink-0">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      void openPath(appPaths.app_data_dir).catch((err: unknown) => {
                        toast.error("Не удалось открыть каталог", { description: String(err) });
                      });
                    }}
                  >
                    Открыть
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => void copyPathLine("Каталог данных", appPaths.app_data_dir)}
                  >
                    Копировать
                  </Button>
                </div>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="settings-sqlite-path">Файл базы SQLite</Label>
              <div className="flex flex-col gap-2 lg:flex-row lg:items-start">
                <p
                  id="settings-sqlite-path"
                  className="min-w-0 flex-1 break-all rounded-md border bg-muted/30 px-3 py-2 font-mono text-xs"
                >
                  {appPaths.sqlite_db_path}
                </p>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="shrink-0"
                  onClick={() => void copyPathLine("Путь к базе", appPaths.sqlite_db_path)}
                >
                  Копировать
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      ) : null}

      {isTauri() ? (
        <Card>
          <CardHeader>
            <CardTitle>Папка игры</CardTitle>
            <CardDescription>
              Поиск типовой установки Counter-Strike (Steam) на этом компьютере. Для записи конфигов используйте экспорт →
              «Записать в папку» и укажите каталог <code className="text-xs">cstrike</code>.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button
              type="button"
              variant="secondary"
              loading={gameBusy}
              onClick={() => {
                setGameBusy(true);
                void detectGameInstallation()
                  .then((r) => {
                    setGamePath(r.path);
                    setGameHint(r.hint);
                  })
                  .finally(() => setGameBusy(false));
              }}
            >
              Найти установку…
            </Button>
            {gameHint ? <p className="text-sm text-muted-foreground">{gameHint}</p> : null}
            {gamePath ? (
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
                <p className="min-w-0 flex-1 break-all rounded-md border bg-muted/30 px-3 py-2 font-mono text-xs">
                  {gamePath}
                </p>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="shrink-0"
                  onClick={() => {
                    void openPath(gamePath).catch((err: unknown) => {
                      toast.error("Не удалось открыть папку", { description: String(err) });
                    });
                  }}
                >
                  Открыть в проводнике
                </Button>
              </div>
            ) : null}
          </CardContent>
        </Card>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>О приложении</CardTitle>
          <CardDescription>Локальный помощник по конфигам CS 1.6 и GoldSrc.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p className="flex flex-wrap items-center gap-2">
            Версия <Badge variant="secondary">{pkg.version}</Badge>
          </p>
          {isTauri() && backendPing ? (
            <div className="flex flex-col gap-2 sm:flex-row sm:items-start">
              <p className="min-w-0 flex-1 break-all rounded-md border border-border/60 bg-muted/20 px-2 py-1.5 font-mono text-xs text-muted-foreground">
                {backendPing}
              </p>
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="shrink-0"
                onClick={() => void copyPathLine("Ответ ядра", backendPing)}
              >
                Копировать
              </Button>
            </div>
          ) : null}
          <p className="text-muted-foreground">
            В оконном режиме сверху может отображаться собственная полоса заголовка с кнопками свернуть / развернуть /
            закрыть.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
