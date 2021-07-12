from datetime import datetime

from litebot.utils.embeds import InfoEmbed


class VoteResultsEmbed(InfoEmbed):
    def __init__(self, action, application, config, votes):
        total = sum(votes.values())
        yes_votes = votes[config["vote_yes_emoji"]]
        no_votes = votes[config["vote_no_emoji"]]

        try:
            yes_amount = round((yes_votes / total) * 10)
            no_amount = round((no_votes / total) * 10)
        except ZeroDivisionError:
            yes_amount = 0
            no_amount = 0

        description = f"Vote Results: {':blue_square:' * yes_amount}{':red_square:' * no_amount}" if yes_amount or no_amount else ""

        super().__init__("", description=description, timestamp=datetime.utcnow())
        self.set_author(name=f"Vote Results for {application.name}")
        self.add_field(name="Result", value=action)
        self.add_field(name=f"{config['vote_yes_emoji']} Votes:", value=yes_votes, inline=False)
        self.add_field(name=f"{config['vote_no_emoji']} Votes:", value=no_votes, inline=False)