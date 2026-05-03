from flask import Flask, render_template, jsonify
from researcher import run_all_topics
import threading
import time
import os
import schedule

app = Flask(__name__)

cache = {
    "results": None,
    "last_updated": None,
    "status": "idle"
}

def run_research_background():
    cache["status"] = "running"
    cache["results"] = run_all_topics()
    cache["last_updated"] = time.strftime("%Y-%m-%d %H:%M")
    cache["status"] = "done"
    print(f">>> Scheduled research completed at {cache['last_updated']}")

def start_scheduler():
    schedule.every().monday.at("07:00").do(run_research_background)
    print(">>> Scheduler started — runs every Monday at 07:00")
    while True:
        schedule.run_pending()
        time.sleep(60)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status")
def status():
    return jsonify({
        "status": cache["status"],
        "last_updated": cache["last_updated"]
    })

@app.route("/api/results")
def results():
    return jsonify(cache["results"] or {})

@app.route("/api/refresh", methods=["POST"])
def refresh():
    if cache["status"] != "running":
        thread = threading.Thread(target=run_research_background)
        thread.daemon = True
        thread.start()
    return jsonify({"status": "started"})

if __name__ == "__main__":
    scheduler_thread = threading.Thread(target=start_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)