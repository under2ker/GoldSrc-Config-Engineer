import {
  applyLocale,
  applyReduceMotion,
  applyTheme,
  readLocale,
  readReduceMotion,
  readTheme,
} from "@/lib/appPrefs";

applyTheme(readTheme());
applyLocale(readLocale());
applyReduceMotion(readReduceMotion());
