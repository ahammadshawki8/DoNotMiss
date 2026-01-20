#!/usr/bin/env python3
"""
Configuration Verification Script for DoNotMiss
Run this before deploying to check if all files are properly configured
"""

import os
import json
import re

def check_file_exists(path):
    """Check if file exists"""
    return os.path.exists(path)

def read_file(path):
    """Read file content"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return None

def check_backend():
    """Verify backend configuration"""
    print("\n📦 Checking Backend...")
    
    issues = []
    
    # Check required files
    files = [
        'backend/app.py',
        'backend/requirements.txt',
        'backend/Procfile',
        'backend/runtime.txt',
        'backend/.env.example'
    ]
    
    for file in files:
        if check_file_exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING")
            issues.append(f"Missing file: {file}")
    
    # Check app.py has correct endpoints
    app_content = read_file('backend/app.py')
    if app_content:
        endpoints = ['/health', '/api/tasks', '/api/tasks/<int:task_id>/mark-sent']
        for endpoint in endpoints:
            if endpoint in app_content:
                print(f"  ✅ Endpoint: {endpoint}")
            else:
                print(f"  ❌ Endpoint: {endpoint} - MISSING")
                issues.append(f"Missing endpoint: {endpoint}")
    
    return issues

def check_extension():
    """Verify extension configuration"""
    print("\n🔌 Checking Chrome Extension...")
    
    issues = []
    
    # Check required files
    files = [
        'donotmiss-extension/manifest.json',
        'donotmiss-extension/background.js',
        'donotmiss-extension/content.js',
        'donotmiss-extension/content.css'
    ]
    
    for file in files:
        if check_file_exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING")
            issues.append(f"Missing file: {file}")
    
    # Check manifest.json
    manifest_content = read_file('donotmiss-extension/manifest.json')
    if manifest_content:
        try:
            manifest = json.loads(manifest_content)
            
            # Check manifest version
            if manifest.get('manifest_version') == 3:
                print(f"  ✅ Manifest V3")
            else:
                print(f"  ⚠️  Not using Manifest V3")
                issues.append("Extension should use Manifest V3")
            
            # Check permissions
            if 'contextMenus' in manifest.get('permissions', []):
                print(f"  ✅ Context menu permission")
            else:
                print(f"  ❌ Missing context menu permission")
                issues.append("Missing contextMenus permission")
            
            # Check host permissions
            if manifest.get('host_permissions'):
                print(f"  ✅ Host permissions configured")
                host = manifest['host_permissions'][0]
                if 'localhost' in host or 'example.com' in host:
                    print(f"  ⚠️  Backend URL not updated: {host}")
                    issues.append("Update host_permissions with your Render URL")
            else:
                print(f"  ❌ No host permissions")
                issues.append("Add host_permissions for backend")
        except:
            print(f"  ❌ Invalid JSON in manifest.json")
            issues.append("manifest.json has invalid JSON")
    
    # Check background.js for backend URL
    bg_content = read_file('donotmiss-extension/background.js')
    if bg_content:
        match = re.search(r"BACKEND_URL\s*=\s*['\"]([^'\"]+)['\"]", bg_content)
        if match:
            url = match.group(1)
            print(f"  ℹ️  Backend URL: {url}")
            if 'localhost' in url or 'example.com' in url:
                print(f"  ⚠️  Backend URL not updated")
                issues.append("Update BACKEND_URL in background.js with your Render URL")
        else:
            print(f"  ❌ BACKEND_URL not found")
            issues.append("BACKEND_URL not defined in background.js")
    
    return issues

def check_forge():
    """Verify Forge app configuration"""
    print("\n⚡ Checking Forge App...")
    
    issues = []
    
    # Check required files
    files = [
        'donotmiss-forge/manifest.yml',
        'donotmiss-forge/src/index.js',
        'donotmiss-forge/package.json'
    ]
    
    for file in files:
        if check_file_exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING")
            issues.append(f"Missing file: {file}")
    
    # Check if React app is built
    if check_file_exists('donotmiss-forge/static/dashboard/build'):
        print(f"  ✅ React app built")
    else:
        print(f"  ⚠️  React app not built yet")
        issues.append("Run: cd donotmiss-forge/static/dashboard && npm run build")
    
    # Check index.js for backend URL
    index_content = read_file('donotmiss-forge/src/index.js')
    if index_content:
        match = re.search(r"FLASK_BACKEND_URL\s*=.*?['\"]([^'\"]+)['\"]", index_content)
        if match:
            url = match.group(1)
            print(f"  ℹ️  Backend URL: {url}")
            if 'localhost' in url or 'example.com' in url:
                print(f"  ⚠️  Backend URL not updated")
                issues.append("Update FLASK_BACKEND_URL in src/index.js with your Render URL")
        else:
            # Check for process.env
            if 'process.env.FLASK_BACKEND_URL' in index_content:
                print(f"  ℹ️  Using environment variable for backend URL")
    
    # Check manifest.yml for permissions
    manifest_content = read_file('donotmiss-forge/manifest.yml')
    if manifest_content:
        if 'external:' in manifest_content and 'fetch:' in manifest_content:
            print(f"  ✅ External fetch permissions configured")
            if 'localhost' in manifest_content or 'example.com' in manifest_content:
                print(f"  ⚠️  Backend URL not updated in manifest.yml")
                issues.append("Update backend URL in manifest.yml permissions")
        else:
            print(f"  ❌ Missing external fetch permissions")
            issues.append("Add external fetch permissions in manifest.yml")
    
    return issues

def check_render():
    """Verify Render configuration"""
    print("\n☁️  Checking Render Configuration...")
    
    issues = []
    
    if check_file_exists('render.yaml'):
        print(f"  ✅ render.yaml")
        
        content = read_file('render.yaml')
        if content:
            if 'donotmiss-backend' in content:
                print(f"  ✅ Backend service configured")
            else:
                print(f"  ❌ Backend service not found")
                issues.append("Backend service not configured in render.yaml")
            
            if 'donotmiss-db' in content:
                print(f"  ✅ Database configured")
            else:
                print(f"  ❌ Database not found")
                issues.append("Database not configured in render.yaml")
    else:
        print(f"  ❌ render.yaml - MISSING")
        issues.append("Missing render.yaml for deployment")
    
    return issues

def main():
    print("=" * 60)
    print("🔍 DoNotMiss Configuration Verification")
    print("=" * 60)
    
    all_issues = []
    
    # Check all components
    all_issues.extend(check_backend())
    all_issues.extend(check_extension())
    all_issues.extend(check_forge())
    all_issues.extend(check_render())
    
    # Summary
    print("\n" + "=" * 60)
    if all_issues:
        print(f"⚠️  Found {len(all_issues)} issue(s):")
        print("=" * 60)
        for i, issue in enumerate(all_issues, 1):
            print(f"{i}. {issue}")
        print("\n💡 Fix these issues before deploying")
    else:
        print("✅ All checks passed!")
        print("=" * 60)
        print("\n🚀 Ready to deploy!")
        print("\nNext steps:")
        print("1. Push to GitHub: git push origin main")
        print("2. Deploy on Render: https://dashboard.render.com/")
        print("3. Update extension with Render URL")
        print("4. Deploy Forge app: forge deploy")
    
    print()

if __name__ == "__main__":
    main()
