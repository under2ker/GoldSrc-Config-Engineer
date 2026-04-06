import type { CfgConfigParsed } from "@/types/api";

/** Лёгкий разбор `.cfg` в браузере (ориентир: `goldsr_cfg_core::parse_cfg_text_to_config`). */
export function parseCfgTextForCompleteness(text: string): Pick<CfgConfigParsed, "settings" | "binds" | "buy_binds"> {
  const settings: Record<string, string> = {};
  const binds: Record<string, string> = {};
  const buy_binds: Record<string, string> = {};
  const bindRe = /^bind\s+"([^"]+)"\s+"(.*)"\s*$/i;

  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim();
    if (!line || line.startsWith("//")) {
      continue;
    }
    const lower = line.toLowerCase();
    if (lower.startsWith("bind ")) {
      const m = bindRe.exec(line);
      if (m) {
        binds[m[1]] = m[2];
      }
      continue;
    }
    if (lower.startsWith("alias ") || lower.startsWith("exec ")) {
      continue;
    }
    const pair = parseCvarLine(line);
    if (pair) {
      settings[pair[0]] = pair[1];
    }
  }

  return { settings, binds, buy_binds };
}

function parseCvarLine(line: string): [string, string] | null {
  const trimmed = line.trim();
  const firstSpace = trimmed.search(/\s/);
  if (firstSpace <= 0) {
    return null;
  }
  const key = trimmed.slice(0, firstSpace).trim();
  if (!key) {
    return null;
  }
  const lw = key.toLowerCase();
  if (lw === "bind" || lw === "alias" || lw === "exec") {
    return null;
  }
  let rest = trimmed.slice(firstSpace).trim();
  if (rest.length >= 2 && rest.startsWith('"') && rest.endsWith('"')) {
    rest = rest.slice(1, -1);
  }
  return [key, rest];
}

function hasSettingKey(settings: Record<string, string>, pred: (k: string) => boolean): boolean {
  return Object.keys(settings).some((k) => pred(k.toLowerCase()));
}

export type ConfigCompletenessSection = {
  id: string;
  label: string;
  ok: boolean;
};

export type CompletenessHints = {
  /** На главной выбран режим и есть сгенерированный в сессии .cfg (режим «учтён»). */
  sessionHasMode?: boolean;
};

export type ConfigCompletenessResult = {
  done: number;
  total: number;
  pct: number;
  sections: ConfigCompletenessSection[];
};

/**
 * Десять секций по мотивам CustomTkinter (`gui.py` `_upd`): параметры, бинды, режим,
 * сеть, видео, прицел, мышь, звук, FPS, закупка/алиасы закупки.
 */
export function computeConfigCompleteness(
  cfg: Pick<CfgConfigParsed, "settings" | "binds" | "buy_binds"> & {
    mode?: string | null;
    mode_key?: string | null;
    preset_name?: string | null;
  },
  hints?: CompletenessHints,
): ConfigCompletenessResult {
  const { settings, binds, buy_binds } = cfg;
  const modeOk =
    !!(cfg.mode_key?.trim() || cfg.mode?.trim() || cfg.preset_name?.trim()) || !!hints?.sessionHasMode;

  const sections: ConfigCompletenessSection[] = [
    {
      id: "settings",
      label: "Параметры (CVAR)",
      ok: Object.keys(settings).length > 0,
    },
    {
      id: "binds",
      label: "Бинды",
      ok: Object.keys(binds).length > 0,
    },
    {
      id: "mode",
      label: "Режим / пресет",
      ok: modeOk,
    },
    {
      id: "net",
      label: "Сеть (rate, updaterate…)",
      ok: hasSettingKey(
        settings,
        (k) =>
          k.startsWith("rate") ||
          k.startsWith("cl_cmdrate") ||
          k.startsWith("cl_updaterate") ||
          k.startsWith("ex_interp") ||
          k.startsWith("cl_rate") ||
          k.includes("net_graph"),
      ),
    },
    {
      id: "video",
      label: "Видео / OpenGL",
      ok: hasSettingKey(
        settings,
        (k) =>
          k.startsWith("gl_") ||
          k.includes("gamma") ||
          k.includes("brightness") ||
          k.startsWith("r_gamma") ||
          k.startsWith("r_detailtextures"),
      ),
    },
    {
      id: "crosshair",
      label: "Прицел",
      ok: hasSettingKey(settings, (k) => k.includes("crosshair")),
    },
    {
      id: "mouse",
      label: "Мышь / чувствительность",
      ok: hasSettingKey(
        settings,
        (k) =>
          k.startsWith("sensitivity") ||
          k.startsWith("m_yaw") ||
          k.startsWith("m_pitch") ||
          k.includes("zoom_sensitivity"),
      ),
    },
    {
      id: "sound",
      label: "Звук",
      ok: hasSettingKey(settings, (k) => k.startsWith("volume") || k.startsWith("snd_") || k === "_snd_mixahead"),
    },
    {
      id: "fps",
      label: "FPS / производительность",
      ok: hasSettingKey(
        settings,
        (k) => k.startsWith("fps_") || k.startsWith("max_fps") || k === "developer" || k.startsWith("gl_max"),
      ),
    },
    {
      id: "buy",
      label: "Закупка",
      ok:
        Object.keys(buy_binds).length > 0 ||
        Object.values(binds).some((v) => /\bbuy\b/i.test(v)) ||
        hasSettingKey(settings, (k) => k.includes("buy")),
    },
  ];

  const done = sections.filter((s) => s.ok).length;
  const total = sections.length;
  const pct = total > 0 ? Math.round((done / total) * 100) : 0;

  return { done, total, pct, sections };
}
