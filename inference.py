import requests
import os
import time

BASE = os.getenv("API_BASE_URL", "http://localhost:7860")
TASKS = ["easy", "medium", "hard"]

def run_task(task):
    print(f"[START] task={task}", flush=True)

    requests.post(f"{BASE}/reset")

    total_reward = 0.0
    steps = 0
    actions = ["clean_nulls", "deduplicate", "clean_nulls"]

    for action in actions:
        steps += 1
        r = requests.post(f"{BASE}/step", json={"action_type": action})
        res = r.json()

        reward = float(res.get("reward", 0.0))
        total_reward += reward

        print(f"[STEP] step={steps} reward={reward}", flush=True)

        if res.get("done", False):
            break

        time.sleep(0.1)

    score = max(0.0, min(1.0, total_reward / max(steps, 1)))
    print(f"[END] task={task} score={score:.2f} steps={steps}", flush=True)

if __name__ == "__main__":
    for task in TASKS:
        run_task(task)
