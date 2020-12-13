from utils.utils import *


class ServerCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(brief="`run <server_name> <command>` Can be used to run commands to the server")
    @perms_check('members_role')
    async def run(self, ctx, *args):
        if len(args) == 0:
            raise commands.errors.CommandInvokeError
        elif len(args) == 1:
            server_name = get_server(self.client, ctx)
            command = args[0]
        else:
            if args[0] in self.client.servers:
                server_name = args[0]
                command = (' '.join(args).partition(f'{server_name} ')[2])
            else:
                server_name = get_server(self.client, ctx)
                command = ' '.join(args)

        operator_server = self.client.servers[server_name.lower()]['operator']
        rcon_details = self.client.rcons[server_name]['rcon']
        rcon = MCRcon(rcon_details[0], rcon_details[1], rcon_details[2])
        if operator_server:
            operator_role = get(ctx.author.guild.roles, id=self.client.config['operator_role'][0])
            if operator_role in ctx.author.roles:
                response = rcon.command(f'/{command}')
                if response:
                    await ctx.send(f'''```{response}```''')
            else:
                raise commands.CheckFailure
        else:
            response = rcon.command(f'/{command}')
            if response:
                await ctx.send(f'''```{response}```''')

    @commands.command(brief="`whitelist add|remove <player_name>` Whitelists a player on all servers and OPS them where possible")
    @perms_check('operator_role')
    async def whitelist(self, ctx, action, player_name):
        whitelists = []
        ops = []
        for server in self.client.servers:
            rcon_details = self.client.rcons[server]['rcon']
            rcon = MCRcon(rcon_details[0], rcon_details[1], rcon_details[2])

            if action.lower() == "add" or "remove":
                whitelist_resp = rcon.command(f"/whitelist {action} {player_name}")
                if player_name in whitelist_resp:
                    whitelists.append(server)

            if not self.client.servers[server]["operator"]:
                if action.lower() == "add":
                    op_resp = rcon.command(f"/op {player_name}")
                    if "Nothing" not in op_resp:
                        ops.append(server)
                elif action.lower() == "remove":
                    op_resp = rcon.command(f"/deop {player_name}")
                    if "Nothing" not in op_resp:
                        ops.append(server)

        if action.lower() == "add":
            await ctx.send(f"```Whitelisted {player_name} on {len(whitelists)} servers. Oped {player_name} on {len(ops)} servers```")
        elif action.lower() == "remove":
            await ctx.send(f"```Unwhitelisted {player_name} on {len(whitelists)} servers. Deoped {player_name} on {len(ops)} servers```")



