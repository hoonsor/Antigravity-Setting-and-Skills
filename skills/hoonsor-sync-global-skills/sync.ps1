# $env:USERPROFILE\.gemini\config\skills\hoonsor-sync-global-skills\sync.ps1
# This script is used to sync Antigravity settings and skills repository.

$ErrorActionPreference = "Stop"

# 1. Define paths
$ConfigDir = "$env:USERPROFILE\.gemini\config"
$AntigravityDir = "$env:USERPROFILE\.gemini\antigravity"
$SkillsDir = "$ConfigDir\skills"
$BackupMetaDir = "$ConfigDir\_meta_backups"
$McpConfigFile = "$ConfigDir\mcp_config.json"
$McpTemplateFile = "$ConfigDir\mcp_config.json.template"
$GitignoreFile = "$ConfigDir\.gitignore"
$RemoteUrl = "https://github.com/hoonsor/Antigravity-Setting-and-Skills"

Write-Host "=== Start Antigravity Settings and Skills Sync ===" -ForegroundColor Cyan

# 2. Mask sensitive keys in mcp_config.json and output to mcp_config.json.template
if (Test-Path $McpConfigFile) {
    Write-Host "Masking sensitive keys in mcp_config.json..." -ForegroundColor Yellow
    try {
        $json = Get-Content -Raw -Path $McpConfigFile | ConvertFrom-Json
        
        # Mask GitHub Token
        if ($json.mcpServers.'github-mcp-server'.env.GITHUB_PERSONAL_ACCESS_TOKEN) {
            $json.mcpServers.'github-mcp-server'.env.GITHUB_PERSONAL_ACCESS_TOKEN = "YOUR_GITHUB_PAT_HERE"
        }
        
        # Mask Google Drive local paths
        if ($json.mcpServers.gdrive.env.GDRIVE_OAUTH_PATH) {
            $json.mcpServers.gdrive.env.GDRIVE_OAUTH_PATH = "YOUR_GDRIVE_OAUTH_PATH_HERE"
        }
        if ($json.mcpServers.gdrive.env.GDRIVE_CREDENTIALS_PATH) {
            $json.mcpServers.gdrive.env.GDRIVE_CREDENTIALS_PATH = "YOUR_GDRIVE_CREDENTIALS_PATH_HERE"
        }
        
        # Output template
        $json | ConvertTo-Json -Depth 10 | Out-File -FilePath $McpTemplateFile -Encoding utf8
        Write-Host "Masked template generated: $McpTemplateFile" -ForegroundColor Green
    } catch {
        Write-Warning "Failed to mask mcp_config.json: $($_.Exception.Message)"
    }
} else {
    Write-Host "mcp_config.json not found, skipping masking." -ForegroundColor Yellow
}

# 3. Backup external config and error learning to config/_meta_backups/
if (-not (Test-Path $BackupMetaDir)) {
    New-Item -ItemType Directory -Path $BackupMetaDir -Force | Out-Null
}

# Backup gemini.md
$GeminiMdSrc = "$AntigravityDir\gemini.md"
$GeminiMdBak = "$BackupMetaDir\gemini.md"
if (Test-Path $GeminiMdSrc) {
    Write-Host "Backing up gemini.md..." -ForegroundColor Yellow
    Copy-Item -Path $GeminiMdSrc -Destination $GeminiMdBak -Force
    Write-Host "gemini.md backed up." -ForegroundColor Green
}

# Backup hoonsor-error-learning
$KnowledgeSrc = "$AntigravityDir\knowledge\hoonsor-error-learning"
$KnowledgeBak = "$BackupMetaDir\hoonsor-error-learning"
if (Test-Path $KnowledgeSrc) {
    Write-Host "Backing up hoonsor-error-learning..." -ForegroundColor Yellow
    if (Test-Path $KnowledgeBak) {
        Remove-Item -Path $KnowledgeBak -Recurse -Force | Out-Null
    }
    Copy-Item -Path $KnowledgeSrc -Destination $KnowledgeBak -Recurse -Force
    Write-Host "hoonsor-error-learning backed up." -ForegroundColor Green
}

