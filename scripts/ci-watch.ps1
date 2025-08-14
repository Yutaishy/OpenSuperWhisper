# CI/CD Pipeline Monitor and Auto-Retry Script (PowerShell)
# Monitors GitHub Actions workflows and automatically retries failed jobs

param(
    [string]$WorkflowName = "CI/CD Pipeline",
    [int]$MaxRetries = 3,
    [int]$RetryDelay = 60,
    [int]$BackoffMultiplier = 2,
    [switch]$Once,
    [switch]$Debug,
    [switch]$Help
)

# Configuration
$ErrorActionPreference = "Stop"
$RetryCount = 0
$ConsecutiveFailures = 0

# Show help
if ($Help) {
    @"
CI/CD Pipeline Monitor and Auto-Retry Script

Usage: ci-watch.ps1 [OPTIONS]

Options:
    -WorkflowName NAME     Workflow name to monitor (default: "CI/CD Pipeline")
    -MaxRetries N         Maximum retry attempts (default: 3)
    -RetryDelay SECONDS   Initial retry delay in seconds (default: 60)
    -Once                Run once and exit (default: continuous monitoring)
    -Debug               Enable debug output
    -Help                Show this help message

Examples:
    # Monitor default workflow continuously
    .\ci-watch.ps1
    
    # Monitor specific workflow once
    .\ci-watch.ps1 -WorkflowName "Build" -Once
    
    # Custom retry settings
    .\ci-watch.ps1 -MaxRetries 5 -RetryDelay 30
"@
    exit 0
}

# Logging functions
function Write-Log {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message" -ForegroundColor Cyan
}

function Write-Error-Log {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] ERROR: $Message" -ForegroundColor Red
}

function Write-Warning-Log {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] WARNING: $Message" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] SUCCESS: $Message" -ForegroundColor Green
}

# Check if gh CLI is installed
function Test-GhCli {
    $gh = Get-Command gh -ErrorAction SilentlyContinue
    if (-not $gh) {
        Write-Error-Log "GitHub CLI (gh) is not installed"
        Write-Host "Install it from: https://cli.github.com/"
        exit 1
    }
    
    # Check if authenticated
    try {
        gh auth status 2>&1 | Out-Null
    } catch {
        Write-Error-Log "Not authenticated with GitHub"
        Write-Host "Run: gh auth login"
        exit 1
    }
}

# Get latest workflow run
function Get-LatestRun {
    param([string]$Workflow = $WorkflowName)
    
    if ($Debug) {
        Write-Log "Fetching latest run for workflow: $Workflow"
    }
    
    try {
        $runs = gh run list `
            --workflow="$Workflow" `
            --limit=1 `
            --json databaseId,status,conclusion,headBranch,displayTitle,createdAt `
            | ConvertFrom-Json
        
        return $runs[0]
    } catch {
        Write-Warning-Log "Failed to fetch workflow runs: $_"
        return $null
    }
}

# Get run details
function Get-RunDetails {
    param([int]$RunId)
    
    try {
        gh run view $RunId --json status,conclusion,jobs | ConvertFrom-Json
    } catch {
        Write-Warning-Log "Failed to get run details: $_"
        return $null
    }
}

# Wait for workflow completion
function Wait-ForCompletion {
    param(
        [int]$RunId,
        [int]$Timeout = 3600
    )
    
    Write-Log "Monitoring run #$RunId..."
    
    $elapsed = 0
    $checkInterval = 30
    
    while ($elapsed -lt $Timeout) {
        try {
            $status = gh run view $RunId --json status -q .status
            
            switch ($status) {
                "completed" {
                    return $true
                }
                { $_ -in "in_progress", "queued", "waiting" } {
                    Write-Host "." -NoNewline
                    Start-Sleep -Seconds $checkInterval
                    $elapsed += $checkInterval
                }
                default {
                    Write-Warning-Log "Unknown status: $status"
                    return $false
                }
            }
        } catch {
            Write-Error-Log "Error checking status: $_"
            return $false
        }
    }
    
    Write-Warning-Log "Timeout waiting for run completion"
    return $false
}

# Retry failed jobs
function Invoke-RetryFailedJobs {
    param([int]$RunId)
    
    Write-Log "Retrying failed jobs for run #$RunId"
    
    # Get failed jobs
    try {
        $runDetails = gh run view $RunId --json jobs | ConvertFrom-Json
        $failedJobs = $runDetails.jobs | Where-Object { $_.conclusion -eq "failure" }
        
        if ($failedJobs.Count -eq 0) {
            Write-Success "No failed jobs to retry"
            return $true
        }
        
        Write-Warning-Log "Failed jobs found:"
        $failedJobs | ForEach-Object {
            Write-Host "  - $($_.name)"
        }
    } catch {
        Write-Error-Log "Failed to get job details: $_"
        return $false
    }
    
    # Retry with exponential backoff
    $currentDelay = $RetryDelay
    
    for ($i = 1; $i -le $MaxRetries; $i++) {
        Write-Log "Retry attempt $i/$MaxRetries (waiting ${currentDelay}s)..."
        Start-Sleep -Seconds $currentDelay
        
        # Trigger retry
        try {
            gh run rerun $RunId --failed 2>&1 | Out-Null
            Write-Success "Retry triggered successfully"
            
            # Wait for completion
            if (Wait-ForCompletion -RunId $RunId) {
                $conclusion = gh run view $RunId --json conclusion -q .conclusion
                
                if ($conclusion -eq "success") {
                    Write-Success "Run succeeded after retry!"
                    $script:ConsecutiveFailures = 0
                    return $true
                }
            }
        } catch {
            Write-Error-Log "Failed to trigger retry: $_"
        }
        
        $currentDelay *= $BackoffMultiplier
        $script:RetryCount++
    }
    
    Write-Error-Log "Max retries ($MaxRetries) exceeded"
    $script:ConsecutiveFailures++
    return $false
}

