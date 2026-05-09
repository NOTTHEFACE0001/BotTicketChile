import discord
from discord.ext import commands
from discord import app_commands, ui
from flask import Flask
from threading import Thread
import os
from datetime import datetime

# --- CONEXIÓN PARA RENDER ---
app = Flask('')
@app.route('/')
def home(): return "🇨🇱 CHILE RP ONLINE 🇨🇱"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- CONFIGURACIÓN ---
intents = discord.Intents.default()
intents.members = True 
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Bases de datos temporales
sanciones_db = {}
usuarios_dni = {}

@bot.event
async def on_ready():
    print(f'✅ BOT CHILE RP READY: {bot.user}')
    await bot.tree.sync()

# --- 🆔 REGISTRO CIVIL (DNI ORIGINAL) ---
@bot.tree.command(name="registrar_dni", description="Registro Civil")
@app_commands.choices(estado_civil=[
    app_commands.Choice(name="SOLTERO/A", value="SOLTERO/A"),
    app_commands.Choice(name="CASADO/A", value="CASADO/A")
])
async def registrar_dni(interaction: discord.Interaction, nombre: str, apellido: str, rut: str, sangre: str, ocupacion: str, estado_civil: str, lugar_nacimiento: str, fecha_nacimiento: str):
    usuarios_dni[str(interaction.user.id)] = {
        "nombre": f"{nombre} {apellido}".upper(),
        "rut": rut,
        "sangre": sangre,
        "ocupacion": ocupacion,
        "estado": estado_civil,
        "lugar": lugar_nacimiento,
        "fecha": fecha_nacimiento
    }
    embed = discord.Embed(title="💻 REGISTRO CIVIL EXITOSO", color=0xFFFFFF)
    embed.add_field(name="👤 NOMBRE:", value=f"{nombre} {apellido}".upper(), inline=False)
    embed.add_field(name="🆔 RUT:", value=rut, inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ver_dni", description="Ver el DNI")
async def ver_dni(interaction: discord.Interaction, usuario: discord.Member):
    datos = usuarios_dni.get(str(usuario.id))
    if datos:
        embed = discord.Embed(title=f"🇨🇱 DNI DE {datos['nombre']}", color=0x0000FF)
        for c, v in datos.items(): embed.add_field(name=c.upper(), value=v, inline=True)
        await interaction.response.send_message(embed=embed)
    else: await interaction.response.send_message("❌ Sin registro.")

# --- 🚔 COMANDOS POLICIALES Y MUERTE ---
@bot.tree.command(name="fichar_sujeto", description="Colocar antecedentes")
async def fichar(interaction: discord.Interaction, usuario: discord.Member, delito: str):
    if str(usuario.id) not in sanciones_db: sanciones_db[str(usuario.id)] = []
    sanciones_db[str(usuario.id)].append(delito.upper())
    await interaction.response.send_message(f"👮‍♂️ **SUJETO FICHADO:** {usuario.mention}\n📝 **DELITO:** {delito.upper()}")

@bot.tree.command(name="realizar_ck", description="Character Kill")
async def ck(interaction: discord.Interaction, usuario: discord.Member, motivo: str):
    usuarios_dni.pop(str(usuario.id), None)
    sanciones_db.pop(str(usuario.id), None)
    await interaction.response.send_message(f"💀 **{usuario.name} HA PASADO A MEJOR VIDA.**\n💬 **MOTIVO:** {motivo.upper()}")

# --- ⚖️ NUEVO COMANDO DE APELACIÓN INDEPENDIENTE ---
@bot.tree.command(name="apelar", description="Enviar una apelación de sanción o CK")
@app_commands.choices(tipo_apelacion=[
    app_commands.Choice(name="Apelar Sanción / Ficha", value="Sanción Policial"),
    app_commands.Choice(name="Apelar CK (Character Kill)", value="CK (Muerte Total)")
])
async def apelar(interaction: discord.Interaction, tipo_apelacion: str, motivo: str):
    # Canal donde el Staff recibe las apelaciones
    canal_staff = discord.utils.get(interaction.guild.channels, name="apelaciones-staff")
    
    embed = discord.Embed(title="⚖️ NUEVA SOLICITUD DE APELACIÓN", color=0xE74C3C)
    embed.add_field(name="👤 USUARIO:", value=interaction.user.mention, inline=True)
    embed.add_field(name="📁 TIPO:", value=tipo_apelacion, inline=True)
    embed.add_field(name="📝 MOTIVO DE APELACIÓN:", value=motivo.upper(), inline=False)
    embed.set_footer(text=f"ID del Usuario: {interaction.user.id}")

    if canal_staff:
        await canal_staff.send(embed=embed)
        await interaction.response.send_message(f"✅ {interaction.user.mention}, tu apelación por **{tipo_apelacion}** ha sido enviada al Staff.", ephemeral=True)
    else:
        # Si no existe el canal, lo envía al canal donde se usó el comando
        await interaction.response.send_message("✅ Apelación enviada (Staff: cread canal 'apelaciones-staff' para recibir esto en privado).", embed=embed)

# --- 📊 GESTIÓN DEL SERVIDOR ---
@bot.tree.command(name="encuesta", description="Crear encuesta")
async def encuesta(interaction: discord.Interaction, pregunta: str):
    await interaction.response.send_message(f"📊 **ENCUESTA:** {pregunta}")
    msg = await interaction.original_response()
    await msg.add_reaction("✅"); await msg.add_reaction("❌")

@bot.tree.command(name="abrir_servidor")
async def abrir(interaction: discord.Interaction):
    await interaction.response.send_message("🟢 **SERVIDOR ABIERTO** @everyone")

@bot.tree.command(name="cerrar_servidor")
async def cerrar(interaction: discord.Interaction, motivo: str):
    await interaction.response.send_message(f"🔴 **SERVIDOR CERRADO:** {motivo} @everyone")

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))