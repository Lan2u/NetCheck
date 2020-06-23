# Std Library imports
import threading
import time
import os
import webbrowser

# Imports from external libraries
from flask import Flask, render_template, jsonify, request

# Imports from this program
import netConn as nc
import error
from error import ConnectionFailedError

app = Flask(__name__)

net = None

update_thread = None

INDEX_TEMPLATE_PATH = "index.html"

# INDEX_TEMPLATE_PATH = os.path.join("templates", "index.html")

def update_net_state(net):
    try:
        net.ping_all()
    except error.Error:
        print("Local networking ping failure")

class NetUpdateThread (threading.Thread):
    def __init__(self, net, update_period=1):
        threading.Thread.__init__(self)
        self.net = net
        self.update_period = update_period
        self.running = True

    def run(self):
        while self.running:
            update_net_state(self.net)
            time.sleep(self.update_period)
    
    def stop(self):
        self.running = False

@app.route('/host_status', methods=['GET'])
def get_status():
    return jsonify(net.get_status())

@app.route('/', methods=['GET'])
def index():
    return render_template(INDEX_TEMPLATE_PATH, name=net.get_name())


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

# Server shutdown, to make this as easy as possible this is done as a /shutdown route.
# This is obviously not an ideal solution because if you leave the localhost/shutdown page open
# then you won't be able to start the server as chrome auto-refresh will trigger the shutdown immediately.
@app.route('/shutdown', methods=['GET'])
def shutdown():
    shutdown_server()
    update_thread.stop()
    update_thread.join()
    exit(0)
    return 'Server shutting down...'

def startup():
    print("Starting...")
    global net
    net = nc.create_from_file("config.json")
    global update_thread
    update_thread = NetUpdateThread(net)
    update_thread.start()

if __name__ == "__main__" :
    webbrowser.open("http://localhost:16780/", 2)
    startup()
    app.run(port=16780)