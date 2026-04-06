import { toast } from "sonner";

import { catalogReloadLocal, catalogSyncNow } from "@/lib/api";
import { interpolate } from "@/lib/i18n";
import { useCatalogStore } from "@/stores/catalogStore";
import type { CatalogSyncReport } from "@/types/api";

/** Проверка на сервере и загрузка изменённых JSON; обновляет стор каталога и показывает тосты. */
export async function catalogSyncNowWithUi(t: (key: string) => string): Promise<CatalogSyncReport> {
  const r = await catalogSyncNow();
  await useCatalogStore.getState().load();
  const summary = interpolate(t("diagnosticsPage.catalog.syncResult"), {
    checked: r.checked,
    updated: r.updated,
    skipped: r.skippedNotModified,
    errors: r.errors.length,
  });
  toast.success(t("diagnosticsPage.catalog.syncOk"), { description: summary });
  if (r.errors.length > 0) {
    toast.message(t("diagnosticsPage.catalog.errorsTitle"), {
      description: r.errors.join("\n"),
    });
  }
  return r;
}

/** Перечитать JSON из локальной папки без сети. */
export async function catalogReloadLocalWithUi(t: (key: string) => string): Promise<void> {
  await catalogReloadLocal();
  await useCatalogStore.getState().load();
  toast.success(t("diagnosticsPage.catalog.reloadOk"));
}
