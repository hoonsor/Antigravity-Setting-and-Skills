[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

function Convert-UriToPath ($folderUri) {
    if ([string]::IsNullOrEmpty($folderUri)) { return $null }
    $decoded = [System.Uri]::UnescapeDataString($folderUri)
    if ($decoded -match "^file:///(.*)$") {
        $path = $matches[1] -replace '/', '\'
        return $path
    }
    return $decoded
}

$projectsDir = Join-Path $env:USERPROFILE ".gemini\config\projects"
if (-not (Test-Path $projectsDir)) {
    Write-Host "找不到專案設定目錄: $projectsDir" -ForegroundColor Red
    exit 1
}

$jsonFiles = Get-ChildItem -Path $projectsDir -Filter "*.json" | Where-Object { $_.Name -ne "outside-of-project.json" }

$results = @()
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  AntiGravity #全更新 - 所有登記專案遠端檢測與同步  " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

foreach ($file in $jsonFiles) {
    try {
        $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
        $projectName = $content.name
        if ([string]::IsNullOrEmpty($projectName)) {
            $projectName = $file.BaseName
        }

        $resources = $content.projectResources.resources
        if ($null -eq $resources -or $resources.Count -eq 0) {
            continue
        }

        foreach ($res in $resources) {
            $folderUri = $res.folderUri
            $localPath = Convert-UriToPath $folderUri
            if ([string]::IsNullOrEmpty($localPath)) {
                continue
            }

            $item = [PSCustomObject]@{
                ProjectName = $projectName
                Path = $localPath
                Status = ""
                Detail = ""
            }

            if (-not (Test-Path $localPath)) {
                $item.Status = "略過"
                $item.Detail = "本地資料夾不存在"
                $results += $item
                continue
            }

            # 檢查是否為 Git 倉庫
            git -C "$localPath" rev-parse --is-inside-work-tree 2>$null | Out-Null
            if ($LASTEXITCODE -ne 0) {
                $item.Status = "略過"
                $item.Detail = "非 Git 倉庫"
                $results += $item
                continue
            }

            # 檢查是否有設定遠端倉庫
            $remotes = git -C "$localPath" remote 2>$null
            if ([string]::IsNullOrWhiteSpace($remotes)) {
                $item.Status = "略過"
                $item.Detail = "未設定遠端倉庫 (無 remote)"
                $results += $item
                continue
            }

            Write-Host "正在檢測專案: $projectName ($localPath) ..." -ForegroundColor Yellow

            # Fetch 最新遠端資訊
            git -C "$localPath" fetch --all --prune 2>$null | Out-Null

            $currentBranch = git -C "$localPath" rev-parse --abbrev-ref HEAD 2>$null
            $localHead = git -C "$localPath" rev-parse HEAD 2>$null
            $remoteHead = git -C "$localPath" rev-parse "@{u}" 2>$null
            if ([string]::IsNullOrEmpty($remoteHead)) {
                $remoteHead = git -C "$localPath" rev-parse "origin/$currentBranch" 2>$null
            }

            if ([string]::IsNullOrEmpty($remoteHead)) {
                $item.Status = "略過"
                $item.Detail = "找不到對應的遠端追蹤分支"
                $results += $item
                continue
            }

            if ($localHead -eq $remoteHead) {
                $item.Status = "已是最新"
                $item.Detail = "本機與遠端分支 ($currentBranch) 內容完全一致"
                $results += $item
                continue
            }

            # 不一致，使用智慧 rebase 方式進行合併
            Write-Host "  -> 發現變更，正在執行 git pull --rebase ..." -ForegroundColor Cyan
            $pullOutput = git -C "$localPath" pull --rebase 2>&1
            if ($LASTEXITCODE -eq 0) {
                $item.Status = "成功更新"
                $item.Detail = "已透過 rebase 成功與遠端同步 ($currentBranch)"
            } else {
                # 發生衝突或失敗，安全中止 rebase
                git -C "$localPath" rebase --abort 2>$null | Out-Null
                $item.Status = "更新失敗"
                $item.Detail = "可能存在衝突或網路問題，已還原變更"
            }

            $results += $item
        }
    } catch {
        continue
    }
}

Write-Host "`n==================================================" -ForegroundColor Cyan
Write-Host "                 同步更新結果彙總                 " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

$results | Format-Table -Property @{Name="專案名稱";Expression={$_.ProjectName}}, @{Name="狀態";Expression={$_.Status}}, @{Name="詳細說明";Expression={$_.Detail}} -AutoSize

Write-Host "完成檢測共 $($results.Count) 個專案路徑。" -ForegroundColor Green
