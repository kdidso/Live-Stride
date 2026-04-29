import firebase_admin
from firebase_admin import credentials, db
import time
import json
import os
import requests
from datetime import datetime, timezone, timedelta


# =========================
# Firebase setup
# =========================
firebase_key = os.environ["FIREBASE_KEY_JSON"]
key_data = json.loads(firebase_key)

cred = credentials.Certificate(key_data)

firebase_admin.initialize_app(cred, {
    "databaseURL": "https://livestride-default-rtdb.firebaseio.com"
})


# =========================
# Supabase setup
# =========================
SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

SUPABASE_HEADERS = {
    "apikey": SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}


# =========================
# Firebase cleanup
# =========================
def cleanup_old_firebase_runners():
    now = int(time.time() * 1000)
    cutoff = now - 30 * 60 * 1000  # 30 minutes ago

    ref = db.reference("runners")
    runners = ref.get()

    if not runners:
        print("No Firebase runners found.")
        return

    deleted = 0

    for runner_id, data in runners.items():
        timestamp = data.get("timestamp")

        if timestamp and timestamp < cutoff:
            print(f"Deleting Firebase runner {runner_id} (timestamp: {timestamp})")
            ref.child(runner_id).delete()
            deleted += 1

    print(f"Deleted {deleted} Firebase runner(s).")


# =========================
# Supabase cleanup
# =========================
def cleanup_old_supabase_runs():
    cutoff_dt = datetime.now(timezone.utc) - timedelta(minutes=30)
    cutoff_iso = cutoff_dt.isoformat()

    # 1. Find old runs
    runs_url = f"{SUPABASE_URL}/rest/v1/runs"
    params = {
        "select": "id,runner_name,started_at,is_live",
        "started_at": f"lt.{cutoff_iso}"
    }

    response = requests.get(
        runs_url,
        headers=SUPABASE_HEADERS,
        params=params,
        timeout=30
    )
    response.raise_for_status()

    old_runs = response.json()

    if not old_runs:
        print("No old Supabase runs found.")
        return

    run_ids = [run["id"] for run in old_runs]

    print(f"Found {len(run_ids)} old Supabase run(s).")

    # 2. Delete run_points first
    for run_id in run_ids:
        points_url = f"{SUPABASE_URL}/rest/v1/run_points"
        delete_points_params = {
            "run_id": f"eq.{run_id}"
        }

        points_response = requests.delete(
            points_url,
            headers=SUPABASE_HEADERS,
            params=delete_points_params,
            timeout=30
        )
        points_response.raise_for_status()

        print(f"Deleted Supabase run_points for run {run_id}")

    # 3. Delete runs
    for run_id in run_ids:
        delete_run_params = {
            "id": f"eq.{run_id}"
        }

        run_response = requests.delete(
            runs_url,
            headers=SUPABASE_HEADERS,
            params=delete_run_params,
            timeout=30
        )
        run_response.raise_for_status()

        print(f"Deleted Supabase run {run_id}")

    print(f"Deleted {len(run_ids)} Supabase run(s).")


if __name__ == "__main__":
    cleanup_old_firebase_runners()
    cleanup_old_supabase_runs()
