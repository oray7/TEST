Set-Location "C:\Users\OnlyRayaN\Desktop\automated-email-sender-main"

Write-Host "Auto-sync active -- checking every 10 seconds..." -ForegroundColor Cyan

while ($true) {
    $status = & git status --porcelain
    if ($status) {
        & git add -A
        $msg = "Auto-sync $(Get-Date -Format 'HH:mm:ss')"
        & git commit -m $msg | Out-Null
        & git push 2>&1 | Out-Null
        Write-Host "Synced to GitHub -- $msg" -ForegroundColor Green
    }
    Start-Sleep -Seconds 10
}
