"""Bot para baixar PDFs de websites. Usa cookies para sites com login."""

import os
import re
import sys
from http.cookiejar import MozillaCookieJar
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

ARQUIVO_COOKIES = "cookies.txt"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


def carregar_sessao(cookies_path: str | None = None) -> requests.Session:
    sessao = requests.Session()
    sessao.headers.update(HEADERS)
    caminho = cookies_path or os.path.join(os.path.dirname(os.path.abspath(__file__)), ARQUIVO_COOKIES)
    if os.path.exists(caminho):
        try:
            jar = MozillaCookieJar(caminho)
            jar.load(ignore_discard=True)
            sessao.cookies = jar
            print("  [Sessão logada] Cookies carregados de cookies.txt\n")
        except Exception as e:
            print(f"  [Aviso] Não foi possível carregar cookies.txt: {e}\n")
    return sessao


def encontrar_pdfs(url: str, sessao: requests.Session | None = None) -> list[str]:
    sessao = sessao or requests.Session()
    sessao.headers.update(HEADERS)
    try:
        response = sessao.get(url, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Erro ao acessar {url}: {e}")
        return []

    return _extrair_pdfs_html(response.text, url)


def _extrair_pdfs_html(html: str, base_url: str, apenas_versao_original: bool = False) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    pdfs = []

    def _filtro_versao(tag) -> bool:
        if not apenas_versao_original:
            return True
        texto = tag.get_text(strip=True).lower()
        return "versão original" in texto or "versao original" in texto

    for tag in soup.find_all("a", href=True):
        texto = tag.get_text(strip=True).lower()
        if "baixar" in texto and ("livro" in texto or "eletrônico" in texto or "eletronico" in texto):
            if _filtro_versao(tag):
                href = tag["href"].strip()
                if href and not href.startswith("#") and "javascript" not in href.lower():
                    pdfs.append(urljoin(base_url, href))

    if pdfs:
        return list(set(pdfs))

    if not apenas_versao_original:
        for link in soup.find_all("a", href=True):
            href = link["href"].strip()
            if href.lower().endswith(".pdf") or ".pdf" in href.lower():
                pdfs.append(urljoin(base_url, href))

        for tag in soup.find_all(["embed", "object", "iframe"], src=True):
            src = tag.get("data") or tag.get("src", "")
            if src and ".pdf" in src.lower():
                pdfs.append(urljoin(base_url, src))

    if not apenas_versao_original:
        for tag in soup.find_all(attrs=lambda x: x and any(k in str(x) for k in ["data-href", "data-url", "data-download"])):
            for attr in ["data-href", "data-url", "data-download"]:
                val = tag.get(attr, "")
                if val and ("pdf" in val.lower() or "download" in val.lower() or "livro" in val.lower()):
                    pdfs.append(urljoin(base_url, val))
        for tag in soup.find_all("a", href=True):
            href = tag["href"].strip()
            if any(k in href.lower() for k in ["/download", "/material", "livro", "ebook", "pdf"]):
                if href and not href.startswith("#"):
                    pdfs.append(urljoin(base_url, href))

    return list(set(pdfs))


def _criar_driver(download_dir: str | None = None):
    from selenium import webdriver
    opcoes_comuns = [
        "--disable-blink-features=AutomationControlled",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--window-size=1920,1080",
        "--lang=pt-BR",
    ]
    prefs = {}
    if download_dir:
        pasta_abs = os.path.abspath(download_dir)
        os.makedirs(pasta_abs, exist_ok=True)
        prefs = {
            "download.default_directory": pasta_abs,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "plugins.always_open_pdf_externally": True,
        }

    def _adicionar_opcoes(opts):
        for arg in opcoes_comuns:
            opts.add_argument(arg)
        if prefs:
            opts.add_experimental_option("prefs", prefs)

    bravo_paths = [
        os.path.expandvars(r"%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\BraveSoftware\Brave-Browser\Application\brave.exe"),
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
    ]
    for bravo_path in bravo_paths:
        if bravo_path and os.path.exists(bravo_path):
            try:
                from selenium.webdriver.chrome.options import Options as ChromeOptions
                opts = ChromeOptions()
                opts.binary_location = bravo_path
                _adicionar_opcoes(opts)
                return webdriver.Chrome(options=opts)
            except Exception:
                break

    try:
        from selenium.webdriver.edge.options import Options as EdgeOptions
        opts = EdgeOptions()
        _adicionar_opcoes(opts)
        return webdriver.Edge(options=opts)
    except Exception:
        pass

    try:
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        opts = ChromeOptions()
        _adicionar_opcoes(opts)
        return webdriver.Chrome(options=opts)
    except Exception as e:
        raise RuntimeError(
            "Não foi possível iniciar o navegador. Instale Brave, Edge ou Chrome."
        )


def encontrar_pdfs_selenium(url: str, pasta_destino: str = "pdfs", cookies_path: str | None = None) -> tuple[list[str], requests.Session | None, int]:
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    except ImportError as e:
        print(f"  [Erro] Para modo --browser, instale: pip install selenium webdriver-manager")
        print(f"  Detalhe: {e}")
        return [], None, 0

    caminho_cookies = cookies_path or os.path.join(os.path.dirname(os.path.abspath(__file__)), ARQUIVO_COOKIES)
    dominio = urlparse(url).netloc
    base_url = f"https://{dominio}"

    driver = None
    try:
        driver = _criar_driver(download_dir=pasta_destino)
        driver.implicitly_wait(10)

        if os.path.exists(caminho_cookies):
            driver.get(base_url)
            try:
                jar = MozillaCookieJar(caminho_cookies)
                jar.load(ignore_discard=True)
                for cookie in jar:
                    c = {
                        "name": cookie.name,
                        "value": cookie.value,
                        "domain": cookie.domain.lstrip(".") if cookie.domain.startswith(".") else cookie.domain,
                    }
                    if cookie.path:
                        c["path"] = cookie.path
                    if cookie.secure:
                        c["secure"] = True
                    try:
                        driver.add_cookie(c)
                    except Exception:
                        pass
                print("  [Sessão logada] Cookies carregados no navegador\n")
            except Exception as e:
                print(f"  [Aviso] Cookies: {e}\n")

        print("  Navegando para a página (aguarde)...")
        import time
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
        except ImportError:
            pass
        def _fechar_alerta(d):
            try:
                WebDriverWait(d, 2).until(EC.alert_is_present())
                d.switch_to.alert.accept()
                time.sleep(0.5)
            except Exception:
                pass
        driver.get(url)
        time.sleep(8)
        _fechar_alerta(driver)
        time.sleep(1)
        _fechar_alerta(driver)
        try:
            html = driver.page_source
        except Exception:
            _fechar_alerta(driver)
            html = driver.page_source if driver else ""
        pdfs = _extrair_pdfs_html(html, url)

        cliques = 0
        if not pdfs:
            try:
                from selenium.webdriver.common.by import By
                botoes = list(driver.find_elements(By.PARTIAL_LINK_TEXT, "Baixar Livro"))
                vistos = set()
                for btn in botoes:
                    try:
                        href = btn.get_attribute("href")
                        if href and href.startswith("http") and "javascript" not in href.lower():
                            if href not in vistos:
                                pdfs.append(href)
                                vistos.add(href)
                        elif btn.is_displayed() and btn.is_enabled():
                            texto = btn.text.strip()[:50]
                            if texto not in vistos:
                                btn.click()
                                time.sleep(2)
                                cliques += 1
                                vistos.add(texto)
                                print(f"  [Clique] {texto}... (download via navegador)")
                    except Exception:
                        pass
            except Exception as e:
                print(f"  [Aviso] Busca por botões: {e}")

        sessao = requests.Session()
        sessao.headers.update(HEADERS)
        for c in driver.get_cookies():
            sessao.cookies.set(c["name"], c["value"], domain=c.get("domain", ""))

        return pdfs, sessao, cliques

    finally:
        if driver:
            driver.quit()


def baixar_pdfs_curso(url_curso: str, pasta_destino: str = "pdfs", apenas_aula: int | None = None) -> int:
    try:
        from selenium.webdriver.common.by import By
    except ImportError:
        print("  [Erro] Instale: pip install selenium")
        return 0

    caminho_cookies = os.path.join(os.path.dirname(os.path.abspath(__file__)), ARQUIVO_COOKIES)
    base_url = f"https://{urlparse(url_curso).netloc}"
    driver = None

    try:
        driver = _criar_driver(download_dir=pasta_destino)
        driver.implicitly_wait(10)

        if os.path.exists(caminho_cookies):
            driver.get(base_url)
            try:
                jar = MozillaCookieJar(caminho_cookies)
                jar.load(ignore_discard=True)
                for cookie in jar:
                    c = {
                        "name": cookie.name,
                        "value": cookie.value,
                        "domain": cookie.domain.lstrip(".") if cookie.domain.startswith(".") else cookie.domain,
                    }
                    if cookie.path:
                        c["path"] = cookie.path
                    try:
                        driver.add_cookie(c)
                    except Exception:
                        pass
                print("  [Sessao logada] Cookies carregados\n")
            except Exception:
                pass

        print("  Buscando URLs das aulas...")
        import time
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        def fechar_alerta(d):
            try:
                WebDriverWait(d, 2).until(EC.alert_is_present())
                d.switch_to.alert.accept()
                time.sleep(0.5)
            except Exception:
                pass

        driver.get(url_curso)
        time.sleep(10)
        fechar_alerta(driver)
        time.sleep(2)
        fechar_alerta(driver)

        aulas_urls = set()
        dominio = urlparse(url_curso).netloc
        for tentativa in range(3):
            try:
                fechar_alerta(driver)
                for a in driver.find_elements(By.TAG_NAME, "a"):
                    href = a.get_attribute("href") or ""
                    if "/aulas/" in href and dominio in href:
                        match = re.search(r"(https://[^/]+/[^/]+/cursos/\d+/aulas/\d+)", href)
                        if not match:
                            match = re.search(r"(https://[^/]+/app/dashboard/cursos/\d+/aulas/\d+)", href)
                        if match:
                            aulas_urls.add(match.group(1))
                if aulas_urls:
                    break
            except Exception:
                fechar_alerta(driver)
                time.sleep(2)
                pass

        aulas_lista = sorted(aulas_urls)
        if not aulas_lista:
            print("  Nenhuma aula encontrada.")
            return 0

        if apenas_aula is not None:
            if apenas_aula < 1 or apenas_aula > len(aulas_lista):
                print(f"  [Erro] Aula {apenas_aula} inexistente (1 a {len(aulas_lista)}).")
                return 0
            aulas_lista = [aulas_lista[apenas_aula - 1]]
            print(f"  Baixando apenas Aula {apenas_aula:02d} (versao original)\n")
        else:
            print(f"  Encontradas {len(aulas_lista)} aula(s) - apenas versao original\n")

        sessao = requests.Session()
        sessao.headers.update(HEADERS)
        total = 0

        for i, url_aula in enumerate(aulas_lista):
            num_aula = f"{(apenas_aula if apenas_aula is not None else i + 1):02d}"
            print(f"\n  Aula {num_aula}")
            driver.get(url_aula)
            time.sleep(5)
            fechar_alerta(driver)
            time.sleep(1)
            fechar_alerta(driver)

            try:
                html = driver.page_source
            except Exception:
                fechar_alerta(driver)
                html = driver.page_source if driver else ""
            pdfs = _extrair_pdfs_html(html, url_aula, apenas_versao_original=True)

            if not pdfs:
                try:
                    fechar_alerta(driver)
                    botoes = driver.find_elements(By.PARTIAL_LINK_TEXT, "versão original")
                    botoes += driver.find_elements(By.PARTIAL_LINK_TEXT, "versao original")
                except Exception:
                    fechar_alerta(driver)
                    botoes = []
                for btn in botoes:
                    try:
                        parent = btn.find_element(By.XPATH, "./ancestor::a")
                        href = parent.get_attribute("href")
                        if href and href.startswith("http") and "javascript" not in href.lower():
                            pdfs.append(href)
                            break
                    except Exception:
                        try:
                            href = btn.get_attribute("href")
                            if href and href.startswith("http"):
                                pdfs.append(href)
                                break
                        except Exception:
                            pass

            for c in driver.get_cookies():
                sessao.cookies.set(c["name"], c["value"], domain=c.get("domain", ""))

            for link in pdfs[:1]:
                if baixar_pdf(link, pasta_destino, sessao, nome_sugerido=f"Aula_{num_aula}.pdf"):
                    total += 1

        return total

    except Exception as e:
        print(f"  [Erro] {e}")
        return 0
    finally:
        if driver:
            driver.quit()


def nome_seguro(url: str, indice: int = 0) -> str:
    nome = os.path.basename(urlparse(url).path)
    if not nome or not nome.lower().endswith(".pdf"):
        nome = f"documento_{indice}.pdf"
    nome = re.sub(r'[<>:"/\\|?*]', "_", nome)
    return nome[:200]


def baixar_pdf(url: str, pasta: str = "pdfs", sessao: requests.Session | None = None, nome_sugerido: str | None = None, max_tentativas: int = 3) -> bool:
    import time
    os.makedirs(pasta, exist_ok=True)
    nome = (re.sub(r'[<>:"/\\|?*]', "_", nome_sugerido) if nome_sugerido else nome_seguro(url))
    if nome and not nome.lower().endswith(".pdf"):
        nome += ".pdf"
    caminho = os.path.join(pasta, nome)

    base, ext = os.path.splitext(nome)
    contador = 1
    while os.path.exists(caminho):
        nome = f"{base}_{contador}{ext}"
        caminho = os.path.join(pasta, nome)
        contador += 1

    sessao = sessao or requests.Session()
    sessao.headers.update(HEADERS)

    for tentativa in range(1, max_tentativas + 1):
        try:
            response = sessao.get(url, timeout=120, stream=True)
            response.raise_for_status()

            with open(caminho, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"  [OK] Baixado: {nome}")
            return True
        except requests.RequestException as e:
            if os.path.exists(caminho):
                try:
                    os.remove(caminho)
                except Exception:
                    pass
            if tentativa < max_tentativas:
                print(f"  [Tentativa {tentativa}/{max_tentativas}] Falhou, tentando novamente em 5s...")
                time.sleep(5)
            else:
                print(f"  [ERRO] Ao baixar apos {max_tentativas} tentativas: {e}")
                return False
    return False


def baixar_pdfs_site(url: str, pasta: str = "pdfs", sessao: requests.Session | None = None, usar_selenium: bool = False) -> int:
    print(f"\nAnalisando: {url}")

    if usar_selenium:
        pdfs, sessao, cliques = encontrar_pdfs_selenium(url, pasta)
    else:
        pdfs = encontrar_pdfs(url, sessao)
        cliques = 0

    if not pdfs and cliques == 0:
        print("  Nenhum PDF encontrado.")
        return 0

    baixados = cliques
    if pdfs:
        print(f"  Encontrados {len(pdfs)} link(s) de PDF")
        for link in pdfs:
            if baixar_pdf(link, pasta, sessao):
                baixados += 1

    return baixados


def main():
    pasta_destino = "pdfs"
    if "--pasta" in sys.argv:
        idx = sys.argv.index("--pasta")
        if idx + 1 < len(sys.argv):
            pasta_destino = sys.argv[idx + 1]
    if "-p" in sys.argv:
        idx = sys.argv.index("-p")
        if idx + 1 < len(sys.argv):
            pasta_destino = sys.argv[idx + 1]

    usar_selenium = "--browser" in sys.argv or "-b" in sys.argv
    modo_curso = "--curso" in sys.argv or "-c" in sys.argv
    excluir = set()
    if "--pasta" in sys.argv and sys.argv.index("--pasta") + 1 < len(sys.argv):
        excluir.add(sys.argv[sys.argv.index("--pasta") + 1])
    if "-p" in sys.argv and sys.argv.index("-p") + 1 < len(sys.argv):
        excluir.add(sys.argv[sys.argv.index("-p") + 1])

    apenas_aula = None
    if "--aula" in sys.argv:
        idx = sys.argv.index("--aula")
        if idx + 1 < len(sys.argv) and sys.argv[idx + 1].isdigit():
            apenas_aula = int(sys.argv[idx + 1])
            excluir.add(sys.argv[idx + 1])
    if "-a" in sys.argv:
        idx = sys.argv.index("-a")
        if idx + 1 < len(sys.argv) and sys.argv[idx + 1].isdigit():
            apenas_aula = int(sys.argv[idx + 1])
            excluir.add(sys.argv[idx + 1])

    urls = [u for u in sys.argv[1:] if not u.startswith("-") and u not in excluir]

    if not urls:
        print("  Uso: python bot_pdf.py --curso <URL> ou python bot_pdf.py <URL>")
        print("  Exemplo: python bot_pdf.py --curso https://.../cursos/123456/aulas")
        return

    print("=== Bot de Download de PDFs ===\n")

    if modo_curso:
        if apenas_aula:
            print("  [Modo curso] Apenas aula", apenas_aula, "\n")
        else:
            print("  [Modo curso] Baixando de todas as aulas\n")
        total = baixar_pdfs_curso(urls[0], pasta_destino, apenas_aula=apenas_aula)
    elif usar_selenium:
        print("  [Modo navegador] Usando Brave/Edge/Chrome (Selenium)\n")
        sessao = None
        total = 0
        for url in urls:
            total += baixar_pdfs_site(url, pasta_destino, sessao, usar_selenium=True)
    else:
        sessao = carregar_sessao()
        total = 0
        for url in urls:
            total += baixar_pdfs_site(url, pasta_destino, sessao, usar_selenium=False)

    print(f"\nTotal: {total} PDF(s) baixado(s) em '{pasta_destino}/'")


if __name__ == "__main__":
    main()
