import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import os
import datetime

# 1. SERVIDOR WEB PARA RENDER
app = Flask('')
@app.route('/')
def home(): return "Sistema Chile RP Todo-en-Uno Activo ⚖️📊"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# 2. CONFIGURACIÓN DEL BOT
intents = discord.Intents.default()
intents.members = True 
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

sanciones_db = {} 

@bot.event
async def on_ready():
    print(f'✅ Bot Conectado: {bot.user.name}')
    await bot.tree.sync()

# --- 📊 COMANDO DE ENCUESTA (EL QUE FALTABA) ---
@bot.tree.command(name="encuesta", description="Crea una encuesta rápida con reacciones")
async def encuesta(interaction: discord.Interaction, pregunta: str, opcion1: str, opcion2: str):
    embed = discord.Embed(
        title="📊 NUEVA ENCUESTA", 
        description=f"**{pregunta}**\n\n1️⃣ {opcion1}\n2️⃣ {opcion2}", 
        color=discord.Color.green()
    )
    embed.set_footer(text="¡Vota reaccionando abajo!")
    await interaction.response.send_message(embed=embed)
    # Esto es para que el bot ponga las reacciones solo
    mensaje = await interaction.original_response()
    await mensaje.add_reaction("1️⃣")
    await mensaje.add_reaction("2️⃣")

# --- ⚖️ SISTEMA DE SANCIONES COMPLETO ---
@bot.tree.command(name="sancionar", description="Menú completo de sanciones")
@app_commands.choices(accion=[
    app_commands.Choice(name="Advertencia (Warn)", value="warn"),
    app_commands.Choice(name="Mutear (Timeout)", value="mute"),
    app_commands.Choice(name="Expulsar (Kick)", value="kick"),
    app_commands.Choice(name="Lista Negra (Blacklist/Ban)", value="ban")
])
async def sancionar(interaction: discord.Interaction, usuario: discord.Member, accion: str, motivo: str, pruebas: str, tiempo_minutos: int = 0):
    user_id = str(usuario.id)
    if user_id not in sanciones_db: sanciones_db[user_id] = []

    detalles = ""
    if accion == "warn": detalles = "⚠️ ADVERTENCIA"
    elif accion == "mute":
        tiempo = datetime.timedelta(minutes=tiempo_minutos)
        await usuario.timeout(tiempo, reason=motivo)
        detalles = f"🔇 MUTE ({tiempo_minutos} min)"
    elif accion == "kick":
        await usuario.kick(reason=motivo)
        detalles = "👢 KICK"
    elif accion == "ban":
        await usuario.ban(reason=motivo)
        detalles = "🚫 BLACKLIST"

    sanciones_db[user_id].append({"tipo": detalles, "motivo": motivo, "pruebas": pruebas, "mod": interaction.user.name})

    embed = discord.Embed(title="🛡️ REGISTRO DE SANCIÓN", color=discord.Color.red())
    embed.add_field(name="Usuario", value=usuario.mention, inline=True)
    embed.add_field(name="Acción", value=detalles, inline=True)
    embed.add_field(name="Motivo", value=motivo, inline=False)
    embed.add_field(name="Pruebas", value=pruebas, inline=False)
    await interaction.response.send_message(embed=embed)

# --- 📋 COMANDOS DE HISTORIAL ---
@bot.tree.command(name="ver_historial", description="Ver expediente de un usuario")
async def ver_historial(interaction: discord.Interaction, usuario: discord.Member):
    user_id = str(usuario.id)
    if user_id not in sanciones_db or not sanciones_db[user_id]:
        await interaction.response.send_message(f"✅ {usuario.name} está limpio.")
        return
    embed = discord.Embed(title=f"📋 Historial de {usuario.name}", color=discord.Color.blue())
    for i, s in enumerate(sanciones_db[user_id], 1):
        embed.add_field(name=f"Sanción #{i}", value=f"**{s['tipo']}**\nMotivo: {s['motivo']}\nMod: {s['mod']}", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="borrar_historial", description="Limpia las sanciones")
async def borrar_historial(interaction: discord.Interaction, usuario: discord.Member):
    sanciones_db[str(usuario.id)] = []
    await interaction.response.send_message(f"🧹 Historial de {usuario.mention} borrado.")

# --- 📢 APERTURA Y CIERRE ---
@bot.tree.command(name="abrir_servidor", description="Apertura")
async def abrir_servidor(interaction: discord.Interaction):
    await interaction.response.send_message(content="@everyone", embed=discord.Embed(title="✅ SERVIDOR ABIERTO", color=discord.Color.blue()))

@bot.tree.command(name="cerrar_servidor", description="Cierre")
async def cerrar_servidor(interaction: discord.Interaction):
    await interaction.response.send_message(content="@everyone", embed=discord.Embed(title="❌ SERVIDOR CERRADO", color=discord.Color.red()))

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
