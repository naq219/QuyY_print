param(
  [switch]$Prod,
  [switch]$Preview
)

$ProjectName = "huynhde"

Write-Host ""
Write-Host "=============================" -ForegroundColor Cyan
Write-Host "  Deploy Cham soc Thanh vien" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host ""

# Neu khong co tham so, hoi nguoi dung
if (-not $Prod -and -not $Preview) {
  Write-Host "Chon moi truong deploy:" -ForegroundColor Yellow
  Write-Host "  1) Production  (huynhde.pages.dev)"
  Write-Host "  2) Preview     (<hash>.huynhde.pages.dev)"
  Write-Host ""
  $choice = Read-Host "Nhap 1 hoac 2"
  if ($choice -eq "1") { $Prod = $true }
  else { $Preview = $true }
}

# Build
Write-Host ""
Write-Host "[1/2] Building..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) {
  Write-Host "Build THAT BAI!" -ForegroundColor Red
  exit 1
}
Write-Host "Build THANH CONG!" -ForegroundColor Green

# Deploy
Write-Host ""
if ($Prod) {
  Write-Host "[2/2] Deploy len PRODUCTION..." -ForegroundColor Yellow
  npx wrangler pages deploy dist --project-name=$ProjectName --branch=main --commit-dirty=true
} else {
  Write-Host "[2/2] Deploy len PREVIEW..." -ForegroundColor Yellow
  npx wrangler pages deploy dist --project-name=$ProjectName --branch=preview --commit-dirty=true
}

if ($LASTEXITCODE -ne 0) {
  Write-Host "Deploy THAT BAI!" -ForegroundColor Red
  exit 1
}

Write-Host ""
Write-Host "=============================" -ForegroundColor Green
Write-Host "  Deploy THANH CONG!" -ForegroundColor Green
if ($Prod) {
  Write-Host "  URL: https://$ProjectName.pages.dev" -ForegroundColor Green
} else {
  Write-Host "  Xem URL preview o tren" -ForegroundColor Green
}
Write-Host "=============================" -ForegroundColor Green
