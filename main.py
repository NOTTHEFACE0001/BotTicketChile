import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import datetime

# --- CONFIGURACIÓN DEL MONITOR (KEEP ALIVE) ---
app = Flask('')
@app.route('/')
def home():
    return "Bot de Chile RP está en línea 🟢"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- CONFIGURACIÓN DEL BOT ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Diccionario temporal para el historial (En un bot real, usa una base de datos)
historial_sanciones = {}

@bot.event
async def on_ready():
    print(f'✅ Conectado como {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="Moderando Chile RP 🇨🇱"))

# --- COMANDOS DE ADMINISTRACIÓN ---

@bot.command()
@commands.has_permissions(administrator=True)
async def sancionar(ctx, usuario: discord.Member, *, razon="No especificada"):
    if usuario.id not in historial_sanciones:
        historial_sanciones[usuario.id] = []
    
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    historial_sanciones[usuario.id].append(f"⚠️ {razon} ({fecha})")
    
    embed = discord.Embed(title="🚫 Jugador Sancionado", color=discord.Color.red())
    embed.add_field(name="👤 Usuario", value=usuario.mention, inline=True)
    embed.add_field(name="📝 Razón", value=razon, inline=True)
    embed.set_footer(text="Acción registrada en el historial")
    await ctx.send(embed=embed)

@bot.command()
async def historial(ctx, usuario: discord.Member):
    sanciones = historial_sanciones.get(usuario.id, [])
    
    embed = discord.Embed(title=f"📋 Historial de {usuario.name}", color=discord.Color.blue())
    if sanciones:
        embed.description = "\n".join(sanciones)
    else:
        embed.description = "✅ Este jugador está limpio. No tiene sanciones."
    
    await ctx.send(embed=embed)

# --- COMANDOS DE ESTADO DEL SERVIDOR ---

@bot.command()
@commands.has_permissions(administrator=True)
async def cerrar(ctx):
    embed = discord.Embed(
        title="🛑 SERVIDOR CERRADO",
        description="El servidor de Chile RP ha cerrado sus puertas por ahora.\n\n**Estado:** 🔴 Offline",
        color=discord.Color.dark_red()
    )
    embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJndzB6MHg0eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/H7ZpZ9H1OQ8A0/giphy.gif")
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def abrir(ctx):
    embed = discord.Embed(
        title="✅ SERVIDOR ABIERTO",
        description="¡Ya puedes entrar a Chile RP! Los esperamos a todos.\n\n**Estado:** 🟢 Online",
        color=discord.Color.green()
    )
    embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJndzB6MHg0eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKMGpxxcaXNmA92/giphy.gif")
    await ctx.send(embed=embed)

# --- COMANDO DE ENCUESTA ---

@bot.command()
async def encuesta(ctx, *, pregunta):
    embed = discord.Embed(
        title="📊 Nueva Encuesta",
        description=f"**{pregunta}**\n\n✅ Reacciona para votar.",
        color=discord.Color.gold(),
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_footer(text=f"Enviada por {ctx.author.display_name}")
    
    mensaje = await ctx.send(embed=embed)
    await mensaje.add_reaction("✅")
    await mensaje.add_reaction("❌")

# Iniciar servidor web y el Bot
keep_alive()
bot.run('MTQ5ODAwNDM0MzcxNzM2MzkzMw.GY60eb.OGGWmDIDN04LgqJv--n4eJEulvdv9Y48uUSsm0')