/** Грубая классификация строки .cfg для фильтра в таблице сравнения. */
export type CfgLineCategory =
  | "network"
  | "video"
  | "audio"
  | "mouse"
  | "movement"
  | "bind"
  | "buy"
  | "other";

export const CFG_LINE_CATEGORY_LABEL: Record<CfgLineCategory, string> = {
  network: "Сеть / тики",
  video: "Видео / рендер",
  audio: "Звук",
  mouse: "Мышь / чувствительность",
  movement: "Движение",
  bind: "bind / alias",
  buy: "Покупки",
  other: "Прочее",
};

const ALL_CATEGORIES: CfgLineCategory[] = [
  "network",
  "video",
  "audio",
  "mouse",
  "movement",
  "bind",
  "buy",
  "other",
];

export function listCfgLineCategories(): CfgLineCategory[] {
  return ALL_CATEGORIES;
}

/** Эвристика по первому токену и известным префиксам CVAR. */
export function inferCfgLineCategory(line: string): CfgLineCategory {
  const t = line.trim();
  if (!t || t.startsWith("//") || t.startsWith("#")) {
    return "other";
  }
  const lower = t.toLowerCase();

  if (lower.startsWith("bind ") || lower.startsWith("alias ")) {
    return "bind";
  }
  if (lower.includes("buy") && (lower.startsWith("bind ") || lower.includes("menuselect"))) {
    return "buy";
  }

  const head = lower.split(/\s+/)[0] ?? "";

  if (
    head.includes("rate") ||
    head.startsWith("cl_cmdrate") ||
    head.startsWith("cl_updaterate") ||
    head.startsWith("cl_dlmax") ||
    head.startsWith("ex_interp") ||
    head.startsWith("cl_latency") ||
    head.startsWith("pushlatency")
  ) {
    return "network";
  }

  if (
    head.startsWith("volume") ||
    head.startsWith("hisound") ||
    head.startsWith("loadas8bit") ||
    head.startsWith("voice_") ||
    head.startsWith("s_")
  ) {
    return "audio";
  }

  if (
    head.startsWith("sensitivity") ||
    head.startsWith("m_yaw") ||
    head.startsWith("m_pitch") ||
    head.startsWith("m_filter") ||
    head.startsWith("zoom_sensitivity_ratio") ||
    head.startsWith("lookspring") ||
    head.startsWith("lookstrafe")
  ) {
    return "mouse";
  }

  if (
    head.startsWith("cl_") &&
    (head.includes("bob") ||
      head.includes("crosshair") ||
      head.includes("dynamic") ||
      head.includes("fps") ||
      head.includes("gamma") ||
      head.includes("bright") ||
      head.startsWith("cl_gl") ||
      head.includes("fov") ||
      head.includes("minmodels") ||
      head.includes("r_detail") ||
      head.includes("r_draw") ||
      head.includes("r_mirror") ||
      head.includes("r_water") ||
      head.includes("gl_") ||
      head.includes("gamma") ||
      head.includes("maxfps"))
  ) {
    return "video";
  }

  if (
    head.startsWith("gl_") ||
    head.startsWith("brightness") ||
    head.startsWith("gamma") ||
    head.startsWith("lightgamma") ||
    head.startsWith("texgamma") ||
    head.startsWith("fps_max") ||
    head.startsWith("fps_modemax") ||
    head.startsWith("default_fov")
  ) {
    return "video";
  }

  if (
    head.startsWith("+") ||
    head.startsWith("-") ||
    head.startsWith("cl_anglespeedkey") ||
    head.startsWith("cl_forwardspeed") ||
    head.startsWith("cl_backspeed") ||
    head.startsWith("cl_sidespeed") ||
    head.startsWith("cl_movespeedkey")
  ) {
    return "movement";
  }

  return "other";
}
