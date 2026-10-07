# Place the kitchen jar order: honey jar, jam jar 1, jam jar 2.
# Start the settler, the bridge, and the hotel UI first.
# Leave kitchen.wbt paused until the printed job id is the bridge goal, then press Play.
# Usage:
#   .\scripts\next_order.ps1 -Order

param(
    [switch]$Order
)

$ErrorActionPreference = "Stop"

function Need($name, $url) {
    try {
        $code = curl.exe -s --max-time 8 -o NUL -w "%{http_code}" $url
    } catch {
        $code = "000"
    }
    if ($code -eq "000") {
        throw "$name is not answering at $url"
    }
    Write-Host "$name $code"
}

Need "Settler" "http://127.0.0.1:8788/health"
Need "Hotel" "http://127.0.0.1:3001/"
Need "Bridge" "http://127.0.0.1:8787/robots/servebot-1/goal"

$goal = curl.exe -s --max-time 8 "http://127.0.0.1:8787/robots/servebot-1/goal"
Write-Host "Goal $goal"
if (-not $Order) {
    Write-Host "Ready. Order with .\scripts\next_order.ps1 -Order, confirm the job id, then press Play."
    exit 0
}
if ($goal -ne "{}") {
    throw "Bridge already has a goal ($goal). Finish that kitchen run before ordering again."
}

$body = '{"room":"room-1204","items":["honey jar","jam jar 1","jam jar 2"]}'
$orderResult = Invoke-RestMethod -Uri "http://127.0.0.1:3001/api/order" -Method POST -ContentType "application/json" -Body $body -TimeoutSec 180
Write-Host "Order $($orderResult.jobId) $($orderResult.room) $($orderResult.items -join ', ')"
Start-Sleep -Seconds 2
$goal = curl.exe -s --max-time 8 "http://127.0.0.1:8787/robots/servebot-1/goal"
Write-Host "Goal $goal"
if ($goal -notmatch [regex]::Escape($orderResult.jobId)) {
    throw "The settler did not store this job. Do not press Play."
}
Write-Host "Goal matches. Press Play once. servebot-1 waits for this job, then moves the three jars."
