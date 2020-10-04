# Commands

Documentation for all the commands that the bot can perform

## Server Status
`status <server_name>` will return the status of the server including players online inside an embed

## Server Commands
`run <server_name> <command>` will execute a command on the server. Requires the `Operator` tag in the `config.json` to be `False` or for the user to have the specified `server-op` role. 

## Server TPS
`tps <server_name>` will return the server's TPS and MSPT.

**Aliases:** `mspt`

## Backup Command
`backup <server_name>` `[create]` will create a backup of the server's world file inside the specified backups directory. `[list]` will list all the available backups within the backups directory. Requires `server-op` role.

## Scoreboard Command
`scoreboard <objective>` will create an image of the ingame scoreboard associated to that objective, for all whitelisted players from the specified server. It will also get the total value from all scores. 

`scoreboard <objective> --all` Will return the same image for all players that have ever logged in to the server instead of just whitelisted players.

**Aliases:** `sb`

## Clear Command
`clear <number>` will delete the last `<number>` messages from chat. Requires `manage-messages` permission.

## Bot Management
`load <cog_name>` will load a module, the `<cog_name>` is the name of the `.py` folder inside of the `commands` directory. Requires `administrator` permission.
`unload <cog_name>` will unload a module, the `<cog_name>` is the name of the `.py` folder inside of the `commands` directory. Requires `administrator` permission.
`reload <cog_name>` will reload a module, the `<cog_name>` is the name of the `.py` folder inside of the `commands` directory. Requires `administrator` permission.

