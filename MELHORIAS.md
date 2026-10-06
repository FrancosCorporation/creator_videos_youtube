# MELHORIAS — creator_videos_youtube

> **Gerado por análise de código em 2026-10-05** · Stack: Python 3 + YouTube Data API v3 (estudo de 2022)
> Branch `main` · 73 LOC em 2 arquivos · `.env.example` presente · sem requirements.txt · sem testes · sem CI
>
> **Este arquivo é um plano de execução.** Cada item tem ID, `arquivo:linha`, mudança exata,
> critério de aceite e comando de verificação.

---

## 0. Como usar este documento

1. Execute na ordem **P0 → P1 → P2 → P3**, respeitando as ondas da §8.
2. Ao terminar um item: marque `- [x]`, rode o **Verificação**, comite `fix(<ID>): descrição`.
3. Este é um projeto de estudo — itens P0 são de **funcionalidade** (o fluxo OAuth não roda mais), não de produção.
4. **Idioma:** português.

---

## 1. Diagnóstico executivo

Dois scripts de estudo: `Main_api.py` lista vídeos populares via **API key**; `Main_json.py` usa **OAuth 2.0**
(`InstalledAppFlow`) com `client_secret.json`. Ambos leem config de variáveis de ambiente.

**O que está bem (não regredir):**

| Item | Evidência |
|---|---|
| `.env.example` presente com as 2 variáveis | `.env.example` |
| `.gitignore` cobre `.env` e `client_secret*.json` | `.gitignore` |
| README avisa para **revogar** credencial antiga | README (seção final) |
| Chave via `os.environ.get`, não literal | `Main_api.py:16` |
| `OAUTHLIB_INSECURE_TRANSPORT` deixado **comentado** | `Main_api.py:12`, `Main_json.py:14` |

**O que está quebrado:**

1. **OAuth não roda:** `flow.run_console()` (`Main_json.py:31`) — Google desligou o OOB/console flow
   (deprecated 2022, removido 2023). Todo o fluxo `Main_json.py` lança exceção.
2. **Fallbacks silenciosos:** key vazia (`Main_api.py:16`) → erro da API em runtime com mensagem crua;
   `client_secret.json` default inexistente → `FileNotFoundError` sem contexto.
3. Sem `requirements.txt`, sem tratamento de erro, sem testes, sem CI. README descreve comportamento
   ("abre o navegador") que o código nunca teve.

---

## 2. Tabela de prioridades

| ID | Título | Sev | Arquivo | Depende de |
|---|---|---|---|---|
| BUG-01 | `run_console()` desligado pela Google — OAuth morto | **P0** | `Main_json.py:31` | — |
| BUG-02 | Fallbacks vazios sem fail-fast (key/client_secret) | **P0** | `Main_api.py:16`, `Main_json.py:24` | — |
| SEC-01 | Sem requirements.txt (deps Google sem pin) | **P1** | *(ausente)* `requirements.txt` | — |
| BUG-03 | `execute()` sem tratamento; `errors` importado e nunca usado | **P1** | `Main_json.py:11,36` | — |
| DOC-01 | README descreve "abre o navegador" mas `run_console` é fluxo de console | **P2** | `README.md` | BUG-01 |
| TEST-01 | Zero testes | **P2** | *(ausente)* | BUG-01 |
| DEVOPS-01 | Sem CI/lint | **P2** | *(ausente)* `.github/workflows/` | — |
| IMP-01 | Boilerplate duplicado entre os 2 scripts | **P3** | `Main_api.py`, `Main_json.py` | — |

---

## 3. Segurança

### SEC-01 · Sem requirements.txt — bibliotecas Google sem pin · [P1]

- **Arquivo:** *(ausente)* `requirements.txt`
- **Evidência:** `googleapiclient.discovery` (`Main_api.py:9`), `google_auth_oauthlib.flow` e
  `googleapiclient.errors` (`Main_json.py:9-11`) importados; nenhum manifest de dependências no repo.
  README manda `pip install google-api-python-client google-auth-oauthlib` **solto**.
- **Impacto:** instalação irreproduzível; sem pin não há `pip audit` nem Dependabot; mudança de API do
  Google passa despercebida até quebrar em runtime.
- **Mudança:** criar `requirements.txt` com versões fixas testadas:
  `google-api-python-client==<ver>`, `google-auth-oauthlib==<ver>`.
- **Aceite:** `pip install -r requirements.txt` instala versões fixas.
- **Verificação:**
  ```bash
  cat requirements.txt && pip install -r requirements.txt --dry-run 2>&1 | tail -3
  ```

---

## 4. Bugs e defeitos funcionais

