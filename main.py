import os
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import datetime
import random

# --- CONFIGURACIÓN DEL MONITOR (KEEP ALIVE) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot de Gran Chile RP está en línea 🟢"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- CONFIGURACIÓN DEL BOT ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

LOGO_URL = "https://cdn.discordapp.com/attachments/1386117665889718392/1505025241813090434/WhatsApp_Image_2026-04-24_at_14.47.16-removebg-preview.png?ex=6a091f7b&is=6a07cdfb&hm=bc2cbacda598eb5f6d962736cf9911913fa4bc8a9a47e91bf595306f5094ffe0&"

historial_sanciones = {}

# ─────────────────────────────────────────────
#  FUNCIONES AUXILIARES
# ─────────────────────────────────────────────

def generar_rut() -> str:
    numero = random.randint(5_000_000, 25_000_000)
    dv = calcular_dv(numero)
    return f"{numero:,}".replace(",", ".") + "-" + str(dv)

def calcular_dv(rut: int) -> str:
    reversed_digits = [int(d) for d in reversed(str(rut))]
    factors = [2, 3, 4, 5, 6, 7]
    total = sum(d * factors[i % 6] for i, d in enumerate(reversed_digits))
    remainder = 11 - (total % 11)
    if remainder == 11:
        return "0"
    elif remainder == 10:
        return "K"
    return str(remainder)

def calcular_edad(fecha_nacimiento: str) -> str:
    try:
        nacimiento = datetime.datetime.strptime(fecha_nacimiento, "%d/%m/%Y")
        hoy = datetime.datetime.now()
        edad = hoy.year - nacimiento.year - (
            (hoy.month, hoy.day) < (nacimiento.month, nacimiento.day)
        )
        return str(edad)
    except ValueError:
        return "INVALIDA"

# ─────────────────────────────────────────────
#  EVENTO ON_READY (SINCRO INSTANTÁNEA POR SERVIDOR)
# ─────────────────────────────────────────────

