import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from Config import Configuration
from Events import Events
from Scryfall import ScryfallRequest
import logging


# Configuración de logging
logging.basicConfig(level=logging.INFO)

# Cargar configuraciones desde .env
load_dotenv()
token = os.getenv('bot_token')
prefix = Configuration.prefix

# Inicializar el bot con todos los intents habilitados
bot = commands.Bot(command_prefix=prefix, intents=discord.Intents.all())

# Evento cuando el bot está listo
@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user.name}")
    countUsers.start()
    tryScryScrape.start()

# Comando para la configuración inicial del bot
@bot.command()
async def setup(ctx):
    bot.setup = True
    await ctx.send("Configuración completada 🟢")

# Evento que se dispara cuando un nuevo miembro se une
@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    
    try:
        # Asignar rol al nuevo miembro
        join_role = discord.utils.get(member.guild.roles, name=Configuration.member_join_role)
        if join_role:
            await member.add_roles(join_role)
        else:
            logging.warning("Role not found.")
    except Exception as e:
        logging.error(f"Error al añadir el rol al usuario: {e}")
        return

    # Crear tarjeta de bienvenida
    await Events.sendWellcomeMessage(member, channel)
    

# Variables para el conteo de usuarios
previousTotalMembers = 0
previousActiveMembers = 0
previousTotalBots = 0
# Tarea para contar usuarios y bots cada 5 minutos
@tasks.loop(minutes=5) 
async def countUsers():
    global previousTotalMembers, previousActiveMembers, previousTotalBots

    try:
        guild_id = bot.get_guild(Configuration.guild_id)
        member_channel = bot.get_channel(Configuration.counter_member_channel_id)
        active_channel = bot.get_channel(Configuration.counter_active_member_channel_id)
        bot_channel = bot.get_channel(Configuration.counter_bot_channel_id)
    except Exception as e:
        logging.error(f"Error al cargar los IDs de los canales: {e}")
        return

    if guild_id is not None:
        totalMembers = sum(1 for member in guild_id.members if not member.bot)
        activeMembers = sum(1 for member in guild_id.members if not member.bot and member.status != discord.Status.offline)
        totalBots = sum(1 for member in guild_id.members if member.bot)

        # Verificar si ha habido cambios
        if (totalMembers != previousTotalMembers or 
            activeMembers != previousActiveMembers or 
            totalBots != previousTotalBots):

            previousTotalMembers = totalMembers
            previousActiveMembers = activeMembers
            previousTotalBots = totalBots

            if member_channel and active_channel and bot_channel:
                # Actualizar nombres de canales si el bot tiene permisos
                try:
                    if member_channel.permissions_for(guild_id.me).manage_channels:
                        await member_channel.edit(name=f"【 👥 】 Miembros: {totalMembers}")
                    if active_channel.permissions_for(guild_id.me).manage_channels:
                        await active_channel.edit(name=f"【 🟢 】 Activos: {activeMembers}")
                    if bot_channel.permissions_for(guild_id.me).manage_channels:
                        await bot_channel.edit(name=f"【 🤖 】 Bots: {totalBots}")
                except discord.Forbidden:
                    logging.warning("Permisos insuficientes para editar uno de los canales")
            else:
                logging.warning("No se encontraron uno o más canales especificados.")
    else:
        logging.warning(f"No se ha encontrado el servidor con ID: {Configuration.guild_id}")

#Peticiones a la API de ScryFall
@tasks.loop(minutes=15)
async def tryScryScrape():
    await ScryfallRequest.send_sets_data(bot)

bot.run(token)
