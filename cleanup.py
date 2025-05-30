import firebase_admin
from firebase_admin import credentials, db
import time

# Initialize Firebase with service account
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://livestride-default-rtdb.firebaseio.com"
})

now = int(time.time() * 1000)
cutoff = now - (30 * 60 * 1000)

ref = db.reference("runners")
snapshot = ref.get()

removed = 0

if snapshot:
    for key, data in snapshot.items():
        # Get timestamp if path exists and contains at least one coordinate
        stop_time = None
        path = data.get("path")
        if isinstance(path, list) and path:
            last_point = path[-1]
            stop_time = last_point.get("timestamp")
        elif isinstance(path, dict):
            stop_time = path.get("timestamp")

        if stop_time and stop_time < cutoff:
            print(f"Deleting: {key} (timestamp: {stop_time})")
            ref.child(key).delete()
            removed += 1

print(f"Removed {removed} runner(s).")