@bot.event
async def on_ready():
    print(f'✅ Conectado como {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="Moderando Gran Chile RP 🇨🇱"))
    
    # ID de tu servidor configurado para forzar la barra instantánea
    ID_SERVIDOR = 1486083692089704619  

    try:
        print(f"🔄 Sincronizando comandos de barra en el servidor {ID_SERVIDOR}...")
        
        # 1. Copiamos el comando /dni a este servidor específico
        guild = discord.Object(id=ID_SERVIDOR)
        bot.tree.copy_global_to(guild=guild)
        
        # 2. Sincronizamos la barra directo en este server sin esperar horas
        synced = await bot.tree.sync(guild=guild)
        
        print(f"✅ ¡Listo! {len(synced)} slash command(s) activos en este servidor.")
    except Exception as e:
        print(f"❌ Error al sincronizar barra: {e}")

# ─────────────────────────────────────────────
#  SLASH COMMAND: /dni (CON TODAS LAS OPCIONES)
# ─────────────────────────────────────────────

@bot.tree.command(name="dni", description="Crea tu cédula de identidad de Gran Chile RP con opciones completas")
@app_commands.describe(
    nombre           = "Tu nombre (en el RP)",
    apellido         = "Tu apellido (en el RP)",
    nombre_roblox    = "Tu nombre de usuario en Roblox",
    fecha_nacimiento = "Tu fecha de nacimiento — formato DD/MM/AAAA",
    sexo             = "Selecciona tu sexo",
    tipo_sangre      = "Selecciona tu tipo de sangre",
    ocupacion        = "Selecciona tu ocupación en el RP",
    estado_civil     = "Selecciona tu estado civil",
    pais             = "País de origen (en el RP)",
    ciudad           = "Ciudad o localidad de origen (en el RP)"
)
@app_commands.choices(
    sexo=[
        app_commands.Choice(name="♂️ Masculino",   value="Masculino"),
        app_commands.Choice(name="♀️ Femenino",    value="Femenino"),
        app_commands.Choice(name="⚧️ No binario",  value="No binario"),
    ],
    tipo_sangre=[
        app_commands.Choice(name="🩸 A+",   value="A+"),
        app_commands.Choice(name="🩸 A-",   value="A-"),
        app_commands.Choice(name="🩸 B+",   value="B+"),
        app_commands.Choice(name="🩸 B-",   value="B-"),
        app_commands.Choice(name="🩸 AB+",  value="AB+"),
        app_commands.Choice(name="🩸 AB-",  value="AB-"),
        app_commands.Choice(name="🩸 O+",   value="O+"),
        app_commands.Choice(name="🩸 O-",   value="O-"),
    ],
    ocupacion=[
        app_commands.Choice(name="👮 Carabinero",            value="Carabinero"),
        app_commands.Choice(name="🕵️ Detective / PDI",      value="Detective / PDI"),
        app_commands.Choice(name="🚑 Paramédico / SAMU",     value="Paramédico / SAMU"),
        app_commands.Choice(name="🚒 Bombero",               value="Bombero"),
        app_commands.Choice(name="⚖️ Abogado",               value="Abogado"),
        app_commands.Choice(name="👨‍⚕️ Médico",               value="Médico"),
        app_commands.Choice(name="🏦 Empresario",            value="Empresario"),
        app_commands.Choice(name="🔧 Mecánico",              value="Mecánico"),
        app_commands.Choice(name="🚖 Taxista",               value="Taxista"),
        app_commands.Choice(name="🍳 Cocinero / Chef",       value="Cocinero / Chef"),
        app_commands.Choice(name="🏗️ Obrero / Constructor",  value="Obrero / Constructor"),
        app_commands.Choice(name="🎓 Estudiante",            value="Estudiante"),
        app_commands.Choice(name="💼 Desempleado",           value="Desempleado"),
        app_commands.Choice(name="🎭 Otros",                 value="Otros"),
    ],
    estado_civil=[
        app_commands.Choice(name="💛 Soltero/a",    value="Soltero/a"),
        app_commands.Choice(name="💍 Casado/a",     value="Casado/a"),
        app_commands.Choice(name="💔 Divorciado/a", value="Divorciado/a"),
        app_commands.Choice(name="🖤 Viudo/a",      value="Viudo/a"),
    ]
)
async def dni(
    interaction: discord.Interaction,
    nombre: str,
    apellido: str,
    nombre_roblox: str,
    fecha_nacimiento: str,
    sexo: str,              
    tipo_sangre: str,       
    ocupacion: str,         
    estado_civil: str,      
    pais: str,
    ciudad: str
):
    edad = calcular_edad(fecha_nacimiento)

    if edad == "INVALIDA":
        await interaction.response.send_message(
            "❌ Fecha inválida. Usa el formato **DD/MM/AAAA** (ejemplo: 15/03/2000).",
            ephemeral=True
        )
        return

    rut           = generar_rut()
    fecha_emision = datetime.datetime.now().strftime("%d/%m/%Y")

    embed = discord.Embed(
        title="🪪  CÉDULA DE IDENTIDAD — GRAN CHILE RP",
        description=(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🇨🇱  **REPÚBLICA DE GRAN CHILE RP**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        color=0xD52B1E,
        timestamp=datetime.datetime.utcnow()
    )

    embed.set_thumbnail(url=LOGO_URL)
    embed.set_author(name="Gran Chile RP — Registro Civil", icon_url=LOGO_URL)

    embed.add_field(name="👤 Nombre completo",     value=f"`{nombre} {apellido}`",      inline=True)
    embed.add_field(name="🎮 Usuario Roblox",      value=f"`{nombre_roblox}`",           inline=True)
    embed.add_field(name="🪪 RUT",                  value=f"`{rut}`",                     inline=True)

    embed.add_field(name="⚧️ Sexo",                 value=f"`{sexo}`",                    inline=True) 
    embed.add_field(name="🩸 Tipo de sangre",      value=f"`{tipo_sangre}`",             inline=True) 
    embed.add_field(name="💼 Ocupación",           value=f"`{ocupacion}`",               inline=True) 

    embed.add_field(name="💍 Estado civil",        value=f"`{estado_civil}`",            inline=True) 
    embed.add_field(name="🌎 País de origen",      value=f"`{pais}`",                    inline=True)
    embed.add_field(name="📍 Ciudad / Localidad",  value=f"`{ciudad}`",                  inline=True)

    embed.add_field(name="🎂 Fecha de nacimiento", value=f"`{fecha_nacimiento}`",         inline=True)
    embed.add_field(name="🔢 Edad",                value=f"`{edad} años`",               inline=True)
    embed.add_field(name="📅 Fecha de emisión",    value=f"`{fecha_emision}`",           inline=True)

    embed.add_field(
        name="\u200b",
        value=(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "✅ *Documento emitido por el Registro Civil de Gran Chile RP*\n"
            "⚠️ *Este documento es válido únicamente dentro del servidor.*"
        ),
        inline=False
    )

    embed.set_footer(
        text=f"Solicitado por {interaction.user.display_name} • Gran Chile RP",
        icon_url=interaction.user.display_avatar.url
    )

    await interaction.response.send_message(
        content=(
            f"🎉 ¡Bienvenido/a a **Gran Chile RP**, {nombre}!\n"
            f"Tu cédula de identidad ha sido creada exitosamente. 🇨🇱"
        ),
        embed=embed
    )

# ─────────────────────────────────────────────
#  COMANDOS CLÁSICOS (PREFIX !)
# ─────────────────────────────────────────────

@bot.command()
@commands.has_permissions(administrator=True)
async def sancionar(ctx, usuario: discord.Member, *, razon="No especificada"):
    if usuario.id not in historial_sanciones:
        historial_sanciones[usuario.id] = []
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    historial_sanciones[usuario.id].append(f"⚠️ {razon} ({fecha})")
    embed = discord.Embed(title="🚫 Jugador Sancionado", color=discord.Color.red())
    embed.set_thumbnail(url=LOGO_URL)
    embed.add_field(name="👤 Usuario", value=usuario.mention, inline=True)
    embed.add_field(name="📝 Razón",   value=razon,           inline=True)
    embed.set_footer(text="Acción registrada en el historial • Gran Chile RP")
    await ctx.send(embed=embed)

@bot.command()
async def historial(ctx, usuario: discord.Member):
    sanciones = historial_sanciones.get(usuario.id, [])
    embed = discord.Embed(title=f"📋 Historial de {usuario.name}", color=discord.Color.blue())
    embed.set_thumbnail(url=LOGO_URL)
    embed.description = "\n".join(sanciones) if sanciones else "✅ Este jugador está limpio. No tiene sanciones."
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def cerrar(ctx):
    embed = discord.Embed(
        title="🛑 SERVIDOR CERRADO",
        description="El servidor de Gran Chile RP ha cerrado sus puertas por ahora.\n\n**Estado:** 🔴 Offline",
        color=discord.Color.dark_red()
    )
    embed.set_thumbnail(url=LOGO_URL)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def abrir(ctx):
    embed = discord.Embed(
        title="✅ SERVIDOR ABIERTO",
        description="¡Ya puedes entrar a Gran Chile RP! Los esperamos a todos.\n\n**Estado:** 🟢 Online",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=LOGO_URL)
    await ctx.send(embed=embed)

@bot.command()
async def encuesta(ctx, *, pregunta):
    embed = discord.Embed(
        title="📊 Nueva Encuesta",
        description=f"**{pregunta}**\n\n✅ Reacciona para votar.",
        color=discord.Color.gold(),
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_thumbnail(url=LOGO_URL)
    embed.set_footer(text=f"Enviada por {ctx.author.display_name} • Gran Chile RP")
    mensaje = await ctx.send(embed=embed)
    await mensaje.add_reaction("✅")
    await mensaje.add_reaction("❌")

# ─────────────────────────────────────────────
#  MANEJO DE ERRORES
# ─────────────────────────────────────────────

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ No tienes permisos para usar este comando.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Faltan argumentos. Revisa cómo usar el comando.")

# ─────────────────────────────────────────────
#  INICIO DEL BOT
# ─────────────────────────────────────────────

keep_alive()
bot.run(os.environ.get('TOKEN'))
