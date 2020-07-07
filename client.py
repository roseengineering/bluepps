
from bluepy import btle
from datetime import datetime

def checksum(data):
    x = 0
    for c in bytes(data): x ^= c
    return b'$%s*%02X\r\n' % (data, x)

class MyDelegate(btle.DefaultDelegate):
    def __init__(self, chandle, handler):
        self.chandle = chandle
        self._handler = handler
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, chandle, data):
        if self.chandle == chandle:
            print('>', data)
            if data:
                d = data.split(b',')
                utc = d[0].strip()
                date = d[1].strip()
                res = b'GPRMC,%s,A,,,,,,,%s,,,' % (utc, date)
                self._handler(checksum(res))

mac = 'f0:08:d1:60:39:0e'
service_uuid = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
char_uuid = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

def initialize(handler):
    print('connecting to bluetooth device:', mac)
    per = btle.Peripheral(mac, addrType=btle.ADDR_TYPE_PUBLIC)
    svc = per.getServiceByUUID(service_uuid)
    ch = svc.getCharacteristics(char_uuid)[0]
    chandle = ch.getHandle()
    delegate = MyDelegate(chandle, handler)
    per.setDelegate(delegate)
    return per

if __name__ == "__main__":
    def onconnect(data):
        print(' ', data)
    while True:
        try:
            per = initialize(onconnect)
            while True:
                per.waitForNotifications(1.0)
        except btle.BTLEDisconnectError:
            print('bluetooth device connection dropped...')


