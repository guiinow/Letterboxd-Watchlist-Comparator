import time

import cloudscraper
import pandas as pd
from bs4 import BeautifulSoup


def fetch_letterboxd_list_from_url(base_url, max_retries=3, is_watchlist=False, list_name=None):
    """
    Extrai filmes de uma lista ou watchlist do Letterboxd via web scraping.
    
    Args:
        base_url: URL da lista do Letterboxd
        max_retries: Número máximo de tentativas por página
        is_watchlist: Se True, usa parser para watchlist (sem /detail/)
        list_name: Nome identificador da lista (para rastrear origem)
        
    Returns:
        DataFrame com os filmes da lista
    """
    movies = []
    page = 1
    
    # Normalizar URL - listas usam /detail/, watchlist não
    if not is_watchlist and "/detail/" not in base_url:
        base_url = base_url.rstrip('/') + '/detail/'
    else:
        base_url = base_url.rstrip('/') + '/'
    
    # Usar cloudscraper para contornar proteção anti-bot
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )

    while True:
        url = f"{base_url}page/{page}/"
        print(f"Acessando: {url}...")
        
        success = False
        for attempt in range(max_retries):
            try:
                # Delay antes de cada requisição
                if attempt > 0:
                    wait_time = 2 ** attempt  # Exponential backoff: 2, 4, 8 segundos
                    print(f"  Tentativa {attempt + 1}/{max_retries}, aguardando {wait_time}s...")
                    time.sleep(wait_time)
                
                response = scraper.get(url)
                
                if response.status_code == 200:
                    success = True
                    break
                elif response.status_code == 403:
                    print(f"  Bloqueado (403), tentando novamente...")
                    # Recriar o scraper para nova sessão
                    scraper = cloudscraper.create_scraper(
                        browser={
                            'browser': 'chrome',
                            'platform': 'windows',
                            'desktop': True
                        }
                    )
                else:
                    print(f"  Erro: Status {response.status_code}")
                    break
                    
            except Exception as e:
                print(f"  Erro na tentativa {attempt + 1}: {e}")
        
        if not success:
            print(f"  Falha ao acessar página {page} após {max_retries} tentativas")
            break
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        page_movies = []
        
        if is_watchlist:
            # Watchlist: títulos estão no alt das imagens dentro de film-poster
            for poster in soup.find_all('div', class_='film-poster'):
                img = poster.find('img')
                if img and img.get('alt'):
                    title = img.get('alt').strip()
                    if title:
                        page_movies.append({'Name': title, 'Source': list_name or 'Watchlist'})
        else:
            # Listas com /detail/: títulos estão em h2 > a
            for h2 in soup.find_all('h2'):
                a = h2.find('a')
                if a and '/film/' in a.get('href', ''):
                    title = a.text.strip()
                    if title:
                        page_movies.append({'Name': title, 'Source': list_name or 'Lista'})
        
        if not page_movies:
            break
        
        movies.extend(page_movies)
        print(f"  Filmes encontrados nesta página: {len(page_movies)}")
            
        # Verificar se há próxima página
        if not soup.find('a', class_='next'):
            break
            
        page += 1
        time.sleep(2)  # Delay maior entre páginas
    
    print(f"Total de filmes extraídos da lista: {len(movies)}")
    return pd.DataFrame(movies)


def comparar_listas(watchlist_url, urls):
    """
    Compara a watchlist online com outras listas do Letterboxd.
    
    Args:
        watchlist_url: URL da sua watchlist no Letterboxd
        urls: Lista de dicts com 'url' e 'nome' para comparar
        
    Returns:
        DataFrame com os filmes em comum e suas origens
    """
    print("Carregando sua watchlist...")
    df_watchlist = fetch_letterboxd_list_from_url(watchlist_url, is_watchlist=True, list_name="Sua Watchlist")
    
    if df_watchlist.empty:
        print("Erro ao carregar a watchlist.")
        return pd.DataFrame()

    df_watchlist['match_name'] = df_watchlist['Name'].astype(str).str.lower().str.strip()

    all_external_movies = []
    for url_info in urls:
        url = url_info['url'] if isinstance(url_info, dict) else url_info
        list_name = url_info['nome'] if isinstance(url_info, dict) else url.split('/')[-2]
        print(f"\nProcessando lista: {list_name}")
        df_list = fetch_letterboxd_list_from_url(url, list_name=list_name)
        if not df_list.empty:
            all_external_movies.append(df_list)
    
    if not all_external_movies:
        print("Nenhum filme extraído das listas online.")
        return pd.DataFrame()

    df_external = pd.concat(all_external_movies, ignore_index=True)
    df_external['match_name'] = df_external['Name'].astype(str).str.lower().str.strip()

    # Agrupar as origens por filme
    df_external_grouped = df_external.groupby('match_name').agg({
        'Name': 'first',
        'Source': lambda x: ', '.join(x.unique())
    }).reset_index()

    # Cruzamento
    matches = pd.merge(df_watchlist[['Name', 'match_name']], df_external_grouped, on='match_name', suffixes=('_sua', '_lista'))
    matches = matches.rename(columns={'Source': 'Em quais listas'})
    
    return matches


# --- EXECUÇÃO ---
# Sua watchlist (substitua pelo seu username)
minha_watchlist = "https://letterboxd.com/guiinow/watchlist/"

# Listas para comparar
urls_para_analisar = [
    {'url': "https://letterboxd.com/cinemabrocado/list/acervo-cinema-brocado/", 'nome': "Acervo Cinema Brocado"},
    {'url': "https://letterboxd.com/manel12/list/catalogo-nicho/", 'nome': "Catálogo Nicho"}
]

try:
    resultados = comparar_listas(minha_watchlist, urls_para_analisar)

    if not resultados.empty:
        print("\n=== Filmes encontrados em comum ===")
        colunas_exibir = ['Watchlist', 'Em quais acervos']
        
        print(resultados[colunas_exibir].drop_duplicates().to_string(index=False))
        print(f"\nTotal de correspondências: {len(resultados.drop_duplicates(subset=['match_name']))}")
    else:
        print("\nNenhum filme em comum foi encontrado.")
except Exception as e:
    print(f"Erro ao processar: {e}")