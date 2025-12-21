from flask import Flask, render_template, request
import time

app = Flask(__name__)

# usuários online (em memória)
online_users = {}

TIMEOUT = 15  # segundos

def get_online_count():
    now = time.time()
    # remove usuários inativos
    inactive = [ip for ip, t in online_users.items() if now - t > TIMEOUT]
    for ip in inactive:
        del online_users[ip]
    return len(online_users)

@app.before_request
def track_user():
    ip = request.remote_addr
    online_users[ip] = time.time()

@app.route("/")
def home():
    return render_template("index.html", online=get_online_count())

@app.route("/games")
def games():
    return render_template("games.html", online=get_online_count())

@app.route("/about")
def about():
    return render_template("about.html", online=get_online_count())

@app.route("/discord")
def discord():
    return render_template("discord.html", online=get_online_count())

@app.route("/credits")
def credits():
    return render_template("credits.html", online=online_users)

@app.route("/journal")
def journal():
    return render_template("journal.html", online=online_users)

if __name__ == "__main__":
    app.run(debug=True)
