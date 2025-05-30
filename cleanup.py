import firebase_admin
from firebase_admin import credentials, db
import time

# Initialize Firebase app using the service account key
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://livestride-default-rtdb.firebaseio.com"
})

# Define the cutoff time (30 minutes ago)
now = int(time.time() * 1000)
cutoff = now - (30 * 60 * 1000)

# Reference the runners in the database
ref = db.reference("runners")
snapshot = ref.get()

if snapshot:
    removed = 0
    for key, data in snapshot.items():
        timestamp = None
        path = data.get("path")

        if isinstance(path, dict):
            timestamp = path.get("timestamp")
        elif isinstance(path, list) and len(path) > 0 and isinstance(path[-1], dict):
            timestamp = path[-1].get("timestamp")

        if timestamp and timestamp < cutoff:
            ref.child(key).delete()
            removed += 1

    print(f"Removed {removed} old runner(s).")
else:
    print("No runners found.")
