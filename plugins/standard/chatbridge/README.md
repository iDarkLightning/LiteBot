# ChatBridge

This plugin implements a bidirectional chatbridge between the server and discord as well as a bidrectional chatbridge between servers

## Requirements

You must be using [litebot-mod](https://github.com/iDarkLightning/litebot-mod) server-side for this plugin to work. In order for the best experience it is reccomended that you also run [litetech-additions](https://github.com/LiteTechMC/litetech-additions) on both the server and the client.

## Configuration
For the server -> discord bridge to work properly, you must [follow these instructions](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) to create a webhook for each of your servers.
Once you have the webhook URLs, simply fill those fields out in the config for each server.

Your resulting config should look something like this:
```json
"Server -> Discord Bridge":{
    "enabled":true,
    "config":{
        "webhook_urls":{
            "smp":"https://discord.com/api/webhooks/",
            "cmp":"https://discord.com/api/webhooks/"
        }
    }
}
```
