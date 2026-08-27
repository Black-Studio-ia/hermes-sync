"""
Secrets handling: encrypt/decrypt .env and auth.json before syncing.
Uses Fernet symmetric encryption with a key derived from a user-provided passphrase.
"""
import os
import base64
import hashlib
import getpass
from pathlib import Path
from typing import Tuple, List, Optional


def _derive_key(passphrase: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256",
        passphrase.encode("utf-8"),
        salt,
        100_000,
        dklen=32,
    )


def encrypt_file(src_path: str, dest_path: str, passphrase: str) -> Tuple[bool, str]:
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        return False, "cryptography package required. Install: pip install cryptography"

    try:
        salt = os.urandom(16)
        key = _derive_key(passphrase, salt)
        with open(src_path, "rb") as f:
            data = f.read()
        fernet_key = base64.urlsafe_b64encode(key)
        fernet = Fernet(fernet_key)
        encrypted = fernet.encrypt(data)
        with open(dest_path, "wb") as f:
            f.write(salt + encrypted)
        return True, f"Encrypted {src_path} -> {dest_path}"
    except Exception as e:
        return False, f"Encryption failed: {e}"


def decrypt_file(src_path: str, dest_path: str, passphrase: str) -> Tuple[bool, str]:
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        return False, "cryptography package required. Install: pip install cryptography"

    try:
        with open(src_path, "rb") as f:
            raw = f.read()
        if len(raw) < 16:
            return False, "Invalid encrypted file: too short"
        salt = raw[:16]
        encrypted = raw[16:]
        key = _derive_key(passphrase, salt)
        fernet_key = base64.urlsafe_b64encode(key)
        fernet = Fernet(fernet_key)
        decrypted = fernet.decrypt(encrypted)
        with open(dest_path, "wb") as f:
            f.write(decrypted)
        return True, f"Decrypted {src_path} -> {dest_path}"
    except Exception as e:
        return False, f"Decryption failed: {e}"


def encrypt_secrets_in_dir(
    hermes_dir: str,
    passphrase: str,
    temp_dir: str,
) -> Tuple[bool, str, List[str]]:
    encrypted_files: List[str] = []
    hermes_path = Path(hermes_dir)

    env_path = hermes_path / ".env"
    if env_path.exists():
        dest = Path(temp_dir) / ".env.enc"
        ok, msg = encrypt_file(str(env_path), str(dest), passphrase)
        if ok:
            encrypted_files.append(str(dest))
        else:
            return False, f"Failed to encrypt .env: {msg}", encrypted_files

    auth_path = hermes_path / "auth.json"
    if auth_path.exists():
        dest = Path(temp_dir) / "auth.json.enc"
        ok, msg = encrypt_file(str(auth_path), str(dest), passphrase)
        if ok:
            encrypted_files.append(str(dest))
        else:
            return False, f"Failed to encrypt auth.json: {msg}", encrypted_files

    if not encrypted_files:
        return True, "No secret files found to encrypt", encrypted_files

    return True, f"Encrypted {len(encrypted_files)} file(s)", encrypted_files


def decrypt_secrets_in_dir(
    temp_dir: str,
    hermes_dir: str,
    passphrase: str,
) -> Tuple[bool, str]:
    temp_path = Path(temp_dir)
    hermes_path = Path(hermes_dir)

    env_enc = temp_path / ".env.enc"
    env_dest = hermes_path / ".env"
    if env_enc.exists():
        ok, msg = decrypt_file(str(env_enc), str(env_dest), passphrase)
        if not ok:
            return False, f"Failed to decrypt .env: {msg}"

    auth_enc = temp_path / "auth.json.enc"
    auth_dest = hermes_path / "auth.json"
    if auth_enc.exists():
        ok, msg = decrypt_file(str(auth_enc), str(auth_dest), passphrase)
        if not ok:
            return False, f"Failed to decrypt auth.json: {msg}"

    return True, "Secrets decrypted successfully"


def get_passphrase(confirm: bool = True) -> str:
    passphrase = getpass.getpass("Encryption passphrase: ")
    if confirm:
        confirm_pass = getpass.getpass("Confirm passphrase: ")
        if passphrase != confirm_pass:
            raise ValueError("Passphrases do not match")
    if not passphrase:
        raise ValueError("Passphrase cannot be empty")
    return passphrase