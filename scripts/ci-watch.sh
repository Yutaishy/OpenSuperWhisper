#!/bin/bash
#
# CI/CD Pipeline Monitor and Auto-Retry Script
# Monitors GitHub Actions workflows and automatically retries failed jobs

set -e

# Configuration
MAX_RETRIES=${MAX_RETRIES:-3}
RETRY_DELAY=${RETRY_DELAY:-60}  # Initial delay in seconds
BACKOFF_MULTIPLIER=${BACKOFF_MULTIPLIER:-2}
WORKFLOW_NAME=${WORKFLOW_NAME:-"CI/CD Pipeline"}
DEBUG=${DEBUG:-false}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Counters
RETRY_COUNT=0
CONSECUTIVE_FAILURES=0

# Print with timestamp
log() {
    echo -e "${CYAN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS:${NC} $1"
}

# Check if gh CLI is installed
check_gh_cli() {
    if ! command -v gh &> /dev/null; then
        error "GitHub CLI (gh) is not installed"
        echo "Install it from: https://cli.github.com/"
        exit 1
    fi
    
    # Check if authenticated
    if ! gh auth status &> /dev/null; then
        error "Not authenticated with GitHub"
        echo "Run: gh auth login"
        exit 1
    fi
}

# Get latest workflow run
get_latest_run() {
    local workflow="${1:-$WORKFLOW_NAME}"
    
    if [ "$DEBUG" = true ]; then
        log "Fetching latest run for workflow: $workflow"
    fi
    
    gh run list \
        --workflow="$workflow" \
        --limit=1 \
        --json databaseId,status,conclusion,headBranch,displayTitle,createdAt \
        | jq -r '.[0]'
}

# Get specific run details
get_run_details() {
    local run_id=$1
    gh run view "$run_id" --json status,conclusion,jobs
}

# Wait for workflow to complete
wait_for_completion() {
    local run_id=$1
    local timeout=${2:-3600}  # Default 1 hour timeout
    local elapsed=0
    local check_interval=30
    
    log "Monitoring run #$run_id..."
    
    while [ $elapsed -lt $timeout ]; do
        local status=$(gh run view "$run_id" --json status -q .status)
        
        case "$status" in
            completed)
                return 0
                ;;
            in_progress|queued|waiting)
                echo -n "."
                sleep $check_interval
                elapsed=$((elapsed + check_interval))
                ;;
            *)
                warning "Unknown status: $status"
                return 1
                ;;
        esac
    done
    
    warning "Timeout waiting for run completion"
    return 1
}

# Retry failed jobs
retry_failed_jobs() {
    local run_id=$1
    local current_delay=$RETRY_DELAY
    
    log "Retrying failed jobs for run #$run_id"
    
    # Get failed jobs
    local failed_jobs=$(gh run view "$run_id" --json jobs \
        | jq -r '.jobs[] | select(.conclusion == "failure") | .name')
    
    if [ -z "$failed_jobs" ]; then
        success "No failed jobs to retry"
        return 0
    fi
    
    warning "Failed jobs found:"
    echo "$failed_jobs" | while read -r job; do
        echo "  - $job"
    done
    
    # Retry with exponential backoff
    for i in $(seq 1 $MAX_RETRIES); do
        log "Retry attempt $i/$MAX_RETRIES (waiting ${current_delay}s)..."
        sleep $current_delay
        
        # Trigger retry
        if gh run rerun "$run_id" --failed 2>/dev/null; then
            success "Retry triggered successfully"
            
            # Wait for completion
            if wait_for_completion "$run_id"; then
                local conclusion=$(gh run view "$run_id" --json conclusion -q .conclusion)
                
                if [ "$conclusion" = "success" ]; then
                    success "Run succeeded after retry!"
                    CONSECUTIVE_FAILURES=0
                    return 0
                fi
            fi
        else
            error "Failed to trigger retry"
        fi
        
        current_delay=$((current_delay * BACKOFF_MULTIPLIER))
        RETRY_COUNT=$((RETRY_COUNT + 1))
    done
    
    error "Max retries ($MAX_RETRIES) exceeded"
    CONSECUTIVE_FAILURES=$((CONSECUTIVE_FAILURES + 1))
    return 1
}

