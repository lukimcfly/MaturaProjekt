# Speichert das Bild aus der Windows-Zwischenablage als PNG.
#
# Verwendung (PowerShell, im Projektordner):
#   .\Bilder\zwischenablage-speichern.ps1 saw-oszillator-v3
#   .\Bilder\zwischenablage-speichern.ps1 breadboard-mixer -Ordner Aufbau
#
# Das Datum wird automatisch vorangestellt: 2026-08-19_saw-oszillator-v3.png

param(
    [Parameter(Mandatory=$true)][string]$Name,
    [ValidateSet('Schaltplaene','Aufbau','Messungen')][string]$Ordner = 'Schaltplaene'
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$img = [System.Windows.Forms.Clipboard]::GetImage()
if (-not $img) {
    Write-Host "Kein Bild in der Zwischenablage. Erst das Bild kopieren (Snipping Tool / Strg+C)." -ForegroundColor Yellow
    exit 1
}

$ziel = Join-Path $PSScriptRoot $Ordner
if (-not (Test-Path $ziel)) { New-Item -ItemType Directory -Path $ziel | Out-Null }

$datei = Join-Path $ziel ("{0}_{1}.png" -f (Get-Date -Format 'yyyy-MM-dd'), $Name)
$img.Save($datei, [System.Drawing.Imaging.ImageFormat]::Png)
$img.Dispose()

Write-Host "Gespeichert: $datei ($([math]::Round((Get-Item $datei).Length/1KB,1)) KB)" -ForegroundColor Green
