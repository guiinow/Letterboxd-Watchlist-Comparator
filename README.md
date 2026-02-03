# Letterboxd Watchlist Comparator

Compara sua watchlist do Letterboxd com listas públicas para encontrar filmes em comum.

## Funcionalidades

- Identifica filmes em comum entre sua watchlist e listas públicas do Letterboxd
- Dois modos de leitura da watchlist:
  - **Via CSV**: usando arquivo exportado do Letterboxd
  - **Via URL**: lendo diretamente da sua página de watchlist

## Requisitos

- Python 3.10+
- Dependências: `pandas`, `beautifulsoup4`, `cloudscraper`

## Instalação

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/letterboxd-comparator.git
cd letterboxd-comparator

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install pandas beautifulsoup4 cloudscraper
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
