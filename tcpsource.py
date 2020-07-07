
import socket
from client import initialize
from bluepy import btle

HOST = '127.0.0.1'
PORT = 8888

def listen(s):
    done = False
    while not done:
        print('waiting for connection...')
        s.listen()
        conn, addr = s.accept()
        print('connected.')
        with conn:
            try:
                def onconnect(data):
                    print(' ', data)
                    conn.sendall(data)
                per = initialize(onconnect)
                while True:
                    per.waitForNotifications(1.0)
            except BrokenPipeError:
                print('socket disconnected')
            except btle.BTLEDisconnectError:
                print('bluetooth device disconnected')
            except KeyboardInterrupt:
                print('keyboard interrupt while connected')
                done = True
            finally:
                print('disconnecting from bluetooth device')
                per.disconnect()


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    try:
        listen(s)
    except KeyboardInterrupt:
        print('keyboard interrupt while listening')

main()


