# prusa-connect-proxy on host

Basic nginx configs that do not require containers or extra logging.
Tested on Raspberry Pi.

## Installation

Make sure host which runs this proxy has static address, for example it static
in DHCP config in given network.

Example for Raspberry Pi:

```bash
sudo apt-get install -y nginx
sudo cp *.conf /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

Now nginx listens on ports:

- `8889` and points to `buddy-a.connect.prusa3d.com` - use with specific
  printers with PrusaConnect on firmware, such as Prusa Mini+
- `8890` and points to `connect.prusa3d.com` - anything else such as on
  RaspberryPi with PrusaLink

Use command `ip a` to list addresses and write down IP address under which this
host is reachable over LAN network, let say it is `my-proxy-ip`.

Next, configure your [Prusa printer](../README.md)
