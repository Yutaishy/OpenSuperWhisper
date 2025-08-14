#!/bin/bash
#
# Issue Monitor and Management Script
# Monitors GitHub issues and automates triage/response

set -e

# Configuration
REPO=${GITHUB_REPOSITORY:-"opensuperwhisper/opensuperwhisper"}
DAYS_STALE=${DAYS_STALE:-30}
DAYS_CLOSE=${DAYS_CLOSE:-7}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Print banner
echo "========================================="
echo "GitHub Issue Monitor"
echo "Repository: $REPO"
echo "========================================="

# Check gh CLI
if ! command -v gh &> /dev/null; then
    echo -e "${RED}GitHub CLI (gh) is required${NC}"
    exit 1
fi

# Function to print section
print_section() {
    echo ""
    echo -e "${BLUE}▶ $1${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# ==========================================
# Issue Statistics
# ==========================================
print_section "Issue Statistics"

OPEN_ISSUES=$(gh issue list --repo "$REPO" --state open --json number --jq '. | length')
OPEN_BUGS=$(gh issue list --repo "$REPO" --state open --label bug --json number --jq '. | length')
OPEN_FEATURES=$(gh issue list --repo "$REPO" --state open --label enhancement --json number --jq '. | length')
NEEDS_TRIAGE=$(gh issue list --repo "$REPO" --state open --label needs-triage --json number --jq '. | length')

echo "Open Issues: $OPEN_ISSUES"
echo "  Bugs: $OPEN_BUGS"
echo "  Features: $OPEN_FEATURES"
echo "  Needs Triage: $NEEDS_TRIAGE"

# ==========================================
# Critical Issues
# ==========================================
print_section "Critical Issues"

CRITICAL=$(gh issue list --repo "$REPO" --state open --search "critical in:title,body" --json number,title,labels,createdAt --jq '.[] | "\(.number): \(.title)"')

if [ -n "$CRITICAL" ]; then
    echo -e "${RED}Found critical issues:${NC}"
    echo "$CRITICAL"
else
    echo -e "${GREEN}No critical issues found${NC}"
fi

# ==========================================
# Stale Issues
# ==========================================
print_section "Stale Issue Management"

# Find stale issues
STALE_DATE=$(date -d "$DAYS_STALE days ago" +%Y-%m-%d)

echo "Checking for issues older than $DAYS_STALE days..."

gh issue list --repo "$REPO" --state open --json number,title,updatedAt,labels | \
jq -r --arg date "$STALE_DATE" '.[] | select(.updatedAt < $date) | select(.labels | map(.name) | index("stale") | not) | .number' | \
while read -r issue_num; do
    if [ -n "$issue_num" ]; then
        echo "  Marking #$issue_num as stale..."
        
        gh issue comment "$issue_num" --repo "$REPO" --body "This issue has been automatically marked as stale because it has not had recent activity. It will be closed in $DAYS_CLOSE days if no further activity occurs. Thank you for your contributions."
        
        gh issue edit "$issue_num" --repo "$REPO" --add-label "stale"
    fi
done

# ==========================================
# Close Stale Issues
# ==========================================
print_section "Closing Abandoned Issues"

CLOSE_DATE=$(date -d "$((DAYS_STALE + DAYS_CLOSE)) days ago" +%Y-%m-%d)

gh issue list --repo "$REPO" --state open --label stale --json number,updatedAt | \
jq -r --arg date "$CLOSE_DATE" '.[] | select(.updatedAt < $date) | .number' | \
while read -r issue_num; do
    if [ -n "$issue_num" ]; then
        echo "  Closing #$issue_num..."
        
        gh issue close "$issue_num" --repo "$REPO" --comment "This issue was closed automatically due to inactivity. Feel free to reopen if the issue persists."
    fi
done

# ==========================================
# Auto-label Issues
# ==========================================
print_section "Auto-labeling Issues"

# Label bugs
gh issue list --repo "$REPO" --state open --json number,title,body,labels | \
jq -r '.[] | select(.labels | length == 0) | select(.title + .body | test("(?i)(bug|error|crash|fail|broken|wrong|issue|problem)")) | .number' | \
while read -r issue_num; do
    if [ -n "$issue_num" ]; then
        echo "  Adding 'bug' label to #$issue_num"
        gh issue edit "$issue_num" --repo "$REPO" --add-label "bug,needs-triage"
    fi
done

# Label features
gh issue list --repo "$REPO" --state open --json number,title,body,labels | \
jq -r '.[] | select(.labels | length == 0) | select(.title + .body | test("(?i)(feature|enhance|add|implement|support|request)")) | .number' | \
while read -r issue_num; do
    if [ -n "$issue_num" ]; then
        echo "  Adding 'enhancement' label to #$issue_num"
        gh issue edit "$issue_num" --repo "$REPO" --add-label "enhancement,needs-triage"
    fi
done

# ==========================================
# Duplicate Detection
# ==========================================
print_section "Duplicate Detection"

echo "Checking for potential duplicates..."

# Get all open issues
gh issue list --repo "$REPO" --state open --json number,title --jq '.[] | "\(.number):\(.title)"' | \
while IFS=: read -r num1 title1; do
    gh issue list --repo "$REPO" --state open --json number,title --jq '.[] | "\(.number):\(.title)"' | \
    while IFS=: read -r num2 title2; do
        if [ "$num1" -lt "$num2" ]; then
            # Simple similarity check (you might want to use a more sophisticated algorithm)
            if [[ "${title1,,}" == *"${title2,,}"* ]] || [[ "${title2,,}" == *"${title1,,}"* ]]; then
                echo -e "${YELLOW}Potential duplicates: #$num1 and #$num2${NC}"
            fi
        fi
    done
done

# ==========================================
# Response Time Analysis
# ==========================================
print_section "Response Time Analysis"

echo "Analyzing response times..."

NO_RESPONSE=$(gh issue list --repo "$REPO" --state open --json number,comments,createdAt | \
jq -r '.[] | select(.comments == 0) | .number' | wc -l)

echo "Issues without any response: $NO_RESPONSE"

if [ "$NO_RESPONSE" -gt 0 ]; then
    echo -e "${YELLOW}Consider responding to these issues${NC}"
fi

# ==========================================
# Generate Report
# ==========================================
print_section "Generating Report"

REPORT_FILE="issue-report-$(date +%Y%m%d).md"

cat > "$REPORT_FILE" << EOF
# Issue Management Report
Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
Repository: $REPO

## Summary
- **Open Issues**: $OPEN_ISSUES
  - Bugs: $OPEN_BUGS
  - Features: $OPEN_FEATURES
  - Needs Triage: $NEEDS_TRIAGE
- **Issues without response**: $NO_RESPONSE

## Actions Taken
- Issues marked as stale: $(gh issue list --repo "$REPO" --label stale --state open --json number --jq '. | length')
- Issues auto-labeled: Check workflow logs

## Recommendations
1. Respond to issues without any comments
2. Review and triage new issues
3. Close or update stale issues
4. Review potential duplicates

## Top Contributors This Month
$(gh api "repos/$REPO/contributors?since=$(date -d '30 days ago' +%Y-%m-%d)" --jq '.[:5] | .[] | "- \(.login): \(.contributions) contributions"')

EOF

echo -e "${GREEN}Report saved to: $REPORT_FILE${NC}"

# ==========================================
# Summary
# ==========================================
echo ""
echo "========================================="
echo -e "${GREEN}Issue monitoring complete!${NC}"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Review issues needing triage"
echo "2. Respond to unanswered issues"
echo "3. Check the generated report: $REPORT_FILE"