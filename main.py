import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import os

# SERVIDOR WEB PARA MANTENERLO VIVO
app = Flask('')

@app.route('/')
def home():
    return "¡Bot de Encuestas activo! 📊"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# CONFIGURACIÓN DEL BOT
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Conectado como {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        print(f"✅ Se han sincronizado {len(synced)} comandos.")
    except Exception as e:
        print(e)

# COMANDO DE ENCUESTA
@bot.tree.command(name="encuesta", description="Crea una encuesta rápida")
@app_commands.describe(pregunta="¿Qué quieres preguntar?", opcion1="Primera opción", opcion2="Segunda opción")
async def encuesta(interaction: discord.Interaction, pregunta: str, opcion1: str, opcion2: str):
    embed = discord.Embed(
        title="📊 NUEVA ENCUESTA",
        description=f"**{pregunta}**\n\n1️⃣ {opcion1}\n2️⃣ {opcion2}",
        color=discord.Color.green()
    )
    embed.set_footer(text="Vota reaccionando abajo")
    
    # Enviar el mensaje
    await interaction.response.send_message(embed=embed)
    
    # Obtener el mensaje enviado para ponerle las reacciones
    mensaje = await interaction.original_response()
    await mensaje.add_reaction("1️⃣")
    await mensaje.add_reaction("2️⃣")

keep_alive()
token = os.getenv('DISCORD_TOKEN')
bot.run(token)