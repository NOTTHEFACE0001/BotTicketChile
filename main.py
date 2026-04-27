import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import os

# 1. SERVIDOR WEB PARA RENDER
app = Flask('')
@app.route('/')
def home():
    return "¡Bot Chile RP Multiusos Activo! 📊✅❌"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. CONFIGURACIÓN DEL BOT
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Conectado como {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        print(f"✅ Sincronizados {len(synced)} comandos.")
    except Exception as e:
        print(e)

# 3. COMANDO DE ENCUESTA
@bot.tree.command(name="encuesta", description="Crea una encuesta rápida")
async def encuesta(interaction: discord.Interaction, pregunta: str, opcion1: str, opcion2: str):
    embed = discord.Embed(title="📊 ENCUESTA", description=f"**{pregunta}**\n\n1️⃣ {opcion1}\n2️⃣ {opcion2}", color=discord.Color.green())
    await interaction.response.send_message(embed=embed)
    mensaje = await interaction.original_response()
    await mensaje.add_reaction("1️⃣")
    await mensaje.add_reaction("2️⃣")

# 4. COMANDO PARA ABRIR SERVIDOR
@bot.tree.command(name="abrir_servidor", description="Anuncia la apertura del servidor")
async def abrir_servidor(interaction: discord.Interaction):
    embed = discord.Embed(
        title="✅ SERVIDOR ABIERTO",
        description="¡El servidor de **Chile RP** ya está disponible!\n\n¡Entra ya y disfruta del mejor rol!",
        color=discord.Color.blue()
    )
    embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJueW94bmZ4bmZ4bmZ4bmZ4bmZ4bmZ4bmZ4bmZ4bmZ4bmZ4JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKMGpxxcaOXYT60/giphy.gif")
    await interaction.response.send_message(content="@everyone", embed=embed)

# 5. COMANDO PARA CERRAR SERVIDOR
@bot.tree.command(name="cerrar_servidor", description="Anuncia el cierre del servidor")
async def cerrar_servidor(interaction: discord.Interaction):
    embed = discord.Embed(
        title="❌ SERVIDOR CERRADO",
        description=(
            "El servidor ha cerrado sus puertas por hoy.\n\n"
            "**¡Gracias a todos por participar!**\n"
            "Nos vemos en la próxima jornada de rol."
        ),
        color=discord.Color.red()
    )
    embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM2ZicW9ueGZ4bmZ4bmZ4bmZ4bmZ4bmZ4bmZ4bmZ4bmZ4bmZ4bmZ4JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKVUn7iM8FMEU24/giphy.gif")
    await interaction.response.send_message(content="@everyone", embed=embed)

# 6. ENCENDER BOT
keep_alive()
token = os.getenv('DISCORD_TOKEN')
bot.run(token)