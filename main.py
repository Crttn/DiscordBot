import os
from dotenv import load_dotenv
import urllib.request
import json
from config import Config
import discord
from discord.ext import commands


# Configuración inicial

load_dotenv()
token = os.getenv('bot_token')

prefix = Config.prefix

bot = commands.Bot(command_prefix=prefix, intents=discord.Intents.all())

# Variables de configuración del bot
bot.setup = False
bot.join_role_name = Config.role_name_new_user
bot.verify_role_name = Config.role_name_verified
bot.message_id = Config.message_id
bot.channel_id = Config.channel_id

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.command()
async def setup(ctx):
    try:
        message_id = int(bot.message_id)
        channel_id = int(bot.channel_id)
    except ValueError:
        return await ctx.send("Invalid Message ID or Channel ID passed")
    except Exception as e:
        return await ctx.send(f"An error occurred: {e}")

    channel = bot.get_channel(channel_id)
    if channel is None:
        return await ctx.send("Channel Not Found")

    try:
        message = await channel.fetch_message(message_id)
    except discord.NotFound:
        return await ctx.send("Message Not Found")
    except Exception as e:
        return await ctx.send(f"An error occurred: {e}")
    
    try:
        await message.add_reaction("✅")
    except Exception as e:
        return await ctx.send(f"Failed to add reaction: {e}")

    await ctx.send("Setup Successful 🟢")
    bot.setup = True

@bot.event
async def on_raw_reaction_add(payload):
    if not bot.setup:
        return print(f"Bot is not set up. Type {prefix}setup to set up the bot")

    if payload.message_id == int(bot.message_id) and str(payload.emoji) == "✅":
        guild = bot.get_guild(payload.guild_id)
        if guild is None:
            return print("Guild Not Found. Terminating Process")
        
        role = discord.utils.get(guild.roles, name=bot.verify_role_name)
        old_role = discord.utils.get(guild.roles, name=bot.join_role_name)
        if role is None:
            return print("Role Not Found. Terminating Process")
        
        member = guild.get_member(payload.user_id)
        if member is None:
            return
        
        try:
            if old_role in member.roles:
                await member.remove_roles(old_role)
                print(f"Removed old role '{old_role.name}' from {member.name}")
            await member.add_roles(role)
            print(f"Assigned role '{role.name}' to {member.name}")
        except discord.Forbidden:
            print(f"Failed to add/remove role: Missing Permissions for {member.name}")
        except Exception as e:
            print(f"Failed to add/remove role: {e}")

@bot.event
async def on_member_join(member):
    guild = member.guild
    role = discord.utils.get(guild.roles, name=bot.join_role_name)
    
    if role is None:
        return print(f"Role '{bot.join_role_name}' not found. Ensure the role exists.")
    
    try:
        await member.add_roles(role)
        print(f"Assigned role '{role.name}' to {member.name}")
    except discord.Forbidden:
        print(f"Failed to add role: Missing Permissions for {member.name}")
    except Exception as e:
        print(f"Failed to add role: {e}")

bot.run(token)