# Examples

Real-world usage scenarios for hermes-sync.

## Scenario 1: Two devices, one sync

**Setup (Device A — Home PC):**

```bash
# Install
pip install hermes-sync

# Initialize sync with your private Git repo
hermes-sync init \
  --remote https://github.com/yourname/hermes-private.git \
  --user "Your Name" \
  --email "you@example.com"
```

This creates a Git repository with your `~/.hermes/` contents (excluding `.env` and `auth.json`).

**Setup (Device B — Work Laptop):**

```bash
# Clone the repo first
git clone https://github.com/yourname/hermes-private.git ~/hermes-sync-repo

# Pull into ~/.hermes/
hermes-sync pull --repo ~/hermes-sync-repo --remote https://github.com/yourname/hermes-private.git
```

Done. Your skills, profiles, config, and memory are now on the laptop.

## Scenario 2: Encrypted secrets

If you need to sync `.env` or `auth.json`:

```bash
# Set passphrase (same on all devices)
export HERMES_SYNC_PASSPHRASE="your-strong-passphrase-here"

# On Device A
hermes-sync push --remote https://github.com/yourname/hermes-private.git

# On Device B (with same passphrase)
hermes-sync pull --repo ~/hermes-sync-repo --remote https://github.com/yourname/hermes-private.git
```

The `.env` and `auth.json` are encrypted with Fernet + PBKDF2 before sync, and decrypted on pull.

## Scenario 3: Regular sync workflow

```bash
# After making changes on Device A
hermes-sync push --remote https://github.com/yourname/hermes-private.git

# On Device B, before starting work
hermes-sync pull --repo ~/hermes-sync-repo --remote https://github.com/yourname/hermes-private.git
```

## Scenario 4: Check what's changed

```bash
# See what's different in the sync repo
hermes-sync status --repo ~/hermes-sync-repo
```

## Tips

1. **Use a dedicated private repo** — don't reuse an existing repo
2. **Use SSH keys** for Git auth instead of passwords
3. **Backup your passphrase** — if lost, encrypted files cannot be recovered
4. **Test with a dummy repo first** — try the workflow before trusting it with real secrets
5. **Pull before making changes on a new device** — avoid conflicts

---

*For more details, see the main [README](../README.md).*