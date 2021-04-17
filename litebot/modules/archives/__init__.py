from . import archive_command

def setup(bot):
    bot.add_cog(archive_command.ArchiveCommand(bot))