import os
import random
from twitchio.ext import commands
import arrow
from git import Repo
from pymongo import MongoClient
from rich import print


class BassettBot(commands.Bot):
    def __init__(self):
        mongodb_client = MongoClient(os.environ["DB_URL"])
        mongodb_db = mongodb_client[os.environ["DB_NAME"]]

        self.config = mongodb_db.bot.find_one({"name": os.environ["BOT_NAME"]})
        self.config["db"] = mongodb_db

        super().__init__(
            irc_token=os.environ["TMI_TOKEN"],
            client_id=os.environ["CLIENT_ID"],
            nick=self.config["bot_nickname"],
            prefix=self.config["bot_prefix"],
            initial_channels=self.config["channels"],
        )

    def _update_strip(self, light_options):
        self.config["db"].strips.update_one(
            {"_id": self.config["strip_id"]}, {"$set": light_options}
        )

    async def _output_content(self, ctx, name):
        if (content := self.config["text_content"].get(name, None)) is not None:
            await ctx.send(content)
        else:
            await ctx.send(f"Sorry I don't know anything about '{name}'")

    async def _social_url(self, ctx, name):
        if (social_url := self.config["socials"].get(name, None)) is not None:
            await ctx.send(social_url)
        else:
            await ctx.send(
                f"Hrm, I don't recognise that site. His username is probably 'aaronbassett', it is most everywhere else…"
            )

    # Events don't need decorators when subclassed
    async def event_ready(self):
        print(f"Ready | {self.config['bot_nickname']}")

    async def event_message(self, message):
        await self.handle_commands(message)

    @commands.command(name="lastcommit")
    async def lastcommit(self, ctx, repo_name=None):
        if repo_name is not None:
            if (repo_location := self.config["repos"].get(repo_name, None)) is not None:
                repo = Repo(repo_location)
                commit = repo.commit("main")
                commited_datetime = arrow.get(commit.committed_datetime)

                await ctx.send(
                    f"The last commit on {repo_name} was {commited_datetime.humanize()}: '{commit.message}'"
                )
            else:
                await ctx.send(f"I can't find a repo with the name '{repo_name}'")
        else:
            await ctx.send(
                f"You need to select a repo: {', '.join(self.config['repos'])}"
            )

    @commands.command(name="lights")
    async def lights(self, ctx, name=None, hex_color=None):
        available_light_names = ["rainbow", "ripple", "cylon", "static"]
        if name in available_light_names:
            if hex_color:
                self._update_strip({"animation": name, "hex_color": hex_color})
            else:
                self._update_strip({"animation": name})
        elif name == "speed" and hex_color:
            speed = float(hex_color)
            self._update_strip({"animation_speed": speed})
        else:
            await ctx.send(
                f"You can specify the following lights types: {', '.join(available_light_names)}. To adjust the speed use !lights speed <new speed>"
            )

    @commands.command(name="newrelic")
    async def newrelic(self, ctx):
        await self._output_content(ctx, "newrelic")

    @commands.command(name="workingon")
    async def workingon(self, ctx):
        await self._output_content(ctx, "workingon")

    @commands.command(name="keyboard")
    async def keyboard(self, ctx):
        await self._output_content(ctx, "keyboard")

    @commands.command(name="twitter")
    async def twitter(self, ctx):
        await self._social_url(ctx, "twitter")

    @commands.command(name="github")
    async def github(self, ctx):
        await self._social_url(ctx, "github")

    @commands.command(name="linkedin")
    async def linkedin(self, ctx):
        await self._social_url(ctx, "linkedin")

    @commands.command(name="instagram")
    async def instagram(self, ctx):
        await self._social_url(ctx, "instagram")

    @commands.command(name="relicans")
    async def relicans(self, ctx):
        await self._social_url(ctx, "relicans")

    @commands.command(name="cmds")
    async def cmds(self, ctx):
        print(self.commands)
        await ctx.send(
            f"Available commands: !{', !'.join(self.commands)}, {', '.join(['!theme', '!line or !highlight'])}"
        )


if __name__ == "__main__":
    bot = BassettBot()
    bot.run()