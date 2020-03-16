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
        total = 0
        check_roll = self.valid(roll)
        if check_roll == 0:
            await ctx.send(f'Please use valid characters @{ctx.author.name}')

        if check_roll == -1:
            dice, size, add, sub, drop = self.splitter(roll)
            result = rolling_dice(dice, size)
            total = sum(result) + add - sub
            if drop > 0 and dice > drop:
                for i in range(drop):
                    result.remove(min(result))
            else:
                await ctx.send(f'You are trying to drop more dice than you rolled, please keep at least 1 die @{ctx.author.name}')
            
            if len(result) > 1:
                await ctx.send(f'Here are your dice! ({unpack(result)}) and the total: {total} @{ctx.author.name}')
            else:
                await ctx.send(f'Here are your dice! ({total}) @{ctx.author.name}')

        elif check_roll == 1:
            dice, size, add, sub, drop = self.splitter(roll[1:])
            if roll.startswith('!', 0):
                adv = 1
            elif roll.startswith('*', 0):
                dis = 1
            res1 = rolling_dice(dice, size)
            res2 = rolling_dice(dice, size)
            if adv:
                result = res1 if res1 > res2 else res2
            elif:
                result = res1 if res1 < res2 else res2
            if len(result) > 1:
                await ctx.send(f'Here are your dice! ({self.unpack(result)}) and the total: {sum(result)} @{ctx.author.name}')
            else:
                await ctx.send(f'Here are your dice! ({sum(result)}) @{ctx.author.name}')

    def valid(self, roll):
        # ([!\*]).(\d*)(d\d*)?((?:[+d-](?:\d+)))
        allowed_chars = set("0123456789+-d!*")
        adv_pat  = re.compile('^([!\*])(\d{1,2})([d]\d{1,3})?(?:[+d-](?:\d{1,3}))$')
        # \d*)(d\d*)?((?:[+d-](?:\d+)))
        simp_pat = re.compile('^(\d{1,2})([d]\d{1,3})?(?:([+d-](\d{1,3})))$')
        if set(roll).issubset(allowed_chars) and adv_pat.match(roll):
            return 1 #adv/dis Valid input
        elif set(roll).issubset(allowed_chars) and simp_pat.match(roll):
            return -1 #normal input
        else:
            return 0 #Error with input

    def splitter(self, roll):
        def dice_value(roll, value):
            dice = roll.split("d")[0]
            value[0] = int(dice)
            return value
        
        def sides_value(self, roll, value):
            sides = re.split(r"[d\+\-]\s*", roll)[1]
            value[1] = int(sides)
            return value
        
        def add_value(self, roll, value):
            add = re.split(r'[d\+]\s*', roll)[2]
            value[2] = int(add)
            return value
        
        def sub_value(self, roll, value):
            sub = re.split(r'[d\-]\s*', roll)[2]
            value[3] = int(sub)
            return value
        
        def drop_value(self, roll, value):
            drop = re.split(r'[d]\s*', roll)[2]
            value[4] = int(drop)
            return value

        def split(self, flist, default = [0, 0, 0, 0, 0]):
            for f in flist:
                try:
                    temp = f(roll, default)
                except:
                    continue
            return default
        return split(([dice_value, sides_value, add_value, sub_value, drop_value]))
    
    def unpack(self, s):
        return list(map(int, s))

    def rolling_dice(self, dice, size):
        result = []
        for i in range(dice):
            roll = random.randint(1, size)
            result.append(roll)
        return result