### BUG-01 · `flow.run_console()` desligado pela Google — fluxo OAuth morto · [P0]

- **Arquivo:** `Main_json.py:31`
- **Evidência:**
  ```python
  credentials = flow.run_console()
  ```
  O fluxo out-of-band (`run_console`) foi **deprecated em 2023 e desligado** pela Google — não há
  mais tela de consentimento para fluxo de console. O script lança exceção antes de construir o
  cliente `youtube`.
- **Impacto:** o ponto de entrada OAuth do projeto **não funciona** em ambiente algum. Só o fluxo
  por API key (`Main_api.py`) roda.
- **Mudança:** migrar para fluxo local com servidor: `InstalledAppFlow.run_local_server(port=0)`
  (recomendação atual do Google) ou `run_local_server(open_browser=False)` + manual. Alternativa
  atual: usar **API key** (já existe no `Main_api.py`) se o script só lê `mostPopular`.
- **Aceite:** `python Main_json.py` completa o fluxo e imprime a resposta (sem exceção).
- **Verificação:**
  ```bash
  grep -n 'run_console' Main_json.py || echo "fluxo migrado"
  grep -n 'run_local_server' Main_json.py
  ```

### BUG-02 · Fallbacks vazios sem fail-fast · [P0]

- **Arquivo:** `Main_api.py:16`, `Main_json.py:24`
- **Evidência:**
  ```python
  DEVELOPER_KEY = os.environ.get("YOUTUBE_API_KEY", "")                      # Main_api.py:16
  client_secrets_file = os.environ.get("YOUTUBE_CLIENT_SECRETS_FILE", "client_secret.json")  # Main_json.py:24
  ```
  Sem a env var, o script **não acusa erro no início** — segue com key vazia e falha com erro da API
  do Google em runtime (HTTP 403 confuso) ou com `FileNotFoundError` cru quando o arquivo default
  não existe.
- **Impacto:** primeiro contato do usuário é um traceback sem dizer "faltou a env var". O README
  já exige `.env` — o código devia falhar rápido com a mesma exigência.
- **Mudança:** fail-fast no topo: se `not os.environ.get("YOUTUBE_API_KEY")` → `sys.exit("defina YOUTUBE_API_KEY (ver .env.example)")`; checar `os.path.exists(client_secrets_file)` antes do flow com mensagem equivalente.
- **Aceite:** sem a env var, o script sai com código ≠ 0 e mensagem clara, sem traceback.
- **Verificação:**
  ```bash
  env -u YOUTUBE_API_KEY python Main_api.py 2>&1 | head -3   # mensagem clara, não 403
  ```

### BUG-03 · `execute()` sem tratamento; import morto · [P1]

- **Arquivo:** `Main_json.py:11,36` (e `Main_api.py:26`)
- **Evidência:** `response = request.execute()` sem `try/except` em ambos os scripts;
  `import googleapiclient.errors` (`Main_json.py:11`) nunca é referenciado — import morto.
- **Impacto:** erro de cota/quota/credencial vira traceback cru; o import que deveria tratar o erro
  existe mas não é usado.
- **Mudança:** `try/except HttpError` (já importado!) com mensagem de cota/credencial; remover import
  morto ou usá-lo.
- **Aceite:** erro da API vira mensagem acionável (cota vs credencial vs rede).
- **Verificação:**
  ```bash
  grep -n 'except.*HttpError\|errors\.' Main_json.py Main_api.py
  ```

---

## 5. Qualidade: testes

### TEST-01 · Zero testes · [P2]

- **Arquivo:** *(ausente)* `test_*.py`
- **Evidência:** nenhum arquivo de teste; `find . -name 'test*'` vazio.
- **Impacto:** `BUG-02` (fallback silencioso) é exatamente o que um teste de "sem env var → exit" pegaria.
- **Mudança:** testes unitários **sem rede**: (a) sem `YOUTUBE_API_KEY` → `SystemExit`;
  (b) `client_secret` inexistente → mensagem clara; (c) mock do `build()` só para checar argumentos.
- **Aceite:** `pytest` ≥ 3 testes verdes.
- **Verificação:**
  ```bash
  python -m pytest -q 2>&1 | tail -3
  ```

---

## 6. DevOps / Infra

### IMP-01 · Boilerplate duplicado entre os scripts · [P3]

- **Arquivo:** `Main_api.py:14-20`, `Main_json.py:17-31`
- **Evidência:** ambos constroem `api_service_name/api_version` e `build()` quase idênticos;
  `def main()` + `if __name__ == '__main__'` duplicados.
