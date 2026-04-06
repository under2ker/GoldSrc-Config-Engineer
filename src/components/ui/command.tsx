import * as React from "react";
import {
  Command as CommandPrimitive,
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "cmdk";
import { Search } from "lucide-react";
import { cn } from "@/lib/utils";

const Command = React.forwardRef<
  React.ElementRef<typeof CommandPrimitive>,
  React.ComponentPropsWithoutRef<typeof CommandPrimitive>
>(({ className, ...props }, ref) => (
  <CommandPrimitive
    ref={ref}
    className={cn(
      "flex h-full w-full flex-col overflow-hidden rounded-md bg-popover text-popover-foreground",
      className,
    )}
    {...props}
  />
));
Command.displayName = "Command";

const CommandDialogShell = CommandDialog;

const CommandInputField = React.forwardRef<
  React.ElementRef<typeof CommandInput>,
  React.ComponentPropsWithoutRef<typeof CommandInput>
>(({ className, ...props }, ref) => (
  <div className="flex items-center border-b border-border px-3" cmdk-input-wrapper="">
    <Search className="mr-2 size-4 shrink-0 opacity-50" aria-hidden />
    <CommandInput
      ref={ref}
      className={cn(
        "flex h-10 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50",
        className,
      )}
      {...props}
    />
  </div>
));
CommandInputField.displayName = "CommandInputField";

const CommandListStyled = React.forwardRef<
  React.ElementRef<typeof CommandList>,
  React.ComponentPropsWithoutRef<typeof CommandList>
>(({ className, ...props }, ref) => (
  <CommandList
    ref={ref}
    className={cn("max-h-[min(18rem,50vh)] overflow-y-auto overflow-x-hidden p-1", className)}
    {...props}
  />
));
CommandListStyled.displayName = "CommandListStyled";

const CommandEmptyStyled = React.forwardRef<
  React.ElementRef<typeof CommandEmpty>,
  React.ComponentPropsWithoutRef<typeof CommandEmpty>
>(({ className, ...props }, ref) => (
  <CommandEmpty ref={ref} className={cn("py-6 text-center text-sm text-muted-foreground", className)} {...props} />
));
CommandEmptyStyled.displayName = "CommandEmptyStyled";

const CommandGroupStyled = React.forwardRef<
  React.ElementRef<typeof CommandGroup>,
  React.ComponentPropsWithoutRef<typeof CommandGroup>
>(({ className, ...props }, ref) => (
  <CommandGroup
    ref={ref}
    className={cn(
      "overflow-hidden p-1 text-foreground [&_[cmdk-group-heading]]:px-2 [&_[cmdk-group-heading]]:py-1.5 [&_[cmdk-group-heading]]:text-xs [&_[cmdk-group-heading]]:font-medium [&_[cmdk-group-heading]]:text-muted-foreground",
      className,
    )}
    {...props}
  />
));
CommandGroupStyled.displayName = "CommandGroupStyled";

const CommandSeparatorStyled = React.forwardRef<
  React.ElementRef<typeof CommandSeparator>,
  React.ComponentPropsWithoutRef<typeof CommandSeparator>
>(({ className, ...props }, ref) => (
  <CommandSeparator ref={ref} className={cn("-mx-1 h-px bg-border", className)} {...props} />
));
CommandSeparatorStyled.displayName = "CommandSeparatorStyled";

const CommandItemStyled = React.forwardRef<
  React.ElementRef<typeof CommandItem>,
  React.ComponentPropsWithoutRef<typeof CommandItem>
>(({ className, ...props }, ref) => (
  <CommandItem
    ref={ref}
    className={cn(
      "relative flex cursor-default select-none items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-none data-[disabled=true]:pointer-events-none data-[selected=true]:bg-accent data-[selected=true]:text-accent-foreground data-[disabled=true]:opacity-50",
      className,
    )}
    {...props}
  />
));
CommandItemStyled.displayName = "CommandItemStyled";

export {
  Command,
  CommandDialogShell as CommandDialog,
  CommandEmptyStyled as CommandEmpty,
  CommandGroupStyled as CommandGroup,
  CommandInputField as CommandInput,
  CommandItemStyled as CommandItem,
  CommandListStyled as CommandList,
  CommandSeparatorStyled as CommandSeparator,
};
