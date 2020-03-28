from twitchio.ext import commands
import datetime

@commands.cog()
class Pathofexile:
    def __init__(self, bot):
        self.bot = bot
        #self.league = await self.bot.db.execute

    async def event_ready(self):
        print('poe.cog loaded')
        #might move this elsewhere, or change table structure
        await self.bot.db.execute("CREATE SCHEMA IF NOT EXISTS poe")

        await self.bot.db.execute(
                """CREATE TABLE IF NOT EXISTS poe.store (
                timestamp       TIMESTAMPTZ PRIMARY KEY DEFAULT NOW(),
                league          TEXT,
                name            TEXT,
                detailed_name   TEXT,
                chaosvalue      INT
                )
                """
            )
        await self.get_cur([4,5])
    @commands.command(aliases= ('price',))
    async def get_currency_price(self, ctx, detailed_name:str, league:str):
        league = league.lstrip()

        value = await self.bot.db.fetchval(
            """
            SELECT chaosvalue FROM poe.currency
            WHERE league = $1 and name = $2 
            order by timestamp desc
            """,
            league, detailed_name
        )
        url = 'Placeholder'
        #Todo add a pathofexiletrade link for the itemm, ran through tinyurl or equiv to save space on link.
        ctx.send(f'{detailed_name} current average value is {value} Chaos Orbs. Here is a link to pathofexiletrade shortened by tinyurl {url}')

    async def get_leagues(self, league_ids:list):
        """
        param: league_ids:: takes a list of 1 or more of these numbers 0 = Standard, 1 = Hardcore, 4= Temp, 5 = Hardcore Temp
        """
        url = 'http://api.pathofexile.com/leagues'
        async with self.bot.aiohttp_session.get(url) as resp:
            league = await resp.json()
            #Returns based on ids and list comprehension
            return [league[x]['id'] for x in league_ids]

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
                        if x == base[1] and y == types[0] or x == base[1] and y == types[1]:
                            continue
                        url = f'https://poe.ninja/api/data/{x}?'
                        params = {'league':i, 'type': y}
                        async with self.bot.aiohttp_session.get(url, params=params) as resp:
                            if resp.status != 200:
                                #todo add loggging of errors instead of just skipping over?
                                continue
                            currencies = await resp.json()
                            for t in currencies['lines']:                        
                                if x == base[0]:
                                    if t['chaosEquivalent'] > 5:
                                        await self.bot.db.execute(
                                            """
                                            INSERT INTO poe.currency (timestamp, league, name, detailed_name, chaosvalue)
                                            VALUES ($1, $2, $3, $4 $5)
                                            """,
                                            datetime.datetime.now(), i, t['currencyTypeName'], t['detailsId'], t['chaosEquivalent']
                                        )
                                elif x == base[1]:
                                    if t['chaosValue'] > 5:
                                        await self.bot.db.execute(
                                            """
                                            INSERT INTO poe.currency (timestamp, league, name, detailed_name, chaosvalue)
                                            VALUES ($1, $2, $3, $4, $5)
                                            """,
                                            datetime.datetime.now(), i, t['name'], t['detailsId'], t['chaosValue']
                                        )
            await asyncio.sleep(3600)
    
### pasuse for now
    # async def trade_url(self):

    # async def get_tiny_url(self, trade:str):
    #     url = 'http://tinyurl.com/api-create.php?'
        


# #To do add in aiohttp for using poe.ninja and pathofexile api for grabbing currency information
# #then storing the data somehow, psql? or keyvalue? or other ideas
