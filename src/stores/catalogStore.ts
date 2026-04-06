import { create } from "zustand";
import { getGameModes, getProPresets } from "../lib/api";
import type { GameModeSummary, ProPresetSummary } from "../types/api";

type CatalogState = {
  modes: GameModeSummary[];
  presets: ProPresetSummary[];
  loaded: boolean;
  error: string | null;
  load: () => Promise<void>;
};

export const useCatalogStore = create<CatalogState>((set) => ({
  modes: [],
  presets: [],
  loaded: false,
  error: null,
  load: async () => {
    try {
      const [modes, presets] = await Promise.all([
        getGameModes(),
        getProPresets(),
      ]);
      set({ modes, presets, loaded: true, error: null });
    } catch (e) {
      set({ error: String(e), loaded: true });
    }
  },
}));
