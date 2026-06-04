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

import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import uuid
from datetime import datetime, timezone

# ─────────────────────────────────────────────
#  UTILIDADES DE BASE DE DATOS (JSON LOCAL)
# ─────────────────────────────────────────────

DB_PATH = "data/sanciones.json"

def _cargar_db() -> dict:
    if not os.path.exists(DB_PATH):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        return {}
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _guardar_db(data: dict):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def _obtener_sanciones_usuario(guild_id: str, user_id: str) -> list:
    db = _cargar_db()
    return db.get(guild_id, {}).get(user_id, [])

def _guardar_sancion(guild_id: str, user_id: str, sancion: dict):
    db = _cargar_db()
    db.setdefault(guild_id, {}).setdefault(user_id, []).append(sancion)
    _guardar_db(db)

def _actualizar_sancion(guild_id: str, user_id: str, sancion_id: str, cambios: dict) -> bool:
    db = _cargar_db()
    sanciones = db.get(guild_id, {}).get(user_id, [])
    for s in sanciones:
        if s["id"] == sancion_id:
            s.update(cambios)
            _guardar_db(db)
            return True
    return False

def _eliminar_sancion(guild_id: str, user_id: str, sancion_id: str) -> bool:
    db = _cargar_db()
    sanciones = db.get(guild_id, {}).get(user_id, [])
    nueva_lista = [s for s in sanciones if s["id"] != sancion_id]
    if len(nueva_lista) == len(sanciones):
        return False
    db[guild_id][user_id] = nueva_lista
    _guardar_db(db)
    return True

# ─────────────────────────────────────────────
#  CONSTANTES Y HELPERS VISUALES
# ─────────────────────────────────────────────

TIPOS_SANCION = [
    app_commands.Choice(name="⚠️  Advertencia",    value="advertencia"),
    app_commands.Choice(name="🔇  Mute",            value="mute"),
    app_commands.Choice(name="👢  Kick",            value="kick"),
    app_commands.Choice(name="🔨  Ban",             value="ban"),
    app_commands.Choice(name="⛔  Ban Permanente",  value="ban_permanente"),
    app_commands.Choice(name="🚫  Blacklist",       value="blacklist"),
    app_commands.Choice(name="📛  Sanción Leve",    value="sancion_leve"),
    app_commands.Choice(name="🔴  Sanción Grave",   value="sancion_grave"),
    app_commands.Choice(name="🛑  Sanción Máxima",  value="sancion_maxima"),
]

ESTADO_COLORES = {
    "activa":   0xE74C3C,   # rojo
    "apelada":  0xF39C12,   # naranja
    "inactiva": 0x95A5A6,   # gris
}

TIPO_EMOJIS = {
    "advertencia":   "⚠️",
    "mute":          "🔇",
    "kick":          "👢",
    "ban":           "🔨",
    "ban_permanente":"⛔",
    "blacklist":     "🚫",
    "sancion_leve":  "📛",
    "sancion_grave": "🔴",
    "sancion_maxima":"🛑",
}

TIPO_NOMBRES = {
    "advertencia":   "Advertencia",
    "mute":          "Mute",
    "kick":          "Kick",
    "ban":           "Ban",
    "ban_permanente":"Ban Permanente",
    "blacklist":     "Blacklist",
    "sancion_leve":  "Sanción Leve",
    "sancion_grave": "Sanción Grave",
    "sancion_maxima":"Sanción Máxima",
}

def _timestamp_unix(dt_str: str) -> str:
    """Convierte ISO string a timestamp Discord."""
    try:
        dt = datetime.fromisoformat(dt_str)
        return f"<t:{int(dt.timestamp())}:R>"
    except Exception:
        return dt_str

def _ahora_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _generar_id() -> str:
    return str(uuid.uuid4())[:8].upper()

# ─────────────────────────────────────────────
#  COG PRINCIPAL
# ─────────────────────────────────────────────

