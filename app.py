from flask import Flask, render_template, session
import time
import uuid

app = Flask(__name__)
app.secret_key = "oldstudio-session-key"

# Sessões ativas
online_sessions = {}

TIMEOUT = 20  # segundos sem atividade = offline


def get_online_count():
    now = time.time()

    # Remove sessões inativas
    inactive = [
        sid for sid, last_seen in online_sessions.items()
        if now - last_seen > TIMEOUT
    ]

    for sid in inactive:
        del online_sessions[sid]

    return len(online_sessions)


@app.before_request
def track_session():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())

    online_sessions[session["session_id"]] = time.time()


# ===== INJETAR EM TODAS AS PÁGINAS =====
@app.context_processor
def inject_online():
    return {
        "online": get_online_count()
    }


# ===== ROTAS =====

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

@app.route("/journal")
def journal():
    return render_template("journal.html")

@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)