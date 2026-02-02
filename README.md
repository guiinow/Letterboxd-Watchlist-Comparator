# Letterboxd Watchlist Comparator

Compara sua watchlist do Letterboxd com listas públicas para encontrar filmes em comum.

## Funcionalidades

- Lê sua watchlist exportada do Letterboxd (arquivo CSV)
- Extrai filmes de listas públicas do Letterboxd via web scraping
- Identifica e exibe os filmes em comum entre sua watchlist e as listas online

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

1. Exporte sua watchlist do Letterboxd:
   - Acesse [letterboxd.com/settings/data](https://letterboxd.com/settings/data/)
   - Clique em "Export your data"
   - Extraia o arquivo `watchlist.csv`

2. Edite o arquivo `script.py` com suas configurações:
   - Atualize `meu_arquivo` com o nome do seu CSV
   - Adicione as URLs das listas que deseja comparar em `urls_para_analisar`

3. Execute o script:
```bash
python script.py
```

## Exemplo de saída

```
Carregando sua watchlist...
Total de filmes encontrados: 123

Processando lista: https://letterboxd.com/usuario/list/nome-da-lista/
Total de filmes extraídos da lista: 357

=== Filmes encontrados em comum ===
                    Name_sua   Year
          My Name Ain't Johnny 2008.0
              Neighboring Sounds 2012.0
                      Marighella 2019.0

Total de correspondências: 3
```

## Licença

MIT
