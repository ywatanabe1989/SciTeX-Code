# OpenAthens Security and Cookie Storage

## Cookie Storage Location

OpenAthens session cookies are stored in:
```
~/.scitex/scholar/openathens_sessions/
```

The exact filename depends on your institution:
- `openathens_unimelb_edu_au_session.enc` (for user@unimelb.edu.au)
- `openathens_harvard_edu_session.enc` (for user@harvard.edu)
- `openathens_default_session.enc` (if no email specified)

## Security Features

### 1. Encryption at Rest

All session cookies are encrypted using:
- **Algorithm**: Fernet (symmetric encryption)
- **Key Derivation**: PBKDF2-HMAC-SHA256
- **Iterations**: 100,000
- **Salt**: Machine-specific, stored in `~/.scitex/.scitex_salt`

### 2. File Permissions

- Session files: `0600` (read/write by owner only)
- Salt file: `0600` (read/write by owner only)

### 3. Automatic Migration

If you have existing unencrypted session files (`.json`), they will be:
1. Automatically encrypted on first use
2. Original unencrypted file deleted
3. No action required from you

### 4. Session Expiry

- Sessions expire after ~8 hours
- Expired sessions are automatically detected
- Re-authentication required when expired

## Security Best Practices

1. **Don't share session files** - They're encrypted with your email
2. **Keep your email secure** - It's used to derive the encryption key
3. **Machine-bound** - Sessions only work on the machine where created
4. **Regular cleanup** - Old session files can be safely deleted

## Manual Session Management

### View your sessions:
```bash
ls -la ~/.scitex/scholar/openathens_sessions/
```

### Clear all sessions:
```bash
rm -rf ~/.scitex/scholar/openathens_sessions/*.enc
```

### Check session validity:
```python
from scitex.scholar import Scholar

scholar = Scholar()
if await scholar.is_openathens_authenticate_async():
    print("Session is valid")
else:
    print("Session expired or not found")
```

## What's Encrypted

The following data is encrypted in session files:
- Authentication cookies
- Session tokens
- Expiry timestamps
- Associated email address

## What's NOT Encrypted

- The salt file (it's meant to be random)
- The email hash in metadata (for identification only)
- Log files (they don't contain sensitive data)

## Troubleshooting

### "Failed to decrypt session cache"
- You may be using a different email than when created
- The salt file may have been deleted or changed
- Solution: Delete the session file and re-authenticate_async

### "Permission denied" errors
- Check file permissions: `ls -la ~/.scitex/`
- Fix permissions: `chmod 600 ~/.scitex/scholar/openathens_sessions/*`

### Can't find session files
- Check the logged location when authenticating
- Default: `~/.scitex/scholar/openathens_sessions/`
- Set custom location: `OpenAthensAuthenticator(cache_dir="/my/path")`