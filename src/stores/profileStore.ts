import { create } from "zustand";
import { isTauri } from "@tauri-apps/api/core";
import { profileList } from "@/lib/api";
import type { Profile } from "../types/api";

type ProfileState = {
  profiles: Profile[];
  setProfiles: (profiles: Profile[]) => void;
  /** Перезагрузка из SQLite (только Tauri). */
  refreshProfiles: () => Promise<void>;
};

export const useProfileStore = create<ProfileState>((set) => ({
  profiles: [],
  setProfiles: (profiles) => set({ profiles }),
  refreshProfiles: async () => {
    if (!isTauri()) return;
    try {
      const rows = await profileList();
      set({ profiles: rows });
    } catch {
      set({ profiles: [] });
    }
  },
}));
