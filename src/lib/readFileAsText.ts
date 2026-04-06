/** Чтение локального файла в браузере / WebView (в т.ч. drag-and-drop). */
export function readFileAsText(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result ?? ""));
    reader.onerror = () => reject(reader.error ?? new Error("FileReader error"));
    reader.readAsText(file, "UTF-8");
  });
}
