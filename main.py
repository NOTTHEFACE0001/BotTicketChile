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

# --- 🆔 REGISTRO CIVIL (ACTUALIZADO SIN BORRAR LO OTRO) ---
@bot.tree.command(name="registrar_dni", description="Registro Civil")
@app_commands.choices(
    estado_civil=[
        app_commands.Choice(name="💍 CASADO/A", value="CASADO/A"),
        app_commands.Choice(name="👤 SOLTERO/A", value="SOLTERO/A")
    ],
    sexo=[
        app_commands.Choice(name="👨 MASCULINO", value="MASCULINO"),
        app_commands.Choice(name="👩 FEMENINO", value="FEMENINO")
    ]
)
async def registrar_dni(interaction: discord.Interaction, nombre: str, apellido: str, rut: str, sangre: str, ocupacion: str, estado_civil: str, sexo: str, pais_origen: str, lugar_nacimiento: str, fecha_nacimiento: str):
    # Cálculo de edad
    try:
        fecha_nac = datetime.strptime(fecha_nacimiento, "%d/%m/%Y")
        hoy = datetime.today()
        edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
    except ValueError:
        return await interaction.response.send_message("❌ Formato de fecha inválido. Usa: DD/MM/AAAA", ephemeral=True)

    # Fecha de expiración (10 años)
    fecha_exp = hoy.strftime(f"%d/%m/{hoy.year + 10}")

    usuarios_dni[str(interaction.user.id)] = {
        "nombre": f"{nombre} {apellido}".upper(),
        "rut": rut.upper(),
        "sangre": sangre.upper(),
        "ocupacion": ocupacion.upper(),
        "estado": estado_civil,
        "sexo": sexo,
        "pais": pais_origen.upper(),
        "edad": str(edad),
        "lugar": lugar_nacimiento.upper(),
        "fecha": fecha_nacimiento,
        "expira": fecha_exp
    }
    
    embed = discord.Embed(title="💻 REGISTRO CIVIL EXITOSO", color=0xFFFFFF)
    embed.add_field(name="👤 NOMBRE:", value=f"{nombre} {apellido}".upper(), inline=False)
    embed.add_field(name="🆔 RUT:", value=rut.upper(), inline=True)
    embed.add_field(name="🎂 EDAD:", value=f"{edad} AÑOS", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ver_dni", description="Ver el DNI")
async def ver_dni(interaction: discord.Interaction, usuario: discord.Member):
    datos = usuarios_dni.get(str(usuario.id))
    if datos:
        embed = discord.Embed(title=f"🇨🇱 DNI DE {datos['nombre']}", color=0x0000FF)
        embed.add_field(name="🆔 RUT", value=f"`{datos['rut']}`", inline=True)
        embed.add_field(name="🧬 SANGRE", value=f"`{datos['sangre']}`", inline=True)
        embed.add_field(name="🛠️ OCUPACIÓN", value=f"`{datos['ocupacion']}`", inline=True)
        embed.add_field(name="🚻 SEXO", value=f"`{datos['sexo']}`", inline=True)
        embed.add_field(name="🎂 EDAD", value=f"`{datos['edad']} AÑOS`", inline=True)
        embed.add_field(name="💍 ESTADO", value=f"`{datos['estado']}`", inline=True)
        embed.add_field(name="🌎 PAÍS", value=f"`{datos['pais']}`", inline=True)
        embed.add_field(name="📍 LUGAR NAC.", value=f"`{datos['lugar']}`", inline=True)
        embed.add_field(name="📆 EXPIRACIÓN", value=f"`{datos['expira']}`", inline=True)
        embed.set_thumbnail(url=usuario.display_avatar.url)
        await interaction.response.send_message(embed=embed)
    else: await interaction.response.send_message("❌ Sin registro.")

# --- 🚔 COMANDOS POLICIALES Y MUERTE (SIN CAMBIOS) ---
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

# --- ⚖️ APELACIÓN (SIN CAMBIOS) ---
@bot.tree.command(name="apelar", description="Enviar una apelación de sanción o CK")
@app_commands.choices(tipo_apelacion=[
    app_commands.Choice(name="Apelar Sanción / Ficha", value="Sanción Policial"),
    app_commands.Choice(name="Apelar CK (Character Kill)", value="CK (Muerte Total)")
])
async def apelar(interaction: discord.Interaction, tipo_apelacion: str, motivo: str):
    canal_staff = discord.utils.get(interaction.guild.channels, name="apelaciones-staff")
    embed = discord.Embed(title="⚖️ NUEVA SOLICITUD DE APELACIÓN", color=0xE74C3C)
    embed.add_field(name="👤 USUARIO:", value=interaction.user.mention, inline=True)
    embed.add_field(name="📁 TIPO:", value=tipo_apelacion, inline=True)
    embed.add_field(name="📝 MOTIVO DE APELACIÓN:", value=motivo.upper(), inline=False)
    embed.set_footer(text=f"ID del Usuario: {interaction.user.id}")

    if canal_staff:
        await canal_staff.send(embed=embed)
        await interaction.response.send_message(f"✅ Tu apelación ha sido enviada.", ephemeral=True)
    else:
        await interaction.response.send_message("✅ Apelación enviada (Staff: cread canal 'apelaciones-staff').", embed=embed)

# --- 📢 ENTORNO (DINÁMICO) ---
@bot.tree.command(name="entorno", description="Reportar situación de entorno")
@app_commands.choices(tiempo=[
    app_commands.Choice(name="🕒 Ahora mismo", value="Ahora mismo"),
    app_commands.Choice(name="⏳ Hace 5 minutos", value="Hace 5 minutos"),
    app_commands.Choice(name="📅 Hace un rato", value="Hace un rato")
])
async def entorno(interaction: discord.Interaction, suceso: str, lugar: str, tiempo: app_commands.Choice[str]):
    embed = discord.Embed(title="✨ AVISO DE ENTORNO", color=0x2b2d31)
    embed.add_field(name="🚨 Suceso", value=f"```{suceso.upper()}
```", inline=False)
    embed.add_field(name="📍 Ubicación", value=f"`{lugar.upper()}`", inline=True)
    embed.add_field(name="⏳ Momento", value=f"`{tiempo.value}`", inline=True)
    embed.set_footer(text=f"Reportado por: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# --- 📊 GESTIÓN ---
@bot.tree.command(name="encuesta", description="Crear encuesta")
async def encuesta(interaction: discord.Interaction, pregunta: str):
    await interaction.response.send_message(f"📊 **ENCUESTA:** {pregunta}")
    msg = await interaction.original_response()
    await msg.add_reaction("✅"); await msg.add_reaction("❌")

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))