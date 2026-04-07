import os
import sys
import time
import requests
from openai import OpenAI

TASKS = ["easy", "medium", "hard"]

def log(msg: str) -> None:
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()

API_BASE_URL = os.environ["API_BASE_URL"].rstrip("/")
API_KEY = os.environ["API_KEY"]
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4.1")

client = OpenAI(
    api_key=API_KEY,
    base_url=API_BASE_URL,
)

ENV_BASE = os.environ.get("ENV_BASE_URL", "http://127.0.0.1:7860").rstrip("/")

def choose_actions(task: str) -> list[str]:
    prompt = f"""
You are controlling a data-cleaning environment.
Task: {task}
Return only a comma-separated list of 1 to 3 actions from:
clean_nulls, deduplicate

Example:
clean_nulls,deduplicate
""".strip()

    resp = client.responses.create(
        model=MODEL_NAME,
        input=prompt,
    )
    text = getattr(resp, "output_text", "") or ""
    actions = [a.strip() for a in text.split(",") if a.strip()]
    valid = [a for a in actions if a in {"clean_nulls", "deduplicate"}]
    return valid[:3] or ["clean_nulls", "deduplicate"]

def run_task(task: str) -> None:
    log(f"[START] task={task}")

    try:
        r = requests.post(f"{ENV_BASE}/reset", timeout=10)
        r.raise_for_status()
    except Exception:
        log(f"[STEP] step=1 reward=0.0")
        log(f"[END] task={task} score=0.00 steps=1")
        return

    total_reward = 0.0
    steps = 0

    try:
        actions = choose_actions(task)
    except Exception:
        actions = ["clean_nulls", "deduplicate"]

    for action in actions:
        steps += 1
        try:
            r = requests.post(
                f"{ENV_BASE}/step",
                json={"action_type": action},
                timeout=10,
            )
            r.raise_for_status()
            res = r.json()
            reward = float(res.get("reward", 0.0))
        except Exception:
            reward = 0.0
            res = {}

        total_reward += reward
        log(f"[STEP] step={steps} reward={reward}")

        if res.get("done", False):
            break

        time.sleep(0.05)

    score = max(0.0, min(1.0, total_reward / max(steps, 1)))
    log(f"[END] task={task} score={score:.2f} steps={steps}")

if __name__ == "__main__":
    for task in TASKS:
        run_task(task)
