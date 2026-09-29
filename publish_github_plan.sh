#!/usr/bin/env bash

set -euo pipefail

# ============================================================
# API Gateway - GitHub Project Publisher
#
# Creates:
#   - Labels
#   - Milestones
#   - Issues
#
# Safe to run multiple times.
# Existing milestones, labels and issues are skipped.
# ============================================================

API_VERSION="2026-03-10"

# ------------------------------------------------------------
# Repository
# ------------------------------------------------------------

REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')

echo
echo "=============================================="
echo " GitHub Project Publisher"
echo "=============================================="
echo "Repository: $REPO"
echo

# ------------------------------------------------------------
# GitHub API helper
# ------------------------------------------------------------

gh_api() {
    gh api \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: $API_VERSION" \
        "$@"
}

# ------------------------------------------------------------
# Check authentication
# ------------------------------------------------------------

echo "Checking GitHub authentication..."

gh auth status >/dev/null

echo "✓ GitHub authentication OK"
echo

# ------------------------------------------------------------
# Load existing milestones
# ------------------------------------------------------------

echo "Loading existing milestones..."

MILESTONES_JSON=$(
    gh_api \
        --paginate \
        "repos/$REPO/milestones?state=all&per_page=100" |
        jq -s 'add'
)

declare -A MILESTONE_IDS

while IFS=$'\t' read -r title number; do
    [[ -z "$title" ]] && continue
    MILESTONE_IDS["$title"]="$number"
done < <(
    echo "$MILESTONES_JSON" |
        jq -r '.[] | [.title, .number] | @tsv'
)

echo "✓ Existing milestones loaded: ${#MILESTONE_IDS[@]}"
echo

# ------------------------------------------------------------
# Load existing issues
# ------------------------------------------------------------

echo "Loading existing issues..."

ISSUES_JSON=$(
    gh_api \
        --paginate \
        "repos/$REPO/issues?state=all&per_page=100" |
        jq -s 'add | map(select(.pull_request == null))'
)

declare -A EXISTING_ISSUES

while IFS= read -r title; do
    [[ -z "$title" ]] && continue
    EXISTING_ISSUES["$title"]=1
done < <(
    echo "$ISSUES_JSON" |
        jq -r '.[].title'
)

echo "✓ Existing issues loaded: ${#EXISTING_ISSUES[@]}"
echo

# ------------------------------------------------------------
# Load existing labels
# ------------------------------------------------------------

echo "Loading existing labels..."

LABELS_JSON=$(
    gh_api \
        --paginate \
        "repos/$REPO/labels?per_page=100" |
        jq -s 'add'
)

declare -A EXISTING_LABELS

while IFS= read -r name; do
    [[ -z "$name" ]] && continue
    EXISTING_LABELS["$name"]=1
done < <(
    echo "$LABELS_JSON" |
        jq -r '.[].name'
)

echo "✓ Existing labels loaded: ${#EXISTING_LABELS[@]}"
echo

# ============================================================
# FUNCTIONS
# ============================================================

# ------------------------------------------------------------
# Create label if it doesn't exist
# ------------------------------------------------------------

create_label() {
    local name="$1"
    local color="$2"
    local description="$3"

    if [[ -n "${EXISTING_LABELS[$name]+x}" ]]; then
        echo "  ✓ Label exists: $name"
        return
    fi

    gh_api \
        --method POST \
        "repos/$REPO/labels" \
        --input - <<EOF >/dev/null
{
    "name": "$name",
    "color": "$color",
    "description": "$description"
}
EOF

    EXISTING_LABELS["$name"]=1

    echo "  + Created label: $name"
}

# ------------------------------------------------------------
# Create milestone if it doesn't exist
# ------------------------------------------------------------

