import asyncio
import datetime

from twitchio.ext import commands


@commands.cog()
class Pathofexile:
    def __init__(self, bot):
        self.bot = bot

    async def event_ready(self):
        print('poe.cog loaded')
        #might move this elsewhere, or change table structure
        await self.bot.db.execute("CREATE SCHEMA IF NOT EXISTS poe")

        await self.bot.db.execute(
                """
                CREATE TABLE IF NOT EXISTS poe.currency (
                timestamp       TIMESTAMPTZ PRIMARY KEY DEFAULT NOW(),
                league          TEXT,
                name            TEXT,
                base_type       TEXT,
                chaosvalue      INT
                )
                """
            )
        #await self.get_cur([4,5])
    @commands.command(aliases= ('price','cprice'))
    async def get_currency_price(self, ctx, name:str, league:str='Delirium'):
        league = league.lstrip()
        print(name, league)
        value = list(await self.bot.db.fetchrow(
            """
            SELECT name, chaosvalue  FROM poe.currency
            WHERE lower(league) = $1 and lower(name) = $2 
            order by timestamp desc
            """,
            league.lower(), name.lower()
        ))
        #await self.
        #url = 'Placeholder'
        #Todo add a pathofexiletrade link for the itemm, ran through tinyurl or equiv to save space on link.
        #ctx.send(f'{detailed_name} current average value is {value} Chaos Orbs. Here is a link to pathofexiletrade shortened by tinyurl {url}')

    async def get_leagues(self, league_ids:list):
        """
        param: league_ids:: takes a list of 1 or more of these numbers 0 = Standard, 1 = Hardcore, 4= Temp, 5 = Hardcore Temp
        """
        url = 'http://api.pathofexile.com/leagues'
        async with self.bot.aiohttp_session.get(url) as resp:
            league = await resp.json()
            #Returns based on ids and list comprehension
            return [league[x]['id'] for x in league_ids]
    #async def get_api_data(self, league:list, overview:str, types:list):
        #league = [4,5]
        #overview = 'currencyoverview'
        #types = []
        # url = f'https://poe.ninja/api/data/{overview}?'
        # params = {'league':, 'type': }
        # with self.bot.aiohttp_session(url, params=params) as resp:
            


    async def get_cur(self, league_ids:list):
        """
        param: league_ids:: takes a list of numbers
        0 = Standard, 1 = Hardcore, 4= Temp, 5 = Hardcore Temp
        """
        league = await self.get_leagues(league_ids)
        types = ['Currency', 'Fragment', 'Oil', 'Incubator', 'Scarab', 'Fossil', 'Resonator', 
        'Essence', 'DivinationCard', 'Prophecy', 'BaseType', 'UniqueMap', 'Map', 'UniqueJewel', 
        'UniqueFlask', 'UniqueWeapon', 'UniqueArmour', 'UniqueAccessory']
        base = ['currencyoverview', 'itemoverview']
        while True:
            for i in league:
                for x in base:
                    for y in types:
                        #stops inherently faulty requests, before sending them
                        if x == base[0] and y != types[0] and y != types[1]:
                            continue
                        elif x == base[1] and y == types[0] or x == base[1] and y == types[1]:
                            continue
                        
                        url = f'https://poe.ninja/api/data/{x}?'
                        params = {'league':i, 'type': y}
                        async with self.bot.aiohttp_session.get(url, params=params) as resp:
                            print(resp.status , i, x ,y)
                            assert resp.status == 200
                                #todo add loggging of errors instead of just skipping over?
                                # continue
                            currencies = await resp.json()
                            for t in currencies['lines']:  
                                base_type = 'None'                      
                                if x == base[0]:
                                    if t['chaosEquivalent'] > 50:
                                        await self.bot.db.execute(
                                            """
                                            INSERT INTO poe.currency (timestamp, league, name, base_type, chaosvalue)
                                            VALUES ($1, $2, $3, $4, $5)
                                            """,
                                            datetime.datetime.now(), i, t['currencyTypeName'], base_type, t['chaosEquivalent']
                                        )
                                elif x == base[1]:
                                    if t['chaosValue'] > 50:
                                        
                                        #if t['baseType']:
                                        #    base_type = t['baseType'] 
                                        await self.bot.db.execute(
                                            """
                                            INSERT INTO poe.currency (timestamp, league, name, base_type, chaosvalue)
                                            VALUES ($1, $2, $3, $4, $5)
                                            """,
                                            datetime.datetime.now(), i, t['name'], t['baseType'], t['chaosValue']
                                        )
            await asyncio.sleep(7200)

    #async def trade_url(self, name:str, base:str = None):
    #    build query here or take it as a parameter?





    # async def get_tiny_url(self, trade:str):
    #     url = 'http://tinyurl.com/api-create.php?'
        


# #To do add in aiohttp for using poe.ninja and pathofexile api for grabbing currency information
# #then storing the data somehow, psql? or keyvalue? or other ideas

        
#         await self.bot.db.execute(
#             """CREATE TABLE IF NOT EXISTS poe.fragment
#             timestamp       TIMESTAMPZ DEFAULT NOW(),
#             name            TEXT PRIMARY KEY,
#             chaosvalue      INT
#             """
#         )
        
#         await self.bot.db.execute(
#             """CREATE TABLE IF NOT EXISTS poe.deliriumorb
#             timestamp       TIMESTAMPZ DEFAULT NOW(),
#             name            TEXT PRIMARY KEY,
#             chaosvalue      INT

