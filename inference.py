import requests
import time
import os

BASE = os.getenv("API_BASE_URL", "http://localhost:7860")

TASKS = ["easy", "medium", "hard"]

def run_task(task):
    print(f"[START] task={task}", flush=True)

    # reset
    r = requests.post(f"{BASE}/reset")
    data = r.json()

    total_reward = 0
    steps = 0

    actions = ["clean_nulls", "deduplicate", "clean_nulls"]

    for i, action in enumerate(actions):
        steps += 1

        r = requests.post(
            f"{BASE}/step",
            json={"action_type": action}
        )

        res = r.json()
        reward = res.get("reward", 0)
        total_reward += reward

        print(f"[STEP] step={steps} reward={reward}", flush=True)

        if res.get("done"):
            break

        time.sleep(0.2)

    score = min(max(total_reward / steps, 0), 1.0)

    print(f"[END] task={task} score={score:.2f} steps={steps}", flush=True)


if __name__ == "__main__":
    for t in TASKS:
        run_task(t)
