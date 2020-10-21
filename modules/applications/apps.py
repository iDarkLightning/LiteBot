import gspread
import discord
import json
from discord.ext import commands, tasks
from discord.utils import get

bot = discord.Client()

with open('./modules/applications/application_config.json') as json_file:
    config = json.load(json_file)

class applications(commands.Cog):
    
    def __init__(self, bot):
        self.client = bot
        self.new_application.start()
    
    gc = gspread.service_account('./modules/applications/creds.json')
    sh = gc.open(config['spreadsheet_name'])
    worksheet = sh.get_worksheet(0)
    current_applications = len(worksheet.get_all_values())

    @commands.Cog.listener()
    async def on_ready(self):
        print("Applications are online!")
        self.guild = self.client.get_guild(config['guild_id'])
        self.voting_channel = voting_channel = discord.utils.get(self.guild.text_channels, id=config['voting_channel'])

    @tasks.loop(seconds=10)
    async def new_application(self):
        if len(self.worksheet.get_all_values()) > self.current_applications:
            print("New Application Has Been Recieved!")
            self.current_applications += 1
            application_info = self.worksheet.row_values(self.current_applications)
            questions_info = self.worksheet.row_values(1)
            await self.application_handler(application_info, questions_info)
    
    async def application_handler(self, application_info, questions_info):
        data = dict(zip(questions_info, application_info))
        channel = await self.guild.create_text_channel(name=f'{data[config["ingame_name_question"]]} application', category=self.client.get_channel(config['applications_category']))
        
        embed = discord.Embed(title=f"{data[config['ingame_name_question']]}'s application".upper(), color=0xADD8E6)
        for question in data:
            if question != 'Timestamp':
                if len(data[question]) > 1024:
                    parts = [data[question][i:i+1024] for i in range(0, len(data[question]), 1024)]
                    for i in range((len(parts))):
                        if i == 0:
                            embed.add_field(name=question, value=parts[i], inline=False)
                        elif i > 0:
                            embed.add_field(name='^ Extended', value=parts[i], inline=False)
                else:
                    if data[question]:
                        embed.add_field(name=question, value=data[question], inline=False)
        
        embed.set_footer(text=data['Timestamp'])
        message = await channel.send(embed=embed)
        await message.pin()

        discord_name = ((data[config['discord_name_question']]).partition('#'))
        user = list(filter(lambda u: u.name == discord_name[0] and u.discriminator == discord_name[2], self.guild.members))
        if user:
            await message.channel.set_permissions(user[0], read_messages=True, send_messages=True, attach_files=True)

        message = await self.voting_channel.send(embed=discord.Embed(title=f'Vote on {data[config["ingame_name_question"]]}', color=0xADD8E6))
        await message.add_reaction('\N{THUMBS UP SIGN}')
        await message.add_reaction('\N{THUMBS DOWN SIGN}')

    @commands.command(brief="`close` Closes an application channel (Execute inside channel)")
    @commands.has_permissions(administrator=True)
    async def close(self, ctx):
        if 'application' in str(ctx.message.channel):
            await ctx.message.channel.delete()
        else:
            await ctx.send(embed=discord.Embed(title='This is not an application channel', color=0xFF0000))        

def setup(bot):
    bot.add_cog(applications(bot))