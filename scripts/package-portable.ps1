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

$templatePath = Join-Path $PSScriptRoot "README-PORTABLE.txt"
$text = [System.IO.File]::ReadAllText($templatePath, [System.Text.UTF8Encoding]::new($false))
$text = $text.Replace("{{VERSION}}", $ver)
$readmeDest = Join-Path $staging "README-PORTABLE.txt"
# UTF-8 с BOM — Блокнот и старые программы Windows открывают кириллицу без «иероглифов»
$utf8Bom = New-Object System.Text.UTF8Encoding $true
[System.IO.File]::WriteAllText($readmeDest, $text, $utf8Bom)

$outDir = Join-Path $root "artifacts"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$zipName = "${stagingName}.zip"
$zipPath = Join-Path $outDir $zipName
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }

Compress-Archive -Path $staging -DestinationPath $zipPath -Force
Remove-Item $stagingRoot -Recurse -Force

Write-Host ""
Write-Host "Portable zip: $zipPath"
