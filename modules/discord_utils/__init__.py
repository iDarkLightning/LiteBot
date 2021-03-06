from modules.discord_utils import auto_role, clear, scalable_voice, list, streaming

def setup(bot):
    bot.add_cog(auto_role.AutoRole(bot))
    bot.add_cog(clear.DiscordManagement(bot))
    bot.add_cog(scalable_voice.ScalableVoice(bot))
    bot.add_cog(list.ListCommand(bot))
    bot.add_cog(streaming.Streaming(bot))

def config(bot):
    return {
        'auto_role_id': 1,
        'scalable_voice': {
            'category_id': 1,
            'add_channel_id': 1
        },
        'streaming': {
            'announcements_channel': 1,
            'streaming_role': 1,
            'to_give_roles': []
        }
    }