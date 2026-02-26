# 📚 PDF Download Bot — Organize seus estudos

Bot em Python para baixar materiais em PDF de plataformas de cursos online. Feito por uma estudante, para estudantes que querem ter os materiais organizados localmente de forma eficiente.

## ✨ O que faz

- Baixa PDFs automaticamente de páginas com conteúdo de cursos
- Suporta sites que exigem login (via arquivo de cookies)
- Modo curso: percorre todas as aulas e baixa o material em versão original
- Scripts prontos para rodar vários cursos em sequência

## 🚀 Começando

### Pré-requisitos

- **Python 3.10+** — [Baixar](https://www.python.org/downloads/) (marque "Add Python to PATH")
- **Brave, Edge ou Chrome** — para sites que carregam conteúdo com JavaScript

### Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/pdf-download-bot.git
cd pdf-download-bot

# Instale as dependências
pip install -r requirements.txt
```

### Uso básico

**Um curso:**

```bash
python bot_pdf.py --curso "https://site.com/cursos/123456/aulas"
```

**Especificar pasta de destino:**

```bash
python bot_pdf.py --curso "URL_DO_CURSO" --pasta "pdfs/Minha Materia"
```

**Modo navegador** (para sites com JavaScript/SPA):

```bash
python bot_pdf.py --browser "URL_DA_PAGINA"
```

## 📁 Estrutura do projeto

```
.
├── bot_pdf.py          # Bot principal
├── baixar_cursos.ps1   # Script para vários cursos (edite a lista)
├── baixar_bizus.ps1    # Script de exemplo
├── requirements.txt
├── TUTORIAL.md         # Guia passo a passo detalhado
└── cookies.txt         # (você cria) — sessão logada
```

## 🔐 Sites com login

Para plataformas que exigem login:

1. Instale a extensão **"Get cookies.txt LOCALLY"** no navegador
2. Faça login no site normalmente
3. Exporte os cookies e salve como `cookies.txt` na pasta do bot
4. Execute o bot — ele usará sua sessão

> ⚠️ **Segurança:** Nunca compartilhe `cookies.txt`. Ele está no `.gitignore` para não ir no commit.

## 📖 Mais informações

Consulte o [TUTORIAL.md](TUTORIAL.md) para um guia completo com exemplos e troubleshooting.

## ⚠️ Aviso legal

Use este bot apenas com materiais aos quais você tem acesso legítimo. Respeite os termos de uso das plataformas.

## 📄 Licença

MIT — use como quiser para seus estudos.
