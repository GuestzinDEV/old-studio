from flask import Flask, render_template, request, session
import time
import uuid
import os
from supabase import create_client

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "oldstudio-session-key")

# ================= ONLINE COUNTER =================
online_sessions = {}
TIMEOUT = 20  # segundos

def get_online_count():
    now = time.time()
    inactive = [sid for sid, last_seen in online_sessions.items() if now - last_seen > TIMEOUT]
    for sid in inactive:
        del online_sessions[sid]
    return len(online_sessions)

@app.before_request
def track_and_log():
    # session online
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    online_sessions[session["session_id"]] = time.time()

    # log no Render
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    print(f"[VISIT] IP: {ip} | Path: {request.path}")

@app.context_processor
def inject_online():
    return {"online": get_online_count()}

# ================= SUPABASE =================
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# ================= ROUTES =================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/games")
def games():
    return render_template("games.html")

@app.route("/journal", methods=["GET", "POST"])
def journal():
    error = None

    if request.method == "POST":
        author = request.form.get("author")
        password = request.form.get("password")
        content = request.form.get("content")

        if password != os.environ.get("DEV_PASSWORD"):
            error = "Invalid password."
        else:
            try:
                supabase.table("journal_posts").insert({
                    "author": author,
                    "content": content,
                    "category": "update"
                }).execute()
            except Exception as e:
                error = f"Failed to post update: {e}"

    posts = supabase.table("journal_posts").select("*").order("created_at", desc=True).execute().data

    return render_template("journal.html", posts=posts, error=error)

if __name__ == "__main__":
    app.run(debug=True)