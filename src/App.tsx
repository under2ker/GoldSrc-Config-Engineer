import { lazy } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { MainLayout } from "@/components/layout/MainLayout";
import { DashboardPage } from "@/pages/DashboardPage";

const ComparisonPage = lazy(async () => {
  const m = await import("@/pages/ComparisonPage");
  return { default: m.ComparisonPage };
});
const CrosshairPage = lazy(async () => {
  const m = await import("@/pages/CrosshairPage");
  return { default: m.CrosshairPage };
});
const DiagnosticsPage = lazy(async () => {
  const m = await import("@/pages/DiagnosticsPage");
  return { default: m.DiagnosticsPage };
});
const ExportPage = lazy(async () => {
  const m = await import("@/pages/ExportPage");
  return { default: m.ExportPage };
});
const GameModesPage = lazy(async () => {
  const m = await import("@/pages/GameModesPage");
  return { default: m.GameModesPage };
});
const ImportPage = lazy(async () => {
  const m = await import("@/pages/ImportPage");
  return { default: m.ImportPage };
});
const LaunchOptionsPage = lazy(async () => {
  const m = await import("@/pages/LaunchOptionsPage");
  return { default: m.LaunchOptionsPage };
});
const SensitivityPage = lazy(async () => {
  const m = await import("@/pages/SensitivityPage");
  return { default: m.SensitivityPage };
});
const PresetsPage = lazy(async () => {
  const m = await import("@/pages/PresetsPage");
  return { default: m.PresetsPage };
});
const PreviewPage = lazy(async () => {
  const m = await import("@/pages/PreviewPage");
  return { default: m.PreviewPage };
});
const QuickSetupPage = lazy(async () => {
  const m = await import("@/pages/QuickSetupPage");
  return { default: m.QuickSetupPage };
});
const SettingsPage = lazy(async () => {
  const m = await import("@/pages/SettingsPage");
  return { default: m.SettingsPage };
});
const ProfilesPage = lazy(async () => {
  const m = await import("@/pages/ProfilesPage");
  return { default: m.ProfilesPage };
});
const AliasesPage = lazy(async () => {
  const m = await import("@/pages/AliasesPage");
  return { default: m.AliasesPage };
});

function App() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="quick-setup" element={<QuickSetupPage />} />
        <Route path="modes" element={<GameModesPage />} />
        <Route path="presets" element={<PresetsPage />} />
        <Route path="crosshair" element={<CrosshairPage />} />
        <Route path="sensitivity" element={<SensitivityPage />} />
        <Route path="compare" element={<ComparisonPage />} />
        <Route path="export" element={<ExportPage />} />
        <Route path="import" element={<ImportPage />} />
        <Route path="launch-options" element={<LaunchOptionsPage />} />
        <Route path="preview" element={<PreviewPage />} />
        <Route path="diagnostics" element={<DiagnosticsPage />} />
        <Route path="profiles" element={<ProfilesPage />} />
        <Route path="aliases" element={<AliasesPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default App;