create_milestone() {
    local title="$1"
    local description="$2"

    if [[ -n "${MILESTONE_IDS[$title]+x}" ]]; then
        echo "✓ Milestone exists: $title (#${MILESTONE_IDS[$title]})"
        return
    fi

    milestone_number=$(
        gh_api \
            --method POST \
            "repos/$REPO/milestones" \
            --input - <<EOF |
{
    "title": "$title",
    "description": "$description",
    "state": "open"
}
EOF
            jq -r '.number'
    )

    MILESTONE_IDS["$title"]="$milestone_number"

    echo "+ Created milestone: $title (#$milestone_number)"
}

# ------------------------------------------------------------
# Create issue if it doesn't exist
# ------------------------------------------------------------

create_issue() {
    local title="$1"
    local milestone="$2"
    local labels="$3"

    # --------------------------------------------------------
    # Check whether issue already exists
    # --------------------------------------------------------

    if [[ -n "${EXISTING_ISSUES[$title]+x}" ]]; then
        echo "  ✓ Issue exists: $title"
        return
    fi

    # --------------------------------------------------------
    # Resolve milestone number
    # --------------------------------------------------------

    local milestone_number="${MILESTONE_IDS[$milestone]:-}"

    if [[ -z "$milestone_number" ]]; then
        echo "  ERROR: Milestone not found: $milestone"
        return 1
    fi

    # --------------------------------------------------------
    # Convert comma-separated labels to JSON array
    # --------------------------------------------------------

    local labels_json

    labels_json=$(
        printf '%s' "$labels" |
            jq -R 'split(",") | map(gsub("^\\s+|\\s+$"; ""))'
    )

    # --------------------------------------------------------
    # Build issue payload
    # --------------------------------------------------------

    local payload

    payload=$(
        jq -n \
            --arg title "$title" \
            --arg milestone "$milestone" \
            --argjson milestone_number "$milestone_number" \
            --argjson labels "$labels_json" \
            '{
                title: $title,
                body: (
                    "Part of the **" + $milestone + "** milestone.\n\n" +
                    "This issue tracks the implementation of this item in the API Gateway project."
                ),
                milestone: $milestone_number,
                labels: $labels
            }'
    )

    # --------------------------------------------------------
    # Create issue
    # --------------------------------------------------------

    local issue_number

    issue_number=$(
        gh_api \
            --method POST \
            "repos/$REPO/issues" \
            --input - <<< "$payload" |
            jq -r '.number'
    )

    EXISTING_ISSUES["$title"]=1

    echo "  + Created issue #$issue_number: $title"
}

# ============================================================
# LABELS
# ============================================================

echo "=============================================="
echo " Labels"
echo "=============================================="

create_label \
    "enhancement" \
    "a2eeef" \
    "New functionality or improvement"

create_label \
    "database" \
    "1d76db" \
    "Database and persistence work"

create_label \
    "proxy" \
    "5319e7" \
    "Reverse proxy functionality"

create_label \
    "security" \
    "d73a4a" \
    "Security and access control"

create_label \
    "testing" \
    "0e8a16" \
    "Tests and test infrastructure"

create_label \
    "logging" \
    "fbca04" \
    "Logging and diagnostics"

create_label \
    "observability" \
    "7057ff" \
    "Metrics, monitoring and tracing"

create_label \
    "devops" \
    "0366d6" \
    "CI/CD, deployment and infrastructure"

create_label \
    "error-handling" \
    "b60205" \
    "Error and exception handling"

create_label \
    "configuration" \
    "cfd3d7" \
    "Application configuration"

create_label \
    "documentation" \
    "0075ca" \
    "Documentation"

create_label \
    "performance" \
    "f9d0c4" \
    "Performance and optimization"

echo

# ============================================================
# MILESTONE 1: FOUNDATION
# ============================================================

echo "=============================================="
echo " Milestone 1: Foundation"
echo "=============================================="

create_milestone \
    "Foundation" \
    "Establish the core FastAPI application and database architecture."

create_issue \
    "Project structure and configuration" \
    "Foundation" \
    "enhancement,configuration"

create_issue \
    "FastAPI application setup" \
    "Foundation" \
    "enhancement"

