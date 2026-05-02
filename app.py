from flask import Flask, render_template, jsonify
from researcher import run_all_topics
import threading
import time

app = Flask(__name__)

# Simple in-memory cache
cache = {
    "results": None,
    "last_updated": None,
    "status": "idle"  # idle | running | done
}

def run_research_background():
    cache["status"] = "running"
    cache["results"] = run_all_topics()
    cache["last_updated"] = time.strftime("%Y-%m-%d %H:%M")
    cache["status"] = "done"

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)