#!/bin/zsh

# =============================================================================
# CYBERSECURITY AI PLATFORM - FINAL VERIFICATION SCRIPT
# =============================================================================
# This script performs final verification before GitHub upload
# =============================================================================

echo "🔍 FINAL VERIFICATION FOR GITHUB UPLOAD"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verification results
PASS=0
WARN=0
FAIL=0

check_pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((PASS++))
}

check_warn() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
    ((WARN++))
}

check_fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    ((FAIL++))
}

echo -e "\n${BLUE}1. ESSENTIAL FILES CHECK${NC}"
echo "─────────────────────────────────────"

# Check essential files
if [[ -f "README.md" ]]; then
    check_pass "README.md exists"
else
    check_fail "README.md missing"
fi

if [[ -f "LICENSE" ]]; then
    check_pass "LICENSE exists"
else
    check_fail "LICENSE missing"
fi

if [[ -f ".gitignore" ]]; then
    check_pass ".gitignore exists"
else
    check_fail ".gitignore missing"
fi

if [[ -f "GITHUB_DEPLOYMENT_GUIDE.md" ]]; then
    check_pass "Deployment guide exists"
else
    check_warn "Deployment guide missing"
fi

echo -e "\n${BLUE}2. PROJECT STRUCTURE CHECK${NC}"
echo "─────────────────────────────────────"

# Check core directories
for dir in "core" "agents" "integrations" "config" "docs" "deployment"; do
    if [[ -d "$dir" ]]; then
        check_pass "Directory '$dir' exists"
    else
        check_fail "Directory '$dir' missing"
    fi
done

# Check key files
if [[ -f "core/main.py" ]]; then
    check_pass "Main entry point exists"
else
    check_fail "core/main.py missing"
fi

if [[ -f "agents/health_monitor.py" ]]; then
    check_pass "Health monitor exists (duplicates removed)"
else
    check_fail "agents/health_monitor.py missing"
fi

echo -e "\n${BLUE}3. SECURITY CHECK${NC}"
echo "─────────────────────────────────────"

# Check for sensitive files
sensitive_files=(
    "*.key"
    "*.pem" 
    "*secret*"
    "*password*"
    ".env"
    "api_keys.*"
)

sensitive_found=false
for pattern in "${sensitive_files[@]}"; do
    if ls $pattern 2>/dev/null | grep -q .; then
        check_fail "Sensitive file found: $pattern"
        sensitive_found=true
    fi
done

if [[ "$sensitive_found" = false ]]; then
    check_pass "No sensitive files in root directory"
fi

# Check for symlinks (should be removed)
if find . -type l | grep -q .; then
    check_warn "Symlinks found (may cause issues):"
    find . -type l
else
    check_pass "No problematic symlinks found"
fi

echo -e "\n${BLUE}4. SIZE AND OPTIMIZATION CHECK${NC}"
echo "─────────────────────────────────────"

# Check project size
size=$(du -sh . | cut -f1)
size_mb=$(du -sm . | cut -f1)

if [[ $size_mb -lt 50 ]]; then
    check_pass "Project size optimized: $size"
elif [[ $size_mb -lt 100 ]]; then
    check_warn "Project size acceptable: $size"
else
    check_fail "Project size too large: $size"
fi

# Check for large files
large_files=$(find . -size +10M -type f 2>/dev/null)
if [[ -z "$large_files" ]]; then
    check_pass "No files larger than 10MB"
else
    check_warn "Large files found:"
    echo "$large_files"
fi

# Check for cache files
cache_files=$(find . -name "__pycache__" -o -name "*.pyc" 2>/dev/null)
if [[ -z "$cache_files" ]]; then
    check_pass "No Python cache files found"
else
    check_fail "Python cache files still present"
fi

echo -e "\n${BLUE}5. FRAMEWORK INTEGRATION CHECK${NC}"
echo "─────────────────────────────────────"

# Check CAI integration
if [[ -f "integrations/cai_integration.py" ]] && [[ -d "CAI" ]]; then
    check_pass "CAI framework integration ready"
else
    check_warn "CAI integration may be incomplete"
fi

# Check PentestGPT integration  
if [[ -f "integrations/pentestgpt_integration.py" ]] && [[ -d "PentestGPT" ]]; then
    check_pass "PentestGPT framework integration ready"
else
    check_warn "PentestGPT integration may be incomplete"
fi

# Check agent orchestrator
if [[ -f "core/agent_orchestrator.py" ]]; then
    check_pass "Agent orchestrator exists"
else
    check_fail "Agent orchestrator missing"
fi

echo -e "\n${BLUE}6. DOCUMENTATION CHECK${NC}"
echo "─────────────────────────────────────"

# Check README content
if grep -q "Cybersecurity AI Agent Platform" README.md 2>/dev/null; then
    check_pass "README has proper title"
else
    check_warn "README title may need updating"
fi

if grep -q "Quick Start" README.md 2>/dev/null; then
    check_pass "README has Quick Start section"
else
    check_warn "README missing Quick Start section"
fi

# Check documentation files
doc_files=("docs/DEPLOYMENT_COMPLETE.md" "docs/CAI_vs_PentestGPT_GUIDE.md" "docs/PROJECT_STRUCTURE.md")
for doc in "${doc_files[@]}"; do
    if [[ -f "$doc" ]]; then
        check_pass "Documentation: $(basename $doc)"
    else
        check_warn "Missing documentation: $(basename $doc)"
    fi
done

echo -e "\n${BLUE}VERIFICATION SUMMARY${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ PASSED: $PASS${NC}"
echo -e "${YELLOW}⚠️  WARNINGS: $WARN${NC}"  
echo -e "${RED}❌ FAILED: $FAIL${NC}"

echo -e "\n${BLUE}PROJECT STATISTICS${NC}"
echo "─────────────────────────────────────"
echo "📁 Size: $(du -sh . | cut -f1)"
echo "📂 Files: $(find . -type f | wc -l)"
echo "🐍 Python files: $(find . -name "*.py" | wc -l)"
echo "⚙️  Config files: $(find . -name "*.yaml" -o -name "*.yml" -o -name "*.json" | wc -l)"

if [[ $FAIL -eq 0 ]]; then
    echo -e "\n${GREEN}🎉 PROJECT READY FOR GITHUB UPLOAD!${NC}"
    echo -e "\n${BLUE}Next steps:${NC}"
    echo "1. git init"
    echo "2. git add ."
    echo "3. git commit -m 'Initial commit: Cybersecurity AI Agent Platform'"
    echo "4. git remote add origin <your-repo-url>"
    echo "5. git push -u origin main"
    
    if [[ $WARN -gt 0 ]]; then
        echo -e "\n${YELLOW}Note: $WARN warnings found - review before upload${NC}"
    fi
else
    echo -e "\n${RED}❌ PROJECT NOT READY - $FAIL critical issues found${NC}"
    echo "Please fix the failed checks before uploading to GitHub"
fi

echo -e "\n${BLUE}Happy coding! 🛡️${NC}"