# Create GitHub issue for persistent failures
create_failure_issue() {
    local run_id=$1
    local run_url="https://github.com/$GITHUB_REPOSITORY/actions/runs/$run_id"
    
    local title="CI/CD Pipeline Failure - Auto-retry exhausted"
    local body="## Automated Failure Report

**Run ID:** #$run_id
**URL:** $run_url
**Retries attempted:** $RETRY_COUNT
**Consecutive failures:** $CONSECUTIVE_FAILURES

### Action Required
The CI/CD pipeline has failed after $MAX_RETRIES automatic retry attempts.
Manual intervention is required.

### Failed Jobs
\`\`\`
$(gh run view "$run_id" --json jobs | jq -r '.jobs[] | select(.conclusion == "failure") | .name')
\`\`\`

### Recent Logs
\`\`\`
$(gh run view "$run_id" --log-failed | head -100)
\`\`\`

---
*This issue was automatically created by ci-watch*"
    
    log "Creating GitHub issue for persistent failure..."
    
    gh issue create \
        --title "$title" \
        --body "$body" \
        --label "ci-failure" \
        --label "automated"
}

# Monitor specific workflow
monitor_workflow() {
    local workflow="${1:-$WORKFLOW_NAME}"
    local mode="${2:-watch}"  # watch or once
    
    log "Starting CI/CD monitor for: $workflow"
    log "Mode: $mode | Max retries: $MAX_RETRIES | Initial delay: ${RETRY_DELAY}s"
    
    while true; do
        # Get latest run
        local run_data=$(get_latest_run "$workflow")
        
        if [ -z "$run_data" ] || [ "$run_data" = "null" ]; then
            warning "No runs found for workflow: $workflow"
            
            if [ "$mode" = "once" ]; then
                exit 0
            fi
            
            sleep 60
            continue
        fi
        
        local run_id=$(echo "$run_data" | jq -r .databaseId)
        local status=$(echo "$run_data" | jq -r .status)
        local conclusion=$(echo "$run_data" | jq -r .conclusion)
        local branch=$(echo "$run_data" | jq -r .headBranch)
        local title=$(echo "$run_data" | jq -r .displayTitle)
        
        log "Latest run: #$run_id on $branch - $title"
        log "Status: $status | Conclusion: $conclusion"
        
        case "$status" in
            in_progress|queued|waiting)
                log "Workflow is running, monitoring..."
                wait_for_completion "$run_id"
                conclusion=$(gh run view "$run_id" --json conclusion -q .conclusion)
                ;;
        esac
        
        # Handle based on conclusion
        case "$conclusion" in
            success)
                success "Workflow completed successfully!"
                CONSECUTIVE_FAILURES=0
                ;;
            failure)
                error "Workflow failed!"
                
                if ! retry_failed_jobs "$run_id"; then
                    if [ $CONSECUTIVE_FAILURES -ge 3 ]; then
                        error "Too many consecutive failures!"
                        create_failure_issue "$run_id"
                        
                        if [ "$mode" = "watch" ]; then
                            warning "Pausing monitoring for 30 minutes..."
                            sleep 1800
                        fi
                    fi
                fi
                ;;
            cancelled|skipped)
                warning "Workflow was $conclusion"
                ;;
        esac
        
        if [ "$mode" = "once" ]; then
            break
        fi
        
        # Wait before next check
        log "Waiting 2 minutes before next check..."
        sleep 120
    done
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --workflow|-w)
                WORKFLOW_NAME="$2"
                shift 2
                ;;
            --max-retries|-r)
                MAX_RETRIES="$2"
                shift 2
                ;;
            --delay|-d)
                RETRY_DELAY="$2"
                shift 2
                ;;
            --once|-o)
                MODE="once"
                shift
                ;;
            --debug)
                DEBUG=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Show help message
show_help() {
    cat << EOF
CI/CD Pipeline Monitor and Auto-Retry Script

Usage: $(basename "$0") [OPTIONS]

Options:
    -w, --workflow NAME     Workflow name to monitor (default: "CI/CD Pipeline")
    -r, --max-retries N     Maximum retry attempts (default: 3)
    -d, --delay SECONDS     Initial retry delay in seconds (default: 60)
    -o, --once             Run once and exit (default: continuous monitoring)
    --debug                Enable debug output
    -h, --help             Show this help message

Environment Variables:
    MAX_RETRIES            Maximum retry attempts
    RETRY_DELAY            Initial retry delay
    BACKOFF_MULTIPLIER     Backoff multiplier for retries
    WORKFLOW_NAME          Default workflow name
    DEBUG                  Enable debug mode

Examples:
    # Monitor default workflow continuously
    $(basename "$0")
    
    # Monitor specific workflow once
    $(basename "$0") --workflow "Build" --once
    
    # Custom retry settings
    $(basename "$0") --max-retries 5 --delay 30
    
    # Debug mode
    $(basename "$0") --debug

EOF
}

# Main execution
main() {
    check_gh_cli
    parse_args "$@"
    
    # Set mode default
    MODE=${MODE:-watch}
    
    # Trap for cleanup
    trap 'echo ""; log "Monitor stopped"; exit 0' INT TERM
    
    # Start monitoring
    monitor_workflow "$WORKFLOW_NAME" "$MODE"
}

# Run if not sourced
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi