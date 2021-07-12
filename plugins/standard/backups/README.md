# Backups

This plugin lets you easily manage backups for all your servers.

## Requirements
**YOU MUST BE RUNNING THE BOT ON THE SAME MACHINE AS YOUR SERVERS IF YOU WISH TO USE THIS PLUGIN**

## Usage
Firstly, you must mount your server directories to the docker container.

Rename `volume-config.template.yml` to `volume-config.yml`.
Then, add all your servers to the `volumes` array, with each server directory being mapped `/bot/servers/<server_name>`

Your resulting file should look something like this

```yaml
services:
  bot:
    volumes:
      - "/home/servers/smp:/bot/servers/smp"
      - "/home/servers/cmp:/bot/servers/cmp"
```

On subsequent runs, you must start the bot using the following command otherwise the plugin will not load
```bash
docker-compose -f docker-compose.yml -f volume-config.yml # You can include -d here if you would like to detach from the containers upon starting
```

You can read more about docker volumes [here](https://docs.docker.com/storage/volumes/)