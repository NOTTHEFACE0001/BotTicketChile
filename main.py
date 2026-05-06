import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import os
import datetime

# --- 1. MANTENER ONLINE ---
app = Flask('')
@app.route('/')
def home(): return "🇨🇱 CHILE RP MODERATION ACTIVE 🇨🇱"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- 2. CONFIGURACIÓN ---
intents = discord.Intents.default()
intents.members = True 
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Bases de datos temporales
dni_db = {}
fichas_db = {}
sanciones_db = {} # {user_id: [lista_sanciones]}

@bot.event
async def on_ready():
    print(f'✅ SISTEMA DE SANCIONES VINCULADO: {bot.user.name}')
    await bot.tree.sync()

# --- 3. SISTEMA DE SANCIONES PRO ---

@bot.tree.command(name="sancionar", description="Aplicar una sanción (Advertencia, Mute, Ban)")
@app_commands.choices(tipo=[
    app_commands.Choice(name="ADVERTENCIA (WARN)", value="WARN"),
    app_commands.Choice(name="TIMEOUT (MUTE)", value="MUTE"),
    app_commands.Choice(name="BAN (BLACKIST)", value="BLACKLIST")
])
async def sancionar(interaction: discord.Interaction, usuario: discord.Member, tipo: str, motivo: str):
    user_id = str(usuario.id)
    if user_id not in sanciones_db: sanciones_db[user_id] = []
    
    fecha = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    ID_SANCION = random.randint(1000, 9999)
    nueva_sancion = {"id": ID_SANCION, "tipo": tipo, "motivo": motivo.upper(), "fecha": fecha}
    sanciones_db[user_id].append(nueva_sancion)
    
    embed = discord.Embed(title="⚠️ REGISTRO DE SANCIÓN ADMINISTRATIVA ⚠️", color=0x000000)
    embed.add_field(name="👤 Usuario:", value=usuario.mention, inline=True)
    embed.add_field(name="🆔 ID Sanción:", value=f"#{ID_SANCION}", inline=True)
    embed.add_field(name="🛠️ Tipo:", value=tipo, inline=False)
    embed.add_field(name="💬 Motivo:", value=motivo.upper(), inline=False)
    embed.set_image(url="https://media.tenor.com/f0u5H_2fG6kAAAAM/bye-bye-bye-go-away.gif")
    embed.set_footer(text=f"Fecha: {fecha} | Staff: {interaction.user.name}")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="historial_sanciones", description="Ver el historial de un usuario")
async def historial(interaction: discord.Interaction, usuario: discord.Member):
    user_id = str(usuario.id)
    embed = discord.Embed(title=f"📋 HISTORIAL DE: {usuario.name.upper()}", color=0xf1c40f)
    
    if user_id in sanciones_db and sanciones_db[user_id]:
        texto = ""
        for s in sanciones_db[user_id]:
            texto += f"**#{s['id']}** | {s['tipo']} - {s['motivo']} ({s['fecha']})\n"
        embed.description = texto
    else:
        embed.description = "✅ Este usuario no registra sanciones previas."
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="borrar_sancion", description="Eliminar una sanción específica por su ID")
async def borrar_s(interaction: discord.Interaction, usuario: discord.Member, id_sancion: int):
    user_id = str(usuario.id)
    if user_id in sanciones_db:
        original_count = len(sanciones_db[user_id])
        sanciones_db[user_id] = [s for s in sanciones_db[user_id] if s['id'] != id_sancion]
        
        if len(sanciones_db[user_id]) < original_count:
            await interaction.response.send_message(f"✅ Sanción **#{id_sancion}** eliminada del registro de {usuario.mention}.")
        else:
            await interaction.response.send_message(f"❌ No se encontró la sanción con ID **#{id_sancion}**.")
    else:
        await interaction.response.send_message("❌ El usuario no tiene sanciones.")

# --- 4. COMANDOS DE APERTURA Y CIERRE (FLOW IMAGENES) ---
@bot.tree.command(name="abrir_servidor", description="Apertura oficial")
async def abrir(interaction: discord.Interaction):
    embed = discord.Embed(title="✨ ¡ESTAMOS EN LÍNEA! ✨", color=0x3498db)
    embed.description = "El servidor de **Chile RP** ha abierto sus puertas."
    embed.add_field(name="🟢 Estado", value="Online", inline=True)
    embed.add_field(name="📍 Mapa", value="Chile Continental", inline=True)
    embed.set_footer(text="Administración de Chile RP")
    await interaction.response.send_message(content="@everyone", embed=embed)

# --- 5. ENCUESTA DINÁMICA ---
@bot.tree.command(name="encuesta", description="Crear votación")
async def encuesta(interaction: discord.Interaction, pregunta: str, opcion1: str, opcion2: str):
    embed = discord.Embed(title="📊 ENCUESTA CIUDADANA", description=f"**{pregunta.upper()}**\n\n1️⃣ {opcion1}\n2️⃣ {opcion2}", color=0xf1c40f)
    await interaction.response.send_message(embed=embed)
    m = await interaction.original_response()
    await m.add_reaction("1️⃣")
    await m.add_reaction("2️⃣")

# --- 6. REGISTRO DNI ---
@bot.tree.command(name="registrar_dni", description="Saca tu RUT")
async def registrar(interaction: discord.Interaction, nombre: str, apellido: str, rut: str, edad: int):
    user_id = str(interaction.user.id)
    dni_db[user_id] = {"nombre": nombre.upper(), "apellido": apellido.upper(), "rut": rut, "edad": edad}
    embed = discord.Embed(title="📇 REGISTRO CIVIL: DNI", color=0xffffff)
    embed.add_field(name="👤 NOMBRE:", value=f"{nombre} {apellido}".upper())
    embed.add_field(name="🆔 RUT:", value=rut)
    await interaction.response.send_message(embed=embed)

import random # Necesario para generar IDs de sanción
keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))