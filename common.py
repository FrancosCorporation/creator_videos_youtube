"""Configuração e operações compartilhadas dos exemplos da YouTube API."""

import os
from pathlib import Path

import httplib2
from google.auth.exceptions import GoogleAuthError
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauthlib.oauth2.rfc6749.errors import OAuth2Error

API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
OAUTH_SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]


class UserFacingError(Exception):
    """Erro conhecido que pode ser explicado sem exibir um traceback."""


def build_api_key_client():
    api_key = os.environ.get("YOUTUBE_API_KEY", "").strip()
    if not api_key:
        raise UserFacingError(
            "Defina YOUTUBE_API_KEY no ambiente. Consulte o README e .env.example."
        )

    try:
        return build(
            API_SERVICE_NAME,
            API_VERSION,
            developerKey=api_key,
            cache_discovery=False,
        )
    except (httplib2.HttpLib2Error, OSError) as error:
        raise UserFacingError(
            "Não foi possível conectar à YouTube Data API. Verifique sua rede."
        ) from error


def build_oauth_client():
    secrets_file = Path(
        os.environ.get("YOUTUBE_CLIENT_SECRETS_FILE", "client_secret.json")
    ).expanduser()
    if not secrets_file.is_file():
        raise UserFacingError(
            f"Arquivo OAuth não encontrado: {secrets_file}. Baixe um cliente Desktop "
            "no Google Cloud Console ou ajuste YOUTUBE_CLIENT_SECRETS_FILE."
        )

    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(secrets_file), OAUTH_SCOPES
        )
        credentials = flow.run_local_server(
            host="127.0.0.1",
            port=0,
            open_browser=True,
            authorization_prompt_message=(
                "Autorize o acesso somente de leitura do canal no navegador: {url}"
            ),
            success_message="Autorização concluída. Você pode fechar esta janela.",
        )
        return build(
            API_SERVICE_NAME,
            API_VERSION,
            credentials=credentials,
            cache_discovery=False,
        )
    except (ValueError, OSError) as error:
        raise UserFacingError(
            "Não foi possível ler as credenciais OAuth ou iniciar o retorno local. "
            "Confirme que o arquivo é um cliente Desktop válido e tente novamente."
        ) from error
    except (GoogleAuthError, OAuth2Error) as error:
        raise UserFacingError(
            "A autorização do Google falhou. Confira a tela de consentimento, "
            "o cliente Desktop e a conta selecionada."
        ) from error
    except httplib2.HttpLib2Error as error:
        raise UserFacingError(
            "Não foi possível conectar à YouTube Data API. Verifique sua rede."
        ) from error


def fetch_popular_videos(youtube):
    try:
        response = (
            youtube.videos()
            .list(part="snippet", chart="mostPopular", maxResults=10)
            .execute()
        )
    except HttpError as error:
        status = getattr(error.resp, "status", "desconhecido")
        reason = str(getattr(error, "reason", "")).lower()

        if status == 403 and any(
            marker in reason
            for marker in ("quota", "ratelimit", "dailylimit")
        ):
            raise UserFacingError(
                "A cota da YouTube Data API foi excedida. Consulte a cota "
                "no Google Cloud."
            ) from error
        if status in (401, 403):
            raise UserFacingError(
                "O Google recusou as credenciais. Confira a chave, a API habilitada "
                "e as permissões da conta."
            ) from error
        raise UserFacingError(
            f"A YouTube Data API retornou HTTP {status}. Verifique a configuração "
            "do projeto no Google Cloud."
        ) from error
    except (httplib2.HttpLib2Error, OSError) as error:
        raise UserFacingError(
            "A solicitação não chegou à YouTube Data API. Verifique sua conexão."
        ) from error

    return response.get("items", [])


def print_videos(videos):
    if not videos:
        print("A API não retornou vídeos populares para esta consulta.")
        return

    for index, video in enumerate(videos, start=1):
        snippet = video.get("snippet", {})
        title = snippet.get("title", "Título indisponível").replace("\n", " ")
        channel = snippet.get("channelTitle", "Canal indisponível")
        video_id = video.get("id")

        print(f"{index}. {title}")
        print(f"   Canal: {channel}")
        if isinstance(video_id, str) and video_id:
            print(f"   https://www.youtube.com/watch?v={video_id}")


def run_cli(authentication_mode):
    try:
        if authentication_mode == "api-key":
            youtube = build_api_key_client()
        elif authentication_mode == "oauth":
            youtube = build_oauth_client()
        else:
            raise ValueError("Modo de autenticação desconhecido.")

        print_videos(fetch_popular_videos(youtube))
    except UserFacingError as error:
        raise SystemExit(f"Erro: {error}") from None
