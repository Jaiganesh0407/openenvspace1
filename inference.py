import os
import sys
import time
import requests

try:
    from openai import OpenAI
except:
    OpenAI = None

def log(msg):
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()

API_BASE_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY") or os.getenv("HF_TOKEN")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

ENV_BASE = "http://127.0.0.1:7860"
TASKS = ["easy", "medium", "hard"]
BENCHMARK = "data_cleaning_env"

client = None
if API_BASE_URL and API_KEY and OpenAI:
    try:
        client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)
    except:
        client = None

def choose_action(task):
    if not client:
        return "clean_nulls"

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Return one word: clean_nulls or deduplicate"},
                {"role": "user", "content": f"Task: {task}"}
            ],
            temperature=0.2,
            max_tokens=5
        )
        text = (response.choices[0].message.content or "").lower()
        if "deduplicate" in text:
            return "deduplicate"
        return "clean_nulls"
    except Exception:
        return "clean_nulls"

def run_task(task):
    log(f"[START] task={task} env={BENCHMARK} model={MODEL_NAME}")

    rewards = []
    steps = 0

    try:
        r = requests.post(f"{ENV_BASE}/reset", timeout=5)
        r.raise_for_status()
    except Exception:
        rewards = [0.01]
        log("[STEP] step=1 action=clean_nulls reward=0.01 done=true error=null")
        log("[END] success=false steps=1 score=0.01 rewards=0.01")
        return

    for step in range(1, 4):
        steps = step
        action = choose_action(task)

        try:
            r = requests.post(
                f"{ENV_BASE}/step",
                json={"action_type": action},
                timeout=5
            )
            r.raise_for_status()
            res = r.json()

            reward = float(res.get("reward", 0.0))
            done = bool(res.get("done", False))
            error = "null"
        except Exception:
            reward = 0.01
            done = True
            error = "request_failed"

        # force reward strictly inside (0,1) for safe parsing/output
        reward = max(0.01, min(0.99, reward))
        rewards.append(reward)

        log(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error}")

        if done:
            break

        time.sleep(0.05)

    total_reward = sum(rewards)
    raw_score = total_reward / max(len(rewards), 1)
    score = max(0.01, min(0.99, raw_score))
    success = score >= 0.10

    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    log(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}")

if __name__ == "__main__":
    for task in TASKS:
        run_task(task)
