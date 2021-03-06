import asyncio
import datetime
from pathlib import Path

import aiohttp

import asyncpg
import toml
import twitchio
from twitchio.ext import commands
from utility import logging
from typing import Any, MutableMapping


class Bot(commands.Bot):
    def __init__(self, loop=None, **kwargs):

        loop = loop or asyncio.get_event_loop()

        super().__init__(loop=loop, **kwargs)

        self.aiohttp_session = None
        self.db = self.database = self.database_connection_pool = None
        self.connected_to_database = asyncio.Event()
        self.connected_to_database.set()
        loop.run_until_complete(self.initialize_database())
        for file in Path('cogs').iterdir():
            if file.with_suffix('.py').is_file():
                self.load_module('cogs.' + file.name[:-3])

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
                message             TEXT
            )
            """)
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS twitch.users (
                user_id             INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                channel             TEXT NOT NULL,
                username            TEXT NOT NULL,
                unique              (channel, username)
            )
            """)
        # keep here or in points cog?
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS twitch.points (
                user_id             INT UNIQUE NOT NULL,
                points              INT,
                FOREIGN KEY         (user_id) REFERENCES twitch.users (user_id) ON DELETE CASCADE
            )
            """)
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS twitch.commands (
                channel             TEXT,
                command             TEXT,
                message             TEXT,
                PRIMARY KEY         (channel, command)
            )
            """)

    async def event_ready(self):
        'Called once when bot enters the chat.'
        print(f"{self.nick} is here!")
        # await self.set_rolling_message()
        if not self.aiohttp_session:
            self.aiohttp_session = aiohttp.ClientSession(loop=self.loop)

    async def event_join(self, user):
        'Adds all users to the database and adds starting points'
        # Todo check on how well this scales? should i keep the points adding here?
        # print(type(user))
        username = str(user.name).strip()
        channel = str(user.channel)

        if username != self.nick:
            already_exists: int = await self.db.fetchval(
                """
            SELECT user_id FROM twitch.users
            WHERE username = $1 AND channel = $2
                """,
                username, channel)
            if not already_exists:
                await self.db.execute(
                    """
                    INSERT INTO twitch.users (username, channel)
                    VALUES ($1, $2)
                    ON CONFLICT (username, channel)
                    DO NOTHING
                    """,
                    username, channel)
                await self.db.execute(
                    """
                    INSERT INTO twitch.points (points, user_id)
                    VALUES (1000, (
                        SELECT user_id
                        FROM twitch.users
                        WHERE username = $1 and channel = $2 ))
                    """,
                    username, channel)

    async def event_message(self, message):
        'Lets try to store all messages'
        await self.db.execute(
            """
            INSERT INTO twitch.messagelog (timestamp, channel, author, message)
            VALUES ($1, $2, $3, $4)
            """,
            datetime.datetime.now(), message.channel.name, message.author.name, message.content)

        'Always run on all messages'
        if message.author.name.casefold() == self.nick.casefold():
            return
        # allows for loading in custom class for context,
        # probably not gonna be needed, but leaving the option open.
        ctx = await self.get_context(message, cls=twitchio.Context)

        await self.handle_commands(message, ctx=ctx)

        if 'hello' in ctx.content.casefold():
            await ctx.channel.send(f"Hi, @{ctx.author.name}!")

    async def event_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"That isn't a valid command @{ctx.author.name}")

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'Your command is missing an argument @{ctx.author.name}')
        else:
            logging.twitchio_logger.error(f'[{ctx.channel.name}] {error}')

    async def event_raw_data(self, data):
        logging.raw_data_logger.info(data)

    @commands.command(aliases=('so', 'shoutout'))
    async def shoutouts(self, ctx, username: str) -> None:
        if ctx.author.is_mod == 1:
            await ctx.send(f'This is a shoutout to another fun and awesome streamer, https://www.twitch.tv/{username}')

    @commands.command(name='test')
    async def test(self, ctx):
        await ctx.send('Test Command')


if __name__ == '__main__':

    params: MutableMapping[str, Any] = toml.load('config.toml')
    bot = Bot(prefix='!', **params['botconf'])
    bot.run()
