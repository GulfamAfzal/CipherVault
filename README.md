# CipherVault 🔐
### Zero-Knowledge Encrypted Cloud Storage

CipherVault encrypts your files locally using AES-256-GCM **before** uploading to Google Drive.
Google never sees your plaintext. Ever.

## How It Works
1. Select any file
2. Enter your password
3. File is encrypted on YOUR machine
4. Only the encrypted blob goes to Google Drive
5. Download and decrypt anytime

## Tech Stack
- Python 3.10+
- AES-256-GCM encryption
- PBKDF2-HMAC-SHA256 key derivation (200,000 iterations)
- Google Drive API v3 + OAuth 2.0
- Tkinter GUI

## Setup
```bash
pip install cryptography google-api-python-client google-auth-httplib2 google-auth-oauthlib
```
Add your own `credentials.json` from Google Cloud Console, then:
```bash
python gui.py
```

## Security
Even if your Google account is breached — your files are unreadable without your password.

---
*Built by Gulfam Afzal — 2026*
```

---

## Step 3 — Install Git

👉 Open PowerShell and type:
```
git --version
