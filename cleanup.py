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
        stop_time = data.get("stopTime")
        if stop_time and stop_time < cutoff:
            ref.child(key).delete()
            removed += 1
    print(f"Removed {removed} old runner(s).")
else:
    print("No runners found.")
