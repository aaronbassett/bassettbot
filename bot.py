import os  # for importing env vars for the bot to use
from twitchio.ext import commands
from tinydb import TinyDB
import spacy
from rich import print

db = TinyDB("../pups/db.json")
nlp = spacy.load("en_core_web_trf")

WORKING_ON_VERBS = ["work", "code", "build", "write", "develop", "program", "create"]


def get_total_pushups():
    reports = db.all()

    total_pushups = 0

    for report in reports:
        if report["type"] == "pushups":
            total_pushups = total_pushups + report["count"]

    return total_pushups


class BassettBot(commands.Bot):
    def __init__(self):
        super().__init__(
            irc_token=os.environ["TMI_TOKEN"],
            client_id=os.environ["CLIENT_ID"],
            nick=os.environ["BOT_NICK"],
            prefix=os.environ["BOT_PREFIX"],
            initial_channels=[os.environ["CHANNEL"]],
        )

    # Events don't need decorators when subclassed
    async def event_ready(self):
        print(f"Ready | {self.nick}")

    async def event_message(self, message):
        if message.author.name != "bassettbot":
            doc = nlp(message.content)
            verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"]

            if len(set(verbs).intersection(WORKING_ON_VERBS)) > 0:
                await message.channel.send(
                    f"Hey @{message.author.name} we are currently coding me! A Python Twitch chat bot"
                )

        await self.handle_commands(message)

    # Commands use a decorator...
    @commands.command(name="pushups")
    async def my_command(self, ctx):
        total_pushups = get_total_pushups()
        await ctx.send(
            f"@aaronbassettdev has completed {total_pushups} pushups so far this year"
        )


if __name__ == "__main__":
    bot = BassettBot()
    bot.run()


# What are you building?
# WHat are you coding?
# What is this you're working on today?