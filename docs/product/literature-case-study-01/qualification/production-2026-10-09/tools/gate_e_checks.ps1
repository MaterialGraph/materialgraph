<#
  MaterialGraph PR #44 - Gate E bounded production checks (read-only, 7 requests, >=3 s apart).
    1. Default-off legacy path: POST /objective/chains with the frozen Case Study 01 objective
       (this endpoint intentionally does NOT use the new admission; expected to stay Li-dominated).
    2. Latency spread: 3 x Case Study 01 and 3 x Q4 Strict on Objective Explore, with
       result-identity check against the post-deploy capture (determinism).
    3. Byte-identity of the pre-deploy Case Study 01 response vs the frozen response.
  Usage: powershell -ExecutionPolicy Bypass -File gate_e_checks.ps1
#>
param(
    [string]$Root = 'C:\MaterialGraph-Backups\prod-qualification-pr44',
    [string]$Base = 'https://materialgraph.org',
    [pscredential]$Credential
)
$ErrorActionPreference = 'Stop'
if (-not $Credential) { $Credential = Get-Credential -Message 'MaterialGraph pilot Basic Auth (Nginx)' }
$pw = $Credential.GetNetworkCredential().Password -replace '\\', '\\' -replace '"', '\"'
$un = $Credential.UserName -replace '\\', '\\' -replace '"', '\"'
$curlAuth = "user = `"$($un):$pw`""
function Invoke-Curl { param([string[]]$CurlArgs) $curlAuth | curl.exe -K - @CurlArgs }

$pre  = Get-ChildItem $Root -Directory -Filter 'pre-deploy-*'  | Sort-Object Name | Select-Object -Last 1
$post = Get-ChildItem $Root -Directory -Filter 'post-deploy-*' | Sort-Object Name | Select-Object -Last 1
$stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
$out = "$Root\gate-e-$stamp"; New-Item -ItemType Directory -Force $out | Out-Null
$log = "$out\summary.txt"
function Ids($f) { ((Get-Content $f -Raw | ConvertFrom-Json).ranked_candidates | ForEach-Object material_id) -join ',' }

"== byte identity: pre-deploy cs01 vs frozen" | Tee-Object $log
$h1 = (Get-FileHash "$($pre.FullName)\cs01_response.json").Hash
$h2 = (Get-FileHash "$($pre.FullName)\cs01_frozen_response.json").Hash
"  identical: $($h1 -eq $h2)" | Tee-Object -Append $log

"== default-off legacy endpoint: /objective/chains with CS01 objective" | Tee-Object -Append $log
$cs01 = Get-Content "$($post.FullName)\cs01_request.json" -Raw | ConvertFrom-Json
[IO.File]::WriteAllText("$out\chains_request.json", (@{ objective = $cs01.objective } | ConvertTo-Json -Depth 6 -Compress))
$m = Invoke-Curl @('-sS', '-X', 'POST', "$Base/api/v1/materials/5/discovery/objective/chains", '-H', 'Content-Type: application/json',
    '--data-binary', "@$out\chains_request.json", '-o', "$out\chains_response.json",
    '-w', 'status=%{http_code} time_total=%{time_total}s size=%{size_download}B')
"  $m" | Tee-Object -Append $log
try {
    $r = Get-Content "$out\chains_response.json" -Raw | ConvertFrom-Json
    $ends = @($r.chains | ForEach-Object { $mm = @($_.materials); $e = $mm[-1]
        [pscustomobject]@{ id = $e.material_id; fx = $(if ($e.formula) { $e.formula } else { $e.pretty_formula }) } })
    "  chain end materials: " + (($ends | ForEach-Object { "$($_.id):$($_.fx)" }) -join ', ') | Tee-Object -Append $log
    "  ends containing Na: $(@($ends | Where-Object { $_.fx -cmatch 'Na' }).Count)/$($ends.Count)  Li: $(@($ends | Where-Object { $_.fx -cmatch 'Li' }).Count)" | Tee-Object -Append $log
    "  search_metadata: " + ($r.search_metadata | ConvertTo-Json -Compress) | Tee-Object -Append $log
} catch { "  could not parse: $($_.Exception.Message)" | Tee-Object -Append $log }
Start-Sleep -Seconds 3

"== latency + determinism (Objective Explore)" | Tee-Object -Append $log
$explore = "$Base/api/v1/materials/5/discovery/objective/explore"
foreach ($c in @(@{ n = 'cs01' }, @{ n = 'q4_strict' })) {
    $expected = Ids "$($post.FullName)\$($c.n)_response.json"
    foreach ($i in 1..3) {
        $f = "$out\$($c.n)_run$i.json"
        $t = Invoke-Curl @('-sS', '-X', 'POST', $explore, '-H', 'Content-Type: application/json',
            '--data-binary', "@$($post.FullName)\$($c.n)_request.json", '-o', $f,
            '-w', '%{http_code} %{time_total}')
        $ids = Ids $f
        "  $($c.n) run$i  status/time: $t s  same candidates as post-deploy capture: $($ids -eq $expected)" | Tee-Object -Append $log
        Start-Sleep -Seconds 3
    }
}
"saved to: $out"