[CmdletBinding()]
param(
    [switch]$AcceptCodeQLTerms,
    [switch]$SkipCodeQL,
    [switch]$SkipTruffleHog
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$AppRoot = Join-Path $env:LOCALAPPDATA "ENS-Audit-Runner"
$ToolRoot = Join-Path $AppRoot "tools"
$DownloadRoot = Join-Path $AppRoot "downloads"
New-Item -ItemType Directory -Force -Path $ToolRoot, $DownloadRoot | Out-Null

function Require-Command {
    param([Parameter(Mandatory = $true)][string]$Name, [string]$Help)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' was not found. $Help"
    }
}

function Add-UserPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    $resolved = [System.IO.Path]::GetFullPath($Path)
    $current = [Environment]::GetEnvironmentVariable("Path", "User")
    $parts = @()
    if ($current) { $parts = $current.Split(';') | Where-Object { $_ } }
    if ($parts -notcontains $resolved) {
        $updated = (($parts + $resolved) | Select-Object -Unique) -join ';'
        [Environment]::SetEnvironmentVariable("Path", $updated, "User")
    }
    if (($env:Path.Split(';')) -notcontains $resolved) {
        $env:Path = "$resolved;$env:Path"
    }
}

function Get-LatestReleaseAsset {
    param(
        [Parameter(Mandatory = $true)][string]$Repository,
        [Parameter(Mandatory = $true)][string]$NameRegex
    )
    $headers = @{ "User-Agent" = "ENS-Audit-Runner-Installer" }
    $release = Invoke-RestMethod -Headers $headers -Uri "https://api.github.com/repos/$Repository/releases/latest"
    $matches = @($release.assets | Where-Object { $_.name -match $NameRegex })
    if ($matches.Count -ne 1) {
        throw "Expected exactly one release asset matching '$NameRegex' in $Repository, found $($matches.Count)."
    }
    return $matches[0]
}

function Download-VerifiedAsset {
    param(
        [Parameter(Mandatory = $true)]$Asset,
        [Parameter(Mandatory = $true)][string]$Destination
    )
    Invoke-WebRequest -UseBasicParsing -Uri $Asset.browser_download_url -OutFile $Destination
    if ($Asset.digest -and $Asset.digest.StartsWith("sha256:")) {
        $expected = $Asset.digest.Substring(7).ToLowerInvariant()
        $actual = (Get-FileHash -Algorithm SHA256 -Path $Destination).Hash.ToLowerInvariant()
        if ($actual -ne $expected) {
            Remove-Item -Force $Destination -ErrorAction SilentlyContinue
            throw "SHA-256 verification failed for $($Asset.name)."
        }
    }
}

Write-Host "Installing ENS Audit Runner Python package..." -ForegroundColor Cyan
Require-Command -Name "py" -Help "Install Python 3.12+ from python.org or the Microsoft Store, then rerun this script."
& py -3.12 -c "import sys; assert sys.version_info >= (3, 11)"
& py -3.12 -m pip install --upgrade pip
& py -3.12 -m pip install .
& py -3.12 -m pip install pip-audit detect-secrets bandit

if (-not $SkipCodeQL) {
    if (-not $AcceptCodeQLTerms) {
        Write-Warning "CodeQL was not installed because -AcceptCodeQLTerms was not supplied. Review GitHub CodeQL terms, then rerun with that switch if accepted."
    }
    else {
        Write-Host "Installing latest official CodeQL CLI..." -ForegroundColor Cyan
        $asset = Get-LatestReleaseAsset -Repository "github/codeql-cli-binaries" -NameRegex '^codeql-win64\.zip$'
        $zip = Join-Path $DownloadRoot $asset.name
        Download-VerifiedAsset -Asset $asset -Destination $zip
        $destination = Join-Path $ToolRoot "codeql-release"
        Remove-Item -Recurse -Force $destination -ErrorAction SilentlyContinue
        Expand-Archive -Path $zip -DestinationPath $destination -Force
        $codeqlExe = Get-ChildItem -Path $destination -Filter "codeql.exe" -Recurse -File | Select-Object -First 1
        if (-not $codeqlExe) { throw "CodeQL extraction completed but codeql.exe was not found." }
        Add-UserPath -Path $codeqlExe.DirectoryName
        & $codeqlExe.FullName version
    }
}

if (-not $SkipTruffleHog) {
    Write-Host "Installing latest official TruffleHog..." -ForegroundColor Cyan
    Require-Command -Name "tar.exe" -Help "Windows 10/11 includes tar.exe; update Windows if it is missing."
    $asset = Get-LatestReleaseAsset -Repository "trufflesecurity/trufflehog" -NameRegex '^trufflehog_[0-9.]+_windows_amd64\.tar\.gz$'
    $archive = Join-Path $DownloadRoot $asset.name
    Download-VerifiedAsset -Asset $asset -Destination $archive
    $destination = Join-Path $ToolRoot "trufflehog"
    Remove-Item -Recurse -Force $destination -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Force -Path $destination | Out-Null
    & tar.exe -xzf $archive -C $destination
    $trufflehogExe = Get-ChildItem -Path $destination -Filter "trufflehog.exe" -Recurse -File | Select-Object -First 1
    if (-not $trufflehogExe) { throw "TruffleHog extraction completed but trufflehog.exe was not found." }
    Add-UserPath -Path $trufflehogExe.DirectoryName
    & $trufflehogExe.FullName --version
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Warning "Git is required for pinned repository checkout. Install Git for Windows before running an audit."
}
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Warning "Node.js/npm are required for JavaScript dependency analysis. Install Node.js LTS before running that stage."
}
elseif (-not (Get-Command snyk -ErrorAction SilentlyContinue)) {
    Write-Host "Optional Snyk CLI is not installed. Official npm install command: npm install -g snyk" -ForegroundColor Yellow
}

Write-Host "Windows-native setup complete." -ForegroundColor Green
Write-Host "For Halmos, Echidna, Slither, Mythril, Foundry, and Semgrep, run install-wsl.sh inside Ubuntu/WSL2."
Write-Host "Restart the terminal so persisted user PATH changes are visible to new processes."
