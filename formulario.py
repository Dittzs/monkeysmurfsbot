import discord
from discord.ext import commands
from discord.ui import Select, View
import mercadopago


# Configuração dos intents
intents = discord.Intents.default()
intents.message_content = True  # Necessário para ler o conteúdo das mensagens

# Criação do bot com os intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Autenticação Mercado Pago
sdk = mercadopago.SDK("")  # Chave de API privada

# Função para criar uma preferência de pagamento no Mercado Pago
def criar_preferencia(preco_total):
    preference_data = {
        "items": [
            {
                "title": "EloJob Boosting Service",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": preco_total
            }
        ],
        "back_urls": {
            "success": "https://www.seusite.com/sucesso",
            "failure": "https://www.seusite.com/erro",
            "pending": "https://www.seusite.com/pendente"
        },
        "auto_return": "approved"
    }
    
    # Criar a preferência e retornar o link de pagamento
    preference_response = sdk.preference().create(preference_data)
    return preference_response['response']['init_point']


# Configuração dos intents
intents = discord.Intents.default()
intents.message_content = True  # Necessário para ler o conteúdo das mensagens

# Criação do bot com os intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Dicionário para ordenar ligas e tiers
elo_ordenado = {
    'Ferro': 1, 'Bronze': 2, 'Prata': 3, 'Ouro': 4, 'Platina': 5, 
    'Esmeralda': 6, 'Diamante': 7, 'Mestre': 8, 'Grão-Mestre': 9, 'Desafiante': 10
}

tier_ordenado = {
    'IV': 1, 'III': 2, 'II': 3, 'I': 4
}

# Estrutura de preços
precos = {
   'Ferro': {'Ferro': 6.30, 'Bronze': 26.30, 'Prata': 54.59, 'Ouro': 94.50, 'Platina': 144.89, 'Esmeralda': 216.29, 'Diamante': 358.57, 'Mestre': 603.75, 'Grão-Mestre': 1128, 'Desafiante': 2099},
     'Bronze': {'Bronze': 6.75, 'Prata': 29.40, 'Ouro': 69.30, 'Platina': 119.69, 'Esmeralda': 254.80, 'Diamante': 333.37, 'Mestre': 771.40, 'Grão-Mestre': 1103, 'Desafiante': 2074},
    'Prata': {'Prata': 9.97, 'Ouro': 39.90, 'Platina': 90.30, 'Esmeralda': 161.00, 'Diamante': 303.97, 'Mestre': 549.15, 'Grão-Mestre': 1074, 'Desafiante': 2045},
    'Ouro': {'Ouro': 12.60, 'Platina': 50.40, 'Esmeralda': 121.80, 'Diamante': 264.07, 'Mestre': 509.25, 'Grão-Mestre': 1034, 'Desafiante': 2005},
    'Platina': {'Platina': 17.85, 'Esmeralda': 71.40, 'Diamante': 180.67, 'Mestre': 458.84, 'Grão-Mestre': 983.25, 'Desafiante': 1955},
    'Esmeralda': {'Esmeralda': 35.17, 'Diamante': 142.27, 'Mestre': 387.45, 'Grão-Mestre': 912.00, 'Desafiante': 1883},
    'Diamante': {'Diamante': 60.00 , 'Mestre': 245.17, 'Grão-Mestre': 769.5, 'Desafiante': 1741},
     'Mestre': {'Grão-Mestre': 525.00, 'Desafiante': 1496},
    'Grão-Mestre': {'Desafiante': 1121}
}

# Percentuais para cada tier
percentuais_tier = {
    'III': 100,
    'II': 150,
    'I': 250
}

# Função para calcular o preço com base nas opções selecionadas
def calcular_preco(liga_atual, tier_atual, elo_desejado, tier_desejado, taxa_mmr, stream_online, reducao_kda, servico_solo):
    preco_base = precos[liga_atual].get(elo_desejado, 0)
    
    # Aplicar taxas adicionais
    if taxa_mmr == 'sim':
        preco_base *= 1.32  # Aumenta 32% para taxa MMR
    if stream_online == 'sim':
        preco_base *= 1.30  # Aumenta 30% para stream online
    if reducao_kda == 'sim':
        preco_base *= 1.35  # Aumenta 35% para redução do KDA
    if servico_solo == 'sim':
        preco_base *= 1.50  # Aumenta 50% para serviço solo

    # Aplicar bônus de porcentagem com base no tier desejado
    if tier_desejado in percentuais_tier:
        preco_base *= (1 + percentuais_tier[tier_desejado] / 100)
    
    return round(preco_base, 2)
    
    # Aplicar taxas adicionais
    if taxa_mmr == 'sim':
        preco_base *= 1.32  # Aumenta 32% para taxa MMR
    if stream_online == 'sim':
        preco_base *= 1.30  # Aumenta 30% para stream online
    if reducao_kda == 'sim':
        preco_base *= 1.35  # Aumenta 35% para redução do KDA
    if servico_solo == 'sim':
        preco_base *= 1.50  # Aumenta 50% para serviço solo
    
    return round(preco_base, 2)

