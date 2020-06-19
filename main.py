import netConn as nc
import error
from error import ConnectionFailedError

def main():
    print("Starting...")
    net = nc.create_from_file("config.json")

    try:
        net.ping_all()
    except error.Error:
        print("Failed to ping all")
        exit(0)
    
    time_since = net.last_successful_contact("Google DNS")
    if time_since != None:
        print("Last successful contact elapsed: {:02.2f} secs".format(time_since.total_seconds()))
    else:
        print("Last successful contact elapsed: {secs} secs".format(secs=None))

if __name__ == "__main__" :
    main()