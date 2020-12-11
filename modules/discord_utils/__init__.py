from . import auto_role, discord_management, scalable_voice

def setup(bot):
    bot.cog_loader.load(auto_role.AutoRole())
    bot.cog_loader.load(discord_management.DiscordManagement())
    bot.cog_loader.load(scalable_voice.ScalableVoice())
