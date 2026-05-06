import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import os
import datetime
import random

# --- 1. CONEXIÓN PARA MANTENERLO ONLINE ---
app = Flask('')
@app.route('/')
def home(): return "🇨🇱 CHILE RP ULTIMATE ENGINE ONLINE 🇨🇱"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- 2. CONFIGURACIÓN DEL BOT ---
intents = discord.Intents.default()
intents.members = True 
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Bases de Datos Temporales
dni_db = {}
banco_db = {}
fichas_db = {} # {user_id: [lista_de_antecedentes]}

# --- GIFs ESTILO STICKER CHISTOSOS ---
GIFS = {
    "APERTURA": "https://media.tenor.com/J36vR4Jg884AAAAM/chile-dance.gif",
    "CIERRE": "https://media.tenor.com/Oy68mD9A0kQAAAAM/sad-kitten.gif",
    "POLICIA": "https://media.tenor.com/C7YIu6A_xX4AAAAM/fbi-fbi-open-up.gif",
    "BANCO": "https://media.tenor.com/2PzQ8Y6_jHwAAAAM/money-stack.gif",
    "DNI": "https://media.tenor.com/fU6V3iI_5XkAAAAM/inspecting-cat.gif",
    "CEMENTERIO": "https://media.tenor.com/rN4YQG_M5nMAAAAM/game-over.gif"
}

@bot.event
async def on_ready():
    print(f'✅ SISTEMA UNIFICADO CHILE RP: {bot.user.name}')
    await bot.tree.sync()

# --- 3. SISTEMA DE FICHAS Y ANTECEDENTES (POLICIAL) ---
@bot.tree.command(name="fichar_sujeto", description="PONER ANTECEDENTES A UN WEÓN")
async def fichar(interaction: discord.Interaction, usuario: discord.Member, delito: str):
    user_id = str(usuario.id)
    if user_id not in fichas_db: fichas_db[user_id] = []
    
    fecha = datetime.date.today().strftime("%d/%m/%Y")
    fichas_db[user_id].append(f"[{fecha}] - {delito.upper()}")
    
    embed = discord.Embed(title="👮 ¡¡SUJETO FICHADO POR LA LEY!! 👮", color=0x00247d)
    embed.add_field(name="👤 SOSPECHOSO:", value=usuario.mention)
    embed.add_field(name="📝 DELITO:", value=delito.upper())
    embed.set_image(url=GIFS["POLICIA"])
    embed.set_footer(text="REGISTRO DE CARABINEROS DE CHILE RP")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ver_antecedentes", description="REVISAR LA FICHA POLICIAL")
async def ver_fichas(interaction: discord.Interaction, usuario: discord.Member):
    user_id = str(usuario.id)
    embed = discord.Embed(title=f"📋 ANTECEDENTES: {usuario.name.upper()}", color=0xe74c3c)
    
    if user_id in fichas_db and fichas_db[user_id]:
        lista = "\n".join(fichas_db[user_id])
        embed.description = f"**HISTORIAL CRIMINAL:**\n{lista}"
    else:
        embed.description = "✅ **ESTE CIUDADANO ESTÁ LIMPIO, POR AHORA...**"
    
    embed.set_thumbnail(url=usuario.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# --- 4. SISTEMA DE BANCO (PESOS CHILENOS) ---
@bot.tree.command(name="cajero", description="VER TU PLATA")
async def cajero(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    saldo = banco_db.get(user_id, 5000) # Empiezan con 5 lucas
    banco_db[user_id] = saldo
    
    embed = discord.Embed(title="🏦 BANCO ESTADO CHILE RP", color=0x2ecc71)
    embed.add_field(name="💰 SALDO:", value=f"${saldo:,} CLP")
    embed.set_thumbnail(url=GIFS["BANCO"])
    await interaction.response.send_message(embed=embed)

# --- 5. DNI CON RUT Y APELLIDO ---
@bot.tree.command(name="registrar_dni", description="SACAR EL RUT OFICIAL")
async def registrar(interaction: discord.Interaction, nombre: str, apellido: str, rut: str, edad: int):
    user_id = str(interaction.user.id)
    dni_db[user_id] = {"nombre": nombre.upper(), "apellido": apellido.upper(), "rut": rut, "edad": edad}
    
    embed = discord.Embed(title="📇 REGISTRO CIVIL EXITOSO", color=0xffffff)
    embed.add_field(name="👤 NOMBRE:", value=f"{nombre} {apellido}".upper())
    embed.add_field(name="🆔 RUT:", value=rut)
    embed.set_image(url=GIFS["DNI"])
    await interaction.response.send_message(embed=embed)

# --- 6. COMANDOS DE LA CIUDAD (APERTURA/CIERRE) ---
@bot.tree.command(name="abrir_ciudad", description="ANUNCIO DE CIUDAD ONLINE")
async def abrir(interaction: discord.Interaction):
    embed = discord.Embed(title="🇨🇱 ¡¡LA CIUDAD TÁ ONLINE, WEÓN!! 🇨🇱", description="**¡¡ENTREN YA O SE QUEDAN SIN ROL!!** 🏙️🔥", color=0x00ff00)
    embed.set_image(url=GIFS["APERTURA"])
    await interaction.response.send_message(content="@everyone", embed=embed)

# --- 7. SANCIONES Y CK ---
@bot.tree.command(name="realizar_ck", description="CHARACTER KILL TOTAL")
async def ck(interaction: discord.Interaction, usuario: discord.Member, motivo: str):
    embed = discord.Embed(title="💀 ¡¡CK TOTAL: GAME OVER!! 💀", description=f"**{usuario.mention} PASÓ A MEJOR VIDA.**", color=0x000000)
    embed.add_field(name="💬 MOTIVO:", value=motivo.upper())
    embed.set_image(url=GIFS["CEMENTERIO"])
    await interaction.response.send_message(embed=embed)

# --- ENCENDIDO ---
keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))