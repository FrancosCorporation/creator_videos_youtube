# creator_videos_youtube

Scripts de exemplo que consomem a **YouTube Data API v3**: listagem dos
vídeos mais populares por **API key** e por **OAuth 2.0**.

![Python](https://img.shields.io/badge/Python-3-3776AB?style=flat-square&logo=python&logoColor=white)
![YouTube API](https://img.shields.io/badge/YouTube%20Data%20API-v3-FF0000?style=flat-square&logo=youtube&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/status-estudo-lightgrey?style=flat-square)

## Sobre

**Projeto de estudo** de 2022 criado para praticar integração com APIs do
Google. São dois pontos de entrada independentes:

- `Main_api.py` — autentica com **API key** e lista os vídeos mais populares
  (`videos().list`, `chart=mostPopular`).
- `Main_json.py` — fluxo **OAuth 2.0** (`InstalledAppFlow`) usando um arquivo
  de credenciais do Google Cloud, com escopos de leitura/gestão do canal.

## Como rodar

```bash
pip install google-api-python-client google-auth-oauthlib
```

1. Crie um projeto no [Google Cloud Console](https://console.cloud.google.com/),
   ative a **YouTube Data API v3**.
2. Copie `.env.example` para `.env` e preencha:

```bash
YOUTUBE_API_KEY=sua_api_key
YOUTUBE_CLIENT_SECRETS_FILE=client_secret.json
```

3. Baixe o `client_secret.json` do seu projeto (OAuth Client ID do tipo
   "Desktop") e salve na raiz — o arquivo **não** é versionado.
4. Execute:

```bash
python Main_api.py    # fluxo por API key
python Main_json.py   # fluxo OAuth (abre o navegador)
```

> As credenciais que existiam neste repositório foram removidas do código.
> Se você chegou a usar a chave antiga, **revogue-a** no Google Cloud Console.

## Licença

MIT — veja [LICENSE](LICENSE).
