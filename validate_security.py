#!/usr/bin/env python3
"""
Security Validation Script for Kaggle Submission
Scans the repository for any hardcoded secrets before submitting
Run: python validate_security.py
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Sensitive patterns to detect
SENSITIVE_PATTERNS = {
    "API_KEY": r'(?i)api[_-]?key\s*[=:]\s*["\']([^"\']{20,})["\']',
    "PASSWORD": r'(?i)password\s*[=:]\s*["\']([^"\']{6,})["\']',
    "TOKEN": r'(?i)token\s*[=:]\s*["\']([^"\']{20,})["\']',
    "GEMINI_KEY": r'AIzaSy[A-Za-z0-9_-]{35}',
    "JIRA_TOKEN": r'ATATT[A-Za-z0-9_]{40}',
    "AWS_ACCESS": r'AKIA[0-9A-Z]{16}',
    "AWS_SECRET": r'aws_secret_access_key\s*=\s*[A-Za-z0-9/+=]{40}',
    "GITHUB_TOKEN": r'ghp_[A-Za-z0-9_]{36}',
    "CREDENTIALS_FILE": r'credentials\.json|secrets\.json|\.pem|\.key',
    "DB_PASSWORD": r'(?i)(mysql|postgres|mongodb).*password\s*[=:]\s*["\']([^"\']+)["\']',
}

# Directories to skip
SKIP_DIRS = {'.git', '__pycache__', 'venv', '.venv', 'node_modules', '.pytest_cache', 'build', 'dist', '.egg-info'}

# File extensions to scan
SCAN_EXTENSIONS = {'.py', '.json', '.yml', '.yaml', '.env', '.txt', '.md', '.sh', '.ps1', '.dockerfile'}

def scan_file(file_path: Path) -> List[Tuple[int, str, str]]:
    """Scan a single file for sensitive patterns"""
    findings = []
    # Skip documentation and checklist files
    if any(skip in str(file_path).lower() for skip in ['checklist', 'readme', 'docs', 'validate_security']):
        return findings
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                for pattern_name, pattern in SENSITIVE_PATTERNS.items():
                    if re.search(pattern, line):
                        # Don't report if line contains safe keywords
                        safe_keywords = ['example', 'todo', 'your-', 'placeholder', 'sample', 'pattern', 'regex', 
                                       'template', 'commented', '#', 'documentation', 'SENSITIVE_PATTERNS', 'r\'', 'r"']
                        if any(x in line.lower() for x in safe_keywords):
                            continue
                        findings.append((line_num, pattern_name, line.strip()[:100]))
    except Exception as e:
        print(f"⚠️  Error reading {file_path}: {e}")
    return findings

def scan_directory(start_path: str = '.') -> dict:
    """Recursively scan directory for secrets"""
    results = {
        "total_files_scanned": 0,
        "files_with_issues": [],
        "total_issues": 0,
        "critical_issues": []
    }
    
    path = Path(start_path)
    
    for file_path in path.rglob('*'):
        # Skip directories
        if file_path.is_dir():
            if any(skip in file_path.parts for skip in SKIP_DIRS):
                continue
        
        # Skip files not in our extensions list
        if file_path.suffix.lower() not in SCAN_EXTENSIONS:
            continue
        
        results["total_files_scanned"] += 1
        findings = scan_file(file_path)
        
        if findings:
            results["files_with_issues"].append({
                "file": str(file_path),
                "findings": findings
            })
            results["total_issues"] += len(findings)
            
            # Flag critical issues (not in example or docs)
            if 'example' not in str(file_path).lower() and 'docs' not in str(file_path).lower():
                for line_num, pattern, content in findings:
                    results["critical_issues"].append({
                        "file": str(file_path),
                        "line": line_num,
                        "pattern": pattern,
                        "content": content
                    })
    
    return results

def print_report(results: dict):
    """Print security scan report"""
    print("\n" + "="*70)
    print("🔐 SECURITY VALIDATION REPORT")
    print("="*70 + "\n")
    
    print(f"📊 Summary:")
    print(f"  Files Scanned: {results['total_files_scanned']}")
    print(f"  Issues Found: {results['total_issues']}")
    print(f"  Critical Issues: {len(results['critical_issues'])}\n")
    
    if results["critical_issues"]:
        print("❌ CRITICAL ISSUES DETECTED:\n")
        for issue in results["critical_issues"]:
            print(f"  📄 {issue['file']}:{issue['line']}")
            print(f"     Pattern: {issue['pattern']}")
            print(f"     Content: {issue['content']}\n")
        print("⚠️  STOP! Do not submit with these issues. Remove secrets and add to .gitignore\n")
        return False
    
    print("✅ SECURITY CHECK PASSED!")
    print("   No critical secrets detected in code.\n")
    
    if results["files_with_issues"]:
        print("⚠️  Note: Found some patterns in example/placeholder contexts:")
        for file_issue in results["files_with_issues"]:
            print(f"   - {file_issue['file']} ({len(file_issue['findings'])} matches)")
        print("   These are likely safe (examples/placeholders) but review manually.\n")
    
    return True

def check_gitignore(repo_path: str = '.') -> bool:
    """Verify .gitignore protects secrets"""
    gitignore_path = Path(repo_path) / '.gitignore'
    if not gitignore_path.exists():
        print("⚠️  WARNING: .gitignore not found!\n")
        return False
    
    with open(gitignore_path, 'r') as f:
        gitignore_content = f.read().lower()
    
    critical_patterns = ['.env', '*.key', '*.pem', 'credentials', 'secrets', '.aws', '.gcp']
    missing = [p for p in critical_patterns if p not in gitignore_content]
    
    if missing:
        print(f"⚠️  WARNING: .gitignore missing entries: {missing}\n")
        return False
    
    print("✅ .gitignore looks good - critical patterns protected\n")
    return True

if __name__ == "__main__":
    print("\n🔍 Performing security scan on repository...\n")
    
    # Get repo path from argument or use current directory
    repo_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    # Check .gitignore
    gitignore_ok = check_gitignore(repo_path)
    
    # Scan directory
    results = scan_directory(repo_path)
    
    # Print report
    scan_ok = print_report(results)
    
    print("="*70)
    if scan_ok and gitignore_ok:
        print("✅ Repository is safe for Kaggle submission!")
        sys.exit(0)
    else:
        print("❌ Please fix issues before submitting")
        sys.exit(1)
