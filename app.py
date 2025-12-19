import os
import uuid
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

# 🏠 HOME
@app.route("/")
def home():
    session_id = request.cookies.get("session_id")

    if not session_id:
        session_id = str(uuid.uuid4())

    # Increment total visits
    supabase.table("site_stats").update({
        "total_visits": supabase.rpc("increment", {}).execute()
    }).eq("id", 1).execute()

    # Update online users
    supabase.table("online_users").upsert({
        "session_id": session_id,
        "last_seen": datetime.utcnow().isoformat()
    }).execute()

    response = render_template("index.html")
    res = app.make_response(response)
    res.set_cookie("session_id", session_id, max_age=86400)

    return res

# 📊 STATS API
@app.route("/stats")
def stats():
    # Total visits
    visits = supabase.table("site_stats").select("total_visits").eq("id", 1).execute()
    total_visits = visits.data[0]["total_visits"]

    # Online users (last 2 minutes)
    time_limit = (datetime.utcnow() - timedelta(minutes=2)).isoformat()

    online = supabase.table("online_users") \
        .select("session_id") \
        .gte("last_seen", time_limit) \
        .execute()

    return jsonify({
        "total_visits": total_visits,
        "online_users": len(online.data)
    })

@app.route("/games")
def games():
    return render_template("games.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/discord")
def discord():
    return render_template("discord.html")

if __name__ == "__main__":
    app.run()
