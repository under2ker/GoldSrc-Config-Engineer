/** Частые CVAR для быстрого копирования из палитры команд. */
export type CfgSnippet = {
  id: string;
  label: string;
  snippet: string;
  keywords?: string[];
};

export const CFG_CLIPBOARD_SNIPPETS: CfgSnippet[] = [
  {
    id: "rate",
    label: "rate 100000",
    snippet: "rate 100000",
    keywords: ["network", "сеть"],
  },
  {
    id: "cl_updaterate",
    label: "cl_updaterate 102",
    snippet: "cl_updaterate 102",
    keywords: ["net", "сеть", "cs"],
  },
  {
    id: "cl_cmdrate",
    label: "cl_cmdrate 105",
    snippet: "cl_cmdrate 105",
    keywords: ["net"],
  },
  {
    id: "fps_max",
    label: 'fps_max "100"',
    snippet: 'fps_max "100"',
    keywords: ["video", "кадры"],
  },
  {
    id: "cl_dynamiccrosshair",
    label: 'cl_dynamiccrosshair "0"',
    snippet: 'cl_dynamiccrosshair "0"',
    keywords: ["crosshair", "прицел"],
  },
  {
    id: "bind_attack",
    label: 'bind "MOUSE1" "+attack"',
    snippet: 'bind "MOUSE1" "+attack"',
    keywords: ["bind", "мышь"],
  },
  {
    id: "steam_launch_min",
    label: "Steam: -game cstrike -console +exec autoexec.cfg",
    snippet: "-game cstrike -console +exec autoexec.cfg",
    keywords: ["steam", "запуск", "launch", "hl"],
  },
  {
    id: "sensitivity_default",
    label: 'sensitivity "3"',
    snippet: 'sensitivity "3"',
    keywords: ["мышь", "sens", "dpi"],
  },
];
