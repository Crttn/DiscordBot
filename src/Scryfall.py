import discord
from datetime import datetime
import aiohttp
import logging
from Config import Configuration
import json
import os

class ScryfallRequest:

    @staticmethod
    async def fetch_scryfall_sets(url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()  # Convertimos la respuesta a formato JSON
                        logging.info("Datos de Scryfall obtenidos correctamente.")
                        return data.get('data', []) 
                    else:
                        logging.error(f"Error HTTP al obtener sets de Scryfall: {response.status}")
                        return []
        except aiohttp.ClientConnectorError as e:
            logging.error('Error de conexión:', str(e))
            return []
        except Exception as e:
            logging.error('Error inesperado:', str(e))
            return []
        

    SEEN_SETS_FILE = 'seen_sets.json'

    @staticmethod
    def load_seen_sets():
        try:
            if os.path.exists(ScryfallRequest.SEEN_SETS_FILE):
                with open(ScryfallRequest.SEEN_SETS_FILE, 'r') as f:
                    return set(json.load(f))
            else:
                return set()  # Si el archivo no existe, devolver un conjunto vacío
        except Exception as e:
            logging.error(f"Error al cargar el archivo {ScryfallRequest.SEEN_SETS_FILE}: {e}")
            return set()

    @staticmethod
    def save_seen_sets(seen_sets):
        try:
            with open(ScryfallRequest.SEEN_SETS_FILE, 'w') as f:
                json.dump(list(seen_sets), f)  # Guardamos la lista convertida de 'set' a 'list'
            logging.info("Los sets vistos han sido guardados.")
        except Exception as e:
            logging.error(f"Error al guardar en el archivo {ScryfallRequest.SEEN_SETS_FILE}: {e}")

    @staticmethod
    async def fetch_scryfall_sets():
        url = 'https://api.scryfall.com/sets'
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()  # Convertimos la respuesta a formato JSON
                        logging.info("Datos de Scryfall obtenidos correctamente.")
                        return data.get('data', [])  # Devolver los sets o una lista vacía si no existe 'data'
                    else:
                        logging.error(f"Error HTTP al obtener sets de Scryfall: {response.status}")
                        return []
        except aiohttp.ClientConnectorError as e:
            logging.error('Error de conexión:', str(e))
            return []
        except Exception as e:
            logging.error('Error inesperado:', str(e))
            return []
    
    @staticmethod
    async def send_sets_data(bot):
        # Obtener el canal
        channel = bot.get_channel(Configuration.notices_channel_id)
        if not channel:
            logging.error("Error: No se pudo encontrar el canal.")
            return

        # Obtener la fecha actual
        date_today = datetime.today().date()

        # Cargar los sets ya vistos previamente
        seen_sets = ScryfallRequest.load_seen_sets()

        # Obtener los sets desde Scryfall
        sets_data = await ScryfallRequest.fetch_scryfall_sets()

        # Verificamos si hay sets disponibles
        if not sets_data:
            logging.warning("No se han encontrado sets disponibles o hubo un error en la API de Scryfall.")
            return

        # Procesar los sets recibidos
        sets_enviados = 0
        for card_set in reversed(sets_data):
            try:
                set_release_date = datetime.strptime(card_set['released_at'], '%Y-%m-%d').date()

                # Ignorar sets ya lanzados
                if set_release_date < date_today:
                    continue

                set_id = card_set['id']
                set_name = card_set['name']

                set_totalCards = card_set['card_count']

                # Verificar si el set ya ha sido visto y contiene cartas
                if set_id not in seen_sets & set_totalCards > 0:
                    seen_sets.add(set_id)

                    # Crear el embed con los detalles del set
                    embed = discord.Embed(
                        title="¡Nueva colección!",
                        description=f"__{set_name}__",
                        color=0xDE330C
                    )
                    embed.add_field(
                        name="Fecha de lanzamiento:",
                        value=f"{card_set['released_at']}",
                        inline=False
                    )
                    embed.add_field(
                        name="Número de cartas:",
                        value=f"{card_set['card_count']}",
                        inline=True
                    )
                    embed.add_field(
                        name="Tipo de colección:",
                        value=f"{card_set['set_type']}",
                        inline=True
                    )
                    embed.add_field(
                        name="Más información:",
                        value=f"[MTG Canarias](https://mtgcanarias.com/)", 
                        inline=False
                    )
                    embed.set_thumbnail(
                        url="https://mtgcanarias.com/wp-content/uploads/2023/03/loguito.png"
                    )
                    embed.set_image(
                        url="https://images.ctfassets.net/s5n2t79q9icq/5p96VsqUFOFydvLm9q0d9j/db8816b162d484efb1a2d476252658f6/MTG_Meta-ShareImage.jpg"
                    )
                    embed.set_footer(
                        text="MTG-Canarias",
                        icon_url="https://yt3.googleusercontent.com/oO0NdBych3qL79hrzfj4e7jijDJYdy9mrEKnB1tBNSnu6FvFi4XOg2fPuYpWVf5x1xWdZOC1VA=s900-c-k-c0x00ffffff-no-rj"
                    )

                    # Enviar el mensaje al canal
                    await channel.send("¡Nueva Colección de MTG en Camino! @everyone ")
                    await channel.send(embed=embed)
                    logging.info(f"Enviada la nueva colección: {set_name}")
                    sets_enviados += 1

            except Exception as e:
                logging.error(f"Error procesando el set {card_set['name']}: {e}")

        # Guardar los sets actualizados como vistos solo si se enviaron sets nuevos
        if sets_enviados > 0:
            ScryfallRequest.save_seen_sets(seen_sets)