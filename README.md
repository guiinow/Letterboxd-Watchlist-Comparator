# Letterboxd Watchlist Comparator

Compara sua watchlist do Letterboxd com listas públicas para encontrar filmes em comum.

## Funcionalidades

- Identifica filmes em comum entre sua watchlist e listas públicas do Letterboxd
- Compara sua watchlist com o catálogo da MUBI no Brasil via JustWatch
- Lê a watchlist atual diretamente pela URL do Letterboxd

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

### Comparação com listas do Letterboxd (`script_url.py`)

1. Edite `script_url.py`:
   - Atualize `minha_watchlist` com a URL da sua watchlist (ex: `https://letterboxd.com/seu_usuario/watchlist/`)
   - Adicione as URLs das listas em `urls_para_analisar`

2. Execute:
```bash
python script_url.py
```

### Comparação atual com a MUBI

O comando abaixo busca diretamente sua watchlist atual do Letterboxd e consulta o catálogo da MUBI no Brasil (`country='BR'`). Nenhum CSV é necessário.

```bash
python justwatch_mubi.py
# Ou informe outra URL de watchlist:
python justwatch_mubi.py https://letterboxd.com/outro_usuario/watchlist/
```

O catálogo da MUBI é salvo em `cache/mubi_catalog.json` e reutilizado por 7 dias. O resultado fica em `filmes-mubi.csv`.

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
