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

        try:
            # Verificación de las normas
            if payload.message_id == Config.rules_message_id and str(payload.emoji) == "✅":
                role_verified = discord.utils.get(guild.roles, name=Config.role_name_verified)
                role_new_user = discord.utils.get(guild.roles, name=Config.role_name_new_user)
                if role_verified is None:
                    return print("El rol 'Verificado' no se ha encontrado")
                
                if role_new_user in member.roles:
                    # Elimina el rol "Sin Verificar"
                    await member.remove_roles(role_new_user)
                    print(f"Rol eliminado '{role_new_user.name}' a {member.name}")
                # Agrega el rol "Verificado"
                await member.add_roles(role_verified)
                print(f"Rol asignado '{role_verified.name}' a {member.name}")

            # Reacción para el rol de comandante
            elif payload.message_id == Config.roles_message_id and str(payload.emoji) == "⚫":
                role_commander = discord.utils.get(guild.roles, name=Config.role_name_commander)
                if role_commander is None:
                    return print("El rol 'Commander' no se ha encontrado")
                
                if role_commander in member.roles:
                    # Elimina el rol "Commander"
                    await member.remove_roles(role_commander)
                    print(f"Rol eliminado '{role_commander.name}' a {member.name}")
                else:
                    # Agrega el rol "Commander"
                    await member.add_roles(role_commander)
                    print(f"Rol asignado '{role_commander.name}' a {member.name}")

            # Reacción para el rol de "cEDH"
            elif payload.message_id == Config.roles_message_id and str(payload.emoji) == "🟠":
                role_cEDH = discord.utils.get(guild.roles, name=Config.role_name_cEDH)
                if role_cEDH is None:
                    return print("El rol 'cEDH' no se ha encontrado")
                
                if role_cEDH in member.roles:
                    # Elimina el rol "cEDH"
                    await member.remove_roles(role_cEDH)
                    print(f"Rol eliminado '{role_cEDH.name}' a {member.name}")
                else:
                    # Agrega el rol "cEDH"
                    await member.add_roles(role_cEDH)
                    print(f"Rol asignado '{role_cEDH.name}' a {member.name}")

            # Reacción para el rol de "Pioneer"
            elif payload.message_id == Config.roles_message_id and str(payload.emoji) == "⚪":
                role_pioneer = discord.utils.get(guild.roles, name=Config.role_name_pioneer)
                if role_pioneer is None:
                    return print("El rol 'Pioneer' no se ha encontrado")
                
                if role_pioneer in member.roles:
                    # Elimina el rol "Pioneer"
                    await member.remove_roles(role_pioneer)
                    print(f"Rol eliminado '{role_pioneer.name}' a {member.name}")
                else:
                    # Agrega el rol "Pioneer"
                    await member.add_roles(role_pioneer)
                    print(f"Rol asignado '{role_pioneer.name}' a {member.name}")

            # Reacción para el rol de "Modern"
            elif payload.message_id == Config.roles_message_id and str(payload.emoji) == "🟢":
                role_modern = discord.utils.get(guild.roles, name=Config.role_name_modern)
                if role_modern is None:
                    return print("El rol 'Modern' no se ha encontrado")
                
                if role_modern in member.roles:
                    # Elimina el rol "Modern"
                    await member.remove_roles(role_modern)
                    print(f"Rol eliminado '{role_modern.name}' a {member.name}")
                else:
                    # Agrega el rol "Modern"
                    await member.add_roles(role_modern)
                    print(f"Rol asignado '{role_modern.name}' a {member.name}")

            # Reacción para el rol de "Pauper"
            elif payload.message_id == Config.roles_message_id and str(payload.emoji) == "🔵":
                role_pauper = discord.utils.get(guild.roles, name=Config.role_name_pauper)
                if role_pauper is None:
                    return print("El rol 'Pauper' no se ha encontrado")
                
                if role_pauper in member.roles:
                    # Elimina el rol "Pauper"
                    await member.remove_roles(role_pauper)
                    print(f"Rol eliminado '{role_pauper.name}' a {member.name}")
                else:
                    # Agrega el rol "Pauper"
                    await member.add_roles(role_pauper)
                    print(f"Rol asignado '{role_pauper.name}' a {member.name}")
                
            # Reacción para el rol de "Compraventa"
            elif payload.message_id == Config.roles_message_id and str(payload.emoji) == "📨":
                role_compraventa = discord.utils.get(guild.roles, name=Config.role_name_compraventa)
                if role_compraventa is None:
                    return print("El rol 'Compraventa' no se ha encontrado")
                
                if role_compraventa in member.roles:
                    # Elimina el rol "Compraventa"
                    await member.remove_roles(role_compraventa)
                    print(f"Rol eliminado '{role_compraventa.name}' a {member.name}")
                else:
                    # Agrega el rol "Compraventa"
                    await member.add_roles(role_compraventa)
                    print(f"Rol asignado '{role_compraventa.name}' a {member.name}")

        except discord.Forbidden:
            print(f"Permisos insuficientes para añadir/remover el rol a {member.name}")
        except Exception as e:
            print(f"Error al añadir/remover el rol: {e}")