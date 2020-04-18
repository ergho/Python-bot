import random
import re
from typing import List, Optional, Set, Any

from twitchio.ext import commands


@commands.cog()
class Dice:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=('hide',))
    async def stealth_check(self, ctx) -> None:
        result: List[int] = await self.rolling_dice(1, 20)
        if sum(result) > 12:
            await ctx.send(f'{ctx.author.name} rolled {result} and succeeded hiding.')
        else:
            await ctx.send(f'{ctx.author.name} rolled {result} and failed at hiding.')

    @commands.command(aliases=('roll',))
    async def roll_command(self, ctx, roll: str):
        """
        ! = advantage, * = disadvantage, second d = drop number of dice
        roll follows this structure 1d20+2, !1d20-2, 4d20d1
        """
        adv: Optional[int] = None
        dis: Optional[int] = None
        check_roll: int = await self.valid(roll)
        if check_roll == 0:
            await ctx.send(f'Please use valid characters @{ctx.author.name}')
        if check_roll == 1:
            if roll.startswith('!', 0):
                adv = 1
            if roll.startswith('*', 0):
                dis = 1
            if adv or dis:
                roll = roll[1:]
            dice: int
            size: int
            add: int
            sub: int
            drop: int
            dice, size, add, sub, drop = await self.split(([self.dice_value, self.sides_value, self.add_value, self.sub_value, self.drop_value]), roll)
            if size < 2:
                await ctx.send(f'Send please roll a dice with at least 2 sides @{ctx.author.name}')
                return

            if adv or dis:
                res1: List[int] = await self.rolling_dice(dice, size)
                res2: List[int] = await self.rolling_dice(dice, size)
                if adv:
                    result: List[int] = res1 if res1 > res2 else res2
                else:
                    result = res1 if res1 < res2 else res2
            else:
                result = await self.rolling_dice(dice, size)
            if drop > 0 and dice > drop:
                if dis:
                    for i in range(drop): # type: int
                        result.remove(max(result))
                else:
                    for i in range(drop):
                        result.remove(min(result))
            elif drop > dice:
                await ctx.send(f'You are trying to drop more dice than you rolled, please keep at least 1 die @{ctx.author.name}')
                return
            total: int = sum(result) + add - sub
            # Tries to ensure that messages aren't too long for the chat medium.
            if len(result) > 1 and len(result) < 20:
                res: str = await self.unpack(result)
                await ctx.send(f'Here are your dice! ({res}) and the total: {total} @{ctx.author.name}')
            else:
                await ctx.send(f'Here are your dice! ({total}) @{ctx.author.name}')

    async def valid(self, roll: str) -> int:
        allowed_chars: Set = set('0123456789+-d!*')
        if set(roll).issubset(allowed_chars) and re.match(r'^([!\*])?(\d{1,2})([d]\d{1,3})?(?:[+d-](?:\d{1,3}))$', roll):
            return 1  # valid input
        else:
            return 0  # invalid input

    async def dice_value(self, roll: str, value: list) -> List[int]:
        dice: str = roll.split("d")[0]
        value[0] = int(dice)
        return value

    async def sides_value(self, roll: str, value: list) -> List[int]:
        sides: str = re.split(r"[d\+\-]\s*", roll)[1]
        value[1] = int(sides)
        return value

    async def add_value(self, roll: str, value: list) -> List[int]:
        add: str = re.split(r'[d\+]\s*', roll)[2]
        value[2] = int(add)
        return value

    async def sub_value(self, roll: str, value: list) -> List[int]:
        sub: str = re.split(r'[d\-]\s*', roll)[2]
        value[3] = int(sub)
        return value

    async def drop_value(self, roll: str, value: list) -> List[int]:
        drop: str = re.split(r'[d]\s*', roll)[2]
        value[4] = int(drop)
        return value

    async def split(self, flist: list, roll: str) -> List[int]:
        parameters: List[int] = [0, 0, 0, 0, 0]
        for func in flist: # type: Any
            try:
                await func(roll, parameters)
            except Exception as e:
                print(e)
                continue
        return parameters

    async def unpack(self, result: list) -> str:
        return ', '.join(str(x) for x in result)

    async def rolling_dice(self, dice: int, size: int) -> List[int]:
        result: List[int] = []
        for i in range(dice):
            roll: int = random.randint(1, size)
            result.append(roll)
        return result
