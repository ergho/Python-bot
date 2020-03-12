
import asyncio
import asyncpg
import datetime
import os

from twitchio.ext import commands
from config import config


class Bot(commands.Bot):
    def __init__(self, loop = None, initial_channels = None, **kwargs):

        if initial_channels is None:
            initial_channels = []
        initial_channels = initial_channels.split(' ')
        loop = loop or asyncio.get_event_loop()
        super().__init__(loop = loop, initial_channels = initial_channels, **kwargs)

        for file in sorted(os.listdir('cogs')):
            if file.endswith('.py'):
                self.load_module('cogs.' + file[:-3])
        
        self.db = self.database = self.database_connection_pool = None
        self.connected_to_database = asyncio.Event()
        self.connected_to_database.set()
        loop.run_until_complete(self.initialize_database())

    async def connect_to_database(self):
        if self.database_connection_pool:
            return
        if self.connected_to_database.is_set():
            self.connected_to_database.clear()
            params = config ('database.ini', 'postgresql')
            self.database_connection_pool = await asyncpg.create_pool(**params)

            self.db = self.database = self.database_connection_pool
            self.connected_to_database.set()

        else:
            await self.connected_to_database.wait()
    
    async def initialize_database(self):
        await self.connect_to_database()
        await self.db.execute("CREATE SCHEMA IF NOT EXISTS twitch")
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS twitch.messages (
                timestamp           TIMESTAMPTZ PRIMARY KEY DEFAULT NOW(),
                channel             TEXT,
                author              TEXT,
                message             TEXT,
                message_timestamp   TIMESTAMPTZ
            )
            """
        )
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS twitch.users (
                user_id             SERIAL PRIMARY KEY,
                channel             TEXT,
                username            TEXT
            )
            """
        )
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS twitch.points (
                user_id             INT UNIQUE NOT NULL,
                points              INT,
                FOREIGN KEY         (user_id) REFERENCES twitch.users (user_id) ON DELETE CASCADE
            )
            """
        )
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS twitch.banlist (
                user_id             INT,
                reason              TEXT,

                FOREIGN KEY         (user_id) REFERENCES twitch.users(user_id) 
            )
            """
        )

    async def add_user(self, ctx):
        users = await self.get_chatters(ctx.channel.name)
        return users

    async def event_ready(self):
        'Called once when bot enters the chat.'
        print(f"{self.nick} is here!")

    async def event_message(self, ctx):
        'Lets try to store all messages'
        await self.db.execute(
            """
            INSERT INTO twitch.messages (timestamp, channel, author, message, message_timestamp)
            VALUES ($1, $2, $3, $4, $5)
            """,
            datetime.datetime.now(), ctx.channel.name, ctx.author.name, ctx.content,
            None if ctx.echo else ctx.timestamp.replace(tzinfo = datetime.timezone.utc)
        )
        'Always run on all messages'
        if ctx.author.name.lower() == self.nick.lower():
            return

        await self.handle_commands(ctx)

        if 'hello' in ctx.content.lower():
            await ctx.channel.send(f"Hi, @{ctx.author.name}!")
    
    async def event_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"That isn't a valid command @{ctx.author.name}, use !commands to see valid commands.")
        
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'Your command is missing an argument @{ctx.author.name}')

    @commands.command()
    async def test(self, ctx):
        silly = await self.add_user(ctx)
        for name in silly.all:
            hi = await self.get_users(name)
            print(hi[0][1])
        
        print(ctx.author.is_mod == 1)

if __name__ == '__main__':

    params = config('database.ini', 'botconf')
    bot = Bot(prefix = '!', **params)
    bot.run()
