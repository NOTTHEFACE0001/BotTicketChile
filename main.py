import os
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import datetime
import random
import json

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

# Archivo local para almacenar los DNIs de forma permanente
DB_FILE = "dnis.json"

# ─────────────────────────────────────────────
#  FUNCIONES DE BASE DE DATOS LOCAL
# ─────────────────────────────────────────────

def guardar_dni_db(user_id, datos):
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                db = json.load(f)
        else:
            db = {}
        
        db[str(user_id)] = datos
        
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"❌ Error al guardar DNI en archivo: {e}")

def obtener_dni_db(user_id):
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                db = json.load(f)
                return db.get(str(user_id))
        return None
    except Exception as e:
        print(f"❌ Error al leer DNI del archivo: {e}")
        return None

# ─────────────────────────────────────────────
#  FUNCIONES AUXILIARES DEL DNI
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
    if remainder == 11: return "0"
    elif remainder == 10: return "K"
    return str(remainder)

def calcular_edad(fecha_nacimiento: str) -> str:
    try:
        nacimiento = datetime.datetime.strptime(fecha_nacimiento, "%d/%m/%Y")
        hoy = datetime.datetime.now()
        edad = hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))
        return str(edad)
    except ValueError:
        return "INVALIDA"

def construir_embed_dni(datos, usuario_nombre, avatar_url):
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

    embed.add_field(name="👤 Nombre completo",     value=f"`{datos['nombre']} {datos['apellido']}`",      inline=True)
    embed.add_field(name="🎮 Usuario Roblox",      value=f"`{datos['nombre_roblox']}`",           inline=True)
    embed.add_field(name="🪪 RUT",                  value=f"`{datos['rut']}`",                     inline=True)

    embed.add_field(name="⚧️ Sexo",                 value=f"`{datos['sexo']}`",                    inline=True) 
    embed.add_field(name="🩸 Tipo de sangre",      value=f"`{datos['tipo_sangre']}`",             inline=True) 
    embed.add_field(name="💼 Ocupación",           value=f"`{datos['ocupacion']}`",               inline=True) 

    embed.add_field(name="💍 Estado civil",        value=f"`{datos['estado_civil']}`",            inline=True) 
    embed.add_field(name="🌎 País de origen",      value=f"`{datos['pais']}`",                    inline=True)
    embed.add_field(name="📍 Ciudad / Localidad",  value=f"`{datos['ciudad']}`",                  inline=True)

    embed.add_field(name="🎂 Fecha de nacimiento", value=f"`{datos['fecha_nacimiento']}`",         inline=True)
    embed.add_field(name="🔢 Edad",                value=f"`{datos['edad']} años`",               inline=True)
    embed.add_field(name="📅 Fecha de emisión",    value=f"`{datos['fecha_emision']}`",           inline=True)

    embed.add_field(
        name="\u200b",
        value=(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "✅ *Documento emitido por el Registro Civil de Gran Chile RP*\n"
            "⚠️ *Este documento es válido únicamente dentro del servidor.*"
        ),
        inline=False
    )
    embed.set_footer(text=f"Cédula de {usuario_nombre} • Gran Chile RP", icon_url=avatar_url)
    return embed

# ─────────────────────────────────────────────
#  EVENTO ON_READY (SINCRO TOTAL)
# ─────────────────────────────────────────────

@bot.event
async def on_ready():
    print(f'✅ Conectado como {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="Moderando Gran Chile RP 🇨🇱"))
    
    ID_SERVIDOR = 1486083692089704619  

    try:
        print(f"🔄 Sincronizando todos los comandos Slash en el servidor {ID_SERVIDOR}...")
        guild = discord.Object(id=ID_SERVIDOR)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f"✅ ¡Éxito! {len(synced)} comandos de barra activos.")
    except Exception as e:
        print(f"❌ Error al sincronizar barra: {e}")

# ─────────────────────────────────────────────
#  SLASH COMMANDS
# ─────────────────────────────────────────────

