# Tutorial passo a passo: Bot de Download de PDFs

Guia para organizar seus estudos baixando materiais em PDF automaticamente.

---

## Passo 1: Verificar se o Python está instalado

Abra o **Prompt de Comando** ou **PowerShell** e digite:

```
python --version
```

- Se aparecer algo como `Python 3.12.x`, está pronto.
- Se der erro, baixe em: https://www.python.org/downloads/
  - Marque **"Add Python to PATH"** na instalação.

---

## Passo 2: Abrir a pasta do projeto

No terminal, entre na pasta onde está o bot:

```bash
cd caminho/para/pdf-download-bot
```

Exemplo no Windows (PowerShell):

```powershell
cd C:\Users\SeuUsuario\Documentos\pdf-download-bot
```

---

## Passo 3: Instalar as dependências

```bash
pip install -r requirements.txt
```

Aguarde aparecer `Successfully installed`.

---

## Passo 4: Executar o bot

### Opção A: Passar a URL pela linha de comando

**Modo curso** (recomendado para plataformas de cursos):

```bash
python bot_pdf.py --curso "https://site.com/cursos/123456/aulas"
```

**Página única:**

```bash
python bot_pdf.py https://site.com/pagina-com-pdfs
```

**Múltiplas URLs:**

```bash
python bot_pdf.py https://site1.com/docs https://site2.com/arquivos
```

### Opção B: Usar os scripts PowerShell

1. Edite `baixar_cursos.ps1` ou `baixar_bizus.ps1`
2. Ajuste o array `$cursos` com seus cursos e URLs
3. Execute no PowerShell:

```powershell
.\baixar_cursos.ps1
```

Os PDFs serão salvos em subpastas dentro de `pdfs/`.

---

## Passo 5: Onde ficam os PDFs

Os arquivos são salvos na pasta **`pdfs`** dentro do projeto, organizados por curso:

```
pdfs/
├── Nome do Curso 1/
│   ├── Aula_01.pdf
│   ├── Aula_02.pdf
│   └── ...
└── Nome do Curso 2/
    └── ...
```

---

## Sites que exigem login

O bot usa o arquivo `cookies.txt` para manter sua sessão logada.

### 1. Instalar extensão de cookies

No **Brave**, **Chrome** ou **Edge**:

- Procure por **"Get cookies.txt LOCALLY"** na loja de extensões
- Instale a extensão

### 2. Fazer login no site

1. Abra o navegador e faça login normalmente
2. Vá até a página de aulas ou materiais do curso

### 3. Exportar os cookies

1. Clique no ícone da extensão "Get cookies.txt LOCALLY"
2. Clique em **Export** ou **Download**
3. Salve o arquivo como **`cookies.txt`** na pasta do bot (mesmo diretório do `bot_pdf.py`)

### 4. Rodar o bot

```bash
python bot_pdf.py --curso "URL_DA_PAGINA_DE_AULAS"
```

O bot usa **Brave**, **Edge** ou **Chrome** automaticamente e carrega sua sessão via `cookies.txt`.

> **Importante:** Os cookies expiram. Se voltar erro 404, faça login novamente e exporte um novo `cookies.txt`.

---

## Resumo rápido de comandos

| Ação                 | Comando                                                         |
|----------------------|-----------------------------------------------------------------|
| Instalar dependências | `pip install -r requirements.txt`                             |
| Um curso             | `python bot_pdf.py --curso URL`                                |
| Uma matéria em pasta | `python bot_pdf.py --curso URL --pasta "pdfs/Nome da Materia"` |
| Modo navegador       | `python bot_pdf.py --browser URL`                              |
| Página única         | `python bot_pdf.py URL`                                        |
| Script PowerShell    | `.\baixar_cursos.ps1`                                          |

---

## Problemas comuns

### "Python was not found"

Use o caminho completo do executável ou adicione o Python ao PATH:

```bash
# Windows — ajuste a versão conforme sua instalação
C:\Users\SeuUsuario\AppData\Local\Programs\Python\Python312\python.exe bot_pdf.py --curso URL
```

### PDFs não encontrados

- Sites com muito JavaScript precisam do modo `--browser`
- Confirme que o `cookies.txt` está atualizado
- Verifique se a URL é da página de aulas (contém `/aulas`)

### Erro 404 ao baixar

- Exporte novamente os cookies após fazer login
- Salve o arquivo exatamente como `cookies.txt` na pasta do bot

---

## Boas práticas

1. **Respeite os termos de uso** das plataformas
2. **Não compartilhe** `cookies.txt` (contém dados de sessão)
3. **Um curso por vez:** espere terminar um antes de iniciar outro para evitar queda de sessão
4. Mantenha os cookies atualizados se o site desconectar
