# Упаковка портабл-релиза Windows: exe + DLL из каталога release (после `tauri build --no-bundle`).
# Артефакт: artifacts/GoldSrc-Config-Engineer-<version>-portable-win64.zip

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$pkg = Get-Content (Join-Path $root "package.json") -Raw | ConvertFrom-Json
$ver = $pkg.version
$exeName = "goldsr-config-engineer.exe"

$candidates = @(
    (Join-Path $root "target\release\$exeName"),
    (Join-Path $root "src-tauri\target\release\$exeName")
)

$exePath = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $exePath) {
    Write-Error "Не найден $exeName. Сначала выполните: npm run build:portable:bundle"
}

$releaseDir = Split-Path $exePath -Parent
Write-Host "Release dir: $releaseDir"

$stagingName = "GoldSrc-Config-Engineer-$ver-portable-win64"
$stagingRoot = Join-Path $root "artifacts\staging"
$staging = Join-Path $stagingRoot $stagingName
if (Test-Path $staging) { Remove-Item $staging -Recurse -Force }
New-Item -ItemType Directory -Force -Path $staging | Out-Null

Copy-Item $exePath $staging
Get-ChildItem $releaseDir -Filter "*.dll" -File | ForEach-Object {
    Copy-Item $_.FullName $staging
}

$readme = @"
GoldSrc Config Engineer — портабельная сборка (Windows x64)
Версия: $ver

Запуск: goldsr-config-engineer.exe (из этой папки).

Требуется среда WebView2 (Microsoft Edge WebView2 Runtime). В Windows 10/11 она обычно уже установлена.
Если окно не открывается — установите: https://developer.microsoft.com/microsoft-edge/webview2/

Данные приложения (SQLite, настройки) хранятся в профиле пользователя, не в папке с exe.
"@
$readme | Out-File (Join-Path $staging "README-PORTABLE.txt") -Encoding utf8

$outDir = Join-Path $root "artifacts"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$zipName = "${stagingName}.zip"
$zipPath = Join-Path $outDir $zipName
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }

Compress-Archive -Path $staging -DestinationPath $zipPath -Force
Remove-Item $stagingRoot -Recurse -Force

Write-Host ""
Write-Host "Portable zip: $zipPath"
