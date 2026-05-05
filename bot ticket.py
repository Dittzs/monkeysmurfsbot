import discord
from discord.ext import commands
from discord.ui import Button, View

# Defina as intenções do bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

# Crie o bot com os intents necessários
bot = commands.Bot(command_prefix='!', intents=intents)

# Variável para contar tickets
ticket_counter = 1

# Defina o ID do canal onde o bot enviará o ticket hub
TICKET_HUB_CHANNEL_ID = 1278248389620011010  # Substitua pelo ID do canal desejado

# Defina o ID do canal de transcrições de tickets
TICKET_LOG_CHANNEL_ID = 1278258067984613418  # Substitua pelo ID do canal de logs

# Lista de IDs de administradores e moderadores
ADMIN_IDS = [1276727404580180031]  # Substitua pelo ID do(s) administrador(es)
MODERATOR_ROLE_ID = 1276727404580180031  # Substitua pelo ID do cargo de moderador

# URL da imagem que você deseja adicionar
IMAGE_URL = 'https://i.ibb.co/kgmKz2V/pngegg.png'  # Substitua com a URL da imagem
IMAGE_URL2 = 'https://i.ibb.co/sCRF3D7/monkey-png.png'

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')

    # Envie a mensagem do ticket hub para o canal específico assim que o bot iniciar
    channel = bot.get_channel(TICKET_HUB_CHANNEL_ID)
    if channel:
        # Exclua o canal antigo do ticket hub, se existir
        existing_message = None
        async for message in channel.history(limit=10):
            if message.embeds and message.embeds[0].title == "**Selecione o Serviço**":
                existing_message = message
                break
        if existing_message:
            await existing_message.delete()

        # Crie uma view para os botões do ticket hub
        view = TicketButtonView()

        # Crie uma incorporação (embed) para a mensagem do ticket hub
        embed = discord.Embed(
            title="**Selecione o Serviço**",
            description="Clique no botão abaixo para selecionar o serviço desejado.\n\n",
            color=discord.Color.dark_purple()  # Altere a cor conforme sua preferência
        )
        embed.set_thumbnail(url=IMAGE_URL)  # Adiciona a imagem ao lado da mensagem

        # Envie a mensagem com os botões do ticket hub
        await channel.send(embed=embed, view=view)

# Função para lidar com interações dos botões do ticket hub
class TicketButtonView(View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Elojob", style=discord.ButtonStyle.green, custom_id="elojob")
    async def elojob_button(self, button: Button, interaction: discord.Interaction):
        await self.create_ticket(interaction, "Elojob")

    @discord.ui.button(label="Duoboost", style=discord.ButtonStyle.red, custom_id="duoboost")
    async def duoboost_button(self, button: Button, interaction: discord.Interaction,):
        await self.create_ticket(interaction, "Duoboost")

    @discord.ui.button(label="Suporte", style=discord.ButtonStyle.blurple, custom_id="suporte")
    async def suporte_button(self, button: Button, interaction: discord.Interaction):
        await self.create_ticket(interaction, "Suporte")

    async def create_ticket(self, interaction: discord.Interaction, service_type: str):
        global ticket_counter
        guild = interaction.guild

        # Verifique se o usuário já tem um ticket aberto
        for channel in guild.channels:
            if channel.name.startswith(f"ticket-{interaction.user.name}"):
                await interaction.response.send_message("Você já tem um ticket aberto!", ephemeral=True)
                return

        # Crie um canal de texto com o nome do ticket
        channel_name = f"ticket-{interaction.user.name}"
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True)
        }
        ticket_channel = await guild.create_text_channel(channel_name, overwrites=overwrites)

        # Crie uma incorporação (embed) para a mensagem de criação do ticket
        embed = discord.Embed(
            title=f" **Serviço: {service_type}**",
            description=f"Olá {interaction.user.mention}, já iremos lhe atender, enquanto isso responda o formulário com **!elojob**",
            color=discord.Color.green()  # Altere a cor conforme sua preferência
        )
        embed.set_thumbnail(url=IMAGE_URL2) 

        # Envie a mensagem de criação do ticket
        await ticket_channel.send(embed=embed)

        # Envie a mensagem com os botões de moderação
        claim_button = Button(label="📜 Claim Ticket", style=discord.ButtonStyle.gray, custom_id=f"claim_{channel_name}")
        delete_button = Button(label="🔒 Close Ticket", style=discord.ButtonStyle.gray, custom_id=f"delete_{channel_name}")

        # Crie a view para os botões de moderação
        mod_view = View()
        mod_view.add_item(claim_button)
        mod_view.add_item(delete_button)

        # Envie a mensagem com os botões de moderação
        await ticket_channel.send(view=mod_view)

        ticket_counter += 1
        await interaction.response.send_message(content=f"Você selecionou: {service_type}", ephemeral=True)  # Responde ao usuário sem remover o hub

# Evento para lidar com interações de botões
@bot.event
async def on_interaction(interaction: discord.Interaction):
    custom_id = interaction.data.get('custom_id')
    if custom_id and custom_id.startswith(('claim_', 'delete_')):
        if interaction.user.id in ADMIN_IDS or any(role.id == MODERATOR_ROLE_ID for role in interaction.user.roles):
            if custom_id.startswith('claim_'):
                # Envia uma mensagem no canal do ticket informando que o ticket foi resgatado
                await interaction.channel.send(f"{interaction.user.mention} resgatou o ticket!")
                await interaction.response.send_message(f"Você reivindicou o ticket de {interaction.channel.name}!", ephemeral=True)
            elif custom_id.startswith('delete_'):
                # Salve todas as mensagens do ticket no canal de log
                log_channel = interaction.guild.get_channel(TICKET_LOG_CHANNEL_ID)
                if log_channel:
                    history = []
                    # Coletar o histórico de mensagens corretamente
                    async for msg in interaction.channel.history(limit=1000, oldest_first=True):
                        history.append(msg)

                    # Gerar a transcrição
                    transcript = "\n".join([f"{msg.author.name}: {msg.content}" for msg in history])

                    # Verificar se a transcrição não excede o limite de caracteres de um embed
                    for i in range(0, len(transcript), 4000):
                        embed = discord.Embed(
                            title=f"Transcrição do {interaction.channel.name}",
                            description=transcript[i:i+4000],  # Enviar partes da transcrição
                            color=discord.Color.red()
                        )
                        await log_channel.send(embed=embed)

                # Deletar o canal do ticket
                await interaction.channel.delete()
        else:
            await interaction.response.send_message("Você não tem permissão para realizar essa ação.", ephemeral=True)


# Rode o bot com o token
bot.run('')



