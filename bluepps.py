
# bluetooth

from micropython import const
import struct
import machine
import bluetooth

# gatt constants

_ADV_APPEARANCE_GENERIC_COMPUTER = const(128)
_ADV_TYPE_FLAGS = const(0x01)
_ADV_TYPE_NAME = const(0x09)
_ADV_TYPE_UUID16_COMPLETE = const(0x3)
_ADV_TYPE_UUID32_COMPLETE = const(0x5)
_ADV_TYPE_UUID128_COMPLETE = const(0x7)
_ADV_TYPE_APPEARANCE = const(0x19)

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(4)

# gatt advertising

def advertising_payload(limited_disc=False, br_edr=False, name=None, services=None, appearance=0):
    payload = bytearray()
    def _append(adv_type, value):
        nonlocal payload
        payload += struct.pack("BB", len(value) + 1, adv_type) + value
    _append(
        _ADV_TYPE_FLAGS,
        struct.pack("B", (0x01 if limited_disc else 0x02) + (0x18 if br_edr else 0x04)),
    )
    if name:
        _append(_ADV_TYPE_NAME, name)
    if services:
        for uuid in services:
            b = bytes(uuid)
            if len(b) == 2:
                _append(_ADV_TYPE_UUID16_COMPLETE, b)
            elif len(b) == 4:
                _append(_ADV_TYPE_UUID32_COMPLETE, b)
            elif len(b) == 16:
                _append(_ADV_TYPE_UUID128_COMPLETE, b)
    _append(_ADV_TYPE_APPEARANCE, struct.pack("<h", appearance))
    return payload

# gatt uart service

_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (
    bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY,
)
_UART_SERVICE = (
    _UART_UUID,
    (_UART_TX,)
)

# ble uart class

class BLEUART:
    def __init__(self, ble, name):
        self._connections = set()
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(handler=self._irq)
        ((self._tx_handle,),) = self._ble.gatts_register_services((_UART_SERVICE,))
        self._payload = advertising_payload(name=name, 
            appearance=_ADV_APPEARANCE_GENERIC_COMPUTER)
        self._advertise()

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            if conn_handle in self._connections:
                self._connections.remove(conn_handle)
            self._advertise()

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def write(self, data):
        self._ble.gatts_write(self._tx_handle, data)  # FLAG_READ
        for conn_handle in self._connections:         # FLAG_NOTIFY
            self._ble.gatts_notify(conn_handle, self._tx_handle, data)
            print(' ', data)

# main

NAME = "bluepps"
BAUD = 9600
UART_PORT = 2
LED_PORT = 2

ble = bluetooth.BLE()
bleuart = BLEUART(ble, NAME)
uart = machine.UART(UART_PORT, baudrate=BAUD)
pin = machine.Pin(LED_PORT, machine.Pin.OUT) # GPIO2 is wired to LED1 (blue)
pin.value(0)

while True:
    line = uart.readline()
    if line is not None:
        d = line.split(b',')
        if d[0] == b'$GPRMC' and len(d) > 9:
            utc = d[1].strip()      # hhmmss.ss
            status = d[2].strip()   # A/V
            date = d[9].strip()     # ddmmyy
            if utc and date and status == b'A':
                bleuart.write(utc + b',' + date)
            pin.value(not pin.value())
            print('>', line[:-2])

