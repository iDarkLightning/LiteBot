from . import location_command

def setup(bot):
    bot.add_cog(location_command.LocationCommand(bot))