import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import os
import random
from datetime import datetime, timedelta

# --- CONEXIÓN PARA RENDER ---
app = Flask('')
@app.route('/')
def home(): return "🇨🇱 CHILE RP ONLINE 🇨🇱"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- CONFIGURACIÓN DEL BOT ---
intents = discord.Intents.default()
intents.members = True 
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Bases de datos temporales
banco_db = {}
sanciones_db = {}

@bot.event
async def on_ready():
    print(f'✅ CHILE RP ACTIVADO: {bot.user}')
    await bot.tree.sync()

# --- 🇨🇱 COMANDO: SACAR RUT (CHILE) ---
@bot.tree.command(name="sacar_rut", description="Genera tu carnet de identidad chileno")
@app_commands.choices(estado_civil=[
    app_commands.Choice(name="SOLTERO/A", value="SOLTERO/A"),
    app_commands.Choice(name="CASADO/A", value="CASADO/A")
])
async def rut_chile(
    interaction: discord.Interaction, 
    nombre: str, 
    apellido: str, 
    rut: str, 
    sangre: str, 
    ocupacion: str, 
    estado_civil: str, 
    lugar_nacimiento: str, 
    fecha_nacimiento: str
):
    try:
        # Cálculo de edad
        nacimiento = datetime.strptime(fecha_nacimiento, "%d/%m/%Y")
        hoy = datetime.now()
        edad = hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))

        embed = discord.Embed(title="🇨🇱 REGISTRO CIVIL - CHILE RP", color=0xFF0000)
        embed.add_field(name="👤 NOMBRE COMPLETO", value=f"{nombre} {apellido}".upper(), inline=False)
        embed.add_field(name="🆔 RUT", value=rut, inline=True)
        embed.add_field(name="🩸 GRUPO SANGUÍNEO", value=sangre.upper(), inline=True)
        embed.add_field(name="💼 PROFESIÓN", value=ocupacion.upper(), inline=True)
        embed.add_field(name="💍 ESTADO CIVIL", value=estado_civil, inline=True)
        embed.add_field(name="📍 ORIGEN", value=lugar_nacimiento.upper(), inline=True)
        embed.add_field(name="🎂 EDAD", value=f"{edad} AÑOS", inline=True)
        embed.set_footer(text="Documento Nacional de Identidad - Chile RP")
        
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error en los datos o formato de fecha (DD/MM/AAAA).")

# --- 📊 OTROS COMANDOS (MANTENIDOS) ---
@bot.tree.command(name="encuesta", description="Crear votación")
async def encuesta(interaction: discord.Interaction, pregunta: str):
    embed = discord.Embed(title="📊 ENCUESTA", description=pregunta, color=0x00FF00)
    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")

@bot.tree.command(name="abrir_servidor")
async def abrir(interaction: discord.Interaction):
    await interaction.response.send_message("🟢 **SERVIDOR ONLINE** @everyone")

@bot.tree.command(name="cerrar_servidor")
async def cerrar(interaction: discord.Interaction, motivo: str):
    await interaction.response.send_message(f"🔴 **SERVIDOR CERRADO:** {motivo} @everyone")

# --- INICIO ---
keep_alive()
try:
    bot.run(os.getenv('DISCORD_TOKEN'))
except Exception as e:
    print(f"❌ ERROR CRÍTICO AL INICIAR: {e}")