import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Copy } from "lucide-react";
import { openCfgFile } from "@/lib/cfgFiles";
import { CfgTextPreview } from "@/components/common/CfgTextPreview";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { pageCaptionClass, pageLeadClass, pageShellClass } from "@/lib/layoutTokens";

const SAMPLE = `// Пример .cfg
bind "w" "+forward"
bind "MOUSE1" "+attack"
echo "preview loaded"
`;

export function PreviewPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const appliedFromNavRef = useRef(false);
  const [text, setText] = useState(SAMPLE);
  const [fontSize, setFontSize] = useState([14]);
  const [busy, setBusy] = useState(false);
  const [breakLongLines, setBreakLongLines] = useState(true);

  useEffect(() => {
    if (appliedFromNavRef.current) return;
    const st = location.state as { cfgText?: string } | null;
    if (st?.cfgText) {
      appliedFromNavRef.current = true;
      setText(st.cfgText);
      navigate(location.pathname, { replace: true, state: null });
      toast.message("Подставлен текст из профиля");
    }
  }, [location.pathname, location.state, navigate]);

  return (
    <div className={pageShellClass}>
      <p className={pageLeadClass}>
        Просмотр с подсветкой комментариев и типовых команд. Вставьте текст или откройте .cfg с диска.
      </p>

      <Card>
        <CardHeader>
          <CardTitle>Источник текста</CardTitle>
          <CardDescription>Текст никуда не отправляется — только на этом экране.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              loading={busy}
              onClick={() => {
                setBusy(true);
                void openCfgFile()
                  .then((picked) => {
                    if (!picked) {
                      toast.message("Файл не выбран");
                      return;
                    }
                    setText(picked.text);
                    toast.success("Файл загружен", { description: picked.path });
                  })
                  .finally(() => setBusy(false));
              }}
            >
              Открыть .cfg…
            </Button>
            <Button type="button" variant="outline" onClick={() => setText(SAMPLE)}>
              Подставить пример
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={() => {
                void navigator.clipboard.writeText(text).then(
                  () => toast.success("Текст скопирован"),
                  () => toast.error("Не удалось скопировать"),
                );
              }}
            >
              <Copy className="size-4" />
              Копировать всё
            </Button>
          </div>
          <div className="space-y-2">
            <Label htmlFor="preview-edit">Редактирование / вставка</Label>
            <Textarea
              id="preview-edit"
              value={text}
              onChange={(e) => setText(e.currentTarget.value)}
              className="min-h-[120px] font-mono text-xs"
              spellCheck={false}
            />
          </div>
          <div className="grid gap-2 sm:grid-cols-[minmax(0,10rem)_1fr_minmax(0,2.75rem)] sm:items-center sm:gap-3">
            <Label className="text-sm font-medium leading-snug sm:min-h-[2.5rem] sm:py-1">
              Размер шрифта превью
            </Label>
            <Slider
              min={13}
              max={20}
              step={1}
              value={fontSize}
              onValueChange={setFontSize}
              className="max-w-none py-1 sm:py-0"
            />
            <span className="text-right font-mono text-sm tabular-nums text-muted-foreground">{fontSize[0]}px</span>
          </div>
          <div className="flex items-center justify-between gap-4 rounded-lg border p-3">
            <div>
              <Label htmlFor="pv-wrap">Переносить длинные строки</Label>
              <p className={pageCaptionClass}>Выключите для длинных bind в одну строку.</p>
            </div>
            <Switch id="pv-wrap" checked={breakLongLines} onCheckedChange={setBreakLongLines} />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Превью</CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="min-h-[240px] h-[min(32rem,55vh)] rounded-md border border-border bg-muted/15">
            <CfgTextPreview
              text={text}
              className="p-3"
              fontSizePx={fontSize[0]}
              showLineNumbers
              breakLongLines={breakLongLines}
            />
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}
