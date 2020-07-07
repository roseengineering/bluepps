
import socket
from client import initialize
from bluepy import btle

HOST = '127.0.0.1'
PORT = 5005

def main():
    def onconnect(data):
        print(' ', data)
        s.sendto(data, (HOST, PORT))
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    done = False
    while not done:
        try:
            per = initialize(onconnect)
            while True:
                per.waitForNotifications(1.0)
        except btle.BTLEDisconnectError:
            print('bluetooth device disconnected')
        except KeyboardInterrupt:
            print('keyboard interrupt while connected')
            done = True
        finally:
            print('disconnecting from bluetooth device')
            per.disconnect()

main()

