import discord
from discord import app_commands
from discord.ext import commands
import datetime
import random

# ==========================================
# 1. DEFINICIÓN DEL BOT (PRIMERO QUE TODO)
# ==========================================
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())

    async def setup_hook(self):
        # Esto sincroniza los comandos para que aparezcan en Discord
        await self.tree.sync()
        print(f"Bot conectado como {self.user}")

bot = MyBot()
tree = bot.tree

# Base de datos temporal para antecedentes
antecedentes_db = {}

# ==========================================
# 2. COMANDOS DE IDENTIDAD (DNI) Y ENTORNO
# ==========================================

@tree.command(name="registrar_dni", description="Registrar un nuevo DNI en el sistema")
async def registrar_dni(interaction: discord.Interaction, nombre_rp: str, edad: int):
    # Comando de la foto 64444.jpg
    await interaction.response.send_message(f"✅ DNI registrado para **{nombre_rp}** ({edad} años).", ephemeral=True)

@tree.command(name="ver_dni", description="Ver el DNI de un ciudadano")
async def ver_dni(interaction: discord.Interaction, ciudadano: discord.Member = None):
    # Comando de la foto 64444.jpg con diseño dinámico
    user = ciudadano or interaction.user
    rut = f"{random.randint(10, 25)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(0, 9)}"
    
    embed = discord.Embed(title="🪪 CÉDULA DE IDENTIDAD - CHILE", color=discord.Color.blue())
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="Nombre", value=f"**{user.display_name}**", inline=True)
    embed.add_field(name="RUT", value=f"`{rut}`", inline=True)
    embed.add_field(name="Nacionalidad", value="Chilena", inline=True)
    embed.set_footer(text="Registro Civil - Chile RP")
    await interaction.response.send_message(embed=embed)

@tree.command(name="entorno", description="Enviar un aviso de entorno")
@app_commands.describe(suceso="¿Qué ocurre?", lugar="¿Dónde?", tiempo="¿Cuándo?")
async def entorno(interaction: discord.Interaction, suceso: str, lugar: str, tiempo: str):
    # LÍNEA 135 CORREGIDA (Error de la foto 0c62d88c-c3e9-4ebf-b1d2-9f86cab0ae69)
    embed = discord.Embed(title="✨ AVISO DE ENTORNO", color=0x2b2d31)
    embed.add_field(name="🚨 Suceso", value=f"**{suceso.upper()}**", inline=False)
    embed.add_field(name="📍 Ubicación", value=f"`{lugar}`", inline=True)
    embed.add_field(name="⏳ Momento", value=f"`{tiempo}`", inline=True)
    embed.set_footer(text=f"Reportado por: {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)

# ==========================================
# 3. SISTEMA POLICIAL Y ANTECEDENTES
# ==========================================

@tree.command(name="fichar_sujeto", description="Colocar antecedentes a un ciudadano")
async def fichar_sujeto(interaction: discord.Interaction, ciudadano: discord.Member, delito: str):
    # Comando de la foto 64443.jpg
    user_id = str(ciudadano.id)
    fecha = datetime.datetime.now().strftime("%d/%m/%Y")
    nuevo_registro = f"[{fecha}] - {delito}\n"
    
    antecedentes_db[user_id] = antecedentes_db.get(user_id, "") + nuevo_registro
    await interaction.response.send_message(f"🚓 Ficha policial actualizada para {ciudadano.mention}.")

@tree.command(name="ver_antecedentes", description="Ver la ficha policial de un sujeto")
async def ver_antecedentes(interaction: discord.Interaction, ciudadano: discord.Member):
    user_id = str(ciudadano.id)
    registros = antecedentes_db.get(user_id, "Sin antecedentes penales.")
    
    embed = discord.Embed(title=f"📁 ANTECEDENTES: {ciudadano.name}", color=discord.Color.dark_red())
    embed.add_field(name="Historial", value=f"```{registros}
```", inline=False)
    await interaction.response.send_message(embed=embed)

@tree.command(name="borrar_antecedentes", description="Limpiar el historial de un sujeto")
@app_commands.checks.has_permissions(administrator=True)
async def borrar_antecedentes(interaction: discord.Interaction, ciudadano: discord.Member):
    user_id = str(ciudadano.id)
    if user_id in antecedentes_db:
        del antecedentes_db[user_id]
        await interaction.response.send_message(f"✅ Antecedentes de {ciudadano.name} borrados.", ephemeral=True)
    else:
        await interaction.response.send_message("El ciudadano no tiene antecedentes.", ephemeral=True)

@tree.command(name="realizar_ck", description="Registrar un Character Kill")
async def realizar_ck(interaction: discord.Interaction, ciudadano: discord.Member, razon: str):
    # Comando de la foto 64443.jpg
    await interaction.response.send_message(f"💀 Se ha realizado un CK al usuario {ciudadano.mention}. Razón: {razon}")

# ==========================================
# 4. OTROS COMANDOS (ENCUESTA, APELAR)
# ==========================================

@tree.command(name="encuesta", description="Crear una encuesta rápida")
async def encuesta(interaction: discord.Interaction, pregunta: str):
    # Comando de la foto 64443.jpg
    embed = discord.Embed(title="📊 ENCUESTA", description=pregunta, color=discord.Color.purple())
    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")

@tree.command(name="apelar", description="Enviar una apelación de sanción o CK")
async def apelar(interaction: discord.Interaction, mensaje: str):
    # Comando de la foto 64442.jpg
    await interaction.response.send_message("✅ Tu apelación ha sido enviada al Staff.", ephemeral=True)

# ==========================================
# 5. EJECUCIÓN
# ==========================================
# bot.run("TU_TOKEN_AQUI")