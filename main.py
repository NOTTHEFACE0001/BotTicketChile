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
    return "¡Bot Chile RP Pro Activo! 📊✅❌"

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
    embed = discord.Embed(title="📊 SISTEMA DE ENCUESTAS", description=f"**{pregunta}**\n\n1️⃣ {opcion1}\n2️⃣ {opcion2}", color=discord.Color.from_rgb(46, 204, 113))
    embed.set_footer(text="Tu opinión es importante para Chile RP")
    await interaction.response.send_message(embed=embed)
    mensaje = await interaction.original_response()
    await mensaje.add_reaction("1️⃣")
    await mensaje.add_reaction("2️⃣")

# 4. COMANDO APERTURA (DISEÑO PROFESIONAL)
@bot.tree.command(name="abrir_servidor", description="Anuncia la apertura profesional del servidor")
async def abrir_servidor(interaction: discord.Interaction):
    embed = discord.Embed(
        title="✨ ¡ESTAMOS EN LÍNEA! ✨",
        description="El servidor de **Chile RP** ha abierto sus puertas. ¡Prepárate para la mejor experiencia de rol!",
        color=discord.Color.from_rgb(52, 152, 219) # Azul elegante
    )
    
    embed.add_field(name="🎮 Estado", value="🟢 **Online**", inline=True)
    embed.add_field(name="📍 Mapa", value="Chile Continental", inline=True)
    embed.add_field(name="📢 Aviso", value="Recuerda seguir las reglas de rol en todo momento.", inline=False)
    
    embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJueW94bmZ4bmZ4bmZ4bmZ4bmZ4bmZ4bmZ4bmZ4bmZ4bmZ4JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKMGpxxcaOXYT60/giphy.gif")
    embed.set_footer(text="Administración de Chile RP", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
    
    await interaction.response.send_message(content="@everyone", embed=embed)

# 5. COMANDO CIERRE (DISEÑO PROFESIONAL)
@bot.tree.command(name="cerrar_servidor", description="Anuncia el cierre profesional del servidor")
async def cerrar_servidor(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🌙 ¡FIN DE LA JORNADA! 🌙",
        description="El servidor de **Chile RP** ha finalizado sus operaciones por hoy.",
        color=discord.Color.from_rgb(231, 76, 60) # Rojo elegante
    )
    
    embed.add_field(name="🎮 Estado", value="🔴 **Offline**", inline=True)
    embed.add_field(name="⏰ Regreso", value="Mañana a la hora de siempre", inline=True)
    embed.add_field(name="💬 Soporte", value="Los tickets de soporte siguen abiertos si necesitas ayuda.", inline=False)
    
    embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM2ZicW9ueGZ4bmZ4bmZ4bmZ4bmZ4bmZ4bmZ4bmZ4bmZ4bmZ4bmZ4JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKVUn7iM8FMEU24/giphy.gif")
    embed.set_footer(text="Gracias por preferir Chile RP", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
    
    await interaction.response.send_message(content="@everyone", embed=embed)

# 6. ENCENDER BOT
keep_alive()
token = os.getenv('DISCORD_TOKEN')
bot.run(token)