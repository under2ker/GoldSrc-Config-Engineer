import { z } from "zod";

export const greetFormSchema = z.object({
  name: z
    .string()
    .trim()
    .min(1, "Введите хотя бы один символ")
    .max(80, "Не длиннее 80 символов"),
});

export type GreetFormValues = z.infer<typeof greetFormSchema>;
