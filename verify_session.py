"""
Verify session validity and fetch basic profile info
"""
import os
import json
import sys
import ssl
import certifi
from pathlib import Path
from instagrapi import Client

# Force UTF-8 stdout
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def setup_ssl_bundle():
    ca_path = Path("cacert_win.pem").resolve()
    if not ca_path.exists():
        certs = ssl.enum_certificates('ROOT') + ssl.enum_certificates('CA')
        with open(ca_path, 'w', encoding='utf-8') as f:
            with open(certifi.where(), 'r', encoding='utf-8') as cf:
                f.write(cf.read())
            f.write('\n')
            for cert, encoding, trust in certs:
                if encoding == 'x509_asn':
                    f.write(ssl.DER_cert_to_PEM_cert(cert) + '\n')
    
    os.environ['CURL_CA_BUNDLE'] = str(ca_path)
    os.environ['SSL_CERT_FILE'] = str(ca_path)
    os.environ['REQUESTS_CA_BUNDLE'] = str(ca_path)
    return str(ca_path)

def verify():
    ca_path = setup_ssl_bundle()

    with open("session.json", "r", encoding="utf-8") as f:
        session_data = json.load(f)

    sessionid = session_data.get("sessionid")
    if not sessionid:
        print("[ERROR] No sessionid found in session.json")
        return False

    print("Connecting with saved session...")
    cl = Client()
    
    # Configure adapter SSL verify
    for adapter in cl.private.adapters.values():
        if hasattr(adapter, 'client') and hasattr(adapter.client, 'verify'):
            adapter.client.verify = ca_path
    for adapter in cl.public.adapters.values():
        if hasattr(adapter, 'client') and hasattr(adapter.client, 'verify'):
            adapter.client.verify = ca_path

    cl.login_by_sessionid(sessionid)
    
    try:
        user_info = cl.user_info(cl.user_id)
        print("\n==========================================")
        print("[SUCCESS] Connected to Instagram Successfully!")
        print("==========================================")
        print(f"Username: @{user_info.username}")
        print(f"Full Name: {user_info.full_name}")
        print(f"Followers: {user_info.follower_count}")
        print(f"Following: {user_info.following_count}")
        print(f"Media Count: {user_info.media_count}")
        print(f"Is Private: {user_info.is_private}")
        print("==========================================\n")
        
        # Save dump settings
        cl.dump_settings("instagrapi_session.json")
        print("Saved instagrapi_session.json for rapid future requests.")
        return True
    except Exception as e:
        print(f"[ERROR] Session verification error: {e}")
        return False

if __name__ == "__main__":
    success = verify()
    sys.exit(0 if success else 1)
