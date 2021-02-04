from utils import console
from utils.utils import *
import requests

class ChatBridge(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config = self.client.module_config["chatbridge"]

    @commands.Cog.listener()
    async def on_message(self, message):
        bridge_channels = [self.client.servers[server]["bridge_channel_id"] for server in self.client.servers]
        if message.author.bot or message.channel.id not in bridge_channels:
            return

        (server, *args) = [server for server in self.client.servers if self.client.servers[server]["bridge_channel_id"] == message.channel.id]

        data = {
            "userName": message.author.display_name,
            "userRoleColor": message.author.colour.value
        }

        if len(message.content) > 0:
            data["messageContent"] = message.content

        if message.attachments:
            data["attachments"] = {attachment.filename: attachment.url for attachment in message.attachments}

        headers = {"Authorization": "Bearer " + self.config["litebot_token"]}

        try:
            requests.post(self.config[server]["lta_server_address"], json=data, headers=headers)
        except Exception as e:
            console.error(f"Error when trying to send message to game {e}")