class Sanciones(commands.Cog):
    """Sistema completo de sanciones."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ══════════════════════════════════════════
    #  /sancionar
    # ══════════════════════════════════════════
    @app_commands.command(
        name="sancionar",
        description="Aplica una sanción a un miembro del servidor."
    )
    @app_commands.describe(
        usuario     = "Miembro a sancionar",
        tipo        = "Tipo de sanción",
        razon       = "Razón de la sanción",
        duracion    = "Duración (ej: 1d, 3h, 7d) — opcional",
        prueba      = "URL de imagen/evidencia — opcional",
        notificar   = "¿Notificar al usuario por DM? (por defecto: Sí)",
    )
    @app_commands.choices(tipo=TIPOS_SANCION)
    @app_commands.checks.has_permissions(moderate_members=True)
    async def sancionar(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        tipo: app_commands.Choice[str],
        razon: str,
        duracion: str = None,
        prueba: str = None,
        notificar: bool = True,
    ):
        await interaction.response.defer(ephemeral=False)

        # No se puede sancionar a staff con permisos mayores
        if usuario.top_role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
            embed = discord.Embed(
                description="❌ No puedes sancionar a alguien con un rol igual o superior al tuyo.",
                color=0xE74C3C
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        sancion_id = _generar_id()
        sancion = {
            "id":          sancion_id,
            "tipo":        tipo.value,
            "razon":       razon,
            "moderador_id": str(interaction.user.id),
            "fecha":       _ahora_iso(),
            "duracion":    duracion,
            "prueba":      prueba,
            "estado":      "activa",
            "apelacion":   None,
        }

        _guardar_sancion(
            str(interaction.guild_id),
            str(usuario.id),
            sancion
        )

        emoji = TIPO_EMOJIS.get(tipo.value, "🔴")
        nombre_tipo = TIPO_NOMBRES.get(tipo.value, tipo.value)
        total = len(_obtener_sanciones_usuario(str(interaction.guild_id), str(usuario.id)))

        # ── Embed principal ──
        embed = discord.Embed(
            title=f"{emoji}  Sanción Aplicada",
            color=ESTADO_COLORES["activa"],
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_author(
            name=str(usuario),
            icon_url=usuario.display_avatar.url
        )
        embed.add_field(name="👤 Usuario",       value=usuario.mention,                inline=True)
        embed.add_field(name="🏷️ Tipo",          value=nombre_tipo,                    inline=True)
        embed.add_field(name="🆔 ID Sanción",    value=f"`{sancion_id}`",              inline=True)
        embed.add_field(name="📋 Razón",         value=razon,                          inline=False)
        if duracion:
            embed.add_field(name="⏱️ Duración",  value=duracion,                       inline=True)
        embed.add_field(name="🛡️ Moderador",     value=interaction.user.mention,       inline=True)
        embed.add_field(name="📊 Total Sanciones", value=f"`{total}`",                 inline=True)
        if prueba:
            embed.add_field(name="🔗 Evidencia", value=f"[Ver prueba]({prueba})",      inline=False)
            if prueba.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
                embed.set_image(url=prueba)
        embed.set_footer(text=f"Servidor: {interaction.guild.name}")

        await interaction.followup.send(embed=embed)

        # ── DM al usuario ──
        if notificar:
            try:
                dm_embed = discord.Embed(
                    title=f"{emoji}  Has recibido una sanción",
                    description=f"Has sido sancionado en **{interaction.guild.name}**.",
                    color=ESTADO_COLORES["activa"],
                    timestamp=datetime.now(timezone.utc)
                )
                dm_embed.add_field(name="🏷️ Tipo",      value=nombre_tipo,  inline=True)
                dm_embed.add_field(name="🆔 ID",         value=f"`{sancion_id}`", inline=True)
                dm_embed.add_field(name="📋 Razón",      value=razon,        inline=False)
                if duracion:
                    dm_embed.add_field(name="⏱️ Duración", value=duracion,   inline=True)
                dm_embed.set_footer(text="Si crees que es injusta, puedes apelarla con /apelar_sancion")
                await usuario.send(embed=dm_embed)
            except discord.Forbidden:
                pass  # El usuario tiene DMs cerrados

    # ══════════════════════════════════════════
    #  /historial
    # ══════════════════════════════════════════
    @app_commands.command(
        name="historial",
        description="Muestra el historial de sanciones de un miembro."
    )
    @app_commands.describe(
        usuario  = "Miembro a consultar",
        pagina   = "Página del historial (por defecto: 1)",
        filtro   = "Filtrar por tipo de sanción — opcional",
        solo_activas = "Mostrar solo sanciones activas",
    )
    @app_commands.choices(filtro=TIPOS_SANCION)
    @app_commands.checks.has_permissions(moderate_members=True)
    async def historial(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        pagina: int = 1,
        filtro: app_commands.Choice[str] = None,
        solo_activas: bool = False,
    ):
        await interaction.response.defer(ephemeral=True)

        sanciones = _obtener_sanciones_usuario(
            str(interaction.guild_id),
            str(usuario.id)
        )

        # Aplicar filtros
        if filtro:
            sanciones = [s for s in sanciones if s["tipo"] == filtro.value]
        if solo_activas:
            sanciones = [s for s in sanciones if s["estado"] == "activa"]

        # Ordenar más reciente primero
        sanciones = sorted(sanciones, key=lambda s: s["fecha"], reverse=True)

        POR_PAGINA = 4
        total = len(sanciones)
        total_paginas = max(1, (total + POR_PAGINA - 1) // POR_PAGINA)
        pagina = max(1, min(pagina, total_paginas))
        inicio = (pagina - 1) * POR_PAGINA
        pagina_items = sanciones[inicio:inicio + POR_PAGINA]

        # Conteo por tipo
        conteo = {}
        for s in sanciones:
            t = s["tipo"]
            conteo[t] = conteo.get(t, 0) + 1

        activas  = sum(1 for s in sanciones if s["estado"] == "activa")
        apeladas = sum(1 for s in sanciones if s["estado"] == "apelada")

        embed = discord.Embed(
            title=f"📂  Historial de Sanciones",
            color=0x2F3136,
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_author(
            name=f"{usuario} — {total} sanción(es) total",
            icon_url=usuario.display_avatar.url
        )

        # Resumen rápido
        resumen_lineas = []
        for tipo, cant in conteo.items():
            emoji = TIPO_EMOJIS.get(tipo, "•")
            resumen_lineas.append(f"{emoji} {TIPO_NOMBRES.get(tipo, tipo)}: **{cant}**")
        resumen = "\n".join(resumen_lineas) if resumen_lineas else "Sin registros."

        embed.add_field(
            name="📊 Resumen",
            value=resumen,
            inline=True
        )
        embed.add_field(
            name="📌 Estado",
            value=f"🔴 Activas: **{activas}**\n🟠 Apeladas: **{apeladas}**",
            inline=True
        )
        embed.add_field(name="\u200b", value="\u200b", inline=False)

        if not pagina_items:
            embed.add_field(name="Sin resultados", value="No hay sanciones con ese filtro.", inline=False)
        else:
            for s in pagina_items:
                emoji = TIPO_EMOJIS.get(s["tipo"], "🔴")
                nombre_tipo = TIPO_NOMBRES.get(s["tipo"], s["tipo"])
                estado = s.get("estado", "activa")

                estado_badge = {
                    "activa":   "🔴 Activa",
                    "apelada":  "🟠 Apelada",
                    "inactiva": "⚫ Inactiva",
                }.get(estado, estado)

                mod = f"<@{s['moderador_id']}>"
                fecha_rel = _timestamp_unix(s["fecha"])
                linea = (
                    f"**Razón:** {s['razon']}\n"
                    f"**Moderador:** {mod} · **Fecha:** {fecha_rel}\n"
                    f"**Estado:** {estado_badge}"
                )
                if s.get("duracion"):
                    linea += f" · **Duración:** {s['duracion']}"
                if s.get("apelacion"):
                    linea += f"\n**Apelación:** {s['apelacion']}"

                embed.add_field(
                    name=f"{emoji} [{s['id']}] {nombre_tipo}",
                    value=linea,
                    inline=False
                )

        embed.set_footer(text=f"Página {pagina}/{total_paginas} · {interaction.guild.name}")
        await interaction.followup.send(embed=embed, ephemeral=True)

    # ══════════════════════════════════════════
    #  /apelar_sancion
    # ══════════════════════════════════════════
    @app_commands.command(
        name="apelar_sancion",
        description="Apela una sanción del historial (queda marcada como apelada, no se elimina)."
    )
    @app_commands.describe(
        usuario     = "Miembro cuya sanción se apela",
        sancion_id  = "ID de la sanción (ej: A1B2C3D4)",
        motivo      = "Motivo de la apelación",
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def apelar_sancion(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        sancion_id: str,
        motivo: str,
    ):
        await interaction.response.defer(ephemeral=True)

        sancion_id = sancion_id.upper().strip()
        sanciones = _obtener_sanciones_usuario(
            str(interaction.guild_id),
            str(usuario.id)
        )
        sancion = next((s for s in sanciones if s["id"] == sancion_id), None)

        if not sancion:
            embed = discord.Embed(
                description=f"❌ No encontré la sanción `{sancion_id}` para ese usuario.",
                color=0xE74C3C
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        if sancion["estado"] == "apelada":
            embed = discord.Embed(
                description=f"⚠️ La sanción `{sancion_id}` ya fue apelada anteriormente.",
                color=0xF39C12
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        ok = _actualizar_sancion(
            str(interaction.guild_id),
            str(usuario.id),
            sancion_id,
            {
                "estado":    "apelada",
                "apelacion": motivo,
                "apelado_por": str(interaction.user.id),
                "fecha_apelacion": _ahora_iso(),
            }
        )

        if not ok:
            await interaction.followup.send("❌ Error al actualizar la sanción.", ephemeral=True)
            return

        emoji = TIPO_EMOJIS.get(sancion["tipo"], "🔴")
        nombre_tipo = TIPO_NOMBRES.get(sancion["tipo"], sancion["tipo"])

        embed = discord.Embed(
            title="🟠  Sanción Apelada",
            description="La sanción queda registrada en el historial como **apelada**.",
            color=0xF39C12,
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_author(name=str(usuario), icon_url=usuario.display_avatar.url)
        embed.add_field(name="🆔 ID Sanción",  value=f"`{sancion_id}`",           inline=True)
        embed.add_field(name="🏷️ Tipo",        value=f"{emoji} {nombre_tipo}",   inline=True)
        embed.add_field(name="📋 Razón original", value=sancion["razon"],         inline=False)
        embed.add_field(name="📝 Motivo apelación", value=motivo,                 inline=False)
        embed.add_field(name="🛡️ Apelado por", value=interaction.user.mention,   inline=True)
        embed.set_footer(text=f"Servidor: {interaction.guild.name}")

        await interaction.followup.send(embed=embed)

        # Notificar al usuario por DM
        try:
            dm_embed = discord.Embed(
                title="🟠  Tu sanción ha sido apelada",
                description=f"Una de tus sanciones en **{interaction.guild.name}** fue marcada como apelada.",
                color=0xF39C12
            )
            dm_embed.add_field(name="🆔 ID",    value=f"`{sancion_id}`",    inline=True)
            dm_embed.add_field(name="🏷️ Tipo",  value=nombre_tipo,          inline=True)
            dm_embed.add_field(name="📝 Motivo",value=motivo,               inline=False)
            await usuario.send(embed=dm_embed)
        except discord.Forbidden:
            pass

    # ══════════════════════════════════════════
    #  /borrar_sancion
    # ══════════════════════════════════════════
    @app_commands.command(
        name="borrar_sancion",
        description="Elimina permanentemente una sanción del historial de un miembro."
    )
    @app_commands.describe(
        usuario    = "Miembro al que se le borra la sanción",
        sancion_id = "ID de la sanción a eliminar (ej: A1B2C3D4)",
        motivo     = "Razón para borrarla (queda en log interno)",
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def borrar_sancion(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        sancion_id: str,
        motivo: str,
    ):
        await interaction.response.defer(ephemeral=True)

        sancion_id = sancion_id.upper().strip()
        sanciones = _obtener_sanciones_usuario(
            str(interaction.guild_id),
            str(usuario.id)
        )
        sancion = next((s for s in sanciones if s["id"] == sancion_id), None)

        if not sancion:
            embed = discord.Embed(
                description=f"❌ No encontré la sanción `{sancion_id}` para ese usuario.",
                color=0xE74C3C
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        emoji = TIPO_EMOJIS.get(sancion["tipo"], "🔴")
        nombre_tipo = TIPO_NOMBRES.get(sancion["tipo"], sancion["tipo"])

        # Confirmación visual antes de borrar
        confirm_embed = discord.Embed(
            title="🗑️  Confirmar eliminación",
            description=(
                f"¿Seguro que quieres **borrar permanentemente** esta sanción?\n"
                f"Esta acción **no se puede deshacer**."
            ),
            color=0xE74C3C
        )
        confirm_embed.add_field(name="🆔 ID",    value=f"`{sancion_id}`",          inline=True)
        confirm_embed.add_field(name="🏷️ Tipo",  value=f"{emoji} {nombre_tipo}", inline=True)
        confirm_embed.add_field(name="📋 Razón", value=sancion["razon"],           inline=False)
        confirm_embed.add_field(name="📝 Motivo borrado", value=motivo,             inline=False)

        # View con botones de confirmación
        view = ConfirmarBorrado(
            interaction=interaction,
            guild_id=str(interaction.guild_id),
            user_id=str(usuario.id),
            sancion_id=sancion_id,
            usuario=usuario,
            sancion=sancion,
            motivo=motivo,
        )
        await interaction.followup.send(embed=confirm_embed, view=view, ephemeral=True)

    # ── Manejo de errores global para este Cog ──
    async def cog_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.MissingPermissions):
            embed = discord.Embed(
                description="❌ No tienes permisos para usar este comando.",
                color=0xE74C3C
            )
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            raise error


# ─────────────────────────────────────────────
#  VIEW: Confirmación de borrado
# ─────────────────────────────────────────────

class ConfirmarBorrado(discord.ui.View):
    def __init__(self, interaction, guild_id, user_id, sancion_id, usuario, sancion, motivo):
        super().__init__(timeout=30)
        self.orig_interaction = interaction
        self.guild_id  = guild_id
        self.user_id   = user_id
        self.sancion_id = sancion_id
        self.usuario   = usuario
        self.sancion   = sancion
        self.motivo    = motivo

    @discord.ui.button(label="Sí, eliminar", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.orig_interaction.user:
            await interaction.response.send_message("No puedes usar este botón.", ephemeral=True)
            return

        ok = _eliminar_sancion(self.guild_id, self.user_id, self.sancion_id)
        self.stop()
        for item in self.children:
            item.disabled = True

        if ok:
            emoji = TIPO_EMOJIS.get(self.sancion["tipo"], "🔴")
            nombre_tipo = TIPO_NOMBRES.get(self.sancion["tipo"], self.sancion["tipo"])
            embed = discord.Embed(
                title="✅  Sanción Eliminada",
                description="La sanción fue eliminada permanentemente del historial.",
                color=0x2ECC71,
                timestamp=datetime.now(timezone.utc)
            )
            embed.set_author(name=str(self.usuario), icon_url=self.usuario.display_avatar.url)
            embed.add_field(name="🆔 ID",    value=f"`{self.sancion_id}`",         inline=True)
            embed.add_field(name="🏷️ Tipo",  value=f"{emoji} {nombre_tipo}",     inline=True)
            embed.add_field(name="📝 Motivo",value=self.motivo,                    inline=False)
            embed.add_field(name="🛡️ Borrado por", value=interaction.user.mention, inline=True)
            embed.set_footer(text=f"Servidor: {interaction.guild.name}")
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.edit_message(
                content="❌ No se pudo eliminar la sanción.", view=self
            )

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary, emoji="✖️")
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.orig_interaction.user:
            await interaction.response.send_message("No puedes usar este botón.", ephemeral=True)
            return
        self.stop()
        for item in self.children:
            item.disabled = True
        embed = discord.Embed(description="❎ Operación cancelada.", color=0x95A5A6)
        await interaction.response.edit_message(embed=embed, view=self)


# ─────────────────────────────────────────────
#  SETUP (para cargar el cog en tu bot)
# ─────────────────────────────────────────────

async def setup(bot: commands.Bot):
    await bot.add_cog(Sanciones(bot))



# ─────────────────────────────────────────────
#  INICIO
# ─────────────────────────────────────────────
keep_alive()
bot.run(os.environ.get('TOKEN'))
