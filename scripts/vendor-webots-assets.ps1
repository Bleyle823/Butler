# Copy the catalog protos the hotel world needs from a local webots tree.
# Webots' GitHub downloader drops connections when a world pulls dozens of EXTERNPROTOs.
# These files are Cyberbotics assets, licensed for use only with Webots.

$ErrorActionPreference = "Stop"
$srcRoot = "C:\Users\Omen\Desktop\webots-master\projects"
$dstRoot = Join-Path $PSScriptRoot "..\assets\webots\projects"
$dstRoot = [System.IO.Path]::GetFullPath($dstRoot)

if (-not (Test-Path $srcRoot)) {
  throw "webots-master projects not found at $srcRoot"
}

New-Item -ItemType Directory -Force -Path $dstRoot | Out-Null

$trees = @(
  "objects\backgrounds",
  "objects\floors",
  "objects\apartment_structure",
  "objects\tables",
  "objects\chairs",
  "objects\living_room_furniture",
  "objects\bedroom",
  "objects\kitchen",
  "objects\drinks",
  "objects\factory\containers",
  "objects\factory\tools",
  "objects\lights",
  "objects\solids",
  "objects\geometries",
  "devices\hokuyo",
  "devices\orbbec",
  "robots\pal_robotics\tiago_base",
  "robots\pal_robotics\tiago_extensions"
)

foreach ($tree in $trees) {
  $from = Join-Path $srcRoot $tree
  $to = Join-Path $dstRoot $tree
  Write-Host "copy $tree"
  New-Item -ItemType Directory -Force -Path $to | Out-Null
  robocopy $from $to /E /NFL /NDL /NJH /NJS /nc /ns /np | Out-Null
  if ($LASTEXITCODE -ge 8) { throw "robocopy failed for $tree (code $LASTEXITCODE)" }
}

$appearanceProtos = @(
  "Parquetry", "Roughcast", "VarnishedPine", "BrushedAluminium", "Leather",
  "ShinyLeather", "CarpetFibers", "PaintedWood", "Marble", "MattePaint",
  "GlossyPaint", "Asphalt", "Cardboard", "OldSteel", "ScrewThread"
)
$appearanceTextures = @(
  "parquetry", "roughcast", "varnished_pine", "brushed_aluminium", "leather",
  "shiny_leather", "carpet", "painted_wood", "marble", "matte_car_paint",
  "glossy_car_paint", "asphalt", "cardboard", "old_steel", "screw_thread"
)

$appDst = Join-Path $dstRoot "appearances\protos"
New-Item -ItemType Directory -Force -Path (Join-Path $appDst "textures") | Out-Null
foreach ($name in $appearanceProtos) {
  Copy-Item (Join-Path $srcRoot "appearances\protos\$name.proto") $appDst -Force
}
foreach ($name in $appearanceTextures) {
  $from = Join-Path $srcRoot "appearances\protos\textures\$name"
  $to = Join-Path $appDst "textures\$name"
  if (Test-Path $from) {
    New-Item -ItemType Directory -Force -Path $to | Out-Null
    robocopy $from $to /E /NFL /NDL /NJH /NJS /nc /ns /np | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy failed for appearance texture $name" }
  }
}

$cubicSrc = Join-Path $srcRoot "default\worlds\textures\cubic"
$cubicDst = Join-Path $dstRoot "default\worlds\textures\cubic"
New-Item -ItemType Directory -Force -Path $cubicDst | Out-Null
Copy-Item (Join-Path $cubicSrc "noon_park_empty*") $cubicDst -Force
$tagged = Join-Path $srcRoot "default\worlds\textures\tagged_wall.jpg"
if (Test-Path $tagged) {
  Copy-Item $tagged (Join-Path $dstRoot "default\worlds\textures") -Force
}

$projectsRoot = $dstRoot
Get-ChildItem $projectsRoot -Recurse -Filter *.proto | ForEach-Object {
  $dir = $_.DirectoryName
  $up = @()
  $cursor = $dir
  while ($cursor.TrimEnd("\") -ne $projectsRoot.TrimEnd("\")) {
    $parent = Split-Path $cursor -Parent
    if (-not $parent -or $parent -eq $cursor) { break }
    $up += ".."
    $cursor = $parent
  }
  $prefix = if ($up.Count -gt 0) { ($up -join "/") + "/" } else { "" }
  $text = [System.IO.File]::ReadAllText($_.FullName)
  $updated = $text.Replace("webots://projects/", $prefix)
  if ($updated -ne $text) {
    $utf8 = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($_.FullName, $updated, $utf8)
  }
}

Write-Host "vendored to $dstRoot"
