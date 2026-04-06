import { open, save } from "@tauri-apps/plugin-dialog";
import { readTextFile, writeTextFile } from "@tauri-apps/plugin-fs";

/** Диалог «Сохранить» и запись UTF-8. `null` — отмена. */
export async function saveCfgToDisk(
  content: string,
  defaultPath = "autoexec.cfg",
): Promise<string | null> {
  const path = await save({
    defaultPath,
    filters: [{ name: "GoldSrc / CS 1.6", extensions: ["cfg"] }],
  });
  if (path == null) {
    return null;
  }
  await writeTextFile(path, content);
  return path;
}

/** Диалог «Сохранить» и запись JSON (UTF-8). `null` — отмена. */
export async function saveJsonToDisk(
  content: string,
  defaultPath = "profile.json",
): Promise<string | null> {
  const path = await save({
    defaultPath,
    filters: [{ name: "JSON", extensions: ["json"] }],
  });
  if (path == null) {
    return null;
  }
  await writeTextFile(path, content);
  return path;
}

/** Диалог «Открыть» и чтение текста. `null` — отмена. */
export async function openCfgFile(): Promise<{ path: string; text: string } | null> {
  const path = await open({
    multiple: false,
    filters: [{ name: "Config", extensions: ["cfg"] }],
  });
  if (path == null) {
    return null;
  }
  const p = Array.isArray(path) ? path[0] : path;
  const text = await readTextFile(p);
  return { path: p, text };
}
