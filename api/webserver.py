from aiohttp import web
from utils.utils import *
from .endpoints import add_routes
import datetime
from datetime import datetime
from aiohttp.abc import AbstractAccessLogger
from utils import console
import jwt
from aiohttp_jwt import JWTMiddleware
from aiohttp_middlewares import cors_middleware

class AccessLogger(AbstractAccessLogger):

    def log(self, request, response, time):
        console.log(f'{request.method} request made to {request.path} done in {time}s: Status={response.status}')

class WebServer(commands.Cog):
    def __init__(self, client, port):
        self.client = client
        self.app = web.Application(middlewares=[JWTMiddleware(self.client.secret, algorithms=["HS256"]), cors_middleware(allow_all=True)])
        self.client.loop.create_task(self.init_webserver(port))

    async def init_webserver(self, port):
        add_routes(self.app, self.client)
        runner = web.AppRunner(self.app, access_log_class=AccessLogger)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", port)
        await self.client.wait_until_ready()
        await site.start()
        console.log(f"Web Server is online on Port: {port}")

    @commands.command(brief="`token` Generate a token ")
    @commands.has_permissions(administrator=True)
    async def token(self, ctx):
        token = jwt.encode(
            {
                "user": ctx.message.author.id
            },
            self.client.secret,
            algorithm="HS256"
        )

        embed = discord.Embed(title="Your Token Is", color=0xADD8E6, description=f"```ini\n[{token}]```", timestamp=datetime.utcnow())
        embed.add_field(name="Usage", value="Include the token in your headers with the `Authorization` key\n```py\n{Authorization: 'Bearer " + token + "'}```")
        embed.set_footer(text=f"Please keep this token secret. If you ever accidentally release this, please contact the bot owner to invalidate the token (change the secret)")
        await ctx.message.author.send(embed=embed)
