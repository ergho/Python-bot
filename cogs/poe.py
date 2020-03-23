from twitchio.ext import commands


@commands.cog()
class Pathofexile:
    def __init__(self, bot):
        self.bot = bot
#To do add in aiohttp for using poe.ninja and pathofexile api for grabbing currency information
#then storing the data somehow, psql? or keyvalue? or other ideas

        