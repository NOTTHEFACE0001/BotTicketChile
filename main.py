import discord
from discord.ext import commands
from discord import app_commands
import os
from flask import Flask
from threading import Thread

# --- CONFIGURACIÓN DE FLASK PARA UPTIME ROBOT ---
app = Flask('')

@app.route('/')
def home():
    # Esta es la página que UptimeRobot visitará. Si esto carga, no hay 404.
    return "¡Bot Ticket Chile está activo 24/7! 🎫"

def run():
    # Render y Railway asignan un puerto dinámico, esto lo captura:
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- CONFIGURACIÓN DEL BOT ---
# ¡OJO! He dejado tu token, pero si se vuelve a caer, dale a "Reset Token" en Discord.
TOKEN = "MTQ5ODA4MzQzNzE3MzYzOTMw.G8txBE.suZ_31tRNEYTtC7YApn5T9V7lIeEuKDJ_IS2hQ"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# --- SISTEMA DE TICKETS ---
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) 

    @discord.ui.button(label="Abrir Ticket 🎫", style=discord.ButtonStyle.green, custom_id="btn_abrir_ticket")
    async def ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        channel = await guild.create_text_channel(name=f"ticket-{user.name}", overwrites=overwrites)
        
        embed_welcome = discord.Embed(
            title="Soporte Chile RP",
            description=f"Hola {user.mention}, el Staff te atenderá pronto.\nPresiona el botón rojo para cerrar.",
            color=discord.Color.blue()
        )
        
        view_close = discord.ui.View(timeout=None)
        btn_close = discord.ui.Button(label="Cerrar Ticket 🔒", style=discord.ButtonStyle.red, custom_id="btn_close_ticket")
        
        async def close_callback(inter):
            await inter.channel.delete()
            
        btn_close.callback = close_callback
        view_close.add_item(btn_close)

        await channel.send(embed=embed_welcome, view=view_close)
        await interaction.response.send_message(f"Canal creado: {channel.mention}", ephemeral=True)

# --- COMANDOS ---
@bot.tree.command(name="encuesta", description="Crea una encuesta rápida")
async def encuesta(interaction: discord.Interaction, pregunta: str):
    embed = discord.Embed(title="📊 ENCUESTA", description=pregunta, color=0x2ecc71)
    await interaction.response.send_message("Encuesta creada", ephemeral=True)
    msg = await interaction.channel.send(embed=embed)
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")

@bot.tree.command(name="setup_tickets", description="Poner el botón de tickets en este canal")
async def setup_tickets(interaction: discord.Interaction):
    embed = discord.Embed(title="🎫 SOPORTE CHILE RP", description="Haz clic abajo para abrir un ticket.", color=discord.Color.gold())
    await interaction.channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("Panel configurado.", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    bot.add_view(TicketView())
    print(f'✅ {bot.user} está en línea para Chile RP')

# --- EJECUCIÓN ---
if __name__ == "__main__":
    keep_alive()  # Esto crea la web para que el robot la vea
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"Error al arrancar el bot: {e}")
