

# Bluetooth BLE PPS Service using a ESP32, a GPS Module and Micropython

Do you need a GPS time standard but do not like having your GPS device
tethered to your laptop or desktop using USB?
Maybe you are inside but do not have an outdoor GPS antenna.
Maybe your operating location is not conductive to GPS reception
but are unable move your GPS device far away enough because of USB.

Why not connect your GPS module to your computer over bluetooth BLE instead?
This repo does just this.  It contains a BLE implementation of a GPS PPS device
in Micropython.  Specifically, the code is designed to be run
on a ESP32 microcontroller with Micropython ESP-IDF v4.x firmware 
for BLE support.

### Hardware

First connect your ESP32 to a GPS module using one of the ESP32 UART ports.
The code uses Uart 2.  Next copy bluepps.py to the ESP32.  The blue
led on the ESP32 will blink each second while receiving GPS output.

The ESP32 outputs the current time and date whenever a valid
$GPRMC line is received.  Using the host software below,
this data is then converted back into a valid NMEA $GPRMC line.

While bluepps.py runs, it writes all $GPRMC lines
received from the GPS module to the micropython repl console:

```
> b'$GPRMC,021953.00,V,,,,,,,070720,,,N*73'
> b'$GPRMC,021954.00,V,,,,,,,070720,,,N*74'
> b'$GPRMC,021955.00,V,,,,,,,070720,,,N*75'
> b'$GPRMC,021956.00,V,,,,,,,070720,,,N*76'
> b'$GPRMC,021957.00,V,,,,,,,070720,,,N*77'
> b'$GPRMC,021958.00,V,,,,,,,070720,,,N*78'
> b'$GPRMC,021959.00,V,,,,,,,070720,,,N*79'
> b'$GPRMC,022000.00,V,,,,,,,070720,,,N*7F'
> b'$GPRMC,022001.00,V,,,,,,,070720,,,N*7E'
> b'$GPRMC,022002.02,V,,,,,,,070720,,,N*7F'
> b'$GPRMC,022003.00,V,,,,,,,070720,,,N*7C'
> b'$GPRMC,022004.00,V,,,,,,,070720,,,N*7B'
> b'$GPRMC,022005.00,V,,,,,,,070720,,,N*7A'
> b'$GPRMC,022006.00,V,,,,,,,070720,,,N*79'
> b'$GPRMC,022007.00,V,,,,,,,070720,,,N*78'
> b'$GPRMC,022008.00,V,,,,,,,070720,,,N*77'
> b'$GPRMC,022009.00,V,,,,,,,070720,,,N*76'
> b'$GPRMC,022010.00,V,,,,,,,070720,,,N*7E'
> b'$GPRMC,022011.00,V,,,,,,,070720,,,N*7F'
```

### Software

First install the library bluepy using pip.
Next modify the client.py code with the BLE mac address of your ESP32.
You can use nRF Connect App to find this mac address.  The device
will be named "bluepps".   Another option is to use
the included code scan.py to find the mac address.  Run it using
"python3 scan.py".

### Simple Example

To watch the PPS output from your console run "python3 client.py".
No data will be sent from the ESP32 until a valid NMEA line 
with the current time and date is received from the GPS satellites.
The code client.py converts this data into a valid NMEA $GPRMC output line.
Both time and date must be sent otherwise gpsd will not recognize
the NMEA line as valid PPS data.

To send this NMEA line over a tcp socket instead of to the console
run "python3 tcpsource.py".  tcpsource.py creates a local tcp socket server
on port 8888.  Connect to it using "nc -d localhost 8888".
To send the same NMEA line over a udp socket use
"python3 updsource.py"

### Interfacing Bluepps with Gpsd and Chrony

To listen to either of the tcp or udp services using gpsd and chrony
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

