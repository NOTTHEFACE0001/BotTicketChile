import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import os
import datetime
import random

# --- 1. CONEXIÓN PARA MANTENERLO ONLINE 24/7 ---
app = Flask('')
@app.route('/')
def home(): return "🇨🇱 CHILE RP HUB ONLINE 😂"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- 2. CONFIGURACIÓN DEL BOT ---
intents = discord.Intents.default()
intents.members = True 
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Bases de Datos Temporales
dni_db = {}
blacklist_db = {}
sanciones_db = {}

# --- GIFs ESTILO STICKER CHISTOSOS ---
GIFS = {
    "APERTURA": "https://media.tenor.com/J36vR4Jg884AAAAM/chile-dance.gif",
    "CIERRE": "https://media.tenor.com/Oy68mD9A0kQAAAAM/sad-kitten.gif",
    "BAN": "https://media.tenor.com/f0u5H_2fG6kAAAAM/bye-bye-bye-go-away.gif",
    "CK": "https://media.tenor.com/rN4YQG_M5nMAAAAM/game-over.gif",
    "PK": "https://media.tenor.com/o5X4h37DqOAAAAAM/i-forgot.gif",
    "DNI": "https://media.tenor.com/fU6V3iI_5XkAAAAM/inspecting-cat.gif",
    "VOTO": "https://media.tenor.com/B9_V7V8z3mAAAAAM/vote-elections.gif"
}

@bot.event
async def on_ready():
    print(f'✅ EL BOT ESTÁ VIVO: {bot.user.name}')
    await bot.tree.sync()

# --- 3. COMANDOS DE APERTURA Y CIERRE ---
@bot.tree.command(name="abrir_servidor", description="ANUNCIO DE APERTURA DINÁMICO")
async def abrir(interaction: discord.Interaction):
    embed = discord.Embed(title="🇨🇱 ¡¡LA CIUDAD ESTÁ ONLINE!! 🇨🇱", description="**¡¡ENTRA YA O TE LLEVA EL CUCO, WEÓN!!** 🏙️🔥", color=0x00ff00)
    embed.set_image(url=GIFS["APERTURA"])
    await interaction.response.send_message(content="@everyone", embed=embed)

@bot.tree.command(name="cerrar_servidor", description="ANUNCIO DE CIERRE DINÁMICO")
async def cerrar(interaction: discord.Interaction):
    embed = discord.Embed(title="🔴 ¡¡CIERRE DE CIUDAD!! 🔴", description="**¡¡A DORMIR QUE MAÑANA SE LABURA!! 👋😴**", color=0xff0000)
    embed.set_image(url=GIFS["CIERRE"])
    await interaction.response.send_message(content="@everyone", embed=embed)

# --- 4. SISTEMA DE DNI PRO (RUT, APELLIDO, EDAD) ---
@bot.tree.command(name="registrar_dni", description="SACA TU RUT DE CHILE RP")
async def registrar_dni(interaction: discord.Interaction, nombre: str, apellido: str, rut: str, edad: int, nacionalidad: str):
    user_id = str(interaction.user.id)
    dni_db[user_id] = {"nombre": nombre.upper(), "apellido": apellido.upper(), "rut": rut, "edad": edad, "nacionalidad": nacionalidad.upper()}
    
    embed = discord.Embed(title="📇 ¡¡REGISTRO CIVIL EXITOSO!! 📇", description=f"**BIENVENIDO, {nombre.upper()} {apellido.upper()}**", color=0x2ecc71)
    embed.add_field(name="🆔 RUT:", value=rut, inline=True)
    embed.set_image(url=GIFS["DNI"])
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ver_dni", description="MOSTRAR LOS PAPELES")
async def ver_dni(interaction: discord.Interaction, usuario: discord.Member):
    user_id = str(usuario.id)
    if user_id in dni_db:
        d = dni_db[user_id]
        embed = discord.Embed(title=f"🪪 DNI DE {d['nombre']} {d['apellido']}", color=0xf1c40f)
        embed.add_field(name="🇨🇱 RUT:", value=d['rut'], inline=False)
        embed.add_field(name="📅 EDAD:", value=f"{d['edad']} AÑOS", inline=True)
        embed.add_field(name="🌎 NACIONALIDAD:", value=d['nacionalidad'], inline=True)
        embed.set_thumbnail(url=usuario.display_avatar.url)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("❌ ¡ESTE WEÓN NO TIENE PAPELES!")

# --- 5. CK, PK Y SANCIONES ---
@bot.tree.command(name="realizar_ck", description="GAME OVER PARA EL PERSONAJE")
async def ck(interaction: discord.Interaction, usuario: discord.Member, motivo: str):
    embed = discord.Embed(title="💀 ¡¡CK TOTAL!! 💀", description=f"**{usuario.mention} HA MUERTO PARA SIEMPRE.**", color=0x000000)
    embed.add_field(name="💬 MOTIVO:", value=motivo.upper())
    embed.set_image(url=GIFS["CK"])
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="realizar_pk", description="AMNESIA DE PERSONAJE")
async def pk(interaction: discord.Interaction, usuario: discord.Member, motivo: str):
    embed = discord.Embed(title="🤕 ¡¡PK: AMNESIA!! 🤕", description=f"**{usuario.mention} NO RECUERDA NADA.**", color=0x3498db)
    embed.set_image(url=GIFS["PK"])
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="blacklist_add", description="AÑADIR A BLACKLIST")
async def bl(interaction: discord.Interaction, usuario: discord.Member, motivo: str):
    embed = discord.Embed(title="🚫 ¡¡BLACKLIST!! 🚫", description=f"**{usuario.mention} PA' LA CASA POR WEÓN.**", color=0x000000)
    embed.add_field(name="💬 MOTIVO:", value=motivo.upper())
    embed.set_image(url=GIFS["BAN"])
    await interaction.response.send_message(embed=embed)

# --- 6. ENCUESTA Y APELACIÓN ---
@bot.tree.command(name="encuesta", description="VOTACIÓN DINÁMICA")
async def encuesta(interaction: discord.Interaction, pregunta: str, opcion1: str, opcion2: str):
    embed = discord.Embed(title="📊 ¡¡ENCUESTA CIUDADANA!! 📊", description=f"**¿{pregunta.upper()}?**\n\n1️⃣ {opcion1.upper()}\n2️⃣ {opcion2.upper()}", color=0x00ffff)
    embed.set_image(url=GIFS["VOTO"])
    await interaction.response.send_message(embed=embed)
    m = await interaction.original_response()
    await m.add_reaction("1️⃣")
    await m.add_reaction("2️⃣")

@bot.tree.command(name="apelar", description="APELAR UNA SANCIÓN")
async def apelar(interaction: discord.Interaction, motivo: str):
    embed = discord.Embed(title="⚖️ ¡¡APELACIÓN RECIBIDA!! ⚖️", description=f"**USUARIO:** {interaction.user.mention}\n**MOTIVO:** {motivo.upper()}", color=0x9b59b6)
    await interaction.response.send_message("✅ ¡APELACIÓN ENVIADA AL STAFF!", ephemeral=True)
    await interaction.channel.send(embed=embed)

# --- ENCENDIDO ---
keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))