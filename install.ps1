Param(
	[switch]$Force,
	[switch]$AddAliasC
)

Write-Host "[ccc] Install started..."

function Have-Cmd {
	param([string]$Name)
	$null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

$pythonCmd = "py"
if (-not (Have-Cmd $pythonCmd)) {
	if (Have-Cmd "python") {
		$pythonCmd = "python"
	} else {
		Write-Host "[ccc] Python not found. Install Python 3 and retry." -ForegroundColor Red
		exit 1
	}
}

if (Have-Cmd "pipx") {
	Write-Host "[ccc] pipx found. Installing via pipx..."
	if ($Force) {
		pipx install . --force
	} else {
		pipx install .
	}
} else {
	Write-Host "[ccc] pipx not found. Trying to install via pip (user)..."
	if ($pythonCmd -eq "py") {
		py -3 -m pip install --user pipx
		py -3 -m pipx ensurepath | Out-Null
	} else {
		python -m pip install --user pipx
		python -m pipx ensurepath | Out-Null
	}

	if (Have-Cmd "pipx") {
		Write-Host "[ccc] Installing via pipx..."
		if ($Force) {
			pipx install . --force
		} else {
			pipx install .
		}
	} else {
		Write-Host "[ccc] pipx still unavailable. Installing directly with pip..."
		if ($pythonCmd -eq "py") {
			if ($Force) {
				py -3 -m pip install . --upgrade
			} else {
				py -3 -m pip install .
			}
		} else {
			if ($Force) {
				python -m pip install . --upgrade
			} else {
				python -m pip install .
			}
		}
	}
}

Write-Host "[ccc] Done. You may need to restart PowerShell for 'ccc' to appear in PATH."
Write-Host "[ccc] Check: ccc --version"


if ($AddAliasC) {
	try {
		if (-not (Test-Path -LiteralPath $PROFILE)) {
			New-Item -ItemType File -Path $PROFILE -Force | Out-Null
		}
		Add-Content -Path $PROFILE -Value ""
		Add-Content -Path $PROFILE -Value "# ccc alias"
		Add-Content -Path $PROFILE -Value "Remove-Item Alias:c -ErrorAction SilentlyContinue"
		Add-Content -Path $PROFILE -Value "Set-Alias c ccc"
		Write-Host "[ccc] Added alias 'c' → 'ccc' to `$PROFILE. Restart PowerShell to apply."
	} catch {
		Write-Host "[ccc] Failed to update `$PROFILE for alias 'c'. Configure manually: 'Set-Alias c ccc'" -ForegroundColor Yellow
	}
}

