

# Bluetooth BLE PPS Service using a ESP32, a GPS Module and Micropython

Do you need a GPS time standard but do not like having your GPS device
tethered to your laptop or desktop using USB?
Maybe you are inside but do not have an outdoor GPS antenna.
Maybe your operating location is not conductive to GPS reception
but are unable move your GPS device far away enough.

Why not connect your GPS to you computer using bluetooth BLE instead?
This repo contains a BLE implementation of a GPS PPS device
in Micropython.  Specifically, the code is designed to be run
on a ESP32 microcontroller with Micropython ESP-IDF v4.x firmware 
for BLE support.

### Hardware

First connect your ESP32 to a GPS module using one of the UART ports.
The code uses Uart 2.  Next copy bluepps.py to the ESP32.  The blue
led on the ESP32 will blink each second while receiving GPS output.

The ESP32 outputs the current time and date whenever a valid
$GPRMC line is received.  Using the host software below,
this data is then converted back into a valid NMEA $GPRMC line.
Both time and date must be sent before gpsd will recognize
it as valid PPS data.

### Software

First install the library bluepy using pip.
Next modify the client.py code with the BLE mac address of your ESP32.
You can use nRF Connect App to find this mac address.  The device
will be named "bluepps".   Another option is to use
the included code scan.py to find the mac address.  Run it using
"python3 scan.py".

### Simple Example

To watch the PPS output from your console run "python3 client.py".
No data will be sent from the ESP32 until valid time NMEA data
is received from the GPS satellites.  Client.py converts
this data into a valid NMEA $GPRMC output line.

To send this NMEA line over a tcp socket instead the console
run "python3 tcpsource.py".  This code creates a local tcp socket server
on port 8888.  You can connect to it using "nc -d localhost 8888".
To send the same NMEA line over a udp socket instead use
"python3 updsource.py"

### Using with GPSD 

To listen to either of tcp or udp services using gpsd and chrony,
add the following line to /etc/chrony/chrony.conf.

```
refclock SHM 0 delay 0.5 refid NMEA
```

Next run gpsd using the option "-n" and add the devices 
"tcp://127.0.0.1:8888" or "udp://127.0.0.1:5005" for gpsd to use.
I recommend using the udpsource.py server.

For example, I used the following command to debug chrony and gpsd:

```bash
sudo gpsd -D6 -n -N -b tcp://localhost:8888
-- or --
sudo gpsd -D6 -n -N -b udp://127.0.0.1:5005
```

To watch chrony I used:

```bash
chronyc sources -v
```

