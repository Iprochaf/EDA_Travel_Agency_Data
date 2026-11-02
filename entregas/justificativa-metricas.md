# Justificativa das métricas — Dashboard 2

**Dataset:** Travel Agency Data (buscas de hotel de uma agência de viagens, jan/2013 a dez/2014).
**Público-alvo:** gerência comercial e equipe de marketing da agência, que decidem onde investir (canais, campanhas, produtos) e precisam saber se as buscas estão virando venda.

Todas as métricas recalculam com os filtros do dashboard (período, dispositivo, tipo de compra) e com os intervalos da sidebar.

## Métrica 1: Buscas
- **Variável:** contagem de linhas (cada linha é uma busca)
- **O que mede:** o volume de procura no período e no recorte escolhidos.
- **Por que foi escolhida:** é a base de todas as outras; uma taxa de conversão só faz sentido sabendo sobre quantas buscas ela é calculada.
- **Público-alvo:** gerência comercial e marketing.
- **Qual decisão pode ser apoiada por essa métrica?** Planejar campanhas e equipe de atendimento nos meses de maior procura; identificar quedas de demanda.
- **O que comunica ao público-alvo:** "quanta gente procurou hotel com a gente".

## Métrica 2: Taxa de conversão
- **Variável:** `is_booking` (1 = a busca virou reserva)
- **O que mede:** a proporção de buscas que viraram reserva. O delta mostra a diferença, em pontos percentuais, para a taxa do período completo sem filtros de dispositivo/tipo.
- **Por que foi escolhida:** é o principal indicador de eficiência comercial: mostra se o interesse está virando venda.
- **Público-alvo:** gerência comercial.
- **Qual decisão pode ser apoiada por essa métrica?** Priorizar os segmentos (dispositivo, tipo de compra, canal) que convertem acima da média e investigar os que ficam abaixo (ex.: problemas na experiência mobile).
- **O que comunica ao público-alvo:** "de cada 100 buscas, quantas viram reserva", e se o recorte escolhido está melhor ou pior do que o geral.

## Métrica 3: Antecedência mediana das reservas
- **Variável:** `antecedencia_dias` (derivada: `srch_ci` − `date_time`), só nas buscas com `is_booking = 1`
- **O que mede:** quantos dias antes do check-in o cliente típico reserva. Usa a mediana porque a antecedência é muito assimétrica (há reservas com mais de um ano de antecedência).
- **Por que foi escolhida:** define a janela de tempo em que vale a pena falar com o cliente.
- **Público-alvo:** marketing.
- **Qual decisão pode ser apoiada por essa métrica?** Quando disparar campanhas antes de feriados e alta temporada (ex.: se a mediana é 30 dias, a campanha de julho precisa sair em junho).
- **O que comunica ao público-alvo:** "metade dos clientes reserva com até X dias de antecedência".

## Métrica 4: Estadia média
- **Variável:** `noites` (derivada: `srch_co` − `srch_ci`), só nas reservas
- **O que mede:** quantas noites, em média, cada reserva ocupa.
- **Por que foi escolhida:** junto do volume de reservas, indica o tamanho do negócio gerado (mais noites = mais receita por reserva).
- **Público-alvo:** gerência comercial.
- **Qual decisão pode ser apoiada por essa métrica?** Criar ofertas de estadia longa ou de fim de semana conforme o perfil; negociar tarifas com hotéis.
- **O que comunica ao público-alvo:** "uma reserva típica dura X noites".

## Métrica 5: Reservas em pacote
- **Variável:** `is_package` (1 = hotel comprado junto com voo), só nas reservas
- **O que mede:** a parcela das reservas feitas como pacote.
- **Por que foi escolhida:** pacotes costumam ter margem maior para a agência; acompanhar essa parcela mostra se a venda casada está funcionando.
- **Público-alvo:** gerência comercial e marketing.
- **Qual decisão pode ser apoiada por essa métrica?** Investir (ou não) na divulgação de pacotes e em quais canais/dispositivos fazê-lo.
- **O que comunica ao público-alvo:** "X% das reservas já vêm como pacote".

## Visuais do Dashboard 2

1. **Volume de buscas e conversão por mês** (barras + linha): sazonalidade da procura e se a conversão acompanha.
2. **Conversão por canal de venda** (barras): quais canais trazem buscas que viram reserva. Clicar num canal filtra o gráfico 3 (seleção cruzada do Altair).
3. **Conversão por antecedência** (barras): se quem busca em cima da hora converte mais ou menos do que quem planeja com meses de antecedência.
4. **Conversão por dispositivo e tipo de compra** (barras agrupadas): compara desktop × mobile e pacote × avulso.
