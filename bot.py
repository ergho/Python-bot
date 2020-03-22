import asyncio
import asyncpg
import datetime
import twitchio
import toml

from pathlib import Path
from twitchio.ext import commands
from config import config
from utility import logging


class Bot(commands.Bot):
    def __init__(self, loop = None, **kwargs):

        loop = loop or asyncio.get_event_loop()
        super().__init__(loop = loop, **kwargs)

        for file in Path('cogs').iterdir():
            if file.with_suffix('.py').is_file():
                self.load_module('cogs.' + file.name[:-3])
        
        self.db = self.database = self.database_connection_pool = None
        self.connected_to_database = asyncio.Event()
        self.connected_to_database.set()
        loop.run_until_complete(self.initialize_database())

    async def connect_to_database(self):
        if self.database_connection_pool:
            return
        if self.connected_to_database.is_set():
            self.connected_to_database.clear()
            self.database_connection_pool = await asyncpg.create_pool(**params['database'])

            self.db = self.database = self.database_connection_pool
            self.connected_to_database.set()

        else:
            await self.connected_to_database.wait()
    
    async def initialize_database(self):
        await self.connect_to_database()
        await self.db.execute("CREATE SCHEMA IF NOT EXISTS twitch")
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS twitch.messagelog (
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
                user_id             INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                channel             TEXT NOT NULL,
                username            TEXT NOT NULL,
                unique              (channel, username)
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
            CREATE TABLE IF NOT EXISTS twitch.commands (
                channel             TEXT,
                command             TEXT,
                message             TEXT,
                PRIMARY KEY         (channel, command)
            )
            """
        )
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS twitch.banlist (
                timestamp           TIMESTAMPTZ PRIMARY KEY DEFAULT NOW(),
                user_id             INT,
                reason              TEXT,
                duration            TEXT,
                FOREIGN KEY         (user_id) REFERENCES twitch.users(user_id) 
            )
            """
        )

    async def event_ready(self):
        'Called once when bot enters the chat.'
        print(f"{self.nick} is here!")

    async def event_join(self, user):
        'This is a possible way of making sure all users get added to the database and get an intial entry into points system, not sure how good it handles multiple users at once?'
        username = str(user.name).rstrip()
        channel = str(user.channel)
        already_exists = await self.db.fetchval(
            """
            SELECT user_id from twitch.users
            WHERE username = $1 AND channel = $2
            """,
            username, channel
        )
        if username != self.nick:
            if not already_exists:
                await self.db.execute(
                    """
                    INSERT INTO twitch.users (username, channel)
                    VALUES ($1, $2)
                    ON CONFLICT (username, channel) 
                    DO NOTHING
                    """,
                    username, channel
                )
                await self.db.execute(
                    """
                    INSERT INTO twitch.points (points, user_id)
                    VALUES (1000, (
                        SELECT user_id 
                        FROM twitch.users
                        WHERE username = $1 and channel = $2 ))
                    """,
                    username, channel
                )
        


    async def event_message(self, message):
        'Lets try to store all messages'
        await self.db.execute(
            """
            INSERT INTO twitch.messages (timestamp, channel, author, message, message_timestamp)
            VALUES ($1, $2, $3, $4, $5)
            """,
            datetime.datetime.now(), message.channel.name, message.author.name, message.content,
            None if message.echo else message.timestamp.replace(tzinfo = datetime.timezone.utc)
        )

        'Always run on all messages'
        if message.author.name.lower() == self.nick.lower():
            return
        
        ctx = await self.get_context(message, cls = twitchio.Context)

        await self.handle_commands(message, ctx=ctx)

        if 'hello' in ctx.content.lower():
            await ctx.channel.send(f"Hi, @{ctx.author.name}!")
    
    async def event_command_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(str(error).replace('`', "'").replace('<class' , '').replace('>', ''))

        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(f"That isn't a valid command @{ctx.author.name}")
        
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'Your command is missing an argument @{ctx.author.name}')

    async def event_raw_data(self, data):
        logging.raw_data_logger.info(data)
# #    @commands.check
#     def check_is_mod(ctx):
#         return ctx.author.is_mod == 1
    def is_mod(ctx):
        return ctx.author.is_mod == 1
    
    @commands.command(name='test')
    @commands.check(is_mod)
    async def test(self, ctx):
        print('Wow this worked?')


if __name__ == '__main__':

    #params = config('config.toml', 'botconf')
    params = toml.load('config.toml')
    bot = Bot(prefix = '!', **params['botconf'])
    bot.run()