#             """
#         )
#         await self.bot.db.execute(
#             """CREATE TABLE IF NOT EXISTS poe.watchstone
#             timestamp       TIMESTAMPZ DEFAULT NOW(),
#             name            TEXT PRIMARY KEY,
#             chaosvalue      INT
#             """
#         )
#         await self.bot.db.execute(
#             """CREATE TABLE IF NOT EXISTS poe.oil
#             timestamp       TIMESTAMPZ DEFAULT NOW(),
#             name            TEXT PRIMARY KEY,
#             chaosvalue      INT
#             """
#         )
#         await self.bot.db.execute(
#             """CREATE TABLE IF NOT EXISTS poe.incubator
#             timestamp       TIMESTAMPZ DEFAULT NOW(),
#             name            TEXT PRIMARY KEY,
#             chaosvalue      INT
#             """
#         )
#         await self.bot.db.execute(
#             """CREATE TABLE IF NOT EXISTS poe.scarab
#             timestamp       TIMESTAMPZ DEFAULT NOW(),
#             name            TEXT PRIMARY KEY,
#             chaosvalue      INT
#             """
#         )
#         await self.bot.db.execute(
#             """CREATE TABLE IF NOT EXISTS poe.fossil
#             timestamp       TIMESTAMPZ DEFAULT NOW(),
#             name            TEXT PRIMARY KEY,
#             chaosvalue      INT
#             """
#         )
#         await self.bot.db.execute(
#             """CREATE TABLE IF NOT EXISTS poe.resonator
#             timestamp       TIMESTAMPZ DEFAULT NOW(),
#             name            TEXT PRIMARY KEY,
#             chaosvalue      INT
#             """
#         )
#         await self.bot.db.execute(
#             """CREATE TABLE IF NOT EXISTS poe.essence
#             timestamp       TIMESTAMPZ DEFAULT NOW(),
#             name            TEXT PRIMARY KEY,
#             chaosvalue      INT
#             """
#         )
#         #might add stack size to divinationcard table
#         await self.bot.db.execute(
#             """CREATE TABLE IF NOT EXISTS poe.divinationcard
#             timestamp       TIMESTAMPZ DEFAULT NOW(),
#             name            TEXT PRIMARY KEY,
#             chaosvalue      INT
#             """
#         )
#         await self.bot.db.execute(
#             """CREATE TABLE IF NOT EXISTS poe.prophecy
#             timestamp       TIMESTAMPZ DEFAULT NOW(),
#             name            TEXT PRIMARY KEY,
#             chaosvalue      INT
#             """
#         )
#         #Potentially 
#         await self.bot.db.execute(
#             """CREATE TABLE IF NOT EXISTS poe.skillgem
#             timestamp       TIMESTAMPZ DEFAULT NOW(),
#             name            TEXT PRIMARY KEY,
#             chaosvalue      INT
#             """
#         )
#         #Low confidence data, harder to evaluate
#         await self.bot.db.execute(
#             """CREATE TABLE IF NOT EXISTS poe.enchant
#             timestamp       TIMESTAMPZ DEFAULT NOW(),
#             name            TEXT PRIMARY KEY,
#             chaosvalue      INT
#             """
#         )
#         await self.bot.db.execute(
#             """CREATE TABLE IF NOT EXISTS poe.uniquemap
#             timestamp       TIMESTAMPZ DEFAULT NOW(),
#             name            TEXT PRIMARY KEY,
#             chaosvalue      INT
#             """
#         )
#         await self.bot.db.execute(
#             """CREATE TABLE IF NOT EXISTS poe.map
#             timestamp       TIMESTAMPZ DEFAULT NOW(),
#             name            TEXT PRIMARY KEY,
#             chaosvalue      INT
#             """
#         )
#         await self.bot.db.execute(
#             """CREATE TABLE IF NOT EXISTS poe.uniquejewel
#             timestamp       TIMESTAMPZ DEFAULT NOW(),
#             name            TEXT PRIMARY KEY,
#             chaosvalue      INT
#             """
#         )
#         await self.bot.db.execute(
#             """CREATE TABLE IF NOT EXISTS poe.uniqueflask
#             timestamp       TIMESTAMPZ DEFAULT NOW(),
#             name            TEXT PRIMARY KEY,
#             chaosvalue      INT
#             """
#         )
#         await self.bot.db.execute(
#             """CREATE TABLE IF NOT EXISTS poe.uniqueweapon
#             timestamp       TIMESTAMPZ DEFAULT NOW(),
#             name            TEXT PRIMARY KEY,
#             chaosvalue      INT
#             """
#         )
#         await self.bot.db.execute(
#             """CREATE TABLE IF NOT EXISTS poe.uniquearmor
#             timestamp       TIMESTAMPZ DEFAULT NOW(),
#             name            TEXT PRIMARY KEY,
#             chaosvalue      INT
#             """
#         )
#         await self.bot.db.execute(
#             """CREATE TABLE IF NOT EXISTS poe.uniuqacc
#             timestamp       TIMESTAMPZ DEFAULT NOW(),
#             name            TEXT PRIMARY KEY,
#             chaosvalue      INT
#             """
#         )
#         await self.bot.db.execute(
#             """CREATE TABLE IF NOT EXISTS poe.beast
#             timestamp       TIMESTAMPZ DEFAULT NOW(),
#             name            TEXT PRIMARY KEY,
#             chaosvalue      INT
#             """
#         )
#         await self.bot.db.execute(
#             """CREATE TABLE IF NOT EXISTS poe.vial
#             timestamp       TIMESTAMPZ DEFAULT NOW(),
#             name            TEXT PRIMARY KEY,
#             chaosvalue      INT
#             """
#         )