# 1. COMANDO /DNI (CREAR Y GUARDAR)
@bot.tree.command(name="dni", description="Crea tu cédula de identidad de Gran Chile RP y regístrala")
@app_commands.describe(
    nombre="Tu nombre RP", apellido="Tu apellido RP", nombre_roblox="Usuario de Roblox",
    fecha_nacimiento="DD/MM/AAAA", sexo="Sexo", tipo_sangre="Tipo de sangre",
    ocupacion="Profesión", estado_civil="Estado civil", pais="País", ciudad="Ciudad"
)
@app_commands.choices(
    sexo=[app_commands.Choice(name="♂️ Masculino", value="Masculino"), app_commands.Choice(name="♀️ Femenino", value="Femenino"), app_commands.Choice(name="⚧️ No binario", value="No binario")],
    tipo_sangre=[
        app_commands.Choice(name="🩸 A+", value="A+"), app_commands.Choice(name="🩸 A-", value="A-"),
        app_commands.Choice(name="🩸 B+", value="B+"), app_commands.Choice(name="🩸 B-", value="B-"),
        app_commands.Choice(name="🩸 AB+", value="AB+"), app_commands.Choice(name="🩸 AB-", value="AB-"),
        app_commands.Choice(name="🩸 O+", value="O+"), app_commands.Choice(name="🩸 O-", value="O-")
    ],
    ocupacion=[
        app_commands.Choice(name="👮 Carabinero", value="Carabinero"), app_commands.Choice(name="🕵️ PDI", value="Detective / PDI"),
        app_commands.Choice(name="🚑 SAMU", value="Paramédico / SAMU"), app_commands.Choice(name="🚒 Bombero", value="Bombero"),
        app_commands.Choice(name="⚖️ Abogado", value="Abogado"), app_commands.Choice(name="👨‍⚕️ Médico", value="Médico"),
        app_commands.Choice(name="🏦 Empresario", value="Empresario"), app_commands.Choice(name="🔧 Mecánico", value="Mecánico"),
        app_commands.Choice(name="🚖 Taxista", value="Taxista"), app_commands.Choice(name="🍳 Chef", value="Cocinero / Chef"),
        app_commands.Choice(name="🏗️ Constructor", value="Obrero / Constructor"), app_commands.Choice(name="🎓 Estudiante", value="Estudiante"),
        app_commands.Choice(name="💼 Desempleado", value="Desempleado"), app_commands.Choice(name="🎭 Otros", value="Otros")
    ],
    estado_civil=[
        app_commands.Choice(name="💛 Soltero/a", value="Soltero/a"), app_commands.Choice(name="💍 Casado/a", value="Casado/a"),
        app_commands.Choice(name="💔 Divorciado/a", value="Divorciado/a"), app_commands.Choice(name="🖤 Viudo/a", value="Viudo/a")
    ]
)
async def dni(
    interaction: discord.Interaction, nombre: str, apellido: str, nombre_roblox: str, fecha_nacimiento: str, 
    sexo: str, tipo_sangre: str, ocupacion: str, estado_civil: str, pais: str, ciudad: str
):
    edad = calcular_edad(fecha_nacimiento)
    if edad == "INVALIDA":
        await interaction.response.send_message("❌ Fecha inválida. Usa el formato **DD/MM/AAAA**.", ephemeral=True)
        return

    rut = generar_rut()
    fecha_emision = datetime.datetime.now().strftime("%d/%m/%Y")

    # Guardamos los datos en un diccionario estructurado
    datos_dni = {
        "nombre": nombre, "apellido": apellido, "nombre_roblox": nombre_roblox,
        "fecha_nacimiento": fecha_nacimiento, "edad": edad, "rut": rut,
        "sexo": sexo, "tipo_sangre": tipo_sangre, "ocupacion": ocupacion,
        "estado_civil": estado_civil, "pais": pais, "ciudad": ciudad,
        "fecha_emision": fecha_emision
    }

    # Guardar permanentemente
    guardar_dni_db(interaction.user.id, datos_dni)

    embed = construir_embed_dni(datos_dni, interaction.user.display_name, interaction.user.display_avatar.url)
    await interaction.response.send_message(
        content=f"🎉 ¡Bienvenido/a a **Gran Chile RP**, {nombre}! Tu cédula ha sido creada y registrada en la base de datos.",
        embed=embed
    )

