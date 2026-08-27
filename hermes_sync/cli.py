"""hermes-sync CLI."""
import argparse
import os
import sys
from pathlib import Path

from . import __version__
from .config_sync import get_hermes_dir, sync_push, sync_pull, status

HIDDEN = {'.env', 'auth.json'}
IGNORE = {'.git', '__pycache__', '.DS_Store', 'node_modules'}

def list_files(hermes_dir):
    result = []
    for root, dirs, files in os.walk(str(hermes_dir)):
        dirs[:] = [d for d in dirs if d not in IGNORE]
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, str(hermes_dir))
            if rel in HIDDEN:
                continue
            if rel.startswith('.'):
                continue
            result.append(rel)
    return result

def cmd_init(args):
    hermes = get_hermes_dir()
    repo = args.repo or input("Git repo path (absolute): ").strip()
    remote = args.remote
    user = args.user or input("Git user.name: ").strip()
    email = args.email or input("Git user.email: ").strip()
    branch = args.branch or "main"

    print(f"Initializing sync at: {repo}")
    print(f"Source: {hermes}")

    # Check if repo already exists
    if os.path.exists(repo):
        if os.path.isdir(os.path.join(repo, '.git')):
            print(f"ERROR: {repo} is already a git repository.")
            sys.exit(1)
        os.makedirs(repo, exist_ok=True)

    # Copy files
    import shutil
    shutil.copytree(str(hermes), repo, dirs_exist_ok=True)

    # Remove hidden files from copy
    for hidden in HIDDEN:
        p = os.path.join(repo, hidden)
        if os.path.exists(p):
            os.remove(p)

    # Setup git
    from .git_ops import setup_git_repo, git_remote_add, git_push, git_add, git_commit
    ok, msg = setup_git_repo(repo, user, email, f"hermes-sync init: {hermes}")
    if not ok:
        print(f"ERROR: {msg}")
        sys.exit(1)
    print(f"OK: {msg}")

    if remote:
        ok, msg = git_remote_add(repo, 'origin', remote)
        if not ok:
            print(f"WARNING: {msg}")
        else:
            print(f"OK: {msg}")
            ok, msg = git_push(repo, 'origin', branch)
            if not ok:
                print(f"ERROR: {msg}")
                sys.exit(1)
            print(f"OK: {msg}")

    print(f"\nSync initialized. Push with: hermes-sync push")
    print(f"Pull on another device with: hermes-sync pull --repo {repo} --remote {remote or '<your-remote-url>'}")

def cmd_push(args):
    hermes = get_hermes_dir()
    repo = args.repo or os.path.join(str(Path.home()), '.hermes-sync-repo')
    remote = args.remote

    print(f"Syncing {hermes} -> {repo}")

    # Create temp staging
    import tempfile
    import shutil
    staging = tempfile.mkdtemp(prefix='hermes-push-')
    try:
        stage_path = os.path.join(staging, 'hermes')
        shutil.copytree(str(hermes), stage_path, dirs_exist_ok=True)

        # Remove hidden
        for hidden in HIDDEN:
            p = os.path.join(stage_path, hidden)
            if os.path.exists(p):
                os.remove(p)

        # Git add & commit
        from .git_ops import git_add, git_commit, git_remote_add, git_push
        if not os.path.exists(os.path.join(repo, '.git')):
            print(f"ERROR: {repo} is not a git repo. Run 'init' first.")
            sys.exit(1)

        ok, msg = git_add(repo)
        if not ok:
            print(f"ERROR: {msg}")
            sys.exit(1)

        msg = f"hermes-sync push: {os.path.basename(str(hermes))} @ {os.path.basename(os.getcwd())}"
        ok, msg = git_commit(repo, msg)
        if not ok:
            print(f"ERROR: {msg}")
            sys.exit(1)
        print(f"OK: {msg}")

        if remote:
            ok, msg = git_remote_add(repo, 'origin', remote)
            if not ok:
                print(f"WARNING: {msg}")
            else:
                ok, msg = git_push(repo, 'origin', args.branch)
                if not ok:
                    print(f"ERROR: {msg}")
                    sys.exit(1)
                print(f"OK: {msg}")
        else:
            print("No remote configured. Files staged locally only.")

        # Count
        files = list_files(hermes)
        print(f"\nSynced {len(files)} files from {hermes}")
        if os.path.exists(os.path.join(repo, '.git')):
            print(f"Repo: {repo}")
            if remote:
                print(f"Remote: {remote}")
    finally:
        shutil.rmtree(staging, ignore_errors=True)

def cmd_pull(args):
    hermes = get_hermes_dir()
    repo = args.repo
    remote = args.remote

    if not os.path.exists(repo):
        print(f"ERROR: Repo path {repo} does not exist.")
        sys.exit(1)

    if not os.path.isdir(os.path.join(repo, '.git')):
        print(f"ERROR: {repo} is not a git repository.")
        sys.exit(1)

    if remote:
        from .git_ops import git_pull
        ok, msg = git_pull(repo, 'origin', args.branch)
        if not ok:
            print(f"ERROR: {msg}")
            sys.exit(1)
        print(f"OK: {msg}")

    # Copy back to ~/.hermes/
    import shutil
    backup = str(hermes) + '.bak'
    if os.path.exists(backup):
        shutil.rmtree(backup)
    shutil.move(str(hermes), backup)
    os.makedirs(str(hermes), exist_ok=True)

    for item in os.listdir(repo):
        if item == '.git':
            continue
        src = os.path.join(repo, item)
        dst = os.path.join(str(hermes), item)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)

    if os.path.exists(backup):
        shutil.rmtree(backup)

    print(f"OK: Restored {hermes} from {repo}")

def cmd_status(args):
    repo = args.repo
    from .git_ops import git_status
    ok, msg = git_status(repo)
    if ok:
        print(msg if msg else "(clean)")
    else:
        print(f"ERROR: {msg}")

def main():
    p = argparse.ArgumentParser(
        prog='hermes-sync',
        description='Git-based sync for Hermes Agent ~/.hermes/ across devices. Unofficial companion tool.',
    )
    p.add_argument('--version', action='version', version=f'hermes-sync {__version__}')

    sub = p.add_subparsers(dest='command')

    # init
    i = sub.add_parser('init', help='Initialize sync repo from ~/.hermes/')
    i.add_argument('--repo', help='Path for the git repo (default: ~/.hermes-sync-repo)')
    i.add_argument('--remote', help='Git remote URL (optional)')
    i.add_argument('--user', help='Git user.name')
    i.add_argument('--email', help='Git user.email')
    i.add_argument('--branch', default='main', help='Branch name')

    # push
    pu = sub.add_parser('push', help='Push ~/.hermes/ changes to sync repo')
    pu.add_argument('--repo', help='Path to sync repo')
    pu.add_argument('--remote', help='Git remote URL')
    pu.add_argument('--branch', default='main')

    # pull
    pl = sub.add_parser('pull', help='Pull sync repo into ~/.hermes/')
    pl.add_argument('--repo', required=True, help='Path to sync repo')
    pl.add_argument('--remote', help='Git remote URL')
    pl.add_argument('--branch', default='main')

    # status
    s = sub.add_parser('status', help='Show git status of sync repo')
    s.add_argument('--repo', help='Path to sync repo')

    args = p.parse_args()
    if not args.command:
        p.print_help()
        sys.exit(1)

    dispatch = {
        'init': cmd_init,
        'push': cmd_push,
        'pull': cmd_pull,
        'status': cmd_status,
    }
    dispatch[args.command](args)

if __name__ == '__main__':
    main()
