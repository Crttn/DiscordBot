import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from easy_pil import Editor, load_image_async, Font
from config import Config
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)

# Cargar configuraciones desde .env
load_dotenv()
token = os.getenv('bot_token')
prefix = Config.prefix

# Inicializar el bot con todos los intents habilitados
bot = commands.Bot(command_prefix=prefix, intents=discord.Intents.all())

# Variables para el conteo de usuarios
previousTotalMembers = 0
previousActiveMembers = 0
previousTotalBots = 0

# Evento cuando el bot está listo
@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user.name}")
    countUsers.start()

# Comando para la configuración inicial del bot
@bot.command()
async def setup(ctx):
    bot.setup = True
    logging.info("Configuración del bot completada")
    await ctx.send("Configuración completada 🟢")

# Evento que se dispara cuando un nuevo miembro se une
@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    
    try:
        # Asignar rol al nuevo miembro
        join_role = discord.utils.get(member.guild.roles, name=Config.member_join_role)
        if join_role:
            await member.add_roles(join_role)
        else:
            logging.warning("Role not found.")
    except Exception as e:
        logging.error(f"Error al añadir el rol al usuario: {e}")
        return

    # Crear tarjeta de bienvenida
    try:
        background = Editor("images/pic1.jpg")
        profile_image = await load_image_async(str(member.avatar.url)) if member.avatar else await load_image_async('https://cdn.discordapp.com/embed/avatars/0.png')
        profile = Editor(profile_image).resize((150, 150)).circle_image()
        poppins = Font.poppins(size=50, variant="bold")
        poppins_small = Font.poppins(size=20, variant="light")

        background.paste(profile, (325, 90))
        background.ellipse((325, 90), 150, 150, outline="white", stroke_width=5)
        background.text((400, 260), f"BIENVENIDO A {member.guild.name.upper()}", color="white", font=poppins, align="center")
        background.text((400, 325), f"{member.name}", color="white", font=poppins_small, align="center")
        file = discord.File(fp=background.image_bytes, filename="pic1.jpg")

        await channel.send(f"Hola {member.mention}! Bienvenido a **{member.guild.name.upper()}**. Para más información, visita <#1054543343289376768>")
        await channel.send(file=file)
    except Exception as e:
        logging.error(f"Error al enviar el mensaje de bienvenida: {e}")

# Tarea para contar usuarios y bots cada 5 minutos
@tasks.loop(minutes=5)
async def countUsers():
    global previousTotalMembers, previousActiveMembers, previousTotalBots

    try:
        guild_id = bot.get_guild(Config.guild_id)
        member_channel = bot.get_channel(Config.counter_member_channel_id)
        active_channel = bot.get_channel(Config.counter_active_member_channel_id)
        bot_channel = bot.get_channel(Config.counter_bot_channel_id)
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
        logging.warning(f"No se ha encontrado el servidor con ID: {Config.guild_id}")

# Ejecutar el bot
bot.run(token)
