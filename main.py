import os
from dotenv import load_dotenv
from config import Config
import discord
from easy_pil import Editor, load_image_async, Font
from discord.ext import commands, tasks

# Obtinen las configuraciones necesarias
load_dotenv()
token = os.getenv('bot_token')
prefix = Config.prefix
bot = commands.Bot(command_prefix=prefix, intents=discord.Intents.all())

# Variables de configuración del bot
bot.setup = False
bot.join_role_name = Config.role_name_new_user
bot.verify_role_name = Config.role_name_verified
bot.message_normas_id = Config.message_normas_id
bot.channel_normas_id = Config.channel_normas_id

# Conección incial con el bot
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    countUsers.start()

# Inicia el setup del bot
@bot.command()
async def setup(ctx):
    try:
        message_id = int(bot.message_normas_id)
        channel_id = int(bot.channel_normas_id)
    except ValueError:
        return await ctx.send("ID del canal o del mensaje erroneo")
    except Exception as e:
        return await ctx.send(f"Error en la configuración: {e}")

    channel = bot.get_channel(channel_id)
    if channel is None:
        return await ctx.send("Canal no encontado")

    try:
        message = await channel.fetch_message(message_id)
    except discord.NotFound:
        return await ctx.send("Mensaje no encontrado")
    except Exception as e:
        return await ctx.send(f"Error al encontrar el mensaje: {e}")
    
    try:
        await message.add_reaction("✅")
    except Exception as e:
        return await ctx.send(f"Error al añadir la reacción: {e}")

    bot.setup = True
    print("Configuración del bot compeltada")
    await ctx.send("Configuración compeltada 🟢")

# Asigna el rol "Sin verificar" a los nuevos usuarios y envía una tarjeta de binevenida
@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    background = Editor("images\\pic1.jpg")

    profile_image = None
    # URL de un avatar predeterminado de Discord
    default_avatar = 'https://cdn.discordapp.com/embed/avatars/0.png'

    # Verificar si el usuario tiene un avatar; de lo contrario, usar un avatar predeterminado
    if member.avatar:
        profile_image = await load_image_async(str(member.avatar.url))
    else:
        profile_image = await load_image_async(default_avatar)

    profile = Editor(profile_image).resize((150, 150)).circle_image()
    poppins = Font.poppins(size=50, variant="bold")
    poppins_small = Font.poppins(size=20, variant="light")

    background.paste(profile, (325, 90))
    background.ellipse((325, 90), 150, 150, outline="white", stroke_width=5)
    
    background.text((400, 260), f"BIENVENIDO A {member.guild.name}", color="white", font=poppins, align="center")
    background.text((400, 325), f"{member.name}", color="white", font=poppins_small, align="center")
    
    file = discord.File(fp=background.image_bytes, filename="pic1.jpg")

    await channel.send(f"Hola {member.mention}! Binevenido a **{member.guild.name}** Para mas información ve a **#Normas**")
    await channel.send(file=file)

    #  Asigna el rol "Sin Verificar" a los nuevos usuarios
    guild = member.guild
    role = discord.utils.get(guild.roles, name=bot.join_role_name)

    # Comprueba que el rol exista 
    if role is None:
        return print(f"No se ha encontrado el rol:'{bot.join_role_name}'")
    
    # Agrega el rol "Sin Verificar"
    try:
        await member.add_roles(role)
        print(f"Rol '{role.name}' asignado a {member.name}")
    except discord.Forbidden:
        print(f"Error al añadir el rol, verifica los permisos para {member.name}")
    except Exception as e:
        print(f"Error al agregar el rol: {e}")

