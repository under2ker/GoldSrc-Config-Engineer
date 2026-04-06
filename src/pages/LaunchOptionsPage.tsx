import { useMemo, useState } from "react";
import { toast } from "sonner";
import { Copy, Rocket } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { pageCaptionClass, pageLeadClass, pageShellClass } from "@/lib/layoutTokens";

function buildLaunchLine(opts: {
  gameCstrike: boolean;
  console: boolean;
  novid: boolean;
  noforce: boolean;
  execAutoexec: boolean;
  freq: string;
  dxlevel: string;
  heapsize: string;
  windowed: boolean;
  width: string;
  height: string;
  custom: string;
}): string {
  const parts: string[] = [];
  if (opts.gameCstrike) {
    parts.push("-game", "cstrike");
  }
  if (opts.console) {
    parts.push("-console");
  }
  if (opts.novid) {
    parts.push("-novid");
  }
  if (opts.noforce) {
    parts.push("-noforcemparms", "-noforcemspd");
  }
  if (opts.execAutoexec) {
    parts.push("+exec", "autoexec.cfg");
  }
  const freq = opts.freq.trim();
  if (freq) {
    parts.push("-freq", freq);
  }
  const dx = opts.dxlevel.trim();
  if (dx) {
    parts.push("-dxlevel", dx);
  }
  const heap = opts.heapsize.trim();
  if (heap) {
    parts.push("-heapsize", heap);
  }
  if (opts.windowed) {
    parts.push("-sw");
  } else {
    parts.push("-full");
  }
  const w = opts.width.trim();
  const h = opts.height.trim();
  if (w && h) {
    parts.push("-w", w, "-h", h);
  }
  const extra = opts.custom
    .trim()
    .split(/\s+/)
    .filter((t) => t.length > 0);
  parts.push(...extra);
  return parts.join(" ");
}

