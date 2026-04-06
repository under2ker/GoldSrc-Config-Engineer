import { z } from "zod";

/** URL для загрузки конфига по ссылке (импорт). */
export const importUrlFieldSchema = z
  .string()
  .trim()
  .min(1, "Введите ссылку")
  .refine(
    (s) => {
      try {
        const u = new URL(s);
        return u.protocol === "http:" || u.protocol === "https:";
      } catch {
        return false;
      }
    },
    { message: "Нужна ссылка http:// или https://" },
  );

export const importUrlFormSchema = z.object({
  importUrl: importUrlFieldSchema,
});

export type ImportUrlFormValues = z.infer<typeof importUrlFormSchema>;

/** Лимит записей истории снимков (настройки, Tauri). */
export const settingsHistoryMaxSchema = z.object({
  historyMax: z
    .string()
    .trim()
    .min(1, "Введите число")
    .refine(
      (s) => {
        const n = Number.parseInt(s, 10);
        return !Number.isNaN(n) && n >= 10 && n <= 500;
      },
      { message: "Число от 10 до 500." },
    ),
});

export type SettingsHistoryMaxFormValues = z.infer<typeof settingsHistoryMaxSchema>;

/** Имя профиля при сохранении из импорта. */
export const saveProfileNameSchema = z.object({
  profileName: z
    .string()
    .trim()
    .min(1, "Введите имя")
    .max(120, "Не длиннее 120 символов"),
});

export type SaveProfileNameFormValues = z.infer<typeof saveProfileNameSchema>;
