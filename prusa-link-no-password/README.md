# prusa-link-no-password

Create HTTP forward proxy for Prusa Link for LAN printers.
Allows to access your printer without passwords (well, almost).

Connection diagram:

```mermaid
sequenceDiagram
    browser->>proxy: User connects via web browser to proxy
    proxy->>printer1: proxy connects to the printer and injects auth header
    printer1->>proxy: printer responds with content to proxy
    proxy->>browser: proxy forwards content back to the user browser
```

# Warning

This code is without any warranty, use at your own risk.
This effectively strips any security when accessing printer,
so if someone has access to the host that runs this code,
then they can do whatever they want with the printer,
such as print files / abort existing print, delete files... etc

# Known Limitations

- Tested only with Prusa Mini+ v5.1.2, for other printers/configs
  it probably requires additional headers or changed headers.

# Requirements

- docker
- printer and proxy host should be in the same network to make life easier

# Usage

## Using without docker

You should be able to just copy/paste files from `nginx/conf.d/` to the normal,
standalone nginx to `/etc/nginx/conf.d/`, reload service and you're done.
Anyway, just read below readme for more details, you're gonna need it anyway.

## Using with docker

## Configuring first printer

Edit `nginx/conf.d/printer1.conf` and adjust:

- `10001` - change listening port of the nginx proxy, 10001 to your desired port
- `192.168.1.25` - this is an address of your printer with PrusaLink
- `X-Api-Key` value - this contains key to authorize when you access printer over PrusaLink.

Then edit `docker-compose.yaml` and ensure that ports section targets the port you defined above:

```yaml
    ports:
      - "10001:10001/tcp" # printer1.conf
```

Run `docker-compose start`.

Point your browser to [http://127.0.0.1:10001](http://127.0.0.1:10001)

If you run docker on different host then remember to allow `10001` on the firewall
and just use address of the host, so lets say your NAS is on 192.168.1.20 and
it runs that container then try [http://192.168.1.20:10001](http://192.168.1.20:10001)

## Adding next printer

In general ports should be unique otherwise there will be error when starting
a container (AFAIR).

- copy `nginx/conf.d/printer1.conf` as new file, for example `nginx/conf.d/printer2.conf`
- edit `nginx/conf.d/printer2.conf` - bump port number (let say `10002`), address, X-Api-Key
- edit docker-compose.yaml and add additional port
- restart container `docker-compose restart`
- point your browser to [http://127.0.0.1:10002](http://127.0.0.1:10002)

# Other

## Run in the background

Run in the background:

```shell
docker-compose stop
docker-compose start -d
```

## Single port and multi printer

It's possible to have one listening port and redirection to different printers
based on the path, but the config gets more complex. Usually if you need it then
ask me on Prusa Discord server.
