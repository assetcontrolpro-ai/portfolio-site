from fastapi import FastAPI
import os

app = FastAPI(title="ACP Fund API")

DATA_DIR = os.getenv("DATA_DIR", "/data")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/nav")
def nav():
    """
    Retourne un aperçu de la NAV (si fichier nav.csv existe).
    """
    import pandas as pd
    import os

    nav_file = os.path.join(DATA_DIR, "nav_history.csv")
    if not os.path.exists(nav_file):
        return {"error": "No NAV history yet."}

    df = pd.read_csv(nav_file)
    return {
        "last_date": df["Date"].iloc[-1],
        "last_value": df["Portfolio Value"].iloc[-1],
        "count": len(df),
    }

@app.get("/composition")
def composition():
    """
    Retourne la composition actuelle du portefeuille (si dispo).
    """
    import json

    comp_file = os.path.join(DATA_DIR, "last_composition.json")
    if not os.path.exists(comp_file):
        return {"error": "No composition snapshot yet."}

    with open(comp_file, "r") as f:
        data = json.load(f)
    return data

from fastapi import BackgroundTasks
import subprocess

@app.post("/run-rebalance")
def run_rebalance(background_tasks: BackgroundTasks):
    def task():
        subprocess.run(["python", "rebalance.py"], cwd=os.getcwd())
    background_tasks.add_task(task)
    return {"status": "started", "job": "rebalance"}

@app.post("/run-update")
def run_update(background_tasks: BackgroundTasks):
    def task():
        subprocess.run(["python", "update_nav.py"], cwd=os.getcwd())
    background_tasks.add_task(task)
    return {"status": "started", "job": "update_nav"}
