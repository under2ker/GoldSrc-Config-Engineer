/** Категории советов (Фаза 4 — расширяется до ~50 записей). */
export type TipCategory = "aim" | "movement" | "network" | "visual" | "general";

export type DidYouKnowTip = {
  id: string;
  category: TipCategory;
  /** Текст подсказки для UI (RU). */
  text: string;
};

export const TIP_CATEGORY_LABEL: Record<TipCategory, string> = {
  aim: "Прицел и стрельба",
  movement: "Движение",
  network: "Сеть и тики",
  visual: "Картинка и FPS",
  general: "Общее",
};

/** Стартовый набор; цель Фазы 4 — ~50 советов. */
export const DID_YOU_KNOW_TIPS: DidYouKnowTip[] = [
  {
    id: "autoexec-steam",
    category: "general",
    text: "Положите autoexec.cfg в cstrike и добавьте в параметры запуска Steam строку +exec autoexec.cfg.",
  },
  {
    id: "rates-ping",
    category: "network",
    text: "Перед матчем проверьте rate, cl_updaterate и cl_cmdrate под свой пинг — низкие значения дают «резиновую» стрельбу.",
  },
  {
    id: "dynamic-crosshair",
    category: "visual",
    text: "Отключите cl_dynamiccrosshair, если хотите статичный прицел при движении.",
  },
  {
    id: "backup-cfg",
    category: "general",
    text: "Сохраняйте копию рабочего конфига перед экспериментами — так проще откатиться.",
  },
  {
    id: "compare-page",
    category: "general",
    text: "Сравнение двух .cfg в приложении помогает найти лишние bind и дубли команд.",
  },
  {
    id: "sensitivity-360",
    category: "aim",
    text: "Запишите см на 360° — так проще сравнивать чувствительность с другими конфигами и калькулятором в приложении.",
  },
  {
    id: "cl_bob",
    category: "visual",
    text: "cl_bob и cl_bobcycle влияют на покачивание оружия; для минимального отвлечения часто ставят 0.",
  },
  {
    id: "fps-max",
    category: "visual",
    text: "fps_max ограничивает FPS; для стабильного frametime иногда выгоднее чуть ниже потолок, чем бесконечный max.",
  },
  {
    id: "bunny-goldsrc",
    category: "movement",
    text: "В GoldSrc страйф и прыжок тесно связаны с FPS и биндами — копируйте чужие настройки целиком, а не по одной команде.",
  },
  {
    id: "ex_interp",
    category: "network",
    text: "ex_interp влияет на сглаживание позиций игроков; слишком большие значения дают «запаздывание» моделей.",
  },
  {
    id: "zoom-sensitivity",
    category: "aim",
    text: "Если пользуетесь зумом AWP, проверьте соотношение чувствительности в прицеле и от первого лица — их часто настраивают отдельно.",
  },
  {
    id: "gamma",
    category: "visual",
    text: "gamma и brightness помогают на тёмных картах; слишком высокие значения «съедают» глубину теней.",
  },
  {
    id: "alias-chain",
    category: "general",
    text: "Сложные покупки удобно выносить в alias и привязывать к отдельным клавишам — раздел «Алиасы» в приложении помогает собрать пресет.",
  },
  {
    id: "modular-export",
    category: "general",
    text: "Модульный экспорт раскладывает конфиг по userconfig.cfg, autoexec.cfg и config.cfg — удобно для ручной правки.",
  },
  {
    id: "voice-loopback",
    category: "network",
    text: "Проверьте voice_loopback только при отладке микрофона — в бою он обычно не нужен.",
  },
];

export function pickDailyTip(): DidYouKnowTip {
  const d = new Date();
  const i = (d.getFullYear() + d.getMonth() * 31 + d.getDate()) % DID_YOU_KNOW_TIPS.length;
  return DID_YOU_KNOW_TIPS[i] ?? DID_YOU_KNOW_TIPS[0]!;
}

export function pickRandomTip(excludeId?: string): DidYouKnowTip {
  const pool =
    excludeId != null ? DID_YOU_KNOW_TIPS.filter((t) => t.id !== excludeId) : [...DID_YOU_KNOW_TIPS];
  if (pool.length === 0) return DID_YOU_KNOW_TIPS[0]!;
  return pool[Math.floor(Math.random() * pool.length)]!;
}
