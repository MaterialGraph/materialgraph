<#
  MaterialGraph PR #44 - production Objective Explore capture (pre- or post-deploy).

  Sends exactly two requests to the public API, 2 s apart (well inside the Nginx limit):
    1. cs01      - the frozen Case Study 01 request, byte-for-byte from origin/main
    2. q4_strict - the Q4 Strict request from the frozen qualification baseline
  The route is discovered from production's own /openapi.json, not guessed.
  Everything is saved under C:\MaterialGraph-Backups\prod-qualification-pr44\<label>-<UTC stamp>\.
  Nothing in the repository or on the server is modified.

  Usage:  powershell -ExecutionPolicy Bypass -File capture_production_explore.ps1 -Label pre-deploy
#>
param(
    [Parameter(Mandatory)][ValidateSet('pre-deploy', 'post-deploy')][string]$Label,
    [string]$Repo = 'C:\Users\user\OneDrive\Documents\GitHub\materialgraph',
    [string]$Base = 'https://materialgraph.org',
    [pscredential]$Credential
)
$ErrorActionPreference = 'Stop'

# Pilot Nginx Basic Auth. Prompted interactively; passed to curl via stdin config,
# never on the command line, in history, or in any saved file.
if (-not $Credential) { $Credential = Get-Credential -Message 'MaterialGraph pilot Basic Auth (Nginx)' }
$pw = $Credential.GetNetworkCredential().Password -replace '\\', '\\' -replace '"', '\"'
$un = $Credential.UserName -replace '\\', '\\' -replace '"', '\"'
$curlAuth = "user = `"$($un):$pw`""
function Invoke-Curl { param([string[]]$CurlArgs) $curlAuth | curl.exe -K - @CurlArgs }
$stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
$out = "C:\MaterialGraph-Backups\prod-qualification-pr44\$Label-$stamp"
New-Item -ItemType Directory -Force $out | Out-Null

# Frozen inputs, byte-exact (cmd redirection does not re-encode)
$ev = 'docs/product/literature-case-study-01/evidence'
cmd /c "git -C `"$Repo`" show origin/main:$ev/case01_objective_request.json > `"$out\cs01_request.json`""
cmd /c "git -C `"$Repo`" show origin/main:$ev/case01_objective_response.json > `"$out\cs01_frozen_response.json`""
$qual = (git -C $Repo show "origin/main:$ev/diagnostics/MG-LCS01-PRE-FIX-MULTI-OBJECTIVE-QUALIFICATION.json" | Out-String) | ConvertFrom-Json
$q4 = ($qual.cases | Where-Object case_id -eq 'Q4').registered_request
[IO.File]::WriteAllText("$out\q4_strict_request.json", ($q4 | ConvertTo-Json -Depth 6 -Compress))

# Route from production's own schema
$code = Invoke-Curl @('-sS', '-o', "$out\openapi_raw.json", '-w', '%{http_code}', "$Base/openapi.json")
if ($code -ne '200') { throw "openapi.json returned HTTP $code (check the Basic Auth login)" }
$api = Get-Content "$out\openapi_raw.json" -Raw | ConvertFrom-Json
$tmpl = @($api.paths.PSObject.Properties.Name | Where-Object { $_ -like '*/discovery/objective/explore' })
if ($tmpl.Count -ne 1) { throw "Objective Explore route not unique in openapi.json: $($tmpl -join ', ')" }
$path = $tmpl[0] -replace '\{material_id\}', '5'
[IO.File]::WriteAllText("$out\openapi.json", ($api | ConvertTo-Json -Depth 60 -Compress))

$summary = "$out\summary.txt"
"label: $Label   captured_utc: $stamp   base: $Base" | Tee-Object $summary
"origin/main: $(git -C $Repo rev-parse origin/main)" | Tee-Object -Append $summary
"route: $($tmpl[0]) -> $path" | Tee-Object -Append $summary

foreach ($c in @(@{ n = 'cs01'; b = 'cs01_request.json' }, @{ n = 'q4_strict'; b = 'q4_strict_request.json' })) {
    $m = Invoke-Curl @('-sS', '-X', 'POST', "$Base$path", '-H', 'Content-Type: application/json',
        '--data-binary', "@$out\$($c.b)", '-D', "$out\$($c.n)_headers.txt", '-o', "$out\$($c.n)_response.json",
        '-w', 'status=%{http_code} time_total=%{time_total}s size=%{size_download}B')
    "$($c.n): $m" | Tee-Object -Append $summary
    Start-Sleep -Seconds 2
}

function Show-Result($file) {
    $r = Get-Content $file -Raw | ConvertFrom-Json
    $rc = @($r.ranked_candidates)
    "  candidates: " + (($rc | ForEach-Object { "$($_.material_id):$($_.formula):$($_.score)" }) -join ', ')
    "  formula contains (heuristic) -> Na: $(@($rc | Where-Object { $_.formula -cmatch 'Na' }).Count)/$($rc.Count)" +
    "  Li: $(@($rc | Where-Object { $_.formula -cmatch 'Li' }).Count)  Co: $(@($rc | Where-Object { $_.formula -cmatch 'Co' }).Count)  K: $(@($rc | Where-Object { $_.formula -cmatch 'K(?![a-z])' }).Count)"
    "  chains: " + ((@($r.chains) | ForEach-Object { '[' + ((@($_.materials) | ForEach-Object material_id) -join ',') + ']' }) -join ' ')
    "  search_metadata: " + ($r.search_metadata | ConvertTo-Json -Compress)
    "  top-level keys: " + (($r.PSObject.Properties.Name) -join ', ')
}
$(foreach ($n in 'cs01_frozen', 'cs01', 'q4_strict') {
    "== $n"
    try { Show-Result "$out\$($n)_response.json" } catch { "  could not parse: $($_.Exception.Message)" }
}) | Tee-Object -Append $summary

"saved to: $out"