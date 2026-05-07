import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import os
import random
from datetime import datetime, timedelta

# --- CONEXIÓN PARA RENDER (Keep Alive) ---
app = Flask('')
@app.route('/')
def home(): return "🇨🇱 CHILE RP BOT ONLINE 🇨🇱"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- CONFIGURACIÓN DEL BOT ---
intents = discord.Intents.default()
intents.members = True 
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Bases de datos temporales (Se reinician si el bot se apaga)
banco_db = {}
sanciones_db = {}

@bot.event
async def on_ready():
    print(f'✅ SISTEMA CHILE RP COMPLETO ACTIVADO: {bot.user}')
    await bot.tree.sync()

# --- 🇨🇱 COMANDO: IDENTIFICACIÓN CHILENA (RUT) ---
@bot.tree.command(name="sacar_rut", description="Genera tu carnet de identidad chileno oficial")
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
    fecha_nacimiento: str # Formato: DD/MM/AAAA
):
    try:
        # Cálculo automático de edad
        nacimiento = datetime.strptime(fecha_nacimiento, "%d/%m/%Y")
        hoy = datetime.now()
        edad = hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))

        embed = discord.Embed(title="🇨🇱 REGISTRO CIVIL - CHILE RP", color=0xFF0000)
        embed.add_field(name="👤 NOMBRE COMPLETO", value=f"{nombre} {apellido}".upper(), inline=False)
        embed.add_field(name="🆔 RUT", value=rut, inline=True)
        embed.add_field(name="🩸 GRUPO SANGUÍNEO", value=sangre.upper(), inline=True)
        embed.add_field(name="💼 PROFESIÓN / OCUPACIÓN", value=ocupacion.upper(), inline=True)
        embed.add_field(name="💍 ESTADO CIVIL", value=estado_civil, inline=True)
        embed.add_field(name="📍 LUGAR DE NACIMIENTO", value=lugar_nacimiento.upper(), inline=True)
        embed.add_field(name="🎂 EDAD", value=f"{edad} AÑOS", inline=True)
        embed.set_footer(text="Documento Nacional de Identidad - Chile RP")
        
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("❌ Error: Usa el formato DD/MM/AAAA para la fecha (Ejemplo: 25/12/1995)")

# --- 📊 COMANDO: ENCUESTA ---
@bot.tree.command(name="encuesta", description="Crear una votación rápida")
async def encuesta(interaction: discord.Interaction, pregunta: str):
    embed = discord.Embed(title="📊 ENCUESTA - CHILE RP", description=pregunta, color=0x00FF00)
    await interaction.response.send_message(embed=embed)
    mensaje = await interaction.original_response()
    await mensaje.add_reaction("✅")
    await mensaje.add_reaction("❌")

# --- 🚨 COMANDOS: MODERACIÓN Y SANCIONES ---
@bot.tree.command(name="sancionar", description="Poner una ficha criminal")
async def sancionar(interaction: discord.Interaction, usuario: discord.Member, tipo: str, motivo: str):
    user_id = str(usuario.id)
    if user_id not in sanciones_db: sanciones_db[user_id] = []
    id_s = random.randint(1000, 9999)
    sanciones_db[user_id].append({"id": id_s, "tipo": tipo, "motivo": motivo.upper()})
    await interaction.response.send_message(f"🚨 **FICHA #{id_s}** registrada para {usuario.mention}")

@bot.tree.command(name="historial", description="Ver historial de fichas")
async def historial(interaction: discord.Interaction, usuario: discord.Member):
    user_id = str(usuario.id)
    if user_id in sanciones_db and sanciones_db[user_id]:
        msg = f"📋 **EXPEDIENTE DE {usuario.name}:**\n"
        for s in sanciones_db[user_id]: msg += f"🔹 `#{s['id']}` | {s['tipo']}: {s['motivo']}\n"
        await interaction.response.send_message(msg)
    else: await interaction.response.send_message("✅ Este ciudadano no tiene fichas.")

@bot.tree.command(name="eliminar_sancion", description="Borrar una ficha por ID")
async def eliminar(interaction: discord.Interaction, usuario: discord.Member, id_ficha: int):
    user_id = str(usuario.id)
    if user_id in sanciones_db:
        original = len(sanciones_db[user_id])
        sanciones_db[user_id] = [s for s in sanciones_db[user_id] if s['id'] != id_ficha]
        if len(sanciones_db[user_id]) < original:
            await interaction.response.send_message(f"✅ Ficha **#{id_ficha}** eliminada.")
        else: await interaction.response.send_message("❌ ID de ficha no encontrada.")

# --- 🔓 COMANDOS: ESTADO DEL SERVIDOR ---
@bot.tree.command(name="abrir_servidor", description="Anunciar apertura")
async def abrir(interaction: discord.Interaction):
    embed = discord.Embed(title="🟢 SERVIDOR ABIERTO", description="¡Chile RP está **ONLINE**! Ya pueden entrar.", color=0x00FF00)
    await interaction.response.send_message("@everyone", embed=embed)

@bot.tree.command(name="cerrar_servidor", description="Anunciar cierre")
async def cerrar(interaction: discord.Interaction, motivo: str):
    embed = discord.Embed(title="🔴 SERVIDOR CERRADO", description=f"El servidor está **OFFLINE**.\n**Motivo:** {motivo}", color=0xFF0000)
    await interaction.response.send_message("@everyone", embed=embed)

# --- 🏦 COMANDO: BANCO ---
@bot.tree.command(name="mi_banco", description="Ver saldo")
async def banco(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    balance = banco_db.get(user_id, 50000) # Saldo inicial de 50k
    await interaction.response.send_message(f"🏦 **BANCO DE CHILE:** Tienes **${balance:,}** pesos.")

# --- INICIO DEL BOT ---
keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))