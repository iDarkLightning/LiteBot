from asyncpraw import Reddit
from discord.ext import commands
from litebot.errors import ChannelNotWhitelisted
from litebot.litebot import LiteBot
from litebot.utils import embeds
from litebot.utils.misc import is_image, check_role

USER_AGENT = f"web:idarklightning:litebot:v{LiteBot.VERSION}"
SUBREDDIT = "funny+memes"

class MemesCommand(commands.Cog):
    def __init__(self, bot: LiteBot) -> None:
        self.bot = bot
        self.config = self.bot.module_config["fun_features"]["config"]
        self.reddit_instance = Reddit(
            client_id=self.config["reddit"]["client_id"],
            client_secret=self.config["reddit"]["client_secret"],
            user_agent=USER_AGENT
        )

    @commands.command(name="meme", aliases=["memes"])
    async def _meme(self, ctx: commands.Context) -> None:
        """
        Fetches a meme from the r/funny or r/memes subreddit.
        """
        subreddit = await self.reddit_instance.subreddit(SUBREDDIT)
        meme = None

        while not meme:
            post = await subreddit.random()
            if post.is_self:
                continue

            if post.over_18 and not ctx.channel.is_nsfw():
                continue

            if await is_image(post.url):
                meme = post

        await ctx.send(embed=embeds.InfoEmbed(meme.title).set_image(url=meme.url))

    async def cog_before_invoke(self, ctx: commands.Context) -> None:
        """
        Runs before any command in this cog is invoked.
        Checks if the channel that the command is being invoked in is whitelisted, or if the user is an operator.
        :param ctx: The context that the command is being invoked in
        :type ctx: commands.Context
        :raises: ChannelNotWhitelisted
        """
        if (not check_role(ctx.author, self.bot.config["operators_role"])) and ctx.channel.id not in self.config["whitelisted_channels"]:
            raise ChannelNotWhitelisted

    async def cog_command_error(self, ctx: commands.Context, error: Exception) -> None:
        """
        Handles all errors that may occur for commands in this cog
        :param ctx: The context that the command is being invoked in
        :type ctx: commands.Context
        :param error: The error produced
        :type error: Exception
        """
        if isinstance(error, ChannelNotWhitelisted):
            pass
