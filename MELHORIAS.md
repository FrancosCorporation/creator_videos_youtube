# MELHORIAS — creator_videos_youtube

> **Análise inicial:** 2026-10-05 · **Atualizado:** 2026-10-11 · Python 3.11+ e YouTube Data API v3
> Branch `master` · `Main_api.py`/`Main_json.py` compartilham `common.py` · CI estático · TEST-01 pendente
>
> Plano de execução com evidência, mudança e verificação para cada item.

---

## 0. Como usar este documento

1. Siga P0 → P1 → P2 → P3.
2. Ao concluir um item, marque o estado e rode sua verificação estática.
3. Não versione chaves, `.env` ou JSON de credenciais OAuth.
4. Este projeto é um exemplo de estudo; OAuth real exige credenciais e consentimento do usuário.

---

## 1. Diagnóstico executivo

O projeto tem dois exemplos de leitura da lista `mostPopular`: autenticação por API key e OAuth Desktop.
Os scripts agora compartilham configuração, tratamento de erros e exibição de até dez títulos, canais e links.

**Problemas iniciais corrigidos:**

1. `run_console()` usava o fluxo OAuth fora de banda que o Google não suporta mais.
2. Credenciais ausentes falhavam tarde e com traceback.
3. Erros da API não explicavam cota ou configuração.
4. Não havia versões fixas, CI, nem instrução para exportar as variáveis do `.env`.

**Cuidados mantidos:**

- `.env` e `client_secret*.json` ficam fora do Git.
- OAuth usa apenas `youtube.readonly` e callback local em `127.0.0.1`.
- `OAUTHLIB_INSECURE_TRANSPORT` não é habilitado.
- Não foi adicionado teste automatizado nesta execução.

---

## 2. Tabela de prioridades

| ID | Título | Sev | Arquivos | Estado |
|---|---|---|---|---|
| BUG-01 | OAuth fora de banda substituído por fluxo Desktop loopback | **P0** | `common.py` | Implementado; autorização real requer credenciais locais |
| BUG-02 | Validar API key e arquivo OAuth antes do uso | **P0** | `common.py` | Implementado |
| SEC-01 | Fixar dependências Google | **P1** | `requirements.txt` | Implementado |
| SEC-02 | Metadados remotos podem incluir controles de terminal | **P2** | `common.py` | Implementado nesta reauditoria |
| BUG-03 | Tratar falhas de API e rede | **P1** | `common.py` | Implementado |
| DEVOPS-02 | Python 3.10 fora de suporte no requisito e CI | **P1** | README, pyproject, workflow | Implementado nesta reauditoria |
| TEST-01 | Cobrir configuração e chamadas sem rede | **P2** | *(ausente)* | Pendente |
| DEVOPS-01 | CI com sintaxe e lint | **P2** | `.github/workflows/ci.yml` | Implementado |
| DOC-01 | Documentar instalação e comportamento real | **P2** | `README.md` | Implementado |
| IMP-01 | Remover boilerplate duplicado | **P3** | `common.py`, `Main_api.py`, `Main_json.py` | Implementado |

---

## 3. Segurança

### SEC-01 · Dependências Google sem versões fixas · [P1]

- **Arquivo:** `requirements.txt`
- **Evidência:** os dois scripts dependem de bibliotecas Google, mas o projeto não tinha manifest.
- **Mudança:** fixar `google-api-python-client==2.201.0` e `google-auth-oauthlib==1.5.0`; fixar Ruff `0.17.0` em `requirements-dev.txt`.
- **Aceite:** instalação reproduzível com requisitos de runtime e de desenvolvimento.
- **Estado:** implementado; versões publicadas conferidas em 11/10/2026.
- **Verificação:** `python3 -m pip install -r requirements-dev.txt --dry-run`

### SEC-02 · Metadados remotos podiam controlar o terminal · [P2]

