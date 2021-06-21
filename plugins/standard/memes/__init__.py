__plugin_meta__ = {
    "name": "Memes",
    "description": "View memes from reddit meme subreddits",
    "authors": ["iDarkLightning"],
    "version": "1.0.0"
}

from asyncpraw import Reddit
from discord.ext import commands

from litebot.core import Cog
from litebot.core.context import Context
from litebot.utils import embeds, requests

USER_AGENT = f"web:idarklightning:litebot:v{__plugin_meta__['version']}"

async def is_image(url: str) -> bool:
    """
    Check's if a url is to an image
    :param url: The url to check
    :type url: str
    :return: Whether or not the URL is an image
    :rtype: bool
    """
    res = await requests.fetch(url)
    return "image" in res.headers.get("Content-Type")

class MemesCommand(Cog):
    def __init__(self) -> None:
        self.reddit_instance = None

    @Cog.setting(name="Meme Command",
                 description="Get meme postings from the given subreddits",
                 config={"client_id": "", "client_secret": "", "subreddits": ["funny", "memes"]})
    @commands.command(name="meme", aliases=["memes"])
    async def _meme(self, ctx: Context) -> None:
        """
        Fetches a meme from the r/funny or r/memes subreddit.
        """
        if not self.reddit_instance:
            self.reddit_instance = Reddit(
                                        client_id=ctx.config["client_id"],
                                        client_secret=ctx.config["client_secret"],
                                        user_agent=USER_AGENT
                                    )

        subreddit = await self.reddit_instance.subreddit("+".join(ctx.config["subreddits"]))
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

def setup(bot):
    bot.add_cog(MemesCommand)