# Create GitHub issue for persistent failures
function New-FailureIssue {
    param([int]$RunId)
    
    $repoInfo = gh repo view --json nameWithOwner -q .nameWithOwner
    $runUrl = "https://github.com/$repoInfo/actions/runs/$RunId"
    
    $title = "CI/CD Pipeline Failure - Auto-retry exhausted"
    
    # Get failed jobs
    $failedJobs = gh run view $RunId --json jobs | 
        ConvertFrom-Json | 
        Select-Object -ExpandProperty jobs | 
        Where-Object { $_.conclusion -eq "failure" } | 
        Select-Object -ExpandProperty name
    
    # Get recent logs
    $logs = gh run view $RunId --log-failed 2>&1 | Select-Object -First 100
    
    $body = @"
## Automated Failure Report

**Run ID:** #$RunId
**URL:** $runUrl
**Retries attempted:** $RetryCount
**Consecutive failures:** $ConsecutiveFailures

### Action Required
The CI/CD pipeline has failed after $MaxRetries automatic retry attempts.
Manual intervention is required.

### Failed Jobs
``````
$($failedJobs -join "`n")
``````

### Recent Logs
``````
$($logs -join "`n")
``````

---
*This issue was automatically created by ci-watch*
"@
    
    Write-Log "Creating GitHub issue for persistent failure..."
    
    try {
        gh issue create `
            --title $title `
            --body $body `
            --label "ci-failure" `
            --label "automated"
        
        Write-Success "Issue created successfully"
    } catch {
        Write-Error-Log "Failed to create issue: $_"
    }
}

# Monitor workflow
function Start-WorkflowMonitor {
    param(
        [string]$Workflow = $WorkflowName,
        [bool]$RunOnce = $Once
    )
    
    Write-Log "Starting CI/CD monitor for: $Workflow"
    Write-Log "Mode: $(if ($RunOnce) {'once'} else {'watch'}) | Max retries: $MaxRetries | Initial delay: ${RetryDelay}s"
    
    while ($true) {
        # Get latest run
        $runData = Get-LatestRun -Workflow $Workflow
        
        if (-not $runData) {
            Write-Warning-Log "No runs found for workflow: $Workflow"
            
            if ($RunOnce) {
                exit 0
            }
            
            Start-Sleep -Seconds 60
            continue
        }
        
        $runId = $runData.databaseId
        $status = $runData.status
        $conclusion = $runData.conclusion
        $branch = $runData.headBranch
        $title = $runData.displayTitle
        
        Write-Log "Latest run: #$runId on $branch - $title"
        Write-Log "Status: $status | Conclusion: $conclusion"
        
        # Wait if running
        if ($status -in "in_progress", "queued", "waiting") {
            Write-Log "Workflow is running, monitoring..."
            Wait-ForCompletion -RunId $runId
            $conclusion = gh run view $runId --json conclusion -q .conclusion
        }
        
        # Handle based on conclusion
        switch ($conclusion) {
            "success" {
                Write-Success "Workflow completed successfully!"
                $script:ConsecutiveFailures = 0
            }
            "failure" {
                Write-Error-Log "Workflow failed!"
                
                if (-not (Invoke-RetryFailedJobs -RunId $runId)) {
                    if ($ConsecutiveFailures -ge 3) {
                        Write-Error-Log "Too many consecutive failures!"
                        New-FailureIssue -RunId $runId
                        
                        if (-not $RunOnce) {
                            Write-Warning-Log "Pausing monitoring for 30 minutes..."
                            Start-Sleep -Seconds 1800
                        }
                    }
                }
            }
            { $_ -in "cancelled", "skipped" } {
                Write-Warning-Log "Workflow was $conclusion"
            }
        }
        
        if ($RunOnce) {
            break
        }
        
        # Wait before next check
        Write-Log "Waiting 2 minutes before next check..."
        Start-Sleep -Seconds 120
    }
}

# Main execution
try {
    # Check prerequisites
    Test-GhCli
    
    # Set up trap for Ctrl+C
    [Console]::TreatControlCAsInput = $false
    
    # Start monitoring
    Start-WorkflowMonitor -Workflow $WorkflowName -RunOnce $Once
    
} catch {
    Write-Error-Log "Unexpected error: $_"
    exit 1
} finally {
    Write-Log "Monitor stopped"
}