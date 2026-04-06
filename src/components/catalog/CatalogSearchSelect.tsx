import * as React from "react";
import { Check, ChevronsUpDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import type { GameModeSummary, ProPresetSummary } from "@/types/api";

export type ModeSearchSelectProps = {
  modes: GameModeSummary[];
  value: string;
  onValueChange: (id: string) => void;
  disabled?: boolean;
  id?: string;
  className?: string;
  placeholder?: string;
};

/** Режим игры: выпадающий список с поиском по названию (RU/EN) и id. */
export function ModeSearchSelect({
  modes,
  value,
  onValueChange,
  disabled,
  id,
  className,
  placeholder = "Выберите режим",
}: ModeSearchSelectProps) {
  const [open, setOpen] = React.useState(false);
  const selected = modes.find((m) => m.id === value);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          id={id}
          type="button"
          variant="outline"
          role="combobox"
          aria-expanded={open}
          disabled={disabled}
          className={cn(
            "h-9 w-full justify-between border-input bg-transparent px-3 font-normal shadow-sm hover:bg-transparent",
            className,
          )}
        >
          <span className="truncate text-left">
            {selected ? (
              <>
                {selected.name_ru}{" "}
                <span className="text-muted-foreground">({selected.name_en})</span>
              </>
            ) : (
              <span className="text-muted-foreground">{placeholder}</span>
            )}
          </span>
          <ChevronsUpDown className="ml-2 size-4 shrink-0 opacity-50" aria-hidden />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[var(--radix-popover-trigger-width)] max-w-[min(100vw-2rem,28rem)] p-0" align="start">
        <Command>
          <CommandInput placeholder="Поиск режима…" />
          <CommandList>
            <CommandEmpty>Ничего не найдено.</CommandEmpty>
            <CommandGroup>
              {modes.map((m) => (
                <CommandItem
                  key={m.id}
                  value={m.id}
                  keywords={[m.name_ru, m.name_en, m.id]}
                  onSelect={(current) => {
                    onValueChange(current);
                    setOpen(false);
                  }}
                >
                  <Check className={cn("size-4 shrink-0", value === m.id ? "opacity-100" : "opacity-0")} aria-hidden />
                  <span className="min-w-0 truncate">
                    {m.name_ru}{" "}
                    <span className="text-muted-foreground">({m.name_en})</span>
                  </span>
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}

export type PresetSearchSelectProps = {
  presets: ProPresetSummary[];
  value: string;
  onValueChange: (id: string) => void;
  disabled?: boolean;
  id?: string;
  className?: string;
  placeholder?: string;
};

/** Про-пресет: выпадающий список с поиском по имени, команде, роли. */
export function PresetSearchSelect({
  presets,
  value,
  onValueChange,
  disabled,
  id,
  className,
  placeholder = "Выберите пресет",
}: PresetSearchSelectProps) {
  const [open, setOpen] = React.useState(false);
  const selected = presets.find((p) => p.id === value);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          id={id}
          type="button"
          variant="outline"
          role="combobox"
          aria-expanded={open}
          disabled={disabled}
          className={cn(
            "h-9 w-full justify-between border-input bg-transparent px-3 font-normal shadow-sm hover:bg-transparent",
            className,
          )}
        >
          <span className="truncate text-left">
            {selected ? (
              <>
                {selected.name}{" "}
                <span className="text-muted-foreground">
                  — {selected.team} / {selected.role}
                </span>
              </>
            ) : (
              <span className="text-muted-foreground">{placeholder}</span>
            )}
          </span>
          <ChevronsUpDown className="ml-2 size-4 shrink-0 opacity-50" aria-hidden />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[var(--radix-popover-trigger-width)] max-w-[min(100vw-2rem,28rem)] p-0" align="start">
        <Command>
          <CommandInput placeholder="Поиск пресета…" />
          <CommandList>
            <CommandEmpty>Ничего не найдено.</CommandEmpty>
            <CommandGroup>
              {presets.map((p) => (
                <CommandItem
                  key={p.id}
                  value={p.id}
                  keywords={[p.name, p.team, p.role, p.id]}
                  onSelect={(current) => {
                    onValueChange(current);
                    setOpen(false);
                  }}
                >
                  <Check className={cn("size-4 shrink-0", value === p.id ? "opacity-100" : "opacity-0")} aria-hidden />
                  <span className="min-w-0 truncate">
                    {p.name}{" "}
                    <span className="text-muted-foreground">
                      — {p.team} / {p.role}
                    </span>
                  </span>
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
