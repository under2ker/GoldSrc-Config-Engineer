import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { GLOBAL_KEYBOARD_SHORTCUTS } from "@/lib/keyboardShortcutsMeta";

type KeyboardShortcutsDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

export function KeyboardShortcutsDialog({ open, onOpenChange }: KeyboardShortcutsDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Горячие клавиши</DialogTitle>
          <DialogDescription>
            Сочетания работают в любом разделе. В полях ввода часть сочетаний с Ctrl/⌘ не перехватывается, чтобы можно
            было править текст.
          </DialogDescription>
        </DialogHeader>
        <div className="rounded-md border">
          <table className="w-full text-sm">
            <tbody>
              {GLOBAL_KEYBOARD_SHORTCUTS.map((row) => (
                <tr key={row.action} className="border-b border-border last:border-0">
                  <td className="px-3 py-2 text-muted-foreground">{row.action}</td>
                  <td className="px-3 py-2 text-right font-mono text-xs">{row.keys}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </DialogContent>
    </Dialog>
  );
}
