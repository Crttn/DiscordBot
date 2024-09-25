import discord
from Config import Configuration
from easy_pil import Editor, load_image_async, Font


class Events: 
    async def sendWellcomeMessage(member, channel):
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
            print(f"Error al crear la imagen de bienvenida: {e}")

        return file
    
