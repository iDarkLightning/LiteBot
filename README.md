# LiteBot
LiteBot is a minecraft linking discord bot with other various utilities. It was created for the technical minecraft server [LiteTech](http://discord.litetech.cf). If you would like to use it you can set it up by following the instructions below.

## Installation
Firstly, ensure that you have [Python 3.9](https://www.python.org/downloads/), and [pip](https://pip.pypa.io/en/stable/installing/) installed.

Then install all the requirements with

```bash
python3.9 -m pip install -r requirements.txt
```
Then create a discord application [here](https://discordpy.readthedocs.io/en/latest/discord.html)

Ensure that you have developer mode enabled on discord [here](https://discordia.me/en/developer-mode)

## Configuring the Bot
**RENAME ALL `.TEMPLATE.JSON` to `.JSON`**

Within the server `server.properties`of your server(s) configure these properties:
* `broadcast-rcon-to-ops` should be set to `false` in order to ensure the log files are not cluttered from bot usage
* `enable-rcon` must be set to `true`
* `rcon.port` set to a unique port (not same as server port)
* `rcon.password` create a secure password

Within `config.json` configure the following properties ()
* `token` your bot's token
* `prefix` the prefix you would like to use when running commands
* `server_logo` a direct link to your server's logo
* `members_role` ID of the role that will be able to access the bot
* `operator_role` ID of the role that will be able to execute commands on operator servers and create backups
* `main_guild_id` ID of the main guild that the bot will be used in

* `servers` Array of the configuration of all servers. You can add as many as you would like. If you are not comfortable with the JSON Structure you can read about it [here](https://www.digitalocean.com/community/tutorials/an-introduction-to-json):
    * `name` the name of the server, will be used for commands
    * `server_ip` server IP in format `ip:port`
    * `server_ip_numerical` server IP without any ports
    * `server_rcon_port` the RCON port you set in your `server.properties`
    * `server_rcon_password` the RCON password you set in your `server.properties`
    * `operator` set to either `True` or `False` depending on whether operator role is required to execute commands on this server
    * `bridge_channel_id` if you are using LiteTech Additions, set this to the same bridge channel ID you used there, otherwise leave it at `1`
    * `backup_directory` path to the directory where backups will be stored
    * `world_directory` path to the server's world directory

## Module Configurations
After you first run the bot, the `modules_config.json` will be generated with all the configurations you need to fill in for these modules.
In order to use any of these modules, simple change the `enabled` to `true` and fill in the config if applicable. After you run the bot with
the extension enabled, a list of all the available `cogs` will be added to the module's config. You can then switch any of these cogs to false
in order to prevent them loading. **You must restart the bot for these changes to take effect**

##Maintaining the bot
In order to disable an entire module, you can use the `module` command directly from discord. In order to disable you will have to use the 
`module_config.json` (for now)

## Run
To start the bot, simply run the `bot.py`

If you require any help, feel free to contact me through the LiteTech discord server.
    
