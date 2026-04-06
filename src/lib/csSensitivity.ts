/** Оценки для CS 1.6 / GoldSrc: ориентиры для сравнения настроек, не замена замера в игре. */

/** Условный «eDPI» для сравнения с другими конфигами: DPI × чувствительность в игре. */
export function compareIndex(dpi: number, gameSensitivity: number): number {
  if (!Number.isFinite(dpi) || !Number.isFinite(gameSensitivity) || dpi <= 0 || gameSensitivity <= 0) {
    return 0;
  }
  return dpi * gameSensitivity;
}

/**
 * Популярная оценка см на полный оборот (формула сообщества для CS 1.6 при m_yaw 0.022).
 * При другом m_yaw длина дуги масштабируется обратно пропорционально отклонению от 0.022.
 */
export function approxCmPer360(dpi: number, gameSensitivity: number, mYaw = 0.022): number {
  if (!Number.isFinite(dpi) || !Number.isFinite(gameSensitivity) || dpi <= 0 || gameSensitivity <= 0 || mYaw <= 0) {
    return 0;
  }
  const base = 1030 / (dpi * gameSensitivity);
  return base * (0.022 / mYaw);
}
