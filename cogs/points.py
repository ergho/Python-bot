from twitchio.ext import commands

@commands.cog()
class Points:
    def __init__(self, bot):
        self.bot = bot
    #todo, maybe add something to do with the points?
    #todo, move the points adding and create database here rather than main cog?
    @commands.command(aliases= ('points',))
    async def check_points(self, ctx, username: str = None):
        if username is None:
            username = ctx.author.name
        points = await self.get_points(ctx, username)
        if points:
            await ctx.send(f'{username} have {points} points @{ctx.author.name}')
        else:
            await ctx.send(f'{username} have yet to get any points @{ctx.author.name}')

    @commands.command(aliases = ('a_points', 'adding_points'))
    async def add_points(self, ctx, amount:int, username: str):
        if ctx.author.is_mod == 1:
            await self.modify_points(ctx, points, username, 'add')
            await ctx.send(f'{username} now have {points} points.')
        else:
            await ctx.send('Mod only command!')

    @commands.command(aliases = ('add_all',))
    async def bulk_add_points(self, ctx, amount:int):
        if ctx.author.is_mod == 1:
            users = await self.bot.get_chatters(ctx.channel.name)
            for name in users.all:
                await self.modify_points(ctx, points, name, 'add')
            await ctx.send(f'Added {amount} points to everyone in chat !')
        else:
            await ctx.send('Mod only command!')

    @commands.command(aliases = ('r_points',))
    async def remove_points(self, ctx, amount:int, username:str):
        if ctx.author.is_mod == 1:
            await self.modify_points(ctx, points, username, 'sub')
            await ctx.send(f'{username}, now have {points} points @{ctx.author.name}')
    
    async def get_points(self, ctx, username:str):
        #To do consider using joins rather than subquery,
        #  might lower readability for little to no  benefit?
        points = await self.bot.db.fetchval(
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
        return points
    
    async def modify_points(self, ctx, amount:int, username:str, modify:str):
        
        points = await self.get_points(ctx, username)

        if modify.lower() == 'add':
            points = points + amount
        elif modify.lower == 'sub':
            if amount > points:
                points = 0
            else:
                points = points - amount
        
        await self.bot.db.execute(
            """
            UPDATE twitch.points
            SET points = $1
            WHERE user_id = (
                SELECT user_id FROM twitch.users WHERE username = $2 and channel = $3
            )
            """,
            amount, username, ctx.channel.name
        )