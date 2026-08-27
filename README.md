# hermes-sync

**Git-based sync for Hermes Agent `~/.hermes/` across devices.**

>Sync your Hermes Agent configuration (config, profiles, skills, sessions, memory) between multiple devices using a private Git repository — fully under your control.

| | |
|---|---|
| **Status** | Stable (v0.1.0) |
| **License** | MIT |
| **Python** | 3.8+ |
| **Downloads** | `pip install hermes-sync` |
| **Repository** | [github.com/Black-Studio-ia/hermes-sync](https://github.com/Black-Studio-ia/hermes-sync) |

This is an **unofficial companion tool** and is **NOT affiliated with, endorsed by, or connected to Nous Research** or any official Hermes Agent project. It is a community-built solution addressing the feature request documented in [NousResearch/hermes-agent#20510](https://github.com/NousResearch/hermes-agent/issues/20510).

## The Problem

Hermes Agent stores all configurations, profiles, skills, sessions, and memory locally under `~/.hermes/`. When you use Hermes on multiple devices (e.g., desktop at home + laptop at work), there is no built-in way to synchronize these across devices. Users must manually export/import profiles, copy skills folders, and replicate their setup on each machine.

This is the problem documented in the [original feature request](https://github.com/NousResearch/hermes-agent/issues/20510):

> *"Currently, Hermes stores all configurations, profiles, skills, sessions, and memory locally under `~/.hermes/`. There is no built-in way to sync these across multiple devices."*

## What hermes-sync Does

`hermes-sync` is a simple CLI tool that uses a **private Git repository** (which you fully control) to synchronize your `~/.hermes/` directory between devices.

**It does NOT:**
- Touch any files outside `~/.hermes/`
- Send any data to any server you haven't explicitly chosen
- Expose your API keys or secrets in plain text (encrypts `.env` and `auth.json` before syncing)
- Modify Hermes Agent itself

**It DOES:**
- Copy your `~/.hermes/` configuration to a Git repository you specify
- Pull that configuration onto another device with one command
- Encrypt secret files (`.env`, `auth.json`) with a passphrase you provide

## Installation

```bash
# Clone the repository
git clone https://github.com/BlackStudioIA/hermes-sync.git
cd hermes-sync

# Install in development mode
pip install -e .

# Or install directly from PyPI (when available)
# pip install hermes-sync
```

**Requirements:** Python 3.8+, `git` in your PATH, and a private Git repository (GitHub, GitLab, Bitbucket, or self-hosted).

## Usage

### Initialize sync on your primary device

```bash
# Initialize a sync repo from your existing ~/.hermes/
hermes-sync init --remote https://github.com/yourusername/hermes-sync-private.git --user "Your Name" --email "you@example.com"
```

This will:
1. Copy your `~/.hermes/` contents (excluding `.env` and `auth.json`) to a local Git repository
2. Set up Git with your identity
3. Push to the remote you specify

### Push changes after modifying your setup

```bash
# After adding skills, changing config, etc.
hermes-sync push --remote https://github.com/yourusername/hermes-sync-private.git
```

### Pull on a second device

```bash
# On a new device where Hermes is installed but ~/.hermes/ is empty/minimal
hermes-sync pull --repo /path/to/local/clone --remote https://github.com/yourusername/hermes-sync-private.git
```

Or if you already have a local clone:

```bash
hermes-sync pull --repo /path/to/local/clone
```

### Check sync status

```bash
hermes-sync status --repo /path/to/sync/repo
```

## Encrypting Secrets

By default, `hermes-sync` **excludes** `.env` and `auth.json` from sync for safety. If you want to sync these encrypted:

```bash
# Set the HERMES_SYNC_PASSPHRASE environment variable before push/pull
export HERMES_SYNC_PASSPHRASE="your-strong-passphrase"

# Push (secret files will be encrypted before sync)
hermes-sync push --remote https://github.com/yourusername/hermes-sync-private.git

# On the second device, set the same passphrase
export HERMES_SYNC_PASSPHRASE="your-strong-passphrase"

# Pull (secret files will be decrypted after sync)
hermes-sync pull --repo /path/to/local/clone --remote https://github.com/yourusername/hermes-sync-private.git
```

**Important:** Never commit unencrypted `.env` or `auth.json` to any Git repository. The tool automatically skips these files unless they are encrypted.

## Supported Sync Scope

| Content | Synced? | Notes |
|---------|---------|-------|
| `config.yaml` | Yes | Main configuration |
| Profiles (`profiles/`) | Yes | All profile directories |
| Skills (`skills/`) | Yes | User-created and hub-installed skills |
| Memory (`memories/`, `memory.db`) | Yes | Cross-session memory |
| Sessions (`sessions/`) | Yes | Session history |
| Credential pool (`auth.json`) | **Encrypted only** | Requires passphrase |
| Environment (`.env`) | **Encrypted only** | Requires passphrase |
| Cache, logs, temp files | No | Excluded automatically |
| Git metadata (`.git/`) | No | Not part of sync content |

## Security Considerations

1. **Use a private repository.** Your sync repo should be private — never public. It may contain configuration details that reveal your setup.
2. **Use a strong passphrase** for encrypting secrets. The same passphrase must be available on all devices that need to decrypt secrets.
3. **The passphrase is never stored.** You must set `HERMES_SYNC_PASSPHRASE` environment variable on each device. If you lose the passphrase, encrypted files cannot be recovered.
4. **Git history is permanent.** If you accidentally sync unencrypted secrets, rotate those credentials immediately. Consider using `git filter-repo` or `BFG Repo-Cleaner` to remove secrets from history.
5. **This tool runs entirely locally.** No data leaves your machine except what you explicitly push to your chosen Git remote.

## Unofficial Notice

**This is NOT an official Nous Research product.** It is a community-built tool created by Black Studio IA. It is not endorsed, supported, or maintained by the Hermes Agent team at Nous Research.

Use at your own risk. The Hermes Agent project may introduce native sync features in the future that could conflict with or supersede this tool. Always check the [official issue #20510](https://github.com/NousResearch/hermes-agent/issues/20510) for the latest status of official sync development.

## Troubleshooting

**"repo is not a git repository"**
- Run `hermes-sync init` first on the primary device, or clone an existing sync repo.

**"Permission denied (publickey)" when pushing**
- Ensure your SSH key is added to GitHub/GitLab and loaded in ssh-agent, or use HTTPS with a token.

**"decryption failed"**
- The passphrase doesn't match. Ensure `HERMES_SYNC_PASSPHRASE` is set to the same value used during encrypt. Passphrases are case-sensitive.

**Files not appearing after pull**
- Check that the `hermes-sync` run completed successfully. The tool copies files into `~/.hermes/` — if that directory already existed with content, it may have been merged. Review the output for any errors.

## Alternatives

- [NousResearch/hermes-agent/issues/20510](https://github.com/NousResearch/hermes-agent/issues/20510) — the original feature request (awaiting official implementation)
- [alovwang-sys/hermes-sync](https://github.com/alovwang-sys/hermes-sync) — a different approach: a Hermes plugin (not a standalone CLI) that syncs explicit scopes via multiple backends (OSS, S3, WebDAV)

## Support this project

This tool is provided free and open-source under the MIT license. If you find it useful and want to support its development:

USDT (TRC20): TXQCrX61CceFxX5gnFg9N3ssZEC7MavwBQ

**Contact:** ia.creative.tn@gmail.com

This is an **optional tip** — no guarantees of any return or profit are made or implied. Donations are appreciated but never required. All features remain free regardless of donation status.

---

*Bug reports and feature requests: [github.com/BlackStudioIA/hermes-sync/issues](https://github.com/BlackStudioIA/hermes-sync/issues)*