# 2. NUEVO COMANDO /VER_DNI (MUESTRA EL DNI GUARDADO)
@bot.tree.command(name="ver_dni", description="Muestra tu cédula de identidad registrada (o la de otro usuario)")
@app_commands.describe(usuario="El miembro del que quieres ver el DNI (Opcional, si no pones nadie, verás el tuyo)")
async def ver_dni(interaction: discord.Interaction, usuario: discord.Member = None):
    # Si no selecciona usuario, se busca a sí mismo
    usuario_objetivo = usuario if usuario else interaction.user
    
    datos = obtener_dni_db(usuario_objetivo.id)
    
    if not datos:
        if usuario:
            await interaction.response.send_message(f"❌ El usuario {usuario_objetivo.mention} aún no ha creado su DNI con `/dni`.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ No tienes ninguna cédula registrada. Crea una usando el comando `/dni`.", ephemeral=True)
        return

    embed = construir_embed_dni(datos, usuario_objetivo.display_name, usuario_objetivo.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# 3. COMANDO /SANCIONAR
@bot.tree.command(name="sancionar", description="Sanciona a un usuario por mal comportamiento")
@app_commands.describe(usuario="El usuario a sancionar", razon="¿Por qué lo sancionas?")
async def sancionar(interaction: discord.Interaction, usuario: discord.Member, razon: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Solo administradores pueden sancionar.", ephemeral=True)
        return
    if usuario.id not in historial_sanciones: historial_sanciones[usuario.id] = []
    fecha = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    historial_sanciones[usuario.id].append(f"⚠️ {razon} ({fecha})")
    embed = discord.Embed(title="🚫 Jugador Sancionado", color=discord.Color.red())
    embed.add_field(name="👤 Usuario", value=usuario.mention, inline=True)
    embed.add_field(name="📝 Razón", value=razon, inline=True)
    await interaction.response.send_message(embed=embed)

# 4. COMANDO /HISTORIAL
@bot.tree.command(name="historial", description="Revisa el historial de sanciones de un usuario")
@app_commands.describe(usuario="Usuario a revisar")
async def historial(interaction: discord.Interaction, usuario: discord.Member):
    sanciones = historial_sanciones.get(usuario.id, [])
    embed = discord.Embed(title=f"📋 Historial de {usuario.name}", color=discord.Color.blue())
    embed.description = "\n".join(sanciones) if sanciones else "✅ Este usuario no tiene sanciones."
    embed.set_thumbnail(url=usuario.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# 5. COMANDO /ABRIR
@bot.tree.command(name="abrir", description="Anuncia que el servidor de RP está abierto")
async def abrir(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Sin permisos.", ephemeral=True)
        return
    embed = discord.Embed(title="✅ SERVIDOR ABIERTO", description="¡Ya puedes entrar! Los esperamos.\n\n**Estado:** 🟢 Online", color=discord.Color.green())
    embed.set_thumbnail(url=LOGO_URL)
    await interaction.response.send_message(embed=embed)

# 6. COMANDO /CERRAR
@bot.tree.command(name="cerrar", description="Anuncia que el servidor de RP está cerrado")
async def cerrar(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Sin permisos.", ephemeral=True)
        return
    embed = discord.Embed(title="🛑 SERVIDOR CERRADO", description="El servidor ha cerrado. Gracias por jugar.\n\n**Estado:** 🔴 Offline", color=discord.Color.dark_red())
    embed.set_thumbnail(url=LOGO_URL)
    await interaction.response.send_message(embed=embed)

# 7. COMANDO /ENCUESTA
@bot.tree.command(name="encuesta", description="Crea una votación rápida")
@app_commands.describe(pregunta="¿Qué quieres preguntar?")
async def encuesta(interaction: discord.Interaction, pregunta: str):
    embed = discord.Embed(title="📊 Nueva Encuesta", description=f"**{pregunta}**\n\n✅ Sí | ❌ No", color=discord.Color.gold())
    embed.set_footer(text=f"Por: {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)
    mensaje = await interaction.original_response()
    await mensaje.add_reaction("✅")
    await mensaje.add_reaction("❌")

# ─────────────────────────────────────────────
#  INICIO
# ─────────────────────────────────────────────
keep_alive()
bot.run(os.environ.get('TOKEN'))
