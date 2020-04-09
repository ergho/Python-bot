import asyncio
import datetime
import random

from twitchio.ext import commands


@commands.cog()
class Pathofexile:
    def __init__(self, bot):
        self.bot = bot

    async def event_ready(self):
        await self.initialize_database_poe()

    async def initialize_database_poe(self):

        # might move this elsewhere, or change table structure
        await self.bot.db.execute(
            """
            CREATE SCHEMA IF NOT EXISTS poe
            """
            )
        
        await self.bot.db.execute(
            """
            CREATE EXTENSION IF NOT EXISTS pg_trgm
            WITH SCHEMA poe
            """
            )

        await self.bot.db.execute(
                """
                CREATE TABLE IF NOT EXISTS poe.currency (
                timestamp       TIMESTAMPTZ PRIMARY KEY DEFAULT NOW(),
                league          TEXT,
                name            TEXT,
                base_type       TEXT,
                details_id      TEXT,
                chaosvalue      INT
                )
                """
            )
        await self.get_cur([4,5])

    async def get_leagues(self, league_ids: list):
        """
        param: league_ids: takes a list of 1 or more numbers
        0 = Standard, 1 = Hardcore, 4= Temp, 5 = Hardcore Temp
        """
        url = 'https://api.pathofexile.com/leagues'
        async with self.bot.aiohttp_session.get(url) as resp:
            league = await resp.json()
            return [league[x]['id'] for x in league_ids]
## todo double check bugfix to see if the error to database is gone weird base types on wrong items!
    async def get_currency_from_api(self, league_ids: list, base: str, types: list, price_types: str, name_types: str):
        url = f'https://poe.ninja/api/data/{base}?'
        for ids in league_ids:
            for item in types:
                params = {'league': ids, 'type': item}
                api_response = await self.get_json(url, **params)
                if api_response == 0:
                    print("There's been an error")
                    continue
                for entry in api_response['lines']:
                    base_type = 'None'
                    if 'baseType' in entry:
                        if entry['baseType']:
                            base_type = entry['baseType']
                    # else:
                    #      base_type = 'None'                          
                    if entry[price_types] > 50:
                        await self.bot.db.execute(
                            """
                            INSERT INTO poe.currency (timestamp, league, name, base_type, details_id, chaosvalue)
                            VALUES ($1, $2, $3, $4, $5, $6)
                            """,
                            datetime.datetime.now(), ids, entry[name_types], base_type, entry['detailsId'], entry[price_types]
                            )
    async def get_json(self, url: str, amount_of_tries: int=5, **parameters:dict):
        api_response = None
        tries = 0
        delay = 0
        if len(parameters) == 0:
            parameters = None
        while api_response is None and tries < amount_of_tries:
            try:
                async with self.bot.aiohttp_session.get(url, params=parameters) as resp:
                    resp.raise_for_status()
                    api_response = await resp.json()
            except Exception as e:
                tries += 1
                delay = 2 ** tries + 1
                await asyncio.sleep(delay)
        if api_response is None:
            return 0
        return api_response
    
    async def get_cur(self, league_ids: list):
        """
        param: league_ids:: takes a list of numbers
        0 = Standard, 1 = Hardcore, 4= Temp, 5 = Hardcore Temp
        """
        league = await self.get_leagues(league_ids)
        currency_types = ['Currency', 'Fragment']
        item_types = ['Oil', 'Incubator', 'Scarab','Fossil', 'Resonator',
                      'Essence', 'DivinationCard', 'Prophecy', 'BaseType',
                      'UniqueMap', 'Map', 'UniqueJewel', 'UniqueFlask',
                      'UniqueWeapon', 'UniqueArmour', 'UniqueAccessory']
        price_types = ['chaosEquivalent', 'chaosValue']
        base = ['currencyoverview', 'itemoverview']
        name_types = ['currencyTypeName', 'name']
        while True:
            delay = random.randrange(3500, 3800)

            await self.get_currency_from_api(league, base[0], currency_types, price_types[0], name_types[0])
            await self.get_currency_from_api(league, base[1], item_types, price_types[1], name_types[1])

            await asyncio.sleep(delay)

    @commands.command(aliases=('price', 'cprice'))
    async def get_currency_price(self, ctx, item_name: str, league: str = 'Delirium'):
        league = league.lstrip()
        check_league = await self.get_leagues([4,5])
        if league not in check_league:
            await ctx.send(f'@{ctx.author.name} please check your request and make sure you are using one of the temporary leagues.')
            return

        value = dict(await self.bot.db.fetchrow(
        """
        SELECT name, chaosvalue, base_type, poe.similarity(details_id, $1)  FROM poe.currency
        WHERE lower(league) = $2
        order by similarity desc, timestamp desc
        """,
        item_name, league.lower()
        ))
        # url = 
        # query = 
        # await get_json(url, **parameters)
        if value.get('similarity') < 0.3:
            await ctx.send(f'@{ctx.author.name}, There is no item matching closely enough with your request with an estimated value of 50 chaos above.')
            return
        print(type(value))
        print(value)
    
        await ctx.send(f'@{ctx.author.name}, {value.get("name")} current value in chaos {value.get("chaosvalue")}, placeholder for trade site link of item.')
        
        
        # await self.
        # url = 'Placeholder'
        # Todo add a pathofexiletrade link for the itemm, ran through tinyurl
        # or equiv to save space on link.
        # ctx.send(f'{detailed_name} current average value is {value}
        # Chaos Orbs. Here is a link to pathofexiletrade shortened
        # by tinyurl {url}')
        # for i in league:
        #     for x in base:
        #         for y in types:
        #             # stops inherently faulty requests, before sending them
        #             if x == base[0] and y != types[0] and y != types[1]:
        #                 continue
        #             elif x == base[1] and y == types[0] or x == base[1] and y == types[1]:
        #                 continue

        #             url = f'https://poe.ninja/api/data/{x}?'
        #             params = {'league': i, 'type': y}
        #             async with self.bot.aiohttp_session.get(url, params=params) as resp:
        #                 print(resp.status, i, x, y)
        #                 assert resp.status == 200
        #                 # todo add loggging of errors instead of just skipping over?
        #                 # continue
        #                 currencies = await resp.json()
        #                 for t in currencies['lines']:
        #                     base_type = 'None'
        #                     if x == base[0]:
        #                         if t['chaosEquivalent'] > 50:
        #                             await self.bot.db.execute(
        #                                 """
        #                                 INSERT INTO poe.currency (timestamp, league, name, base_type, chaosvalue)
        #                                 VALUES ($1, $2, $3, $4, $5)
        #                                 """,
        #                                 datetime.datetime.now(), i, t['currencyTypeName'], base_type, t['chaosEquivalent']
        #                             )
        #                     elif x == base[1]:
        #                         if t['chaosValue'] > 50:

        #                             # if t['baseType']:
        #                             #    base_type = t['baseType']
        #                             await self.bot.db.execute(
        #                                 """
        #                                 INSERT INTO poe.currency (timestamp, league, name, base_type, chaosvalue)
        #                                 VALUES ($1, $2, $3, $4, $5)
        #                                 """,
        #                                 datetime.datetime.now(), i, t['name'], t['baseType'], t['chaosValue']
        #                             )





    # async def trade_url(self, name:str, base:str = None):
    #    build query here or take it as a parameter?

    # async def get_tiny_url(self, trade:str):
    #     url = 'http://tinyurl.com/api-create.php?'

# #To do add in aiohttp for using poe.ninja and pathofexile api for grabbing currency information
# #then storing the data somehow, psql? or keyvalue? or other ideas

