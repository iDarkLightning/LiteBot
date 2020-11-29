from modules.discord_utils import auto_role, clear, scalable_voice

def setup(bot):
    bot.load_cog('discord_utils', auto_role.AutoRole(bot))
    bot.load_cog('discord_utils', clear.DiscordManagement(bot))
    bot.load_cog('discord_utils', scalable_voice.ScalableVoice(bot))

def config():
    discord_utils_config = {
        'auto_role_id': 1,
        'scalable_voice': {
            'category_id': 1,
            'add_channel_id': 1
        }
    }
    return discord_utils_config