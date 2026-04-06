import { create } from "zustand";

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

export const useConfigStore = create<ConfigState>((set, get) => ({
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
}));
