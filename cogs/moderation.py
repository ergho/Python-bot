import datetime

from twitchio.ext import commands


@commands.cog()
class Moderation:
    """
    Basic moderation commands and records
    """
    def __init__(self, bot):
        self.bot = bot
        self.allowed_users = []

    async def event_message(self, ctx):
        print('hi')

    @commands.command(aliases=('permit',))
    async def permit_link(self, ctx, username: str, duration: int = 60):
        if ctx.author.is_mod == 1:
            eval_username = await self.bot.db.fetchval(
                """
                SELECT username FROM twitch.users
                WHERE username = $1 AND channel = $2)
                """,
                username.lower(), ctx.channel.name)
            if username != eval_username:
                await ctx.send(f"@{ctx.channel.author}, check the spelling of {username}")
                return
            await self.permit_users(username, 'permit')
            await self.bot.asyncio.sleep(duration)
            await self.permit_users(username, 'remove')
        else:
            await ctx.send('Mod only command!')

    @commands.command(aliases=('timeout',))
    async def timeout_user(self, ctx, username: str, duration: int = 600, reason: str = None):
        if ctx.author.is_mod == 1:
            # to do add user to banlist in database with reason and timeout user for duration.
            await ctx.channel.timeout(username, duration, reason)
        else:
            await ctx.send('Mod only command!')

    @commands.command(aliases=('ban',))
    async def ban_user(self, ctx, username: str, reason: str = None, duration: str = 'Permanent'):
        if ctx.author.is_mod == 1:
            await self.bot.db.execute(
                """
                INSERT INTO twitch.banlist (timestamp, channel, username, reason, duration)
                VALUES ($1, $2, $3, $4, $5)
                """,
                datetime.datetime.now(), ctx.channel.name, username, reason, duration
            )
            # to do add user to the banlist in database with reason why and ban user in chat and duration(permanent)
            await ctx.channel.ban(username, reason)
        else:
            await ctx.send('Mod only command!')

    @commands.command(aliases=('unban',))
    async def unban_user(self, ctx, username: str, reason: str = None):
        if ctx.author.is_mod == 1:
            await ctx.channel.unban(username)
        else:
            await ctx.send('Mod only command!')

    @commands.command(aliases=('slow', 'slowmode'))
    async def slow_mode(self, ctx):
        if ctx.author.is_mod == 1:
            await ctx.channel.slow()
            await ctx.send('Slow mode is now active')
        else:
            await ctx.send('Mod only command!')

    @commands.command(aliases=('slow_off', 'slowoff'))
    async def slow_mode_off(self, ctx):
        if ctx.author.is_mod == 1:
            await ctx.channek.unslow()
            await ctx.send('Slow mode is now off')
        else:
            await ctx.send('Mod only command!')

    @commands.command(aliases=('unban',))
    async def unban_user(self, ctx, username: str, reason: str = None):
        if ctx.author.is_mod == 1:
            pass
        else:
            await ctx.send('Mod only command!')

    async def permit_users(self, username: str, mode: str):
        if 'permit' == mode:
            self.allowed_users.append(username)
        elif 'remove' == mode:
            self.allowed_users.remove(username)
