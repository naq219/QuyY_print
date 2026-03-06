# dp.ps1 — Deploy Production nhanh (không hỏi, không chờ)
$ProjectName = "huynhde"

Write-Host "`n🚀 Deploy PRODUCTION..." -ForegroundColor Cyan

# Build
npm run build
if ($LASTEXITCODE -ne 0) { Write-Host "❌ Build THAT BAI!" -ForegroundColor Red; exit 1 }

# Deploy production
npx wrangler pages deploy dist --project-name=$ProjectName --branch=main --commit-dirty=true
if ($LASTEXITCODE -ne 0) { Write-Host "❌ Deploy THAT BAI!" -ForegroundColor Red; exit 1 }

Write-Host "`n✅ Deploy THANH CONG! → https://$ProjectName.pages.dev`n" -ForegroundColor Green
