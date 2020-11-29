from utils.utils import *


class DiscordManagement(commands.Cog):

    @commands.command(brief="`clear <number>` deletes the last <number> messages sent in the channel")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, message_count=5):
        await ctx.channel.purge(limit=message_count+1)