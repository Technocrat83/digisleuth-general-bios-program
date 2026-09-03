param(
  [string]$ApiUrl = "https://127.0.0.1:27124",
  [string]$ApiKey = $env:OBSIDIAN_API_KEY
)
if (-not $ApiKey) { throw "Set OBSIDIAN_API_KEY first." }
Write-Host "[1/2] Health"
curl.exe -k "$ApiUrl/"
Write-Host "`n[2/2] Vault root"
curl.exe -k -H "Authorization: Bearer $ApiKey" "$ApiUrl/vault/"
