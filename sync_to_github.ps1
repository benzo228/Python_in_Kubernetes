# sync_to_github.ps1
$ErrorActionPreference = "Stop"

# Пути к папкам
$SourceDir = "C:\Users\BIG BOSS\Desktop\Python_in_Kubernetes\Python_in_Kubernetes"
$TargetDir = "C:\Users\BIG BOSS\Desktop\Python_Kuber_Github"

Write-Host "1. Копирование файлов..." -ForegroundColor Cyan
# /E - копировать все подпапки (включая пустые)
# /XD - исключить папки (.git, __pycache__, harbor_helm, data, logs)
# /XF - исключить файлы (секреты и временные)
# /R:1 /W:1 - не пытаться перезапускать копирование при ошибке доступа (чтобы не зависать)
robocopy $SourceDir $TargetDir /E /XD ".git" "__pycache__" ".pytest_cache" "harbor_helm" "data" "logs" /XF "runner-values.yaml" ".env" /R:1 /W:1 /NFL /NDL /NJH /NJS /nc /ns /np

Write-Host "2. Переход в папку GitHub..." -ForegroundColor Cyan
Set-Location $TargetDir

# Проверяем, что мы в правильной ветке
$currentBranch = git branch --show-current
if ($currentBranch -ne "dev") {
    Write-Host "Переключение на ветку dev..." -ForegroundColor Yellow
    git checkout dev
}

Write-Host "3. Коммит и пуш..." -ForegroundColor Cyan
git add .

# Проверяем, есть ли что коммитить
$status = git status --porcelain
if ($status) {
    $commitMessage = "Sync from GitLab: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    git commit -m $commitMessage
} else {
    Write-Host "Нет изменений для коммита." -ForegroundColor Yellow
}

# Пушим с обработкой ошибок
$pushOutput = git push origin dev 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ОШИБКА ПУША!" -ForegroundColor Red
    Write-Host $pushOutput
    Write-Host "Проверьте: 1) Токен в credential manager, 2) Права на репозиторий, 3) Ветку dev" -ForegroundColor Yellow
    exit 1
}

Write-Host "4. Готово! Изменения отправлены в GitHub (ветка dev)." -ForegroundColor Green