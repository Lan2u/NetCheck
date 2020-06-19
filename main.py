# Library imports
import threading
import time

# Imports from this program
import netConn as nc
import error
from error import ConnectionFailedError

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
        self.running = True;

    def run(self):
        while self.running:
            update_net_state(self.net)
            time.sleep(self.update_period)
    
    def stop(self):
        self.running = False;

def main():
    print("Starting...")
    net = nc.create_from_file("config.json")
    update_thread = NetUpdateThread(net)
    update_thread.start()
    time.sleep(5)
    update_thread.stop()
    update_thread.join()

if __name__ == "__main__" :
    main()