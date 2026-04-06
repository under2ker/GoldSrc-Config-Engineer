/**
 * Обёртка над IndexedDB (`idb-keyval`) для кэша и будущего persist Zustand.
 * Фаза 1: реэкспорт; подключение к store — по мере необходимости.
 */
export { clear, del, get, keys, set } from "idb-keyval";
