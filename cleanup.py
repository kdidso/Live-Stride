import firebase_admin
from firebase_admin import credentials, db
import time

# Initialize Firebase
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
        stop_time = None

        # Safely access the timestamp
        path_data = data.get("path")
        if isinstance(path_data, dict):
            stop_time = path_data.get("timestamp")

        if stop_time and stop_time < cutoff:
            print(f"Deleting runner {key} (timestamp: {stop_time})")
            ref.child(key).delete()
            removed += 1

print(f"Finished. Removed {removed} old runner(s).")
