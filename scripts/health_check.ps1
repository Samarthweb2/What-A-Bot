# Section C: "External DB-touching health check every 3 minutes to
# mitigate idle sleep (Render can still restart -- this is mitigation,
# not a guarantee)."
#
# Usage: pass your deployed base URL, e.g.
#   .\health_check.ps1 -BaseUrl "https://emberground.onrender.com"

param(
    [string]$BaseUrl = "http://localhost:8000"
)

while ($true) {
    try {
        $resp = Invoke-WebRequest -Uri "$BaseUrl/health" -UseBasicParsing -TimeoutSec 10
        Write-Host "$(Get-Date -Format u) OK $($resp.StatusCode)"
    } catch {
        Write-Host "$(Get-Date -Format u) FAILED $($_.Exception.Message)"
    }
    Start-Sleep -Seconds 180
}
