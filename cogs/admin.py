import discord
from discord.ext import commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.blocked_users = {}

    @commands.has_permissions(administrator=True)
    @commands.command(name="block-user", description="Block the bot from greeting a user")
    async def block_user(self, ctx, user: discord.Member):
        guild_id = ctx.guild.id
        if guild_id not in self.blocked_users:
            self.blocked_users[guild_id] = set()
        self.blocked_users[guild_id].add(user.id)
        await ctx.send(f"{user.name} will no longer be greeted by the bot.", delete_after=10)

    @commands.has_permissions(administrator=True)
    @commands.command(name="unblock-user", description="Unblock the bot from greeting a user")
    async def unblock_user(self, ctx, user: discord.Member):
        guild_id = ctx.guild.id
        if guild_id in self.blocked_users and user.id in self.blocked_users[guild_id]:
            self.blocked_users[guild_id].remove(user.id)
            await ctx.send(f"{user.name} will now be greeted by the bot.", delete_after=10)
        else:
            await ctx.send(f"{user.name} was not blocked.", delete_after=10)

async def setup(bot):
    await bot.add_cog(Admin(bot))