export function LaunchOptionsPage() {
  const [gameCstrike, setGameCstrike] = useState(true);
  const [console, setConsole] = useState(true);
  const [novid, setNovid] = useState(false);
  const [noforce, setNoforce] = useState(true);
  const [execAutoexec, setExecAutoexec] = useState(true);
  const [freq, setFreq] = useState("144");
  const [dxlevel, setDxlevel] = useState("");
  const [heapsize, setHeapsize] = useState("");
  const [windowed, setWindowed] = useState(false);
  const [width, setWidth] = useState("1280");
  const [height, setHeight] = useState("960");
  const [custom, setCustom] = useState("");

  const line = useMemo(
    () =>
      buildLaunchLine({
        gameCstrike,
        console,
        novid,
        noforce,
        execAutoexec,
        freq,
        dxlevel,
        heapsize,
        windowed,
        width,
        height,
        custom,
      }),
    [
      gameCstrike,
      console,
      novid,
      noforce,
      execAutoexec,
      freq,
      dxlevel,
      heapsize,
      windowed,
      width,
      height,
      custom,
    ],
  );

  async function copyLine() {
    try {
      await navigator.clipboard.writeText(line);
      toast.success("Скопировано", { description: "Вставьте в Steam → CS 1.6 → Свойства → Параметры запуска" });
    } catch {
      toast.error("Не удалось скопировать");
    }
  }

  return (
    <div className={pageShellClass}>
      <div className="flex flex-wrap items-start gap-3">
        <div className="flex size-10 shrink-0 items-center justify-center rounded-xl border border-primary/30 bg-primary/10">
          <Rocket className="size-5 text-primary" strokeWidth={1.75} aria-hidden />
        </div>
        <div className="min-w-0 flex-1 space-y-1">
          <p className="text-sm font-medium text-foreground">Параметры запуска (Steam / GoldSrc)</p>
          <p className={pageLeadClass}>
            Соберите строку для поля «Параметры запуска» у Counter-Strike в библиотеке Steam. Значения ориентировочные —
            проверьте под свою ОС и железо.
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle className="text-base">Частые флаги</CardTitle>
            <CardDescription>Переключатели добавляют или убирают типичные аргументы.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between gap-4 rounded-lg border p-3">
              <div>
                <Label htmlFor="lo-game">-game cstrike</Label>
                <p className={pageCaptionClass}>Старт в модификации Counter-Strike.</p>
              </div>
              <Switch id="lo-game" checked={gameCstrike} onCheckedChange={setGameCstrike} />
            </div>
            <div className="flex items-center justify-between gap-4 rounded-lg border p-3">
              <div>
                <Label htmlFor="lo-console">-console</Label>
                <p className={pageCaptionClass}>Открыть консоль при запуске.</p>
              </div>
              <Switch id="lo-console" checked={console} onCheckedChange={setConsole} />
            </div>
            <div className="flex items-center justify-between gap-4 rounded-lg border p-3">
              <div>
                <Label htmlFor="lo-novid">-novid</Label>
                <p className={pageCaptionClass}>Пропуск видео заставки (если поддерживается).</p>
              </div>
              <Switch id="lo-novid" checked={novid} onCheckedChange={setNovid} />
            </div>
            <div className="flex items-center justify-between gap-4 rounded-lg border p-3">
              <div>
                <Label htmlFor="lo-noforce">-noforcemparms / -noforcemspd</Label>
                <p className={pageCaptionClass}>Не перехватывать настройки мыши Windows.</p>
              </div>
              <Switch id="lo-noforce" checked={noforce} onCheckedChange={setNoforce} />
            </div>
            <div className="flex items-center justify-between gap-4 rounded-lg border p-3">
              <div>
                <Label htmlFor="lo-exec">+exec autoexec.cfg</Label>
                <p className={pageCaptionClass}>Автозапуск вашего конфига из каталога CS.</p>
              </div>
              <Switch id="lo-exec" checked={execAutoexec} onCheckedChange={setExecAutoexec} />
            </div>
            <div className="flex items-center justify-between gap-4 rounded-lg border p-3">
              <div>
                <Label htmlFor="lo-sw">Оконный режим (-sw)</Label>
                <p className={pageCaptionClass}>Иначе — полноэкранный (-full).</p>
              </div>
              <Switch id="lo-sw" checked={windowed} onCheckedChange={setWindowed} />
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle className="text-base">Числа и свой текст</CardTitle>
            <CardDescription>Оставьте поле пустым, чтобы не добавлять флаг.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="lo-freq">-freq (Гц монитора)</Label>
                <Input id="lo-freq" inputMode="numeric" value={freq} onChange={(e) => setFreq(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="lo-dx">-dxlevel</Label>
                <Input
                  id="lo-dx"
                  inputMode="numeric"
                  placeholder="напр. 81"
                  value={dxlevel}
                  onChange={(e) => setDxlevel(e.target.value)}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="lo-heapsize">-heapsize (КБ памяти)</Label>
              <Input
                id="lo-heapsize"
                inputMode="numeric"
                placeholder="напр. 262144 (512 МБ)"
                value={heapsize}
                onChange={(e) => setHeapsize(e.target.value)}
              />
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="lo-w">-w</Label>
                <Input id="lo-w" inputMode="numeric" value={width} onChange={(e) => setWidth(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="lo-h">-h</Label>
                <Input id="lo-h" inputMode="numeric" value={height} onChange={(e) => setHeight(e.target.value)} />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="lo-custom">Свои аргументы</Label>
              <Textarea
                id="lo-custom"
                placeholder="-nofbo … (через пробел)"
                rows={3}
                className="font-mono text-xs"
                value={custom}
                onChange={(e) => setCustom(e.target.value)}
              />
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="border-primary/20 shadow-sm">
        <CardHeader className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <CardTitle className="text-base">Итоговая строка</CardTitle>
            <CardDescription>Вставьте в Steam целиком одной строкой.</CardDescription>
          </div>
          <Button type="button" variant="secondary" size="sm" className="shrink-0 gap-2" onClick={() => void copyLine()}>
            <Copy className="size-4" />
            Копировать
          </Button>
        </CardHeader>
        <CardContent>
          <pre className="max-h-40 overflow-auto whitespace-pre-wrap break-all rounded-lg border bg-muted/40 p-3 font-mono text-xs leading-relaxed">
            {line || "(пусто — включите хотя бы один параметр)"}
          </pre>
        </CardContent>
      </Card>
    </div>
  );
}
