# ddnss-ip-updater

*Made for https://ddnss.de/*

Python Script used to automatically update the ip of a dynamic dns which points to a server (archlinux-based)

## Enabling the service

### Cloning
The wanted path for the service is `/usr/share/ddnss-ip-updater`. The directory will require root permissions

### Configuring the file
Add the configurations into the template-config.json file and rename/move config.json into the folder 
`/usr/share/ddnss-ip-updater/`

```bash
mv ./template-config.json /config.json
```

### Adding the systemctl service
```bash
mv ./ddnss-ip-updater.service /etc/systemd/system/ddnss-ip-updater.service
```

### Reloading the daemon and starting the service
```bash
systemctl daemon-reload
```

```bash
systemctl start ddnss-ip-updater.service
```

### Adding the service to startup
```bash
systemctl enable ddnss-ip-updater.service
```
