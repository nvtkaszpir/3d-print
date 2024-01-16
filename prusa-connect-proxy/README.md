# prusa-connect-proxy

Create HTTP forward proxy for Prusa Connect for LAN.

```text
[3d-printer + special cfg] -> [ host with nginx] -> [connect.prusa3d.com]
```

## Requirements

- firmware on the printer supports Prusa Connect - so you probably need
  firmware newer than 2023.10.1 for given printer (excluding alpha versions)

## Known Limitations

- nginx runs as root, in the future adjust to [docker-nginx-unprivileged](https://github.com/nginxinc/docker-nginx-unprivileged)

## Usage

## Quick how to

1. spawn docker container with nginx listening on 8889
2. configure printer to use that nginx instance
3. ...
4. profit

## Long howto

### Spawn docker container with nginx listening on 8889

Spawn docker container with nginx listening on 8889:

```shell
docker-compose up
```

write down IP address under which container is reachable
over LAN network, let say it is `my-proxy-ip`.

### Configure printer to use that nginx instance

1. Create filename `prusa_printer_settings.ini` for specific printer -
    you can actually use existing config from Prusa Connect and download it
    and then adjust it,

    make sure to define `[service::connect]` section as below,
    just make sure to replace `my-proxy-ip` with the address of the host
    that runs docker with nginx and `myRandomToken` with some token
    (no idea how to generate yet):

    ```ini
    [service::connect]
    hostname = my-proxy-ip
    tls = false
    port = 8889
    token = myRandomToken
    ```

    so if your host that runs docker is `192.168.0.20` and token is `deadbeef`
    then config is

    ```ini
    [service::connect]
    hostname = 192.168.0.20
    tls = false
    port = 8889
    token = deadbeef
    ```

2. turn off the printer
3. remove pendrive from the printer
4. connect pendrive to the printer
5. save `prusa_printer_settings.ini` to the pendrive
6. safe remove pendrive
7. connect pendrive to the printer
8. turn on the printer, wait until it boots
9. go to Settings > Networking > Prusa Connect > Load Settings from pendrive

You should see in the logs of the nginx container that it starts to proxy
requests between the printer and the Prusa Connect:

```log
nginx  | 192.168.1.25 - - [16/Jan/2024:21:49:17 +0000] "POST /p/telemetry HTTP/1.1" 204 0 "-" "-" "-"
nginx  | 192.168.1.25 - - [16/Jan/2024:21:49:21 +0000] "POST /p/telemetry HTTP/1.1" 204 0 "-" "-" "-"
nginx  | 192.168.1.25 - - [16/Jan/2024:21:49:25 +0000] "POST /p/telemetry HTTP/1.1" 204 0 "-" "-" "-"
nginx  | 192.168.1.25 - - [16/Jan/2024:21:49:29 +0000] "POST /p/telemetry HTTP/1.1" 204 0 "-" "-" "-"
nginx  | 192.168.1.25 - - [16/Jan/2024:21:49:33 +0000] "POST /p/telemetry HTTP/1.1" 204 0 "-" "-" "-"
```

## Run nginx in background

```shell
docker-compose stop
docker-compose up -d
```
