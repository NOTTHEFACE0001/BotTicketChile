# ==========================================
# 1. ENTORNO (DINÁMICO) - CORREGIDO
# ==========================================
@bot.tree.command(name="entorno", description="Enviar un aviso de entorno")
@app_commands.describe(suceso="¿Qué ocurre?", lugar="¿Dónde?", tiempo="¿Cuándo?")
async def entorno(interaction: discord.Interaction, suceso: str, lugar: str, tiempo: str):
    embed = discord.Embed(title="✨ AVISO DE ENTORNO", color=0x2b2d31)
    embed.add_field(name="🚨 Suceso", value=f"**{suceso.upper()}**", inline=False)
    embed.add_field(name="📍 Ubicación", value=f"`{lugar}`", inline=True)
    embed.add_field(name="⏳ Momento", value=f"`{tiempo}`", inline=True)
    embed.set_footer(text=f"Reportado por: {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)

# ==========================================
# 2. GESTIÓN Y SISTEMA POLICIAL
# ==========================================
@bot.tree.command(name="encuesta", description="Crear encuesta")
async def encuesta(interaction: discord.Interaction, pregunta: str):
    await interaction.response.send_message(f"📊 **ENCUESTA:** {pregunta}")
    msg = await interaction.original_response()
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")

@bot.tree.command(name="fichar_sujeto", description="Colocar antecedentes a un ciudadano")
async def fichar_sujeto(interaction: discord.Interaction, ciudadano: discord.Member, delito: str):
    fecha = datetime.datetime.now().strftime("%d/%m/%Y")
    # Aquí puedes agregar la lógica para guardar en tu base de datos
    await interaction.response.send_message(f"🚓 Ficha actualizada para {ciudadano.mention}: {delito} ({fecha})")

@bot.tree.command(name="realizar_ck", description="Registrar Character Kill")
async def realizar_ck(interaction: discord.Interaction, ciudadano: discord.Member, razon: str):
    await interaction.response.send_message(f"💀 **CK CONFIRMADO:** {ciudadano.mention} | Razón: {razon}")

# ==========================================
# 3. IDENTIDAD (DNI)
# ==========================================
@bot.tree.command(name="registrar_dni", description="Registrar un nuevo ciudadano")
async def registrar_dni(interaction: discord.Interaction, nombre_rp: str, edad: int):
    await interaction.response.send_message(f"✅ DNI Creado: **{nombre_rp}**", ephemeral=True)

@bot.tree.command(name="ver_dni", description="Mostrar cédula de identidad")
async def ver_dni(interaction: discord.Interaction, ciudadano: discord.Member = None):
    user = ciudadano or interaction.user
    rut = f"{random.randint(10, 25)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(0, 9)}"
    embed = discord.Embed(title="🪪 CÉDULA DE IDENTIDAD - CHILE", color=discord.Color.blue())
    embed.add_field(name="Nombre", value=user.display_name)
    embed.add_field(name="RUT", value=rut)
    await interaction.response.send_message(embed=embed)

# ==========================================
# 4. APELACIONES
# ==========================================
@bot.tree.command(name="apelar", description="Apelar sanción")
async def apelar(interaction: discord.Interaction, motivo: str):
    await interaction.response.send_message("✅ Tu apelación ha sido enviada.", ephemeral=True)