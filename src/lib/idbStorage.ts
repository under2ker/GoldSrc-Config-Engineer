/**
 * Обёртка над IndexedDB (`idb-keyval`).
 * Persist черновика конфига: `configStore` (только веб), ключ `gce-config-v1` через zustand/persist.
 */
export { clear, del, get, keys, set } from "idb-keyval";
