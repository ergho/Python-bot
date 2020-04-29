import datetime
import re

from twitchio.ext import commands
from typing import List, Dict

@commands.cog()
class Moderation:
    """
    Basic moderation commands and records
    """
    def __init__(self, bot):
        self.bot = bot
        self.allowed_users: Dict[str, List[str]] = {}
        self.banned_phrases: Dict[str, List[str]] = {}
        self.pattern = re.compile(r'[^A-Za-z0-9 ]')
        self.bot.loop.run_until_complete(self.initialize_cog())

    # async def event_message(self, ctx):
    #     #await self.parse_messages(ctx)
    #     ## add parser function
    #     if 'hello' in ctx.content:
    #         print('silly ergho')
        
    async def initialize_cog(self):
        await self.intialize_database()
        await self.set_vipusers()
        #await self.set_wordlist()
    async def intialize_database(self):
        await self.bot.db.execute(
            """
            CREATE TABLE IF NOT EXISTS twitch.banlist (
                timestamp           TIMESTAMPTZ PRIMARY KEY DEFAULT NOW(),
                channel             TEXT,
                username            TEXT,
                reason              TEXT,
                duration            TEXT
            )
            """)
        await self.bot.db.execute(
            """
            CREATE TABLE IF NOT EXISTS twitch.wordlist (
                channel             TEXT,
                word                TEXT,
                PRIMARY KEY         (channel, word)
            )
            """)
        await self.bot.db.execute(
            """
            CREATE TABLE IF NOT EXISTS twitch.vipusers (
                channel             TEXT,
                username            TEXT,
                PRIMARY KEY         (channel, username)
            )
            """)
    async def parse_messages(self, ctx) -> None:
        if ctx.author.is_mod == 1 or ctx.author.name == self.bot.nick:
            return
        message: str = self.pattern.sub('', ctx.content.casefold())
        message_list: List[str] = message.split(' ')
        for word in self.banned_phrases[ctx.channel.name]:
            if word in message_list:
                await ctx.channel.timeout(ctx.author.name , 10, "Please keep a civil language")
                
    async def add_wordlist(self, ctx,  word: str) -> None:
        pass
        await self.bot.db.execute(
            """
            INSERT INTO twitch.wordlist (channel, word)
            VALUES ($1, $2)
            ON CONFLICT (channel, word)
            DO NOTHING
            """,
            ctx.channel.name, word
        )
        await self.set_wordlist()

    async def remove_wordlist(self, ctx, word:str) -> None:
        
        await self.bot.db.execute(
            """
            DELETE FROM twitch.wordlist
            WHERE channel = $1 AND word = $2
            """,
            ctx.channel.name, word
        )
        await self.set_wordlist()

    async def set_wordlist(self) -> None:
        wordlist: List[Dict[str, str]] = await self.bot.db.fetch(
            """
            SELECT channel, word FROM twitch.wordlist
            """)
        for index in wordlist: # type: dict
            self.allowed_users[index['channel'].append(index['word'])]
    
    async def set_vipusers(self) -> None:
        vipusers: List[Dict[str, str]] = await self.bot.db.fetch(
            """
            SELECT channel, username FROM twitch.vipusers
            """)
        for index in vipusers: # type: dict
            self.allowed_users[index['channel'].append(index['username'])]

    @commands.command(aliases=('permit',))
    async def permit_link(self, ctx, username: str, duration: int = 60) -> None:
        if ctx.author.is_mod == 1:
            eval_username: str = await self.bot.db.fetchval(
                """
                SELECT username FROM twitch.users
                WHERE username = $1 AND channel = $2)
                """,
                username.casefold(), ctx.channel.name)
            if username.casefold() != eval_username:
                await ctx.send(f'@{ctx.channel.author}, check the spelling of {username}')
                return
            await self.permit_users(ctx.channel.name, username, 'permit')
            await self.bot.asyncio.sleep(duration)
            await self.permit_users(ctx.channel.name, username, 'remove')
        else:
            await ctx.send('Mod only command!')

    @commands.command(aliases=('timeout',))
    async def timeout_user(self, ctx, username: str, duration: int = 600, reason: str = None) -> None:
        if ctx.author.is_mod == 1:
            await ctx.channel.timeout(username, duration, reason)
        else:
            await ctx.send('Mod only command!')

    @commands.command(aliases=('ban',))
    async def ban_user(self, ctx, username: str, reason: str = None, duration: str = 'Permanent') -> None:
        if ctx.author.is_mod == 1:
            await self.bot.db.execute(
                """
                INSERT INTO twitch.banlist (timestamp, channel, username, reason, duration)
                VALUES ($1, $2, $3, $4, $5)
                """,
                datetime.datetime.now(), ctx.channel.name, username, reason, duration
            )
            await ctx.channel.ban(username, reason)
        else:
            await ctx.send('Mod only command!')

    @commands.command(aliases=('unban',))
    async def unban_user(self, ctx, username: str, reason: str = None) -> None:
        if ctx.author.is_mod == 1:
            await ctx.channel.unban(username)
        else:
            await ctx.send('Mod only command!')

    @commands.command(aliases=('slow', 'slowmode'))
    async def slow_mode(self, ctx) -> None:
        if ctx.author.is_mod == 1:
            await ctx.channel.slow()
            await ctx.send('Slow mode is now active')
        else:
            await ctx.send('Mod only command!')

    @commands.command(aliases=('slow_off', 'slowoff'))
    async def slow_mode_off(self, ctx) -> None:
        if ctx.author.is_mod == 1:
            await ctx.channel.unslow()
            await ctx.send('Slow mode is now off')
        else:
            await ctx.send('Mod only command!')

    async def permit_users(self, channel: str, username: str, mode: str) -> None:
        if 'permit' == mode and username not in self.allowed_users:
            self.allowed_users[channel].append(username)
        elif 'remove' == mode:
            self.allowed_users[channel].remove(username)