async def iniciar_formulario(ctx, autor):
    def check(message):
        return message.author == autor

    def check_interaction(interaction):
        return interaction.user == autor

    # Função para deferir a interação corretamente
    async def interaction_defer(interaction):
        await interaction.response.defer()

    try:
        modos = [
            discord.SelectOption(label='SOLO/DUO'),
            discord.SelectOption(label='FLEX')
        ]

        # Liga Atual
        ligas = [
            discord.SelectOption(label='Ferro'),
            discord.SelectOption(label='Bronze'),
            discord.SelectOption(label='Prata'),
            discord.SelectOption(label='Ouro'),
            discord.SelectOption(label='Platina'),
            discord.SelectOption(label='Esmeralda'),
            discord.SelectOption(label='Diamante'),
            discord.SelectOption(label='Mestre'),
            discord.SelectOption(label='Grão-Mestre'),
            discord.SelectOption(label='Desafiante')
        ]

        tiers = [
            discord.SelectOption(label='IV'),
            discord.SelectOption(label='III'),
            discord.SelectOption(label='II'),
            discord.SelectOption(label='I')
        ]

        # Exibir Liga Atual
        await ctx.send(f"{autor.mention}, escolha sua **Liga Atual:**")
        liga_atual_select = Select(placeholder="Selecione a liga atual", options=ligas)
        view = View()
        view.add_item(liga_atual_select)
        await ctx.send(view=view)

        interaction = await bot.wait_for("interaction", check=check_interaction)
        await interaction_defer(interaction)  # Defere a interação
        liga_atual = interaction.data['values'][0]

        # Exibir Tier Atual se não for um elo de alto nível
        if not elo_alto_nivel(liga_atual):
            await ctx.send("**Tier Atual:**")
            tier_atual_select = Select(placeholder="Selecione o tier atual", options=tiers)
            view = View()
            view.add_item(tier_atual_select)
            await ctx.send(view=view)

            interaction = await bot.wait_for("interaction", check=check_interaction)
            await interaction_defer(interaction)  # Defere a interação
            tier_atual = interaction.data['values'][0]
        else:
            tier_atual = None  # Não é necessário para elos de alto nível

        # Elo Desejado
        await ctx.send("**Elo Desejado:**")
        elo_desejado_select = Select(placeholder="Selecione o elo desejado", options=ligas)
        view = View()
        view.add_item(elo_desejado_select)
        await ctx.send(view=view)

        interaction = await bot.wait_for("interaction", check=check_interaction)
        await interaction_defer(interaction)  # Defere a interação
        elo_desejado = interaction.data['values'][0]

        # Verifica se o elo desejado é menor que o elo atual
        if elo_ordenado[elo_desejado] < elo_ordenado[liga_atual]:
            await ctx.send("O elo desejado não pode ser menor que o elo atual. Por favor, escolha um elo desejado válido.")
            return

        # Tier Desejado se o elo não for alto nível
        if not elo_alto_nivel(elo_desejado):
            await ctx.send("**Tier Desejado:**")
            tier_desejado_select = Select(placeholder="Selecione o tier desejado", options=tiers)
            view = View()
            view.add_item(tier_desejado_select)
            await ctx.send(view=view)

            interaction = await bot.wait_for("interaction", check=check_interaction)
            await interaction_defer(interaction)  # Defere a interação
            tier_desejado = interaction.data['values'][0]

            # Verifica se o tier desejado é menor que o tier atual dentro do mesmo elo
            if (elo_ordenado[elo_desejado] == elo_ordenado[liga_atual] and tier_ordenado[tier_desejado] < tier_ordenado[tier_atual]):
                await ctx.send("O tier desejado não pode ser menor que o tier atual dentro do mesmo elo. Por favor, escolha um tier desejado válido.")
                return
        else:
            tier_desejado = None  # Não é necessário para elos de alto nível

        # Modo de Jogo
        await ctx.send("**Fila Desejada:**")
        modo_select = Select(placeholder="Selecione o modo de jogo", options=modos)
        view = View()
        view.add_item(modo_select)
        await ctx.send(view=view)

        interaction = await bot.wait_for("interaction", check=check_interaction)
        await interaction_defer(interaction)  # Defere a interação
        modo_jogo = interaction.data['values'][0]

        # PDLs Iniciais
        await ctx.send("Digite seus **PDLs Iniciais:**")
        pdl_inicial_msg = await bot.wait_for('message', check=check)
        pdl_inicial = pdl_inicial_msg.content
        if not pdl_inicial.isdigit() or not (0 <= int(pdl_inicial) <= 99):
            await ctx.send("O valor dos PDLs Iniciais deve estar entre 0 e 99. Tente novamente.")
            return

        # PDLs Ganhos por Vitória
        await ctx.send("Digite seus **PDLs ganhos por vitória:**")
        pdl_vitoria_msg = await bot.wait_for('message', check=check)
        pdl_vitoria = pdl_vitoria_msg.content
        if not pdl_vitoria.isdigit() or not (0 <= int(pdl_vitoria) <= 99):
            await ctx.send("O valor dos PDLs ganhos por vitória deve estar entre 0 e 99. Tente novamente.")
            return

        # Taxa MMR
        taxa_mmr_options = [
            discord.SelectOption(label='Sim', value='sim'),
            discord.SelectOption(label='Não', value='nao')
        ]
        await ctx.send("Taxa MMR **(+32%)**\nMarque esta opção caso esteja ganhando menos de 15 pontos de liga por vitória.")
        taxa_mmr_select = Select(placeholder="Selecione uma opção", options=taxa_mmr_options)
        view = View()
        view.add_item(taxa_mmr_select)
        await ctx.send(view=view)

        interaction = await bot.wait_for("interaction", check=check_interaction)
        await interaction_defer(interaction)  # Defere a interação
        taxa_mmr = interaction.data['values'][0]

        # Posição de Feitiços
        posicao_feitiços_options = [
            discord.SelectOption(label='FLASH - D', value='flash_d'),
            discord.SelectOption(label='FLASH - F', value='flash_f')
        ]
        await ctx.send("Posição de Feitiços **(Grátis)**\nEscolha a ordem do feitiço de invocador.")
        posicao_feitiços_select = Select(placeholder="Selecione uma opção", options=posicao_feitiços_options)
        view = View()
        view.add_item(posicao_feitiços_select)
        await ctx.send(view=view)

        interaction = await bot.wait_for("interaction", check=check_interaction)
        await interaction_defer(interaction)  # Defere a interação
        posicao_feitiços = interaction.data['values'][0]

        # Serviço Prioritário
        servico_prioritario_options = [
            discord.SelectOption(label='Sim', value='sim'),
            discord.SelectOption(label='Não', value='nao')
        ]
        await ctx.send("Serviço Prioritário **(Grátis)**\nCom esta opção selecionada, seu serviço terá prioridade urgencial.")
        servico_prioritario_select = Select(placeholder="Selecione uma opção", options=servico_prioritario_options)
        view = View()
        view.add_item(servico_prioritario_select)
        await ctx.send(view=view)

        interaction = await bot.wait_for("interaction", check=check_interaction)
        await interaction_defer(interaction)  # Defere a interação
        servico_prioritario = interaction.data['values'][0]

        # Vitória Extra
        vitoria_extra_options = [
            discord.SelectOption(label='Sim', value='sim'),
            discord.SelectOption(label='Não', value='nao')
        ]
        await ctx.send("Vitória Extra **(Grátis)**\nCom esta opção selecionada, após o booster alcançar o elo desejado, ele fará uma vitória adicional.")
        vitoria_extra_select = Select(placeholder="Selecione uma opção", options=vitoria_extra_options)
        view = View()
        view.add_item(vitoria_extra_select)
        await ctx.send(view=view)

        interaction = await bot.wait_for("interaction", check=check_interaction)
        await interaction_defer(interaction)  # Defere a interação
        vitoria_extra = interaction.data['values'][0]

        # Stream Online
        stream_online_options = [
            discord.SelectOption(label='Sim', value='sim'),
            discord.SelectOption(label='Não', value='nao')
        ]
        await ctx.send("Stream Online **(+ 30%)**\nCom esta opção, o jogador irá abrir uma Stream para o cliente acompanhar o serviço.")
        stream_online_select = Select(placeholder="Selecione uma opção", options=stream_online_options)
        view = View()
        view.add_item(stream_online_select)
        await ctx.send(view=view)

        interaction = await bot.wait_for("interaction", check=check_interaction)
        await interaction_defer(interaction)  # Defere a interação
        stream_online = interaction.data['values'][0]

        # Redução do KDA
        reducao_kda_options = [
            discord.SelectOption(label='Sim', value='sim'),
            discord.SelectOption(label='Não', value='nao')
        ]
        await ctx.send("Redução do KDA **(+ 35%)**\nCom esta opção, iremos reduzir propositalmente o KDA durante as partidas(Função disponível somente até o esmeralda).")
        reducao_kda_select = Select(placeholder="Selecione uma opção", options=reducao_kda_options)
        view = View()
        view.add_item(reducao_kda_select)
        await ctx.send(view=view)

        interaction = await bot.wait_for("interaction", check=check_interaction)
        await interaction_defer(interaction)  # Defere a interação
        reducao_kda = interaction.data['values'][0]

        # Serviço Solo
        servico_solo_options = [
            discord.SelectOption(label='Sim', value='sim'),
            discord.SelectOption(label='Não', value='nao')
        ]
        await ctx.send("Serviço Solo **(+ 50%)**\nCom esta opção, nossos jogadores irão jogar solo durante o boosting.")
        servico_solo_select = Select(placeholder="Selecione uma opção", options=servico_solo_options)
        view = View()
        view.add_item(servico_solo_select)
        await ctx.send(view=view)

        interaction = await bot.wait_for("interaction", check=check_interaction)
        await interaction_defer(interaction)  # Defere a interação
        servico_solo = interaction.data['values'][0]

        # Calcula o preço
        preco = calcular_preco(liga_atual, tier_atual, elo_desejado, tier_desejado, taxa_mmr, stream_online, reducao_kda, servico_solo)

        link_pagamento = criar_preferencia(preco)


        # Exibe o resumo das informações coletadas e o preço final
        await ctx.send(f"**Confira seu pedido:**\n"
                       f"Fila Desejada: {modo_jogo}\n"
                       f"Liga Atual: {liga_atual} {tier_atual if tier_atual else ''}\n"
                       f"Elo Desejado: {elo_desejado} {tier_desejado if tier_desejado else ''}\n"
                       f"PDLs Iniciais: {pdl_inicial}\n"
                       f"PDLs por Vitória: {pdl_vitoria}\n"
                       f"Taxa MMR **(+32%)**: {'**Sim**' if taxa_mmr == 'sim' else '**Não**'}\n"
                       f"Posição de Feitiços: {'**FLASH - D**' if posicao_feitiços == 'flash_d' else '**FLASH - F**'}\n"
                       f"Serviço Prioritário: {'**Sim**' if servico_prioritario == 'sim' else '**Não**'}\n"
                       f"Vitória Extra: {'**Sim**' if vitoria_extra == 'sim' else '**Não**'}\n"
                       f"Stream Online **(30%)**: {'**Sim**' if stream_online == 'sim' else '**Não**'}\n"
                       f"Redução do KDA **(35%)**: {'**Sim**' if reducao_kda == 'sim' else '**Não**'}\n"
                       f"Serviço Solo **(50%)**: {'**Sim**' if servico_solo == 'sim' else '**Não**'}\n"
                       f"**Preço Total: R${preco:.2f}**. Para continuar, pague usando o link abaixo:\n{link_pagamento}\n\n"
                       f"**Não esqueça de dar !login após a confirmação da compra!**")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        await ctx.send("Ocorreu um erro durante o processo. Tente novamente.")

# Função para verificar se o elo é de alto nível
def elo_alto_nivel(elo):
    return elo in ['Mestre', 'Grão-Mestre', 'Desafiante']

@bot.event
async def on_message(message):
    if message.content.startswith("!elojob") and message.author != bot.user:
        await iniciar_formulario(message.channel, message.author)

# Insira o token do seu bot aqui
bot.run('')