- **Impacto:** correção aplicada num script esquecida no outro (padrão já observado nos gêmeos `Db_Mongo_*` deste acervo).
- **Mudança:** extrair `common.py` com `build_client(mode)` — modo `api-key`/`oauth`.
- **Aceite:** um único lugar para construir o cliente.
- **Verificação:**
  ```bash
  grep -c 'discovery.build' Main_api.py Main_json.py  # ideal: 1 (no common)
  ```

### DEVOPS-01 · Sem CI/lint · [P2]

- **Arquivo:** *(ausente)* `.github/workflows/`
- **Evidência:** nenhum workflow; nenhum ruff/flake8 configurado.
- **Impacto:** `BUG-01` (API morta) só foi descoberto por análise humana; CI com `py_compile` + ruff é o piso.
- **Mudança:** workflow: `python -m py_compile Main_api.py Main_json.py` + `ruff check .` + (após `TEST-01`) `pytest`.
- **Aceite:** push com erro de sintaxe é bloqueado.
- **Verificação:**
  ```bash
  python -m py_compile Main_api.py Main_json.py && echo OK
  ```

---

## 7. Documentação

### DOC-01 · README descreve fluxo que nunca existiu · [P2]

- **Arquivo:** `README.md`
- **Evidência:** README diz `python Main_json.py  # fluxo OAuth (abre o navegador)` — mas
  `run_console()` **não** abre navegador (era fluxo de colagem de código). Inconsistente com o
  código E com a API atual.
- **Impacto:** quem segue o README espera tela de navegador e não vê (hoje: vê exceção).
- **Mudança:** após `BUG-01`, documentar `run_local_server` (abre navegador sim) e pré-requisitos
  (redirect URI local, escopos lidos de `Main_json.py:15-18`).
- **Aceite:** README == comportamento real pós-correção.
- **Verificação:**
  ```bash
  grep -n 'abre o navegador\|run_local_server' README.md
  ```

---

## 8. Ordem de execução (waves)

### Wave 1 — Fazer rodar (P0)
1. **`BUG-02`** — fail-fast (30 min, desbloqueia uso do fluxo API key).
2. **`BUG-01`** — migrar OAuth para `run_local_server`.

### Wave 2 — Robustez (P1)
3. **`SEC-01`** — requirements.txt.
4. **`BUG-03`** — tratamento de erro com `HttpError`.

### Wave 3 — Qualidade (P2/P3)
5. **`DOC-01`** — sincronizar README com o novo fluxo (só depois do `BUG-01`).
6. **`TEST-01`** + **`DEVOPS-01`**.
7. **`IMP-01`** — dedup opcional.

**Dependências que não podem ser invertidas:** `DOC-01` depois de `BUG-01` (senão documenta o fluxo
antigo) · `TEST-01` depois de `BUG-02` (o teste é que trava o fail-fast).

---

## 9. Fora de escopo / riscos

| Item | Decisão | Motivo |
|---|---|---|
| Commitar `client_secret.json` ou `.env` | **Nunca** | `.gitignore` já cobre — não mexer na cobertura. |
| Reusar chave antiga já vazada | **Não** | README manda revogar; se revisitar o fluxo, chave nova. |
| Aumentar escopos OAuth | **Não** | Escopos em `Main_json.py:15-18` já são amplos (`youtube.force-ssl`, `youtubepartner`); só ampliar com necessidade demonstrada. |
| Vender/comercializar o script | **Fora de escopo** | Projeto de estudo. |

**Riscos desta execução:**

- `run_local_server` exige **redirect URI local** configurado no Google Cloud ( tipo
  `http://localhost:<porta>`) — testar com o console do Google aberto.
- Escopos amplos: rodar o fluxo exige consentimento consciente.

---

## 10. Definição de pronto (DoD)

**Funcional**
- [ ] `BUG-01` — `python Main_json.py` completa sem exceção (fluxo `run_local_server`)
- [ ] `BUG-02` — sem env var: saída com mensagem clara, sem traceback/403
- [ ] `BUG-03` — erro da API vira mensagem acionável

**Segurança/qualidade**
- [ ] `SEC-01` — requirements.txt com pins
- [ ] `TEST-01` — pytest ≥ 3 sem rede
- [ ] `DEVOPS-01` — CI com py_compile + ruff
- [ ] `DOC-01` — README == comportamento real
- [ ] `IMP-01` — dedup (opcional P3)

**Validação final:**
```bash
python -m py_compile Main_api.py Main_json.py && echo OK
grep -n 'run_console' Main_json.py || echo "migrado"
cat requirements.txt
python -m pytest -q 2>&1 | tail -3
```

---

*Fim do plano. Gerado por leitura direta do código em 2026-10-05. Nenhum item já estava corrigido*
*— todos apontam para defeitos ainda presentes.*