# 4. Check and migrate Git repository
$OldGitDir = "$SkillsDir\.git"
$NewGitDir = "$ConfigDir\.git"

if ((Test-Path $OldGitDir) -and (-not (Test-Path $NewGitDir))) {
    Write-Host "Old Git repository found in skills/, migrating to config/..." -ForegroundColor Yellow
    Move-Item -Path $OldGitDir -Destination $NewGitDir -Force
    Write-Host "Git repository migrated." -ForegroundColor Green
}

# 5. Git sync and push
Push-Location $ConfigDir
try {
    # Initialize Git if not exists
    if (-not (Test-Path $NewGitDir)) {
        Write-Host "Initializing Git repository..." -ForegroundColor Yellow
        git init
    }
    
    # Configure remote URL
    $remotes = git remote -v
    if (($remotes | Out-String) -like "*origin*") {
        Write-Host "Setting remote origin URL to: $RemoteUrl" -ForegroundColor Yellow
        git remote set-url origin $RemoteUrl
    } else {
        Write-Host "Adding remote origin URL: $RemoteUrl" -ForegroundColor Yellow
        git remote add origin $RemoteUrl
    }
    
    # Git add
    Write-Host "Staging local changes..." -ForegroundColor Yellow
    git add -A
    
    # Git commit
    $status = git status --porcelain
    if ($status) {
        Write-Host "Local changes detected, committing..." -ForegroundColor Yellow
        git commit -m "chore: auto-sync configuration, skills, and templates (v1.4.0)"
    } else {
        Write-Host "No local changes to commit." -ForegroundColor Green
    }
    
    # Git pull --rebase
    Write-Host "Pulling latest changes from remote (git pull --rebase)..." -ForegroundColor Yellow
    git pull --rebase origin main
    
    # Git push
    Write-Host "Pushing changes to remote (git push)..." -ForegroundColor Yellow
    git push -u origin main
    Write-Host "Git sync completed successfully!" -ForegroundColor Green
} catch {
    Write-Error "Git sync failed: $($_.Exception.Message)"
} finally {
    Pop-Location
}

# 6. Restore remote updates back to local antigravity folders
Write-Host "Checking for remote updates to restore..." -ForegroundColor Yellow

# Restore gemini.md
if (Test-Path $GeminiMdBak) {
    $shouldCopy = $false
    if (Test-Path $GeminiMdSrc) {
        $bakTime = (Get-Item $GeminiMdBak).LastWriteTime
        $srcTime = (Get-Item $GeminiMdSrc).LastWriteTime
        if ($bakTime -gt $srcTime) {
            $shouldCopy = $true
        }
    } else {
        $shouldCopy = $true
    }
    
    if ($shouldCopy) {
        Write-Host "Restoring updated gemini.md to local..." -ForegroundColor Green
        $parentDir = Split-Path $GeminiMdSrc
        if (-not (Test-Path $parentDir)) { New-Item -ItemType Directory -Path $parentDir -Force | Out-Null }
        Copy-Item -Path $GeminiMdBak -Destination $GeminiMdSrc -Force
    }
}

# Restore hoonsor-error-learning
if (Test-Path $KnowledgeBak) {
    $shouldCopy = $false
    if (Test-Path $KnowledgeSrc) {
        $bakTime = (Get-Item $KnowledgeBak).LastWriteTime
        $srcTime = (Get-Item $KnowledgeSrc).LastWriteTime
        if ($bakTime -gt $srcTime) {
            $shouldCopy = $true
        }
    } else {
        $shouldCopy = $true
    }
    
    if ($shouldCopy) {
        Write-Host "Restoring updated hoonsor-error-learning to local..." -ForegroundColor Green
        if (Test-Path $KnowledgeSrc) {
            Remove-Item -Path $KnowledgeSrc -Recurse -Force | Out-Null
        }
        $parentDir = Split-Path $KnowledgeSrc
        if (-not (Test-Path $parentDir)) { New-Item -ItemType Directory -Path $parentDir -Force | Out-Null }
        Copy-Item -Path $KnowledgeBak -Destination $KnowledgeSrc -Recurse -Force
    }
}

Write-Host "=== Sync Process Finished ===" -ForegroundColor Green