# Obtiene la reacción de los nuevos usuarios ante las normas y agrega el rol "Verificado", tambien elimina el rol "Sin Verificar"
@bot.event
async def on_raw_reaction_add(payload):
    if not bot.setup:
        return print(f"El bot no está configurado. Escribe {prefix}setup para configurarlo")

    if payload.message_id == int(bot.message_normas_id) and str(payload.emoji) == "✅":
        guild = bot.get_guild(payload.guild_id)
        if guild is None:
            return print("No se ha encotrado el servidor")
        
        role = discord.utils.get(guild.roles, name=bot.verify_role_name)
        old_role = discord.utils.get(guild.roles, name=bot.join_role_name)
        if role is None:
            return print("El rol no se ha encotrado")
        
        member = guild.get_member(payload.user_id)
        if member is None:
            return
        
        # Añadir/Eliminar roles
        try:
            if old_role in member.roles:
                # Elimina el rol "Sin Verificar"
                await member.remove_roles(old_role)
                print(f"Rol eliminado '{old_role.name}' a {member.name}")
            # Agrega el rol "Verificado"
            await member.add_roles(role)
            print(f"Rol asignado '{role.name}' a {member.name}")
        except discord.Forbidden:
            print(f"Permisos inecesarios para añadir/remover el rol a {member.name}")
        except Exception as e:
            print(f"Error al añadir/remover el rol: {e}")

# Obtiene la cantidad de miembros y bots del discord y la muestra como nombre de canales de voz 
@tasks.loop(minutes=5)
async def countUsers():

    # Obtiene el servidor y los canales apartir del id
    guild_id = bot.get_guild(Config.guild_id)
    member_channel_id = bot.get_channel(Config.counter_member_channel_id)
    active_channel_id = bot.get_channel(Config.counter_active_member_channel_id)
    bot_cannle_id = bot.get_channel(Config.counter_bot_channel_id)

    # Comprueba que exista el servidor
    if guild_id is not None:
        totalMembers = 0
        activeMembers = 0
        totalBots = 0

        # Cuenta los usuarios
        for member in guild_id.members:
            if not member.bot:
                totalMembers += 1
        # Cuenta los usuarios conectados
            if not member.bot and member.status != discord.Status.offline:
                activeMembers += 1
        # Cuenta los bots
            if member.bot:
                totalBots += 1
    else:
        print(f"No se ha encontrado el servidor con id: {guild_id}.")
        return  

    # Modifica el nombre del canal de voz "Miembros"
    if member_channel_id:
        # Verificar permisos para editar el canal
        if member_channel_id.permissions_for(guild_id.me).manage_channels:
            try:
                await member_channel_id.edit(name=f"【 👥 】 Miembros: {totalMembers}")
            except discord.Forbidden:
                print(f"Permisos inecesarios para editar el canal con id: {member_channel_id.name}")
        else:
            print(f"El bot no tiene permisos para editar canales")
    else:
        print(f"No se ha encontrado el canal con id: {member_channel_id}")

    # Modifica el nombre del canal de voz "Activos"
    if active_channel_id:
        # Verificar permisos para editar el canal
        if active_channel_id.permissions_for(guild_id.me).manage_channels:
            try:
                await active_channel_id.edit(name=f"【 🟢 】 Activos: {activeMembers}")
            except discord.Forbidden:
                print(f"Permisos inecesarios para editar el canal con id: {active_channel_id.name}")
        else:
            print(f"El bot no tiene permisos para editar canales")
    else:
        print(f"No se ha encontrado el canal con id: {active_channel_id}")

    # Modifica el nombre del canal de voz "Bots"
    if bot_cannle_id:
        # Verificar permisos para editar el canal
        if bot_cannle_id.permissions_for(guild_id.me).manage_channels:
            try:
                await bot_cannle_id.edit(name=f"【 🤖 】 Bots: {totalBots}")
            except discord.Forbidden:
                print(f"Permisos inecesarios para editar el canal con id: {bot_cannle_id.name}")
        else:
            print(f"El bot no tiene permisos para editar canales")
    else:
        print(f"No se ha encontrado el canal con id: {bot_cannle_id}")

bot.run(token)