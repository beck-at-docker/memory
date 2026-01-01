#!/usr/bin/env python3
"""
Final cleanup - identify what can be removed
"""

from pathlib import Path
import os

def main():
    os.chdir(Path.home() / "Documents" / "private")
    
    print("Memory System - Cleanup Analysis")
    print("=" * 60)
    print()
    
    # Core memory system files (MUST KEEP)
    core_files = {
        # Python core
        "config.py",
        "logging_config.py",
        "insight_system_simple.py",
        "claude_memory_client.py",
        "memory_api.py",
        "memory_mcp_server_simple.py",
        
        # Scripts
        "therapy.sh",
        "therapy_wrapper.sh",
        "start_interactive_memory.sh",
        "setup_env.py",
        "requirements_simple.txt",
        
        # Hooks and utilities  
        "claude_hooks.py",
        "extract_conversation_insights.py",
        "setup_claude_integration.py",
        
        # Tests (part of system)
        "test_system.py",
        "test_access_restriction.py",
        
        # Documentation
        "README.md",
        "README2.md",
        "CLAUDE.md",
        ".env.example",
        ".gitignore",
    }
    
    # Useful additions to keep
    useful_keep = {
        "test_mcp_server.py",  # Test MCP integration
        "test_memory_system.py",  # Test API
        "QUICK_REFERENCE.md",  # Daily reference
    }
    
    # Temporary/fix files to DELETE
    to_delete = {
        "test_fixes.py",  # My test script
        "finalize_setup.py",
        "repair_system.py",
        "quick_fix.sh",
        "verify_system.sh",
        "verify_all_fixes.py",
        "cleanup.py",
        "simple_repair.sh",
        
        # Documentation from fixes
        "FIX_GUIDE.md",
        "README_FIXES.md",
        "SYSTEM_FIXED.md",
        "CONFIGURATION_DONE.md",
        "CONFIGURE_CLAUDE_CODE.md",
        "VERIFICATION_COMPLETE.md",
    }
    
    print("Scanning current directory...")
    existing = {f.name for f in Path(".").iterdir() if f.is_file()}
    
    print("\n📋 CORE SYSTEM FILES (keep):")
    for f in sorted(core_files):
        status = "✓" if f in existing else "✗ MISSING"
        print(f"  {status} {f}")
    
    print("\n📋 USEFUL ADDITIONS (keep):")
    for f in sorted(useful_keep):
        status = "✓" if f in existing else "✗ missing"
        print(f"  {status} {f}")
    
    print("\n🗑️  FILES TO DELETE:")
    deleted = []
    for f in sorted(to_delete):
        if f in existing:
            try:
                Path(f).unlink()
                deleted.append(f)
                print(f"  ✓ Deleted {f}")
            except Exception as e:
                print(f"  ✗ Failed to delete {f}: {e}")
        # else: file doesn't exist, nothing to do
    
    print()
    if deleted:
        print(f"✅ Cleaned up {len(deleted)} temporary files")
    else:
        print("✅ No temporary files found (already clean)")
    
    print()
    print("=" * 60)
    print("Directory is clean and ready!")
    print()
    
    # Check for missing core files
    missing_core = [f for f in core_files if f not in existing]
    if missing_core:
        print("⚠️  WARNING: Missing core files:")
        for f in missing_core:
            print(f"  • {f}")
        print()
        print("These files should exist. Check if they're in a subdirectory.")
    
if __name__ == "__main__":
    main()
