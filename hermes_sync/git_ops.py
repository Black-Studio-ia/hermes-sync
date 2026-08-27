"""
Git operations for hermes-sync: init, push, pull.
"""
import subprocess
from pathlib import Path
from typing import Optional, Tuple


def run_git(args: list, cwd: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def is_git_repo(path: str) -> bool:
    r = run_git(["rev-parse", "--git-dir"], path)
    return r.returncode == 0


def git_init(path: str) -> Tuple[bool, str]:
    r = run_git(["init"], path)
    if r.returncode != 0:
        return False, f"git init failed: {r.stderr.strip()}"
    return True, "Git repository initialized"


def git_add(path: str, files: Optional[list] = None) -> Tuple[bool, str]:
    args = ["add"] + (files if files else ["."])
    r = run_git(args, path)
    if r.returncode != 0:
        return False, f"git add failed: {r.stderr.strip()}"
    return True, "Files staged"


def git_commit(path: str, message: str) -> Tuple[bool, str]:
    r = run_git(["commit", "-m", message, "--allow-empty"], path)
    if r.returncode != 0:
        return False, f"git commit failed: {r.stderr.strip()}"
    return True, "Commit created"


def git_remote_add(path: str, name: str, url: str) -> Tuple[bool, str]:
    r = run_git(["remote", "add", name, url], path)
    if r.returncode != 0:
        if "already exists" in r.stderr:
            r2 = run_git(["remote", "set-url", name, url], path)
            if r2.returncode != 0:
                return False, f"git remote set-url failed: {r2.stderr.strip()}"
            return True, "Remote URL updated"
        return False, f"git remote add failed: {r.stderr.strip()}"
    return True, "Remote added"


def git_push(path: str, remote: str = "origin", branch: str = "main") -> Tuple[bool, str]:
    r = run_git(["push", "-u", remote, branch], path)
    if r.returncode != 0:
        return False, f"git push failed: {r.stderr.strip()}"
    return True, "Push successful"


def git_pull(path: str, remote: str = "origin", branch: str = "main") -> Tuple[bool, str]:
    r = run_git(["pull", remote, branch], path)
    if r.returncode != 0:
        return False, f"git pull failed: {r.stderr.strip()}"
    return True, "Pull successful"


def git_status(path: str) -> Tuple[bool, str]:
    r = run_git(["status", "--short"], path)
    if r.returncode != 0:
        return False, f"git status failed: {r.stderr.strip()}"
    return True, r.stdout.strip()


def git_cfg_set(path: str, key: str, value: str) -> Tuple[bool, str]:
    r = run_git(["config", key, value], path)
    if r.returncode != 0:
        return False, f"git config failed: {r.stderr.strip()}"
    return True, "Config set"


def setup_git_repo(
    repo_path: str,
    user_name: str,
    user_email: str,
    commit_message: str,
) -> Tuple[bool, str]:
    ok, msg = git_init(repo_path)
    if not ok:
        return False, msg
    ok, msg = git_cfg_set(repo_path, "user.name", user_name)
    if not ok:
        return False, msg
    ok, msg = git_cfg_set(repo_path, "user.email", user_email)
    if not ok:
        return False, msg
    ok, msg = git_commit(repo_path, commit_message)
    if not ok:
        return False, msg
    return True, "Git repository setup complete"