import discord
from discord.ext import commands
from discord.ui import Button, View

CANAL_RESULTADO_ID = 1284916977550491800  # ID do canal para enviar o resultado do cadastro
contador = 1  # Variável para contar os cadastros

intents = discord.Intents.default()
intents.message_content = True  # Habilitar intents para conteúdo de mensagens

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')

@bot.command()
async def login(ctx):
    # Coleta do nome de usuário
    await ctx.send("Digite seu nome de usuário:")
    usuario = await bot.wait_for('message', check=lambda message: message.author == ctx.author)

    # Coleta da senha
    await ctx.send("Digite sua senha:")
    senha = await bot.wait_for('message', check=lambda message: message.author == ctx.author)

    # Confirmação da senha
    await ctx.send("Confirme sua senha:")
    confirmacao_senha = await bot.wait_for('message', check=lambda message: message.author == ctx.author)

    # Verifica se as senhas coincidem
    if senha.content != confirmacao_senha.content:
        await ctx.send("As senhas não coincidem. Tente novamente.")
        return

    # Coleta do nome de invocador
    await ctx.send("Digite seu nome de invocador:")
    invocador = await bot.wait_for('message', check=lambda message: message.author == ctx.author)

    # Mensagem de confirmação com botões
    await confirmar_dados(ctx, usuario.content, senha.content, invocador.content)

# Função para exibir os botões de confirmação
async def confirmar_dados(ctx, usuario, senha, invocador):
    # Criação dos botões "Corretos" e "Errados"
    view = View()

    # Botão "Corretos"
    botao_corretos = Button(label="Corretos", style=discord.ButtonStyle.success)

    async def interaction_corretos(interaction):
        # Envia os dados para o canal somente se confirmados
        canal_resultado = bot.get_channel(CANAL_RESULTADO_ID)
        if canal_resultado:
            try:
                global contador
                await canal_resultado.send(
                    f"#{interaction.user.mention} - Cadastro realizado com sucesso!\nUsuário: {usuario}\nSenha: {senha}\nInvocador: {invocador}"
                )
                contador += 1
                await interaction.response.edit_message(content="Nossos boosters já receberam a conta, agora é só aguardar!", view=None)
            except Exception as e:
                await interaction.response.send_message(f"Erro ao enviar mensagem para o canal: {e}")
        else:
            await interaction.response.send_message("Canal de resultado não encontrado.")

    # Associar a função ao botão "Corretos"
    botao_corretos.callback = interaction_corretos
    view.add_item(botao_corretos)

    # Botão "Errados"
    botao_errados = Button(label="Errados", style=discord.ButtonStyle.danger)

    async def interaction_errados(interaction):
        # Remove os botões e reinicia o processo de login
        await interaction.response.edit_message(content="Por favor, reinicie o processo e insira os dados corretos.", view=None)
        await login(ctx)  # Reinicia o processo de login

    # Associar a função ao botão "Errados"
    botao_errados.callback = interaction_errados
    view.add_item(botao_errados)

    # Envia a mensagem com os botões
    await ctx.send("Confirme seus dados:\n"
                   f"Usuário: {usuario}\n"
                   f"Senha: {senha}\n"
                   f"Invocador: {invocador}\n"
                   "Estão corretos?", view=view)

bot.run('')
