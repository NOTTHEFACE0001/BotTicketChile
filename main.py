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
def home(): return "Sistema de Justicia Chile RP Activo ⚖️"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# 2. CONFIGURACIÓN DEL BOT
intents = discord.Intents.default()
intents.members = True 
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# BASE DE DATOS TEMPORAL
sanciones_db = {} 

@bot.event
async def on_ready():
    print(f'✅ Sistema de Justicia Conectado como {bot.user.name}')
    await bot.tree.sync()

# --- COMANDO ÚNICO DE SANCIÓN PROFESIONAL ---

@bot.tree.command(name="sancionar", description="Menú completo de sanciones")
@app_commands.choices(accion=[
    app_commands.Choice(name="Advertencia (Warn)", value="warn"),
    app_commands.Choice(name="Mutear (Timeout)", value="mute"),
    app_commands.Choice(name="Expulsar (Kick)", value="kick"),
    app_commands.Choice(name="Lista Negra (Blacklist/Ban)", value="ban")
])
async def sancionar(
    interaction: discord.Interaction, 
    usuario: discord.Member, 
    accion: str, 
    motivo: str, 
    pruebas: str, 
    tiempo_minutos: int = 0
):
    user_id = str(usuario.id)
    if user_id not in sanciones_db:
        sanciones_db[user_id] = []

    embed = discord.Embed(title="🛡️ REGISTRO DE SANCIÓN", color=discord.Color.dark_red())
    detalles_sancion = ""

    # LÓGICA DE CADA ACCIÓN
    if accion == "warn":
        detalles_sancion = "⚠️ ADVERTENCIA"
        embed.color = discord.Color.gold()
        
    elif accion == "mute":
        if tiempo_minutos > 0:
            tiempo = datetime.timedelta(minutes=tiempo_minutos)
            await usuario.timeout(tiempo, reason=motivo)
            detalles_sancion = f"🔇 MUTE ({tiempo_minutos} min)"
        else:
            await interaction.response.send_message("❌ Debes poner un tiempo en minutos para mutear.", ephemeral=True)
            return

    elif accion == "kick":
        await usuario.kick(reason=motivo)
        detalles_sancion = "👢 EXPULSIÓN (KICK)"

    elif accion == "ban":
        await usuario.ban(reason=motivo)
        detalles_sancion = "🚫 BLACKLIST (BAN)"

    # GUARDAR EN HISTORIAL
    sanciones_db[user_id].append({
        "tipo": detalles_sancion,
        "motivo": motivo,
        "pruebas": pruebas,
        "mod": interaction.user.name,
        "fecha": datetime.datetime.now().strftime("%d/%m/%Y")
    })

    # CONFIGURAR EMBED PARA EL CANAL
    embed.add_field(name="👤 Usuario Sancionado", value=usuario.mention, inline=True)
    embed.add_field(name="⚖️ Acción Aplicada", value=f"**{detalles_sancion}**", inline=True)
    embed.add_field(name="📝 Motivo del Rol", value=motivo, inline=False)
    embed.add_field(name="📸 Pruebas/Evidencia", value=pruebas, inline=False)
    embed.set_footer(text=f"Moderador: {interaction.user.name}")
    embed.set_thumbnail(url=usuario.display_avatar.url)

    await interaction.response.send_message(embed=embed)

# --- COMANDOS DE CONSULTA Y LIMPIEZA ---

@bot.tree.command(name="ver_historial", description="Ver expediente de un usuario")
async def ver_historial(interaction: discord.Interaction, usuario: discord.Member):
    user_id = str(usuario.id)
    if user_id not in sanciones_db or not sanciones_db[user_id]:
        await interaction.response.send_message(f"✅ El usuario {usuario.name} tiene el expediente limpio.")
        return

    embed = discord.Embed(title=f"📋 Expediente de {usuario.name}", color=discord.Color.blue())
    for i, s in enumerate(sanciones_db[user_id], 1):
        embed.add_field(
            name=f"Sanción #{i} - {s['fecha']}", 
            value=f"**Tipo:** {s['tipo']}\n**Motivo:** {s['motivo']}\n**Pruebas:** {s['pruebas']}\n**Mod:** {s['mod']}", 
            inline=False
        )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="borrar_historial", description="Elimina todas las sanciones de un usuario")
async def borrar_historial(interaction: discord.Interaction, usuario: discord.Member):
    sanciones_db[str(usuario.id)] = []
    await interaction.response.send_message(f"🧹 Historial de {usuario.mention} borrado correctamente.")

# --- COMANDOS DE ESTADO ---
@bot.tree.command(name="abrir_servidor", description="Anuncio de apertura")
async def abrir_servidor(interaction: discord.Interaction):
    await interaction.response.send_message(content="@everyone", embed=discord.Embed(title="✅ SERVIDOR ABIERTO", color=discord.Color.green()))

@bot.tree.command(name="cerrar_servidor", description="Anuncio de cierre")
async def cerrar_servidor(interaction: discord.Interaction):
    await interaction.response.send_message(content="@everyone", embed=discord.Embed(title="❌ SERVIDOR CERRADO", color=discord.Color.red()))

# 3. ENCENDER
keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))