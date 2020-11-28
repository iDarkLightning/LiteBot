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
        rcon = self.client.rcons[server_name.lower()]['rcon']
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
