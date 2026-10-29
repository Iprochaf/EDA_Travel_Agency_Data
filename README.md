# Agência de Viagens: Buscas e Reservas

Aplicação em Streamlit da disciplina **Análise e Visualização de Dados** (CESAR School, 2026.2), feita a partir do repositório-modelo das Aulas 21 a 23.

**Link do app:** _(preencher após o deploy: `https://<subdominio>.streamlit.app`)_

## O projeto

**Dataset:** [Travel Agency Data](https://www.kaggle.com/datasets/nhatnguyentran/travel-agency-data) (Kaggle). São 100 mil buscas de hotel feitas por clientes de uma agência de viagens entre jan/2013 e dez/2014, com a indicação de se a busca virou reserva (`is_booking`).

| Aba | O que mostra |
| --- | --- |
| **Dashboard 1: Laboratório** | Mapa de calor da correlação (Spearman ou Pearson) e um histograma por variável quantitativa: distância origem–destino, antecedência, noites, adultos, crianças, quartos e eventos na sessão. Os histogramas podem ser separados entre reserva e só busca. |
| **Dashboard 2: Indicadores comerciais** | Para a gerência comercial e o marketing da agência: 5 métricas (buscas, taxa de conversão, antecedência mediana, estadia média, reservas em pacote) e 4 visuais (evolução mensal, conversão por canal com seleção cruzada, conversão por antecedência, dispositivo × tipo de compra). |

A sidebar tem o seletor de variáveis e um slider de intervalo por variável, que valem para os dois dashboards.

**Stack:** Python, pandas, Streamlit, Altair. Deploy no Streamlit Community Cloud.

### Estrutura

```
app.py                          # aplicação (os dois dashboards)
src/data_loader.py              # leitura do CSV tratado, com @st.cache_data
src/preparacao.py               # tratamento do dataset bruto
src/calculos.py                 # filtros, correlação, histogramas e KPIs
notebooks/eda.ipynb             # EDA da Aula 11
notebooks/preparacao-dados.ipynb  # gera data/clean/dataset.csv
data/raw/                       # CSV baixado do Kaggle (não versionado)
data/clean/dataset.csv          # CSV tratado (versionado: o deploy lê daqui)
entregas/                       # rascunhos dos dashboards e justificativa das métricas
prompts/                        # declaração de uso de IA
.streamlit/config.toml          # identidade visual
```

### Gerando o dado tratado

1. Baixe o dataset no Kaggle, descompacte e coloque o `.csv` em `data/raw/`.
2. Rode `notebooks/preparacao-dados.ipynb` do começo ao fim. A última célula grava `data/clean/dataset.csv`.

### Privacidade

O tratamento remove `user_id`, `user_location_region` e `user_location_city`, que identificam o usuário ou sua localização fina. As demais colunas de localização e destino já vêm como códigos anonimizados no dataset original.

## Setup

Requer **Python 3.11 a 3.15**. Confira a sua versão antes de começar:

| Sistema | Verificar versão |
| --- | --- |
| macOS / Linux | `python3 --version` |
| Windows | `py --version` |

### 1. Criar e ativar o ambiente virtual

O nome do comando do Python muda por sistema (em muitas máquinas `python` nem existe). Use a linha do seu sistema:

| Sistema | Criar | Ativar |
| --- | --- | --- |
| macOS / Linux | `python3 -m venv .venv` | `source .venv/bin/activate` |
| Windows (PowerShell) | `py -m venv .venv` | `.venv\Scripts\Activate.ps1` |
| Windows (cmd) | `py -m venv .venv` | `.venv\Scripts\activate.bat` |

Se você tem várias versões instaladas, escolha uma compatível, por exemplo `python3.12 -m venv .venv` (macOS/Linux) ou `py -3.12 -m venv .venv` (Windows).

Com o ambiente ativo, o terminal mostra `(.venv)` no início da linha. **A partir daqui os comandos são iguais em todos os sistemas**, porque dentro do venv `python` e `pip` sempre existem.

### 2. Instalar, configurar a IA e rodar

```bash
python -m pip install -r requirements.txt

# Skills de IA do Streamlit (ver seção "IA neste projeto")
streamlit skills --yes

streamlit run app.py
```

### Problemas comuns

- **`python: command not found` / `python` não é reconhecido:** use `python3` (macOS/Linux) ou `py` (Windows) só para criar o venv; depois de ativado, `python` funciona.
- **Linux (Debian/Ubuntu): `ensurepip is not available` ou `No module named venv`:** instale `sudo apt install python3-venv` (ou `python3.X-venv` para a sua versão).
- **Windows: "a execução de scripts foi desabilitada" ao ativar no PowerShell:** rode uma vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, ou use o cmd.
- **Python fora de 3.11–3.15:** instale uma versão compatível em [python.org](https://www.python.org/downloads/) e crie o venv com ela, como no exemplo acima.
- **Apareceu `ModuleNotFoundError` ou `streamlit: command not found`:** o venv provavelmente não está ativo. Ative de novo e confira o `(.venv)` no prompt.
- **Erro de certificado no `pip install` (macOS, Python do python.org):** rode `Install Certificates.command`, na pasta Python 3.X em Aplicativos.
- **`DatasetNotFoundError` ao baixar o dataset no notebook (macOS, Python do python.org):** é o mesmo problema de certificado SSL (o `pandas` não consegue ler o CSV da UCI). Rode `Install Certificates.command` e reinicie o kernel. O notebook `eda-com-downloads.ipynb` já define `SSL_CERT_FILE` com o `certifi` como contorno.

## Estrutura de dados: `data/raw` vs `data/clean`

- `data/raw/`: o dataset **bruto**, como foi baixado. Nunca é editado à mão.
- `data/clean/`: o dataset **já tratado**, exportado na última célula de `notebooks/preparacao-dados.ipynb`. O `app.py` lê **somente** desta pasta, via `src/data_loader.py`.

### O que vai para o Git

| Pasta | Versionada? | Por quê |
| --- | --- | --- |
| `data/raw/` | **Não** (só o `.gitkeep`) | O bruto pode ser grande ou ter dados sensíveis, e o app não o usa. |
| `data/clean/` | **Sim** | O Streamlit Community Cloud faz deploy a partir do GitHub e só enxerga o que está no repositório. Sem o CSV tratado no repo, o app funciona na sua máquina e **quebra no deploy**. |

### Antes de dar `git push` com o dado tratado

- **O dado é público ou pode ser compartilhado?** Se não for claramente público, use um **repositório privado** (o Community Cloud permite conectar repositórios privados ao autorizar o GitHub; confirme na hora do deploy). Nesse caso, dê acesso de leitura ao professor (como colaborador ou pela organização).
- **Dado sensível** (nomes, CPF, e-mail, telefone, localização exata etc.): remova ou anonimize na EDA, antes de exportar para `data/clean/`. Isso vale mesmo em repositório privado.
- **Tamanho:** o GitHub rejeita arquivos acima de **100 MB**. Se o CSV tratado for grande, reduza colunas e linhas na EDA ou exporte em Parquet (`df.to_parquet(...)`, exige `pyarrow`).
- **Lembre de commitar o arquivo:** confira com `git status` que `data/clean/dataset.csv` aparece como novo arquivo.

## Passo a passo

O passo a passo detalhado de cada aula (Aulas 21, 22 e 23), com pré-requisitos e objetivos, está em [ROTEIRO.md](ROTEIRO.md). Comece por ele depois do Setup.


## IA neste projeto

Este projeto usa o **streamlit skills**: um conjunto de instruções (arquivos `SKILL.md`) que a ferramenta de IA lê para escrever código Streamlit seguindo boas práticas (estrutura de layout, cache, widgets, etc.).

**Como instalar:** depois do `pip install -r requirements.txt`, rode na raiz do projeto:

```bash
streamlit skills        # interativo
streamlit skills --yes  # sem confirmações
```

O comando cria *symlinks* para as skills que acompanham a sua instalação do Streamlit, então elas se atualizam sozinhas quando você atualiza o pacote. (A opção `--global` instala para todos os projetos, em vez de só este.)

**Onde fica instalado:**

- `.claude/skills/`: lido pelo Claude Code.
- `.agents/skills/`: lido pelo Gemini CLI, que já encontra essa pasta sozinho.

Essas pastas **não são versionadas** (ver `.gitignore`): os symlinks apontam para o seu ambiente virtual e não funcionam em outra máquina. Cada pessoa roda `streamlit skills` no próprio clone.

**Se você usa outra ferramenta** (ChatGPT, Copilot Chat, etc.): abra o `SKILL.md` correspondente em `.agents/skills/` e cole o conteúdo manualmente no início do chat, antes do seu pedido.

O uso de IA deve ser declarado conforme a seção abaixo.

## Pasta `prompts/`

A pasta [prompts/](prompts) guarda só o que é sobre **uso de IA**: o template de prompt para transformar o rascunho de layout em esqueleto de código e a **Declaração de Uso de IA** exigida pelo Plano de Ensino. Veja [prompts/README.md](prompts/README.md).

## Pasta `entregas/`

A pasta [entregas/](entregas) guarda os artefatos de entrega que não são sobre IA: os rascunhos de layout de cada dashboard (`.jpg` ou `.png`) e a justificativa das métricas do Dashboard 2. Veja [entregas/README.md](entregas/README.md) para o detalhe de cada arquivo e o checklist por aula. Não coloque esses arquivos no `.gitignore`.
