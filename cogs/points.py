from twitchio.ext import commands


@commands.cog()
class Points:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases= ('points',))
    async def check_points(self, ctx, username = None):
        
        if username is None:
            username = ctx.channel.name
        stored = await self.bot.db.fetchval(
            """
            SELECT points 
            FROM twitch.points  
            WHERE user_id = (
                select user_id 
                from twitch.users where
                username = $1 and channel = $2)
            """,
            username, ctx.channel.name
        )

        if stored:
            await ctx.send(f'{username} have {stored} points @{ctx.author.name}')
        else:
            await ctx.send(f'{username} have yet to get any points @{ctx.author.name}')

    @commands.command(aliases = ('a_points', 'adding_points'))
    async def add_points(self, ctx, amount:int, username):
        #check = await self.bot.is_mod(ctx)
        if ctx.author.is_mod == 1:
            await self.bot.db.execute(
                """
                INSERT INTO twitch.points (points, user_id)
                VALUES ($1, (
                    SELECT user_id 
                    FROM twitch.users 
                    WHERE username = $2 and channel = $3))
                ON CONFLICT (user_id) DO
                UPDATE SET points = twitch.points.points + $1
                """,
                amount, username, ctx.channel.name
            )
        else:
            await ctx.send('Mod only command!')

    @commands.command()
    async def bulk_add_points(self, ctx, amount:int):
        if ctx.author.is_mod == 1:
            users = await self.bot.get_chatters(ctx.channel.name)
            for name in users.all:
                await self.bot.db.execute(
                    """
                    INSERT INTO twitch.points (points, user_id)
                    VALUES ($1, (
                        SELECT user_id 
                        FROM twitch.users 
                        WHERE username = $2 and channel = $3))
                    ON CONFLICT (user_id) DO
                    UPDATE SET points = twitch.points.points + $1
                    """,
                    amount, name, ctx.channel.name
                )
        else:
            return

    @commands.command(name='r_points')
    async def remove_points(self, ctx, amount:int, username):
        
        stored = await self.bot.db.fetchval(
            """
            SELECT p.points 
            FROM twitch.points as p 
            RIGHT JOIN twitch.users as u 
            ON p.user_id = u.user_id 
            WHERE u.username = $1

            """,
            username
        )

        if amount > stored:
            stored = 0
        else:
            stored = stored - amount

        await self.bot.db.execute(
            """
            UPDATE twitch.points
            SET points = $1
            WHERE user_id = (
                SELECT user_id FROM twitch.users WHERE username = $2
            )
            """,
            stored, username
        )
        await ctx.send(f'{username}, now has {stored} points @{ctx.author.name}')
