import firebase_admin
from firebase_admin import credentials, db
import time
import json
import os

# === Load Firebase key from GitHub secret ===
firebase_key = os.environ['FIREBASE_KEY_JSON']
key_data = json.loads(firebase_key)

# === Initialize Firebase Admin SDK ===
cred = credentials.Certificate(key_data)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://livestride-default-rtdb.firebaseio.com'
})

def cleanup_old_runners():
    now = int(time.time() * 1000)  # Current time in milliseconds
    cutoff = now - 30 * 60 * 1000  # 30 minutes ago

    ref = db.reference('runners')
    runners = ref.get()

    if not runners:
        print("No runners found.")
        return

    deleted = 0
    for runner_id, data in runners.items():
        timestamp = data.get("timestamp")
        if timestamp and timestamp < cutoff:
            print(f"Deleting {runner_id} (timestamp: {timestamp})")
            ref.child(runner_id).delete()
            deleted += 1

    print(f"Deleted {deleted} runner(s).")

if __name__ == "__main__":
    cleanup_old_runners()
