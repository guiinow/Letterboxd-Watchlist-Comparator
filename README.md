# Letterboxd Watchlist Comparator

Compara sua watchlist do Letterboxd com listas públicas para encontrar filmes em comum.

## Funcionalidades

- Identifica filmes em comum entre sua watchlist e listas públicas do Letterboxd
- Compara sua watchlist com o catálogo da MUBI no Brasil via JustWatch
- Dois modos de leitura da watchlist:
  - **Via CSV**: usando arquivo exportado do Letterboxd
  - **Via URL**: lendo diretamente da sua página de watchlist

## Requisitos

- Python 3.10+
- Dependências: `pandas`, `beautifulsoup4`, `cloudscraper`, `JustWatch`

## Instalação

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/letterboxd-comparator.git
cd letterboxd-comparator

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

## Como usar

### Opção 1: Leitura via CSV (`script_csv.py`)

1. Exporte sua watchlist do Letterboxd:
   - Acesse sua watchlist (ex: `https://letterboxd.com/seu_usuario/watchlist/`)
   - Clique em "Export watchlist" para baixar o CSV

2. Edite `script_csv.py`:
   - Atualize `meu_arquivo` com o nome do seu CSV
   - Adicione as URLs das listas em `urls_para_analisar`

3. Execute:
```bash
python script_csv.py
```

### Opção 2: Leitura via URL (`script_url.py`)

1. Edite `script_url.py`:
   - Atualize `minha_watchlist` com a URL da sua watchlist (ex: `https://letterboxd.com/seu_usuario/watchlist/`)
   - Adicione as URLs das listas em `urls_para_analisar`

2. Execute:
```bash
python script_url.py
```

### Comparação com a MUBI via JustWatch

O módulo `justwatch_mubi.py` usa o CSV exportado do Letterboxd e consulta o catálogo da MUBI no Brasil (`country='BR'`). Por padrão, ele lê o CSV `watchlist-guiinow-2026-02-02-22-14-utc.csv` e gera `filmes-mubi.csv`.

```bash
python justwatch_mubi.py
# Ou informe outro CSV:
python justwatch_mubi.py caminho/para/watchlist.csv
```

O catálogo é salvo em `cache/mubi_catalog.json` e reutilizado por 7 dias. A comparação usa título normalizado, variantes em português/inglês e ano de lançamento. O script usa o endpoint GraphQL atual do JustWatch (`https://apis.justwatch.com/graphql`) com o filtro MUBI do Brasil. A lib `JustWatch` e a página pública do provedor ficam como fallbacks para compatibilidade. Se o JustWatch estiver indisponível, o script tenta usar um cache antigo e não interrompe o processo por erro de rede.

## Exemplo de saída

```
Carregando sua watchlist...
Total de filmes encontrados: 123

Processando lista: https://letterboxd.com/usuario/list/nome-da-lista/
Total de filmes extraídos da lista: 357

=== Filmes encontrados em comum ===
                                                 Watchlist                      Em quais acervos
                                                 Fireworks                 Acervo Cinema Brocado
                                              Mango Yellow Acervo Cinema Brocado, Catálogo Nicho
I Travel Because I Have to, I Come Back Because I Love You Acervo Cinema Brocado, Catálogo Nicho
                             The Passion According to G.H.                        Catálogo Nicho
                                                 Macunaima Acervo Cinema Brocado, Catálogo Nicho

Total de correspondências: 27
```

## Licença

MIT
