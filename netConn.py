import socket
import json
from datetime import datetime
from icmplib import ping, SocketPermissionError
from error import ConnectionFailedError
import threading

PING_COUNT = 4

class Config:
    def to_json(self):
        return json.dumps(self)

    def to_file(self, path):
        file = open(path, "w")
        file.write(self.to_json())
        file.close()

def config_from_file(path):
    config = Config()
    file = open(path, "r")
    json_data = json.loads(file.read())
    config.self_name = json_data['self_name']

    config.hosts = {}

    for host_cfg in json_data['hosts']:
        host = host_from_str(host_cfg)
        config.hosts[host.name] = host

    return config

class HostStatus:
    def __init__(self, name, addr, elapsed, last_loss, avg_rtt):
        self.name = name
        self.addr = addr
        self.elapsed = elapsed.total_seconds()
        self.last_loss = last_loss
        self.avg_rtt = avg_rtt

class Host:
    def __init__ (self, address = "127.0.0.1", name="default"):
        self.name = name
        self.addr = address
        self.last_ping = None
        self.last_ping_timestamp = None

    def log_ping(self, ping):
        self.last_ping = ping
        self.last_ping_timestamp = datetime.now()

    def elapsed_since_last_successful_contact(self):
        if self.last_ping_timestamp == None:
            return None
        return datetime.now() - self.last_ping_timestamp

    def gen_host_status(self):
        name = self.name
        addr = self.addr
        elapsed = self.elapsed_since_last_successful_contact()
        last_loss = self.last_ping.packet_loss
        return HostStatus(name, addr, elapsed, last_loss, self.last_ping.avg_rtt)

def host_from_str(host_cfg):
    host = Host()
    host.name = host_cfg['name']
    host.addr = host_cfg['addr']
    return host

class NetConn:
    def __init__ (self, name):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock = sock
        self.hosts = {}
        self.lock = threading.Lock()
        self.name = name

    def get_name(self):
        return self.name

    def _ping_host(self, host):
        try:
            res = ping(host.addr, count=PING_COUNT, interval=0.2)
            host.log_ping(res)
        except SocketPermissionError:
            raise ConnectionFailedError("Failed to ping host")
            
    def send_ping(self, host_name):
        host = self.hosts[host_name]
        self._ping_host(host)

    # Thread-safe.
    def ping_all(self):
        self.lock.acquire()
        for host in self.hosts.values():
            try:
                self._ping_host(host)
            except ConnectionFailedError as e:
                raise e
        self.lock.release()

    def register_host(self, host):
        self.hosts[host.host_name] = host

    def last_successful_contact(self, host_name):
        return self.hosts[host_name].elapsed_since_last_successful_contact()

    # Thread-safe.
    def get_status(self):
        self.lock.acquire()
        status = []
        for host in self.hosts.values():
            status.append(host.gen_host_status().__dict__)
        self.lock.release()
        return status
    

def create_from_config(config):
    nc = NetConn(config.self_name)
    nc.hosts = config.hosts
    return nc

def create_from_file(path):
    config = config_from_file(path)
    return create_from_config(config)