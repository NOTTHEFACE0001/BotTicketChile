import discord
from discord import app_commands
from discord.ext import commands
import datetime
import random
import os

# ==========================================
# 1. CONFIGURACIÓN DEL BOT
# ==========================================
class MyBot(commands.Bot):
    def __init__(self):
        # Usamos todos los privilegios para que no falte nada
        super().__init__(command_prefix="!", intents=discord.Intents.all())

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Bot listo y sincronizado como {self.user}")

bot = MyBot()
tree = bot.tree

# Base de datos temporal (Se borra si el bot se reinicia)
antecedentes_db = {}

# ==========================================
# 2. COMANDOS DE IDENTIDAD (DNI)
# ==========================================

@tree.command(name="registrar_dni", description="Registrar un nuevo ciudadano")
async def registrar_dni(interaction: discord.Interaction, nombre_rp: str, edad: int):
    await interaction.response.send_message(f"✅ Se ha registrado el DNI de **{nombre_rp}**.", ephemeral=True)

@tree.command(name="ver_dni", description="Ver cédula de identidad")
async def ver_dni(interaction: discord.Interaction, ciudadano: discord.Member = None):
    target = ciudadano or interaction.user
    rut = f"{random.randint(10, 25)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(0, 9)}"
    
    embed = discord.Embed(title="🪪 CÉDULA DE IDENTIDAD - CHILE", color=discord.Color.blue())
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="Nombre", value=f"{target.display_name}", inline=True)
    embed.add_field(name="RUT", value=f"{rut}", inline=True)
    embed.set_footer(text="Registro Civil Chile RP")
    await interaction.response.send_message(embed=embed)

# ==========================================
# 3. SISTEMA POLICIAL (LÍNEA 74 CORREGIDA)
# ==========================================

@tree.command(name="fichar_sujeto", description="Agregar antecedentes penales")
async def fichar_sujeto(interaction: discord.Interaction, ciudadano: discord.Member, delito: str):
    user_id = str(ciudadano.id)
    fecha = datetime.datetime.now().strftime("%d/%m/%Y")
    entrada = f"• [{fecha}] {delito}\n"
    
    antecedentes_db[user_id] = antecedentes_db.get(user_id, "") + entrada
    await interaction.response.send_message(f"🚓 Ficha actualizada para {ciudadano.mention}.")

@tree.command(name="ver_antecedentes", description="Ver historial policial")
async def ver_antecedentes(interaction: discord.Interaction, ciudadano: discord.Member):
    user_id = str(ciudadano.id)
    historial = antecedentes_db.get(user_id, "Sin antecedentes registrados.")
    
    embed = discord.Embed(title=f"📁 ARCHIVO POLICIAL: {ciudadano.name}", color=0xff0000)
    
    # Esto es lo que estaba roto: lo dejamos simple para que funcione
    embed.add_field(name="Historial de Delitos", value=historial, inline=False)
    
    await interaction.response.send_message(embed=embed)

# ==========================================
# 4. COMANDOS DE ROL (ENTORNO Y OTROS)
# ==========================================

@tree.command(name="entorno", description="Enviar un aviso de entorno")
async def entorno(interaction: discord.Interaction, suceso: str, lugar: str, tiempo: str):
    # CORRECCIÓN ADICIONAL: Sin comillas triples para evitar fallos
    embed = discord.Embed(title="🚨 AVISO DE ENTORNO", color=0x2b2d31)
    embed.add_field(name="Suceso", value=suceso, inline=False)
    embed.add_field(name="Lugar", value=lugar, inline=True)
    embed.add_field(name="Hora/Tiempo", value=tiempo, inline=True)
    embed.set_footer(text=f"Aviso por: {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)

@tree.command(name="realizar_ck", description="Registrar muerte permanente (CK)")
async def realizar_ck(interaction: discord.Interaction, ciudadano: discord.Member, razon: str):
    await interaction.response.send_message(f"💀 **CHARACTER KILL:** {ciudadano.mention} ha fallecido. Razón: {razon}")

@tree.command(name="encuesta", description="Crear votación")
async def encuesta(interaction: discord.Interaction, pregunta: str):
    embed = discord.Embed(title="📊 ENCUESTA", description=pregunta, color=discord.Color.gold())
    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")

# ==========================================
# 5. EJECUCIÓN
# ==========================================
# Reemplaza el Token o usa variables de entorno
token = os.environ.get('MTQ5ODAwNDM0MzcxNzM2MzkzMw.G2icV9.WWk4EYtaz7tUbKqVElBB4oVo1v2a38DXkzo-9g') 
if token:
    bot.run(TOKEN)
else:
    print("Error: No se encontró el TOKEN en las variables de entorno.")