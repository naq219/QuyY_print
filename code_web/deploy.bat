@echo off
echo ====================================
echo  QuyY Print - Deploy to Cloudflare Pages
echo  Project: inlaphai
echo  URL: inlaphai.pages.dev
echo ====================================
echo.

echo [1/2] Building Nuxt SPA...
call npx nuxi generate
if %ERRORLEVEL% neq 0 (
    echo BUILD FAILED!
    pause
    exit /b 1
)

echo.
echo [2/2] Deploying to Cloudflare Pages (production)...
call npx wrangler pages deploy dist --project-name=inlaphai --branch=main --commit-dirty=true
if %ERRORLEVEL% neq 0 (
    echo DEPLOY FAILED!
    pause
    exit /b 1
)

echo.
echo ====================================
echo  Deploy thanh cong!
echo  URL: https://inlaphai.pages.dev
echo ====================================
pause