create_issue \
    "PostgreSQL integration" \
    "Foundation" \
    "database"

create_issue \
    "SQLAlchemy async ORM setup" \
    "Foundation" \
    "database"

create_issue \
    "Alembic migrations" \
    "Foundation" \
    "database"

create_issue \
    "Health checks" \
    "Foundation" \
    "enhancement"

create_issue \
    "Environment configuration" \
    "Foundation" \
    "configuration"

create_issue \
    "Logging setup" \
    "Foundation" \
    "logging"

create_issue \
    "Global exception handling" \
    "Foundation" \
    "error-handling"

echo

# ============================================================
# MILESTONE 2: API MANAGEMENT
# ============================================================

echo "=============================================="
echo " Milestone 2: API Management"
echo "=============================================="

create_milestone \
    "API Management" \
    "Allow users to register and manage upstream APIs."

create_issue \
    "API database model" \
    "API Management" \
    "database,enhancement"

create_issue \
    "Create API" \
    "API Management" \
    "enhancement"

create_issue \
    "List APIs" \
    "API Management" \
    "enhancement"

create_issue \
    "Get API by ID" \
    "API Management" \
    "enhancement"

create_issue \
    "Search APIs" \
    "API Management" \
    "enhancement"

create_issue \
    "Update API" \
    "API Management" \
    "enhancement"

create_issue \
    "Delete API" \
    "API Management" \
    "enhancement"

create_issue \
    "UUID-based API identifiers" \
    "API Management" \
    "database,enhancement"

create_issue \
    "Duplicate slug handling" \
    "API Management" \
    "error-handling"

create_issue \
    "API validation" \
    "API Management" \
    "enhancement"

create_issue \
    "CRUD tests" \
    "API Management" \
    "testing"

echo

# ============================================================
# MILESTONE 3: REVERSE PROXY MVP
# ============================================================

echo "=============================================="
echo " Milestone 3: Reverse Proxy MVP"
echo "=============================================="

create_milestone \
    "Reverse Proxy MVP" \
    "Make the API Gateway actually proxy requests to registered upstream APIs."

create_issue \
    "Resolve upstream API by slug" \
    "Reverse Proxy MVP" \
    "proxy,enhancement"

create_issue \
    "Build upstream URL" \
    "Reverse Proxy MVP" \
    "proxy,enhancement"

create_issue \
    "Forward HTTP methods" \
    "Reverse Proxy MVP" \
    "proxy,enhancement"

create_issue \
    "Forward query parameters" \
    "Reverse Proxy MVP" \
    "proxy,enhancement"

create_issue \
    "Forward request headers" \
    "Reverse Proxy MVP" \
    "proxy,enhancement"

create_issue \
    "Forward request body" \
    "Reverse Proxy MVP" \
    "proxy,enhancement"

create_issue \
    "Return upstream response" \
    "Reverse Proxy MVP" \
    "proxy,enhancement"

create_issue \
    "Handle upstream 4xx/5xx responses" \
    "Reverse Proxy MVP" \
    "proxy,error-handling"

create_issue \
    "Handle upstream connection errors" \
    "Reverse Proxy MVP" \
    "proxy,error-handling"

create_issue \
    "Handle upstream timeouts" \
    "Reverse Proxy MVP" \
    "proxy,error-handling"

create_issue \
    "Add proxy integration tests" \
    "Reverse Proxy MVP" \
    "proxy,testing"

echo

# ============================================================
# MILESTONE 4: SECURITY
# ============================================================

echo "=============================================="
echo " Milestone 4: Security"
echo "=============================================="

create_milestone \
    "Security" \
    "Protect APIs exposed through the gateway."

create_issue \
    "API key authentication" \
    "Security" \
    "security,enhancement"

create_issue \
    "API key storage and hashing" \
    "Security" \
    "security,database"

create_issue \
    "Authentication middleware/dependency" \
    "Security" \
    "security,enhancement"

create_issue \
    "Per-API access control" \
    "Security" \
    "security,enhancement"

