from flask import Flask, render_template, request
import time
import uuid
import os
from supabase import create_client

app = Flask(__name__)
app.secret_key = "oldstudio-session-key"

# ================= ONLINE COUNTER =================

online_sessions = {}
TIMEOUT = 20

def get_online_count():
    now = time.time()
    inactive = [
        sid for sid, last_seen in online_sessions.items()
        if now - last_seen > TIMEOUT
    ]
    for sid in inactive:
        del online_sessions[sid]
    return len(online_sessions)

@app.before_request
def track_session():
    from flask import session
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    online_sessions[session["session_id"]] = time.time()

@app.context_processor
def inject_online():
    return {"online": get_online_count()}

# ================= SUPABASE =================

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# ================= DEV PASSWORDS =================

DEV_PASSWORDS = {
    "Guestzin": os.environ.get("DEV_GUESTZIN_PASSWORD"),
    "Mrc": os.environ.get("DEV_MRC_PASSWORD")
}

# ================= ROUTES =================

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/games")
def games():
    return render_template("games.html")

@app.route("/discord")
def discord():
    return render_template("discord.html")

@app.route("/credits")
def credits():
    return render_template("credits.html")

@app.route("/about")
def about():
    return render_template("about.html")

# ================= JOURNAL =================

CATEGORY_MAP = {
    "development": "Development Logs",
    "design": "Design Notes",
    "concepts": "Game Concepts",
    "releases": "Release Updates"
}

@app.route("/journal/<category>", methods=["GET", "POST"])
def journal(category):
    if category not in CATEGORY_MAP:
        return "Category not found", 404

    error = None

    if request.method == "POST":
        author = request.form["author"]
        password = request.form["password"]
        content = request.form["content"]

        if DEV_PASSWORDS.get(author) != password:
            error = "Invalid password."
        else:
            supabase.table("journal_posts").insert({
                "author": author,
                "category": CATEGORY_MAP[category],
                "content": content
            }).execute()

    posts = (
        supabase.table("journal_posts")
        .select("*")
        .eq("category", CATEGORY_MAP[category])
        .order("created_at", desc=True)
        .execute()
        .data
    )

    return render_template(
        "journal.html",
        posts=posts,
        current_category=CATEGORY_MAP[category],
        error=error
    )

@app.route("/journal")
def journal_redirect():
    return journal("development")

if __name__ == "__main__":
    app.run(debug=True)