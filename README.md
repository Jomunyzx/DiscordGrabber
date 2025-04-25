# 🔐 Discord Token Tools Collection

This repository contains three Python-based tools for interacting with Discord tokens. These tools are intended for **educational and ethical purposes only**. Misuse of this code may violate Discord's Terms of Service and could be illegal depending on your jurisdiction.

---

## 📁 Project Contents

### 1. `Discord-Token-Grabber-NoHook.py`
> A local-only script that scans popular local storage locations (Discord, browsers) for Discord tokens. It does **not** use any webhook to send data.

**Features:**
- Locates encrypted or plain Discord tokens across common paths.
- Decrypts tokens using the system's master key (if available).
- Verifies tokens via Discord API and prints their creation date and user ID.
- No external communications or webhooks.

---

### 2. `Discord-Token-Grabber-Webhook.py`
> An extended version of the grabber which **automatically uploads** found token details to a specified Discord webhook.

**Features:**
- Everything from the NoHook version.
- Sends token data, user info, Nitro status, 2FA, billing info, and creation time via an embedded Discord message.
- Uses rich formatting and avatars in webhook embeds.
- Designed for automation (run-and-report behavior).

> **🚨 Warning:** This script contains a hardcoded webhook URL. **Do not run this file without understanding its behavior.**

---

### 3. `TokenInfo.py`
> A simple decoder for Discord tokens.

**Features:**
- Takes a Discord token from user input.
- Decodes and prints:
  - **User ID**
  - **Token creation time**
  - **Token signature**

**Usage:**
Run the script and paste any Discord token to receive detailed breakdown info. Type `exit` to quit.

---

## ⚙️ Requirements

Make sure you have Python 3.x installed along with the following libraries:

```bash
pip install pycryptodomex pywin32 requests
```