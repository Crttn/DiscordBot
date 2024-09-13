import discord
from config import Config


def setup(bot): 

    @bot.event
    async def on_raw_reaction_add(payload):
        if not bot.setup:
            return print(f"El bot no está configurado. Escribe {Config.prefix}setup para configurarlo")
        
        guild = bot.get_guild(payload.guild_id)
        if guild is None:
            return print("No se ha encontrado el servidor")
        
        member = guild.get_member(payload.user_id)
        if member is None:
            return