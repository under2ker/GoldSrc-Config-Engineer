import { useProfileStore } from "@/stores/profileStore";

/** Профили из локальной БД (Tauri) и `refreshProfiles`. */
export function useProfiles() {
  const profiles = useProfileStore((s) => s.profiles);
  const refreshProfiles = useProfileStore((s) => s.refreshProfiles);
  return { profiles, refreshProfiles };
}
