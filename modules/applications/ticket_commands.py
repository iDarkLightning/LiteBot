import gspread

from utils.utils import *
import ast

class TicketCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.cursor = self.client.db.cursor()
        self.config = self.client.module_config['applications']

    @commands.command(brief='`ticket view|archive` View the application or archive the channel')
    @perms_check('members_role')
    async def ticket(self, ctx, action, num=None):
        with self.client.db:
            self.cursor.execute('SELECT * FROM apps WHERE channel_id=?', (ctx.channel.id,))
        ticket = self.cursor.fetchone()

        if not ticket and action.lower() != "create":
            await ctx.send(embed=discord.Embed(title='This is not a ticket channel', color=0xADD8E6))
            return

        if action.lower() == 'archive':
            archive_category = get(ctx.guild.channels, id=self.config['archives_category'])
            await ctx.channel.edit(category=archive_category)
            await ctx.send(embed=discord.Embed(title='This channel has been archived', color=0xADD8E6))
        elif action.lower() == 'view':
            embed_list = []
            for embed_str in ticket[3].split('|'):
                embed_dict = ast.literal_eval(embed_str)
                embed_list.append(discord.Embed.from_dict(embed_dict))
            for embed in embed_list:
                await ctx.send(embed=embed)
        elif action.lower() == 'create':
            apps = self.client.get_cog("Applications")

            try:
                answers = apps.worksheet.row_values(int(num) + 1)
                questions = apps.worksheet.row_values(1)
                await apps.create_application(answers, questions)
            except gspread.exceptions.APIError:
                await ctx.send(embed=discord.Embed(
                    title="Sorry, the process encounterd an API error, please try again",
                    color=0xFF0000
                ))