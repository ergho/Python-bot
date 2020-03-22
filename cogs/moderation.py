from twitchio.ext import commands
import datetime

@commands.cog()
class Moderation:
    """
    Basic moderation commands and records
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases = ('timeout',))
    async def timeout_user(self, ctx, username, duration: int, reason: str = None):
        if ctx.author.is_mod == 1:
            #to do add user to banlist in database with reason and timeout user for duration.
            pass
            await ctx.channel.timeout(username, duration, reason)
        else:
            await ctx.send('Mod only command!')

    @commands.command(aliases = ('ban',))
    async def ban_user(self, ctx, username: str, reason : str = None, duration : str = 'Permanent'):
        if ctx.author.is_mod == 1:
            print( username,'hello', reason, 'yep', duration )
            await self.bot.db.execute(
                """
                INSERT INTO twitch.banlist (timestamp, channel, username, reason, duration)
                VALUES ($1, $2, $3, $4, $5)
                """,
                datetime.datetime.now(), ctx.channel.name, username, reason, duration
            )
            print('did it')
            #to do add user to the banlist in database with reason why and ban user in chat and duration(permanent)
            await ctx.channel.ban(username, reason)
        else:
            await ctx.send('Mod only command!')

    @commands.command(aliases = ('unban',))
    async def unban_user(self, ctx, username, reason : str = ''):
        if ctx.author.is_mod == 1:
            pass
            await ctx.channel.unban(username)
        else:
            await ctx.send('Mod only command!')

    @commands.command(aliases = ('slow','slowmode'))
    async def slow_mode(self, ctx):
        if ctx.author.is_mod == 1:
            await ctx.channel.slow()
            await ctx.send('Slow mode is now active')
        else:
            await ctx.send('Mod only command!')

    @commands.command(aliases = ('slow_off', 'slowoff'))
    async def slow_mode_off(self, ctx):
        if ctx.author.is_mod == 1:
            await ctx.channek.unslow()
            await ctx.send('Slow mode is now off')
        else:
            await ctx.send('Mod only command!')
    @commands.command(aliases = ('unban',))
    async def unban_user(self, ctx, username, reason : str = ''):
        if ctx.author.is_mod == 1:
            pass
        else:
            await ctx.send('Mod only command!')