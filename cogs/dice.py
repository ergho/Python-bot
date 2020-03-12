from twitchio.ext import commands

import re
import random


@commands.cog()
class Dice:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='roll')
    async def roll_command(self, ctx, roll : str):

        adv = 0
        dis = 0
        total = 0

        if valid(roll) == -1:
            dice, size, add, sub, drop = splitter(roll)
            result = rolling_dice(dice, size)
            total = sum_of_dice(result)
            if add !=0:
                total = total + add
            if sub !=0:
                total = total - sub
            if drop > 0:
                if dice > drop:
                    for i in range(drop):
                        result.remove(min(result))
                else:
                    await ctx.send(f'You are trying to drop more dice than you rolled, please keep at least 1 die @{ctx.author.name}')
            
            if len(result) > 1:
                await ctx.send(f'Here are your dice! ({unpack(result)}) and the total: {total} @{ctx.author.name}')
            else:
                await ctx.send(f'Here are your dice! ({total}) @{ctx.author.name}')

        elif valid(roll) == 1:
            if roll.startswith('!1d', 0):
                adv = 1
            elif roll.startswith('*1d', 0):
                dis = 1
            dice, size, add, sub, drop = splitter(roll[1:])
            if adv > 0 or dis > 0:
                dice += 1
                result = rolling_dice(dice, size)
                if adv > 0:
                    for i in range(adv):
                        result.remove(min(result))
                        print('hey')
                else:
                    for i in range(dis):
                        result.remove(max(result))
                        print('hello')
            if len(result) > 1:
                await ctx.send(f'Here are your dice! ({unpack(result)}) and the total: {sum_of_dice(result)} @{ctx.author.name}')
            else:
                await ctx.send(f'Here are your dice! ({sum_of_dice(result)}) @{ctx.author.name}')

        elif valid(roll) == 0:
            await ctx.send(f'Please use valid characters @{ctx.author.name}')

def valid(roll):
    allowed_chars = set("0123456789+-d!*")
    adv_pat  = re.compile("([!\*]).(\d*)(d\d*)?((?:[+d-](?:\d+)))")
    simp_pat = re.compile("(\d*)(d\d*)?((?:[+d-](?:\d+)))")
    if set(roll).issubset(allowed_chars) and adv_pat.match(roll):
        return 1 #adv/dis Valid input
    elif set(roll).issubset(allowed_chars) and simp_pat.match(roll):
        return -1 #normal input
    else:
        return 0 #Error with input

def splitter(roll):
    dice = roll.split("d")[0]
    sides = re.split(r"[d\+\-]\s*", roll)[1]
    add = 0
    sub = 0
    drop = 0
    try:
        add = re.split(r'[d\+]\s*', roll)[2]
    except Exception as e:
        print(f'{e} add')
    try:
        sub = re.split(r'[d\-]\s*', roll)[2]
    except Exception as e:
        print(f'{e} sub')
    try:
        drop = re.split(r'[d]\s*', roll)[2]
    except Exception as e:
        print(f'{e} drop')
    return int(dice), int(sides), int(add), int(sub), int(drop)
    
def unpack(s):
    return list(map(int, s))

def rolling_dice(dice, size):
    result = []
    for i in range(dice):
        roll = random.randint(1, size)
        result.append(roll)
    return result

def sum_of_dice(result):
    total = 0
    for i in result:
        total += i

    return total