- **Arquivo:** `common.py`
- **Evidência:** títulos e nomes de canal vêm da resposta da API e eram impressos diretamente; caracteres de controle e de direção bidirecional podem alterar a apresentação no terminal.
- **Mudança:** substituir controles C0/C1 e controles de direção por espaços, usar texto de fallback quando o resultado ficar vazio e só gerar links para IDs de vídeo com 11 caracteres válidos.
- **Aceite:** texto remoto não consegue emitir sequências de controle no terminal e um ID malformado não vira link.
- **Estado:** implementado nesta reauditoria.
- **Verificação:** sintaxe e Ruff passaram localmente em Python 3.14; [CI](https://github.com/FrancosCorporation/creator_videos_youtube/actions/runs/38193332541) passou em Python 3.11 e 3.14. Resposta remota não foi simulada nesta rodada.

---

## 4. Bugs e defeitos funcionais

### BUG-01 · OAuth fora de banda não é suportado · [P0]

- **Arquivo:** `Main_json.py` e `common.py`
- **Evidência:** `InstalledAppFlow.run_console()` usava o fluxo manual de código OOB, bloqueado pelo Google.
- **Mudança:** executar `run_local_server` em `127.0.0.1` com porta efêmera, abrir navegador e pedir apenas `youtube.readonly`.
- **Aceite:** o script usa o fluxo de loopback para app Desktop e lista os vídeos após a autorização.
- **Estado:** código implementado. A autorização real não foi exercitada porque não há `client_secret.json` local nem consentimento disponível.
- **Verificação:** `rg -n 'run_local_server|youtube.readonly|run_console' common.py Main_json.py`

### BUG-02 · Credenciais vazias falhavam sem instrução · [P0]

- **Arquivo:** `common.py`
- **Evidência:** chave vazia seguia para a API; arquivo OAuth ausente causava `FileNotFoundError`.
- **Mudança:** validar `YOUTUBE_API_KEY` e `YOUTUBE_CLIENT_SECRETS_FILE` antes de iniciar cliente ou navegador.
- **Aceite:** configuração ausente produz mensagem clara e saída não zero sem traceback.
- **Verificação:** depois de instalar requisitos, `env -u YOUTUBE_API_KEY python3 Main_api.py`

### BUG-03 · Erros da API apareciam como traceback · [P1]

- **Arquivo:** `common.py`
- **Evidência:** `execute()` não tratava cota, credenciais recusadas ou falha de rede.
- **Mudança:** mapear HTTP 401/403, limites de cota e erros de transporte para mensagens curtas com orientação.
- **Aceite:** o usuário sabe se deve revisar chave/permissões, cota ou conexão; payloads não são exibidos.
- **Verificação:** `rg -n 'except HttpError|cota|credenciais|conexão' common.py`

---

## 5. Qualidade: testes

### TEST-01 · Sem testes automatizados · [P2]

- **Arquivo:** *(ausente)* `test_*.py`
- **Evidência:** não há suíte que cubra credenciais vazias, JSON inexistente ou chamadas simuladas.
- **Mudança:** adicionar testes sem rede cobrindo fail-fast, OAuth ausente e construção do cliente.
- **Aceite:** pelo menos três testes automatizados passam.
- **Estado:** pendente; nenhuma suíte foi adicionada ou executada nesta execução.
- **Verificação futura:** `python3 -m pytest -q`

---

## 6. DevOps / Infra

### DEVOPS-01 · Sem CI/lint · [P2]

- **Arquivo:** `.github/workflows/ci.yml`, `requirements-dev.txt`, `pyproject.toml`
- **Evidência:** não havia checagem automática de sintaxe ou estilo.
- **Mudança:** CI em Python 3.11 e 3.14 com `py_compile` e Ruff; dependências de desenvolvimento fixadas.
- **Aceite:** push ou pull request com erro de sintaxe ou lint falha na CI.
- **Verificação local:** `python3 -m py_compile Main_api.py Main_json.py common.py && ruff check Main_api.py Main_json.py common.py`

### DEVOPS-02 · Python 3.10 chegou ao fim do suporte · [P1]

- **Arquivos:** `README.md`, `pyproject.toml`, `.github/workflows/ci.yml`
- **Evidência:** Python 3.10 encerrou o suporte em 1º de outubro de 2026; o README ainda prometia compatibilidade e o CI só verificava Python 3.14.
- **Mudança:** elevar o mínimo documentado e o alvo do Ruff para Python 3.11; fixar o runner em Ubuntu 24.04 e executar as verificações em Python 3.11 e 3.14.
- **Aceite:** o requisito declarado tem suporte de segurança ativo e ambos os extremos da matriz são verificados no CI.
- **Estado:** implementado e publicado no commit `fd39e2d`; CI passou em Python 3.11 e 3.14 ([execução](https://github.com/FrancosCorporation/creator_videos_youtube/actions/runs/38193332541)).

### IMP-01 · Boilerplate duplicado · [P3]

- **Arquivo:** `Main_api.py`, `Main_json.py`, `common.py`
- **Evidência:** os scripts duplicavam criação de cliente, chamada e apresentação.
- **Mudança:** centralizar clientes, consulta, tratamento de erros e saída em `common.py`; manter dois entrypoints pequenos.
- **Aceite:** os entrypoints selecionam somente o modo de autenticação.
- **Verificação:** `cat Main_api.py Main_json.py && rg -n 'discovery.build|\.list\(' common.py`

---

## 7. Documentação

### DOC-01 · Instruções divergiam do código · [P2]

- **Arquivo:** `README.md`
- **Evidência:** o README dizia que OAuth abria o navegador, mas o código antigo usava console; não explicava o carregamento do `.env`.
- **Mudança:** documentar venv, instalação fixada, exportação do `.env`, chave restrita, OAuth Desktop, callback loopback e erros conhecidos.
- **Aceite:** instalação e os dois comandos descritos correspondem ao código; segredos seguem ignorados.
- **Verificação:** `rg -n 'run_local_server|source \.env|youtube.readonly|requirements.txt' README.md`

---

## 8. Ordem de execução

1. **Wave 1 — P0:** `BUG-02`, `BUG-01`.
2. **Wave 2 — P1:** `SEC-01`, `BUG-03`, `DEVOPS-02`.
3. **Wave 3 — P2/P3:** `SEC-02`, `DOC-01`, `DEVOPS-01`, `IMP-01`; `TEST-01` permanece pendente.

---

## 9. Fora de escopo e riscos

| Item | Decisão | Motivo |
|---|---|---|
| Versionar `.env` ou `client_secret.json` | **Nunca** | Contêm credenciais privadas. |
| Reusar credencial antiga | **Não** | Credencial antiga deve ser revogada no Google Cloud. |
| Publicar, editar ou remover vídeos | **Fora de escopo** | Os scripts apenas consultam a lista de vídeos. |

O OAuth precisa de sessão local com navegador e credencial Desktop do usuário. O escopo mínimo foi reduzido para `youtube.readonly`.

---

## 10. Definição de pronto

**Funcional e segurança**
- [x] `BUG-01` — fluxo loopback e escopo de leitura implementados
- [x] `BUG-02` — validação fail-fast com instruções implementada
- [x] `BUG-03` — erros de API/rede tratados
- [x] `SEC-01` — dependências de runtime fixadas
- [x] `SEC-02` — metadados remotos têm controles de terminal removidos e IDs validados
- [x] `DEVOPS-02` — mínimo atualizado para Python 3.11, suportado pela CI em 3.11 e 3.14

**Qualidade e entrega**
- [ ] `TEST-01` — testes sem rede (pendente)
- [x] `DEVOPS-01` — CI com sintaxe e Ruff
- [x] `DOC-01` — README atualizado
- [x] `IMP-01` — lógica comum centralizada

**Validação estática:**

```bash
python3 -m py_compile Main_api.py Main_json.py common.py
ruff check Main_api.py Main_json.py common.py
python3 -m pip install -r requirements-dev.txt --dry-run
git diff --check
```

---

*Atualizado em 2026-10-11. Validação local em Python 3.14 e CI em Python 3.11/3.14 passaram. TEST-01 e autorização OAuth real permanecem sem validação nesta rodada.*
