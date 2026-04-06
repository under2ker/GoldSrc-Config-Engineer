import { create, type StateCreator } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";
import { isTauri } from "@tauri-apps/api/core";
import { del, get, set } from "@/lib/idbStorage";

export type AliasPreset = "minimal" | "full" | "custom";

/** Текущий черновик конфига — расширится при переносе CfgConfig из Python. */
type ConfigState = {
  selectedModeId: string | null;
  selectedPresetId: string | null;
  /** JSON `CfgConfig` после импорта или загрузки профиля — для сохранения и генерации .cfg. */
  stagedProfileJson: string | null;
  stagedProfileLabel: string | null;
  /** Пресет алиасов для `generate_config` / модульного экспорта (см. `data/aliases.json`). */
  aliasPreset: AliasPreset;
  includePractice: boolean;
  /** Ключи `section:name` — только для `aliasPreset === "custom"`. */
  aliasEnabled: Record<string, boolean>;
  setSelectedModeId: (id: string | null) => void;
  setSelectedPresetId: (id: string | null) => void;
  setStagedProfile: (json: string | null, label: string | null) => void;
  clearStagedProfile: () => void;
  setAliasPreset: (p: AliasPreset) => void;
  setIncludePractice: (v: boolean) => void;
  setAliasEnabled: (key: string, enabled: boolean) => void;
  bulkAliasEnabled: (m: Record<string, boolean>) => void;
};

const configSlice: StateCreator<ConfigState> = (set, get) => ({
  selectedModeId: null,
  selectedPresetId: null,
  stagedProfileJson: null,
  stagedProfileLabel: null,
  aliasPreset: "minimal",
  includePractice: false,
  aliasEnabled: {},
  setSelectedModeId: (selectedModeId) => set({ selectedModeId }),
  setSelectedPresetId: (selectedPresetId) => set({ selectedPresetId }),
  setStagedProfile: (stagedProfileJson, stagedProfileLabel) => set({ stagedProfileJson, stagedProfileLabel }),
  clearStagedProfile: () => set({ stagedProfileJson: null, stagedProfileLabel: null }),
  setAliasPreset: (aliasPreset) => set({ aliasPreset }),
  setIncludePractice: (includePractice) => set({ includePractice }),
  setAliasEnabled: (key, enabled) =>
    set({ aliasEnabled: { ...get().aliasEnabled, [key]: enabled } }),
  bulkAliasEnabled: (aliasEnabled) => set({ aliasEnabled }),
});

/** В браузере — IndexedDB (`idb-keyval`); в Tauri черновик только в памяти (профили — в SQLite). */
const idbPersistStorage = createJSONStorage(() => ({
  getItem: (name) => get<string>(name).then((v) => v ?? null),
  setItem: (name, value) => set(name, value),
  removeItem: (name) => del(name),
}));

export const useConfigStore = isTauri()
  ? create<ConfigState>()(configSlice)
  : create<ConfigState>()(
      persist(configSlice, {
        name: "gce-config-v1",
        version: 1,
        storage: idbPersistStorage,
        partialize: (s) => ({
          selectedModeId: s.selectedModeId,
          selectedPresetId: s.selectedPresetId,
          stagedProfileJson: s.stagedProfileJson,
          stagedProfileLabel: s.stagedProfileLabel,
          aliasPreset: s.aliasPreset,
          includePractice: s.includePractice,
          aliasEnabled: s.aliasEnabled,
        }),
      }),
    );
