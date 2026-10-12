# Ferramentas para criadores de vídeo

Exemplos pequenos de integração com a YouTube Data API v3. Os dois comandos
listam até dez vídeos populares e exibem título, canal e link:

- `Main_api.py` usa uma chave de API para consultar dados públicos.
- `Main_json.py` usa OAuth 2.0 para aplicativo desktop, abrindo o navegador e
  pedindo acesso somente de leitura ao canal.

O gráfico `mostPopular` pode ser limitado por região ou categoria; este exemplo
usa a consulta padrão da API.

## Requisitos e instalação

- Python 3.11 ou superior. Python 3.10 chegou ao fim do suporte em outubro de 2026.
- Uma chave de API ou um cliente OAuth Desktop criado no Google Cloud.

```bash
git clone https://github.com/FrancosCorporation/creator_videos_youtube.git
cd creator_videos_youtube
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
${EDITOR:-nano} .env
set -a
. ./.env
set +a
```

O script não carrega `.env` automaticamente. Os comandos acima exportam as
variáveis para o processo; no Windows, configure as mesmas variáveis na sessão
do PowerShell antes de executar o Python.

## Configurar o Google Cloud

1. Crie ou selecione um projeto no [Google Cloud Console](https://console.cloud.google.com/).
2. Habilite a **YouTube Data API v3**.
3. Para `Main_api.py`, crie uma chave de API e preencha `YOUTUBE_API_KEY` no
   `.env`. Restrinja a chave à YouTube Data API v3 no Console.
4. Para `Main_json.py`, crie um OAuth Client ID do tipo **Desktop app**, baixe o
   JSON para `client_secret.json` na raiz e mantenha-o privado. Se o arquivo
   estiver em outro lugar, ajuste `YOUTUBE_CLIENT_SECRETS_FILE` no `.env`.

O `.gitignore` exclui `.env` e arquivos `client_secret*.json`. Nunca versione
credenciais. As credenciais antigas mencionadas no histórico do repositório
devem ser revogadas no Google Cloud.

## Executar

Com o ambiente virtual ativo e as variáveis carregadas:

```bash
python Main_api.py
python Main_json.py
```

No fluxo OAuth, o Google abre o navegador e redireciona a autorização para um
servidor temporário em `127.0.0.1`. Use uma sessão local com navegador; ao rodar
por SSH ou em servidor sem navegador, prefira `Main_api.py` ou configure um
ambiente desktop acessível.

O OAuth solicita apenas `youtube.readonly`. A autorização não é salva em disco,
então o navegador pode ser aberto novamente em cada execução de `Main_json.py`.
O exemplo consulta dados públicos e não publica, edita ou remove vídeos.

Se a chave estiver vazia ou o JSON OAuth faltar, o programa informa como
corrigir a configuração. Erros de cota e credenciais da API também recebem uma
mensagem curta com o próximo passo.

## Verificações estáticas

```bash
python -m pip install -r requirements-dev.txt
python -m py_compile Main_api.py Main_json.py common.py
ruff check Main_api.py Main_json.py common.py
```

O CI executa sintaxe e lint em Python 3.11 e 3.14. O projeto ainda não tem
testes automatizados.

## Licença

MIT — veja [LICENSE](LICENSE).
