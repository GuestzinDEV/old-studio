from flask import Flask, render_template, jsonify
from supabase import create_client

SUPABASE_URL = "COLE_AQUI"
SUPABASE_KEY = "COLE_AQUI"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

@app.route("/")
def home():
    # Incrementa visitas
    supabase.table("site_stats").update({
        "total_visits": "total_visits + 1"
    }).eq("id", 1).execute()

    return render_template("index.html")

@app.route("/stats")
def stats():
    data = supabase.table("site_stats").select("total_visits").eq("id", 1).execute()
    total_visits = data.data[0]["total_visits"]

    return jsonify({
        "total_visits": total_visits
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
