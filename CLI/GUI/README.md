# GUI — SPDA · Análise de Risco (ABNT NBR 5419-2:2026)

Interface gráfica do software de análise de risco. O visual é a cópia fiel do
design em `guibase/` (feito no Claude design); o motor de cálculo é o do CLI
(pacote Python `spda`) — cálculo, estudo de solução e relatório rodam no
Python, garantindo os mesmos números da linha de comando e dos testes.

## Como rodar

```
python GUI/server.py
```

Abre o navegador em `http://127.0.0.1:8420/` automaticamente.
Opções: `--port N` (porta) e `--no-browser` (não abrir o navegador).

Requisitos: os mesmos do CLI (`pydantic`). Rode a partir da raiz do
repositório ou com o pacote instalado (`pip install -e .`).

## Arquitetura

| Arquivo | Papel | Origem |
|---|---|---|
| `index.html` | Template da interface (runtime DC) | cópia de `guibase/SPDA.dc.html`; muda só o import do motor e a exportação de relatório |
| `support.js` | Runtime do design (React) | cópia idêntica de `guibase/` |
| `spda-model.js` | Enums, rótulos, defaults, projeto exemplo | cópia idêntica de `guibase/` |
| `spda-api.js` | Adaptador do motor: mesma API do `spda-calc.js`, mas delega ao Python via XHR síncrono + cache | novo |
| `server.py` | Servidor local (stdlib): estáticos + `/api/analise`, `/api/pacotes`, `/api/avaliar`, `/api/relatorio`, `/api/ref` | novo |
| `vendor/` | React 18 UMD local (funciona offline; `support.js` só busca CDN se `window.React` faltar) | unpkg |

Diferenças intencionais em relação ao `guibase/`:

- `spda-calc.js` e `spda-relatorio.js` (portes JS do motor) **não são usados**:
  todo cálculo vem de `spda/` (fonte única de verdade).
- "Exportar relatório" gera o memorial completo do CLI
  (`spda.relatorio.memorial`, com notas, diagnóstico e glossário) +
  recomendações do estudo de solução + propostas salvas na GUI.
- Os JSON salvos/carregados pela GUI são compatíveis com o CLI
  (`Teste.json` funciona nos dois).
- Proposta salva idêntica às medidas atuais aparece no relatório com uma nota
  (o guibase omitia em silêncio); combo de proposta com chave ausente mantém o
  valor atual da medida em vez de anulá-la.
- O Estudo de Solução usa as 9 medidas do catálogo do CLI
  (`spda/solucao/catalogo.py`) — SPDA (P_B), toque/passo (P_TA, Tab. B.1),
  DPS coordenado (P_SPD, B.3), incêndio (r_p, C.4), ligação equipotencial na
  entrada (P_EB, B.7), toque na entrada das linhas (P_TU, B.6), blindagem das
  linhas externas (P_LD/C_LI, B.4/B.8), fiação interna (K_S3, B.5) e blindagem
  espacial (K_S2) — o guibase tinha só as 4 primeiras. Os degraus extremos de
  toque/passo (malha equipotencial, descida natural, restrições físicas — P=0)
  aparecem só no simulador manual; a busca automática para em isolação e usa
  orçamento adaptativo (reduz alvos por medida até ≤ 600 combinações).
