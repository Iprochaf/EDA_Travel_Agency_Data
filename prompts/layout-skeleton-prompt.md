# Template: rascunho de layout → esqueleto do app

Prompt usado na Aula 21 para gerar o esqueleto do `app.py` a partir do rascunho.

## Contexto

Sou aluno da disciplina Análise e Visualização de Dados (CESAR School, 2026.2). Estou construindo um app em Streamlit a partir da minha EDA do dataset Travel Agency Data (Kaggle), com buscas de hotel de uma agência de viagens entre 2013 e 2014. O Dashboard 1 é um "laboratório" de distribuição e correlação das variáveis quantitativas.

## Entrada

Rascunho anexado: `entregas/rascunho-dashboard1.png`.

Colunas usadas (já tratadas em `data/clean/dataset.csv`): `orig_destination_distance`, `antecedencia_dias`, `noites`, `srch_adults_cnt`, `srch_children_cnt`, `srch_rm_cnt`, `cnt`, além de `is_booking` (busca virou reserva).

Layout: sidebar à esquerda com um seletor de variáveis e um slider de intervalo por variável; área principal com a correlação à esquerda e um histograma por variável à direita.

Perguntas que o dashboard deve responder: como se distribuem distância, antecedência, noites e hóspedes? Quais variáveis andam juntas? A análise muda quando excluo valores extremos?

## Restrições

- Streamlit; editar só o `app.py`.
- Carregar os dados via `src/data_loader.py` (`load_data()`), nunca por caminho absoluto.
- Nesta aula, só o esqueleto: widgets da sidebar funcionando e lugares marcados para os gráficos. Sem gráficos finais.
- Tratar 0 e 1 variável selecionada sem quebrar.

## Formato de saída

Código completo do `app.py`, com `# TODO` nos pontos que serão implementados na Aula 22.
