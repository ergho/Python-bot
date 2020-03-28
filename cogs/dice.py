from twitchio.ext import commands

import re
import random

@commands.cog()
class Dice:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='roll')
    async def roll_command(self, ctx, roll : str):

        adv = None
        dis = None
        check_roll = await self.valid(roll)

        if check_roll == 0:
            await ctx.send(f'Please use valid characters @{ctx.author.name}')
        elif check_roll == 1:
            if roll.startswith('!', 0):
                adv = 1
            elif roll.startswith('*', 0):
                dis = 1
            if adv or dis:
                dice, size, add, sub, drop = await self.split(([self.dice_value, self.sides_value, self.add_value, self.sub_value, self.drop_value]), roll[1:])
                if size < 2:
                    await(f'Send please roll a dice with at least 2 sides @{ctx.author.name}')
                    break
                res1 = await self.rolling_dice(dice, size)
                res2 = await self.rolling_dice(dice, size)
                if adv:
                    result = res1 if res1 > res2 else res2
                else:
                    result = res1 if res1 < res2 else res2
            else:
                dice, size, add, sub, drop = dice, size, add, sub, drop = await self.split(([self.dice_value, self.sides_value, self.add_value, self.sub_value, self.drop_value]), roll)
                if size < 2:
                    await(f'Send please roll a dice with at least 2 sides @{ctx.author.name}')
                    break
                result = await self.rolling_dice(dice, size)
            
            if drop > 0 and dice > drop:
                if dis:
                    for i in range(drop):
                        result.remove(max(result))
                else:        
                    for i in range(drop):
                        result.remove(min(result))
            elif drop > dice:
                await ctx.send(f'You are trying to drop more dice than you rolled, please keep at least 1 die @{ctx.author.name}')
            total = sum(result) + add - sub
            if len(result) > 1 and len(result) < 20:
                #limits the length of your output
                res = await self.unpack(result)
                await ctx.send(f'Here are your dice! ({res}) and the total: {total} @{ctx.author.name}')
            else:
                await ctx.send(f'Here are your dice! ({total}) @{ctx.author.name}')

    async def valid(self, roll:str) -> int:
        allowed_chars = set('0123456789+-d!*')
        if set(roll).issubset(allowed_chars) and re.match('^([!\*])?(\d{1,2})([d]\d{1,3})?(?:[+d-](?:\d{1,3}))$', roll):
            return 1 # valid input
        else:
            return 0 # invalid input

    async def dice_value(self, roll:str, value:list) -> list:
        dice = roll.split("d")[0]
        value[0] = int(dice)
        return value
    
    async def sides_value(self, roll:str, value:list) -> list:
        sides = re.split(r"[d\+\-]\s*", roll)[1]
        value[1] = int(sides)
        return value
    
    async def add_value(self, roll:str, value:list) -> list:
        add = re.split(r'[d\+]\s*', roll)[2]
        value[2] = int(add)
        return value
    
    async def sub_value(self, roll:str, value:list) -> list:
        sub = re.split(r'[d\-]\s*', roll)[2]
        value[3] = int(sub)
        return value
    
    async def drop_value(self, roll:str, value:list) -> list:
        drop = re.split(r'[d]\s*', roll)[2]
        value[4] = int(drop)
        return value

    async def split(self, flist:list, roll:str) -> list: 
        parameters = [0, 0, 0, 0, 0]
        for func in flist:
            try:
                await func(roll, parameters)
            except:
                continue
        return parameters
    
    async def unpack(self, s)-> list:
        return list(map(int, s))

    async def rolling_dice(self, dice:int, size:int) -> list:
        result = []
        for i in range(dice):
            roll = random.randint(1, size)
            result.append(roll)
        return result
