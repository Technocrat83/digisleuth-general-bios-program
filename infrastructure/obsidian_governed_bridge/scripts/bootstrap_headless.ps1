Write-Host "DIGISLEUTH HEADLESS PLANE"
Write-Host "Run this on a SEPARATE headless/agent device or environment, not against the same local vault path synchronized by Obsidian Desktop."
Write-Host "Requires Node.js 22+ and an Obsidian Sync subscription."
npm install -g obsidian-headless
ob login
ob sync-list-remote
Write-Host 'Next: cd into the dedicated headless vault directory, then run:'
Write-Host '  ob sync-setup --vault "YOUR VAULT NAME"'
Write-Host '  ob sync --continuous'
