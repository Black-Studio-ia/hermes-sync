"""Test: verify hermes-sync can be imported and CLI is structured."""
import os
import sys
import tempfile
import shutil

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

from hermes_sync import __version__, __author__
from hermes_sync.git_ops import (
    git_init, git_add, git_commit, git_remote_add,
    git_push, git_pull, git_status, git_cfg_set, setup_git_repo
)
from hermes_sync.cli import main as cli_main

def test_version():
    assert __version__ == "0.1.0"
    assert __author__ == "Black Studio IA"
    print(f"✓ Version: {__version__}, Author: {__author__}")

def test_git_ops(tmp_path):
    repo = os.path.join(tmp, "test-repo")
    os.makedirs(repo)

    # init
    ok, msg = git_init(repo)
    assert ok, f"git_init failed: {msg}"
    print(f"✓ git_init: {msg}")

    # config
    ok, msg = git_cfg_set(repo, "user.name", "Test User")
    assert ok, f"git_cfg_set failed: {msg}"
    ok, msg = git_cfg_set(repo, "user.email", "test@test.com")
    assert ok, f"git_cfg_set failed: {msg}"

    # commit
    ok, msg = git_commit(repo, "Initial commit")
    assert ok, f"git_commit failed: {msg}"
    print(f"✓ git_commit: {msg}")

    # status
    ok, msg = git_status(repo)
    assert ok, f"git_status failed: {msg}"
    print(f"✓ git_status: clean = {msg == ''}")

    # remote add
    ok, msg = git_remote_add(repo, "origin", "https://example.com/repo.git")
    assert ok, f"git_remote_add failed: {msg}"
    print(f"✓ git_remote_add: {msg}")

    # push (will fail without real remote, but should error gracefully)
    ok, msg = git_push(repo, "origin", "main")
    assert not ok, "push to fake remote should fail"
    print(f"✓ git_push (expected failure): {msg[:50]}...")

    # pull (will fail without real remote)
    ok, msg = git_pull(repo, "origin", "main")
    assert not ok, "pull from fake remote should fail"
    print(f"✓ git_pull (expected failure): {msg[:50]}...")

def test_cli_structure():
    import argparse
    try:
        from hermes_sync.cli import main
        # Just verify the module structure is correct
        print("✓ CLI module structure OK")
    except Exception as e:
        print(f"✗ CLI structure: {e}")
        raise

def test_setup_git_repo(tmp_path):
    repo = os.path.join(tmp, "full-repo")
    os.makedirs(repo, exist_ok=True)
    ok, msg = setup_git_repo(repo, "Test User", "test@test.com", "Init")
    assert ok, f"setup_git_repo failed: {msg}"
    print(f"✓ setup_git_repo: {msg}")

    assert os.path.isdir(os.path.join(repo, ".git"))
    print("✓ .git directory created")

if __name__ == "__main__":
    import tempfile
    tmp = tempfile.mkdtemp(prefix="hermes-sync-test-")
    try:
        test_version()
        test_git_ops(tmp)
        test_cli_structure()
        test_setup_git_repo(tmp)
        print("\n✓ All tests passed")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)