create_issue \
    "Validate upstream URLs" \
    "Security" \
    "security"

create_issue \
    "SSRF protection" \
    "Security" \
    "security"

create_issue \
    "Private/internal IP protection" \
    "Security" \
    "security"

create_issue \
    "Secure header handling" \
    "Security" \
    "security,proxy"

echo

# ============================================================
# MILESTONE 5: RATE LIMITING
# ============================================================

echo "=============================================="
echo " Milestone 5: Rate Limiting"
echo "=============================================="

create_milestone \
    "Rate Limiting" \
    "Control traffic flowing through the API Gateway."

create_issue \
    "Rate-limit configuration per API" \
    "Rate Limiting" \
    "enhancement"

create_issue \
    "Request counting" \
    "Rate Limiting" \
    "enhancement"

create_issue \
    "Sliding/fixed window strategy" \
    "Rate Limiting" \
    "enhancement"

create_issue \
    "429 Too Many Requests" \
    "Rate Limiting" \
    "enhancement,error-handling"

create_issue \
    "Rate-limit response headers" \
    "Rate Limiting" \
    "enhancement"

create_issue \
    "Redis integration" \
    "Rate Limiting" \
    "enhancement,devops"

create_issue \
    "Rate-limit tests" \
    "Rate Limiting" \
    "testing"

echo

# ============================================================
# MILESTONE 6: OBSERVABILITY
# ============================================================

echo "=============================================="
echo " Milestone 6: Observability"
echo "=============================================="

create_milestone \
    "Observability" \
    "Make the gateway observable and operational."

create_issue \
    "Structured request logging" \
    "Observability" \
    "logging,observability"

create_issue \
    "Upstream latency logging" \
    "Observability" \
    "logging,observability"

create_issue \
    "Request/response metrics" \
    "Observability" \
    "observability"

create_issue \
    "Error metrics" \
    "Observability" \
    "observability"

create_issue \
    "Health/readiness endpoints" \
    "Observability" \
    "observability"

create_issue \
    "Correlation/request IDs" \
    "Observability" \
    "observability,logging"

create_issue \
    "Basic monitoring dashboard" \
    "Observability" \
    "observability"

echo

# ============================================================
# MILESTONE 7: QUALITY & RELEASE
# ============================================================

echo "=============================================="
echo " Milestone 7: Quality & Release"
echo "=============================================="

create_milestone \
    "Quality & Release" \
    "Make the API Gateway production-ready and shippable."

create_issue \
    "Increase test coverage" \
    "Quality & Release" \
    "testing"

create_issue \
    "SonarQube quality checks" \
    "Quality & Release" \
    "testing,devops"

create_issue \
    "CI pipeline" \
    "Quality & Release" \
    "devops"

create_issue \
    "Dependency/security scanning" \
    "Quality & Release" \
    "security,devops"

create_issue \
    "Production configuration" \
    "Quality & Release" \
    "configuration,devops"

create_issue \
    "Docker image" \
    "Quality & Release" \
    "devops"

create_issue \
    "Docker Compose" \
    "Quality & Release" \
    "devops"

create_issue \
    "Deployment documentation" \
    "Quality & Release" \
    "documentation"

create_issue \
    "API documentation cleanup" \
    "Quality & Release" \
    "documentation"

create_issue \
    "Release v1.0.0" \
    "Quality & Release" \
    "enhancement"

echo

# ============================================================
# SUMMARY
# ============================================================

echo "=============================================="
echo " GitHub plan published successfully"
echo "=============================================="
echo
echo "Repository:"
echo "  $REPO"
echo
echo "Milestones:"
echo "  1. Foundation"
echo "  2. API Management"
echo "  3. Reverse Proxy MVP"
echo "  4. Security"
echo "  5. Rate Limiting"
echo "  6. Observability"
echo "  7. Quality & Release"
echo
echo "The script is safe to run again."
echo "Existing milestones, labels and issues will be skipped."
echo