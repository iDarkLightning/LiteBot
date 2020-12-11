import discord, traceback
from discord.ext import commands

class ErrorHandling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        
        await self.generic_error_handler(ctx, error)

    async def generic_error_handler(self, ctx, error):
        if self.bot.config.get('error_handling.debug', False):
            stack_trace = ''.join(traceback.format_exception(
                type(error),
                error,
                error.__traceback__
            ))
            
            await ctx.send(embed=discord.Embed(
                title='Uh-oh!',
                description=f'''
An unknown exception occured!
```
{stack_trace}
```''',
                colour=self.bot.config.get_colour('critical_error')
            ))

        else:
            await ctx.send(embed=discord.Embed(
                title='Uh-oh!',
                description='An unknown exception occured! Please report this to the developers.',
                colour=self.bot.config.get_colour('critical_error')
            ))

            raise error

def setup(bot):
    bot.add_cog(ErrorHandling(bot))
