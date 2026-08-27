"""Config sync engine for hermes-sync."""
import os
import shutil
import tempfile
import sys
from pathlib import Path
from typing import List, Tuple, Optional

from .git_ops import (
    git_init, git_add, git_commit, git_remote_add,
    git_push, git_pull, git_status, git_cfg_set, setup_git_repo
)
from .secrets import (
    encrypt_secrets_in_dir, decrypt_secrets_in_dir, get_passphrase
)

HIDDEN_FILES = {'.env', 'auth.json'}
CONSTANT_FILES = {'.gitignore', '.hermes.lock'}

def get_hermes_dir() -> Path:
    d = Path.home() / '.hermes'
    if not d.exists():
        print(f"Error: {d} does not exist.", file=sys.stderr)
        sys.exit(1)
    return d

def list_hermes_files(hermes_dir: Path) -> List[Path]:
    files = []
    for root, dirs, filenames in os.walk(str(hermes_dir)):
        for f in filenames:
            fp = Path(root) / f
            rel = fp.relative_to(hermes_dir)
            name = str(rel)
            if name in HIDDEN_FILES:
                continue
            if name in CONSTANT_FILES:
                continue
            if f.startswith('.') and f not in CONSTANT_FILES:
                continue
            files.append(fp)
    return files

def sync_push(
    repo_path: str,
    hermes_dir: Path,
    remote_url: Optional[str],
    user_name: str,
    user_email: str,
    passphrase: Optional[str],
    branch: str = "main",
) -> Tuple[bool, str]:
    """Push ~/.hermes/ to a git repo."""
    tmp = tempfile.mkdtemp(prefix="hermes_sync_")
    try:
        dest = Path(tmp) / "hermes_content"
        dest.mkdir(parents=True)

        files = list_hermes_files(hermes_dir)
        for fp in files:
            rel = fp.relative_to(hermes_dir)
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(fp), str(target))

        encrypted_files = []
        if passphrase:
            ok, msg, enc_files = encrypt_secrets_in_dir(
                str(hermes_dir), passphrase, str(dest)
            )
            if not ok:
                return False, f"Secret encryption failed: {msg}"
            encrypted_files = enc_files

        ok, msg = setup_git_repo(
            repo_path, user_name, user_email,
            f"Hermes sync: {hermes_dir.name} backup"
        )
        if not ok:
            return False, f"Git setup failed: {msg}"

        gitignore = dest / ".gitignore"
        gitignore.write_text(
            "# Hermes sync auto-generated\n"
            "*.enc\n"
            ".env\n"
            "auth.json\n"
            "__pycache__/\n"
            "*.pyc\n"
            ".DS_Store\n"
        )

        ok, msg = git_add(repo_path)
        if not ok:
            return False, f"Git add failed: {msg}"

        ok, msg = git_commit(repo_path, f"Sync: {hermes_dir.name} at backup")
        if not ok:
            return False, f"Git commit failed: {msg}"

        if remote_url:
            ok, msg = git_remote_add(repo_path, "origin", remote_url)
            if not ok:
                return False, f"Remote setup failed: {msg}"
            ok, msg = git_push(repo_path, "origin", branch)
            if not ok:
                return False, f"Push failed: {msg}"

        return True, f"Synced {len(files)} files (plus {len(encrypted_files)} encrypted secrets) to {repo_path}"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def sync_pull(
    repo_path: str,
    hermes_dir: Path,
    remote_url: str,
    passphrase: Optional[str],
    branch: str = "main",
) -> Tuple[bool, str]:
    """Pull from a git repo into ~/.hermes/."""
    if Path(repo_path).exists() and (Path(repo_path) / ".git").exists():
        ok, msg = git_pull(repo_path, "origin", branch)
        if not ok:
            return False, f"Pull failed: {msg}"
    else:
        import subprocess
        result = subprocess.run(
            ["git", "clone", "--branch", branch, remote_url, repo_path],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return False, f"Clone failed: {result.stderr.strip()}"

    src = Path(repo_path)
    for item in src.iterdir():
        if item.name == '.git':
            continue
        if item.name.endswith('.enc'):
            if passphrase:
                if item.name == '.env.enc':
                    ok, msg = decrypt_secrets_in_dir(
                        str(src), str(hermes_dir), passphrase
                    )
                    if not ok:
                        return False, f"Decrypt failed: {msg}"
                continue
            continue
        if item.is_dir():
            target = hermes_dir / item.name
            if target.exists():
                shutil.rmtree(str(target))
            shutil.copytree(str(item), str(target))
        else:
            target = hermes_dir / item.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(item), str(target))

    return True, f"Pulled and restored ~/.hermes/ from {remote_url}"

def status(repo_path: str) -> Tuple[bool, str]:
    if not Path(repo_path).exists():
        return False, f"Repo not found: {repo_path}"
    ok, msg = git_status(repo_path)
    return ok, msg if ok else f"Status failed: {msg}"