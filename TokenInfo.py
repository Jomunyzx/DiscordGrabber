## ziska info o discord tokenu - UserID, Datum Vytvoreni, Podpis


import base64
import datetime

def decode_discord_token(token):
    parts = token.split('.')
    
    if len(parts) != 3:
        print(f"\n[X] Invalid discord token")
        return
    
    try:
        user_id = base64.b64decode(parts[0] + "==").decode()
    except Exception as e:
        print(f"\n[X] Error in decoding user ID: {e}")
        return

    try:
        creation_time = datetime.datetime.fromtimestamp(int.from_bytes(base64.urlsafe_b64decode(token.split('.')[1] + '=='), 'big') + 1293840000, datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"\n[X] Error in decoding time: {e}")
        return

    signature = parts[2]
    print("\n🎯 Decoded Discrod token:")
    print(f"👤 User ID:   {user_id}")
    print(f"⏳ Creation time:  {creation_time}")
    print(f"🔑 Signature:    {signature}")

while True:
    token = input(f"\n[+] Enter Discord token > ")
    if token == "exit":
        print(f"\nBye!\n")
        exit(1)
    else:
        decode_discord_token(token)