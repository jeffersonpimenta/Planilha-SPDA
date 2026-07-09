// spda-api.js — adaptador do motor de cálculo: mesma API do spda-calc.js do
// design (analisar, analisarMemoria, pacotesParaEstrutura, avaliarCombinacao,
// aplicarCombinacaoAoProjeto, REF), mas delegando os cálculos ao pacote Python
// `spda` (o CLI) via servidor local — fonte única de verdade da NBR 5419-2.
//
// As chamadas usam XHR síncrono: o runtime do design chama o motor de forma
// síncrona dentro de renderVals(); o servidor é localhost e cada resposta é
// cacheada por conteúdo, então só há uma ida ao Python por mudança real.

function postSync(rota, corpo) {
  const xhr = new XMLHttpRequest();
  xhr.open("POST", rota, false); // síncrono por contrato do runtime (ver acima)
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.send(JSON.stringify(corpo));
  if (xhr.status !== 200) {
    let msg = xhr.responseText || `HTTP ${xhr.status}`;
    try { msg = JSON.parse(xhr.responseText).erro || msg; } catch (e) { /* texto puro */ }
    throw new Error(msg);
  }
  return xhr.responseText;
}

function postJson(rota, corpo) { return JSON.parse(postSync(rota, corpo)); }

// Cache LRU simples por chave de conteúdo (JSON da requisição).
function criarCache(max) {
  const mapa = new Map();
  return {
    get(chave, calcular) {
      if (mapa.has(chave)) {
        const v = mapa.get(chave);
        mapa.delete(chave); mapa.set(chave, v); // renova posição LRU
        return v;
      }
      const v = calcular();
      mapa.set(chave, v);
      if (mapa.size > max) mapa.delete(mapa.keys().next().value);
      return v;
    },
  };
}

const cacheAnalise = criarCache(20);
const cachePacotes = criarCache(20);
const cacheAvaliar = criarCache(60);

function analiseCompleta(projeto) {
  const chave = JSON.stringify(projeto);
  return cacheAnalise.get(chave, () => postJson("/api/analise", { projeto }));
}

export function analisar(projeto) { return analiseCompleta(projeto).resultado; }
export function analisarMemoria(projeto) { return analiseCompleta(projeto).memoria; }

// R_T padrão (Tabela 4) vindo das tabelas do CLI — carregado uma vez no import.
export const REF = { RT: postJson("/api/ref", {}).RT };

// ---------------------------------------------------------------------------
// Estudo de Solução — a busca combinatória roda no servidor (Python), uma
// requisição por (projeto, estrutura). A aplicação de uma combinação aos
// campos da estrutura é puramente estrutural (sem cálculo) e fica no cliente,
// preservando os _id internos da UI — mesmo catálogo do design.
// ---------------------------------------------------------------------------
function idxOf(valor, escada) {
  if (valor === "nenhum" && escada.includes(null)) valor = null;
  const i = escada.indexOf(valor === undefined ? null : valor);
  return i === -1 ? null : i;
}
function idxZonas(est, campo, escada) {
  if (!est.zonas.length) return null;
  const idxs = est.zonas.map((z) => idxOf(z.medidas[campo], escada));
  if (idxs.some((i) => i === null)) return null;
  return Math.min(...idxs);
}
function idxSistemas(est, escada) {
  const sistemas = est.zonas.flatMap((z) => z.sistemas_internos);
  if (!sistemas.length) return null;
  const idxs = sistemas.map((s) => idxOf(s.dps, escada));
  if (idxs.some((i) => i === null)) return null;
  return Math.min(...idxs);
}

const ESC_SPDA = [null, "IV", "III", "II", "I"];
const ESC_DPS = [null, "IV", "III", "II", "I", "melhor_I"];
const ESC_TP = ["nenhuma", "avisos", "isolacao", "malha_equipotencial", "descida_natural", "restricoes_fisicas"];
const ESC_TU = ["nenhuma", "avisos", "isolacao", "restricoes_fisicas"];
const ESC_INC = ["nenhuma", "extintor", "fixo_automatico"];
const ESC_EB = [null, "IV", "III", "II", "I", "melhor_I"];
const ESC_BLIND = ["nao_blindada", "rs_5_20", "rs_1_5", "rs_ate_1"];
const ESC_KS3 = [1, 0.5, 0.2, 0.01, 0.0001];
const ESC_KS2 = [1, 0.24, 0.12, 0.06, 0.012];
// Linhas já "melhores" que a escada de blindagem (C_LD = 0) nunca são tocadas.
const TIPOS_LINHA_MELHORES = new Set(["eletroduto_metalico", "fibra_optica", "interface_isolante"]);

function idxLinhas(est, campo, escada) {
  const linhas = est.linhas || [];
  if (!linhas.length) return null;
  const idxs = linhas.map((li) => idxOf(li[campo], escada));
  if (idxs.some((i) => i === null)) return null;
  return Math.min(...idxs);
}
function idxFloat(v, escada) {
  if (typeof v === "string" && v !== "") v = Number(v);
  if (typeof v !== "number" || !isFinite(v)) return null;
  const i = escada.findIndex((dv) => Math.abs(v - dv) <= dv * 1e-9);
  return i === -1 ? null : i;
}
function idxSistemasFloat(est, attr, escada) {
  const sistemas = est.zonas.flatMap((z) => z.sistemas_internos);
  if (!sistemas.length) return null;
  const idxs = sistemas.map((s) => idxFloat(s[attr], escada));
  if (idxs.some((i) => i === null)) return null; // valor custom -> não mexe
  return Math.min(...idxs);
}
function idxBlindagem(est) {
  const linhas = (est.linhas || []).filter((li) => !TIPOS_LINHA_MELHORES.has(li.tipo_externa));
  if (!linhas.length) return null;
  const idxs = [];
  for (const li of linhas) {
    if (li.classe_blindagem === "nao_blindada") idxs.push(0);
    else if (li.tipo_externa === "blindada_interligada" && ESC_BLIND.includes(li.classe_blindagem)) idxs.push(ESC_BLIND.indexOf(li.classe_blindagem));
    else return null; // blindada mas não interligada etc. -> fora da escada
  }
  return Math.min(...idxs);
}
function aplicarLinhas(campo) {
  return (est, valor) => {
    const copia = structuredClone(est);
    (copia.linhas || []).forEach((li) => { li[campo] = valor; });
    return copia;
  };
}
function aplicarSistemasFloat(attr) {
  return (est, valor) => {
    const copia = structuredClone(est);
    copia.zonas.forEach((z) => z.sistemas_internos.forEach((s) => { s[attr] = Number(valor); }));
    return copia;
  };
}

export const MEDIDAS = [
  {
    id: "spda", escada: ESC_SPDA,
    aplicavel() { return true; },
    indiceAtual(est) { return idxOf(est.nivel_spda, ESC_SPDA); },
    aplicar(est, valor) { const copia = structuredClone(est); copia.nivel_spda = valor; return copia; },
  },
  {
    id: "toque_passo", escada: ESC_TP,
    aplicavel(est) { return est.zonas.length > 0; },
    indiceAtual(est) { return idxZonas(est, "protecao_toque_passo", ESC_TP); },
    aplicar(est, valor) { const copia = structuredClone(est); copia.zonas.forEach((z) => { z.medidas.protecao_toque_passo = valor; }); return copia; },
  },
  {
    id: "dps", escada: ESC_DPS,
    aplicavel(est) { return est.zonas.some((z) => z.sistemas_internos.length > 0); },
    indiceAtual(est) { return idxSistemas(est, ESC_DPS); },
    aplicar(est, valor) { const copia = structuredClone(est); copia.zonas.forEach((z) => z.sistemas_internos.forEach((s) => { s.dps = valor; })); return copia; },
  },
  {
    id: "incendio", escada: ESC_INC,
    aplicavel() { return true; },
    indiceAtual(est) { return idxOf(est.providencias_incendio, ESC_INC); },
    aplicar(est, valor) { const copia = structuredClone(est); copia.providencias_incendio = valor; return copia; },
  },
  {
    id: "ligacao_eq", escada: ESC_EB,
    aplicavel(est) { return (est.linhas || []).length > 0; },
    indiceAtual(est) { return idxLinhas(est, "nivel_eb", ESC_EB); },
    aplicar: aplicarLinhas("nivel_eb"),
  },
  {
    id: "toque_entrada", escada: ESC_TU,
    aplicavel(est) { return (est.linhas || []).length > 0; },
    indiceAtual(est) { return idxLinhas(est, "protecao_toque_entrada", ESC_TU); },
    aplicar: aplicarLinhas("protecao_toque_entrada"),
  },
  {
    id: "blindagem_linha", escada: ESC_BLIND,
    aplicavel(est) { return (est.linhas || []).length > 0; },
    indiceAtual(est) { return idxBlindagem(est); },
    aplicar(est, valor) {
      const copia = structuredClone(est);
      (copia.linhas || []).forEach((li) => {
        if (TIPOS_LINHA_MELHORES.has(li.tipo_externa)) return;
        if (valor === "nao_blindada") {
          if (li.classe_blindagem === "nao_blindada") return; // já no degrau base
          // Degrau base coerente: sem crédito de blindagem NEM de C_LI.
          li.tipo_externa = "aerea_nao_blindada";
          li.classe_blindagem = "nao_blindada";
        } else {
          li.tipo_externa = "blindada_interligada";
          li.classe_blindagem = valor;
        }
      });
      return copia;
    },
  },
  {
    id: "fiacao", escada: ESC_KS3, num: true,
    aplicavel(est) { return est.zonas.some((z) => z.sistemas_internos.length > 0); },
    indiceAtual(est) { return idxSistemasFloat(est, "K_S3", ESC_KS3); },
    aplicar: aplicarSistemasFloat("K_S3"),
  },
  {
    id: "blindagem_espacial", escada: ESC_KS2, num: true,
    aplicavel(est) { return est.zonas.some((z) => z.sistemas_internos.length > 0); },
    indiceAtual(est) { return idxSistemasFloat(est, "K_S2", ESC_KS2); },
    aplicar: aplicarSistemasFloat("K_S2"),
  },
];

export function medidasDisponiveis(est) {
  return MEDIDAS.filter((m) => m.aplicavel(est) && m.indiceAtual(est) !== null);
}

export function pacotesParaEstrutura(projeto, est, maxPacotes = 3) {
  const estIndex = projeto.estruturas.indexOf(est);
  const chave = JSON.stringify([projeto, estIndex, maxPacotes]);
  return cachePacotes.get(chave, () =>
    postJson("/api/pacotes", { projeto, estIndex, maxPacotes }));
}

export function avaliarCombinacao(projeto, est, combo) {
  const estIndex = projeto.estruturas.indexOf(est);
  const chave = JSON.stringify([projeto, estIndex, combo]);
  return cacheAvaliar.get(chave, () =>
    postJson("/api/avaliar", { projeto, estIndex, combo }));
}

export function aplicarCombinacaoEmEstrutura(est, combo) {
  // Chave ausente no combo (proposta salva antes de a medida existir na
  // estrutura) mantém o valor atual — nunca anula a medida. Medida sem
  // mudança (ou valor fora da escada) não é aplicada: preserva valores
  // mistos reais (ex.: sistemas com DPS diferentes). Valores de <select>
  // chegam como string; escadas numéricas normalizam via idxFloat.
  let atual = est;
  for (const m of medidasDisponiveis(est)) {
    const iAtual = m.indiceAtual(est);
    const bruto = combo[m.id] === undefined ? m.escada[iAtual] : combo[m.id];
    const iAlvo = m.num ? idxFloat(bruto, m.escada) : idxOf(bruto, m.escada);
    if (iAlvo === null || iAlvo === iAtual) continue;
    atual = m.aplicar(atual, m.escada[iAlvo]);
  }
  return atual;
}

export function aplicarCombinacaoAoProjeto(projeto, estIndex, combo) {
  const p = structuredClone(projeto);
  p.estruturas[estIndex] = aplicarCombinacaoEmEstrutura(p.estruturas[estIndex], combo);
  return p;
}

// Relatório completo (memorial + recomendações + propostas) gerado pelo
// relatório do CLI (spda.relatorio) — devolve o HTML pronto.
export function gerarRelatorioHtml(projeto) {
  return postSync("/api/relatorio", { projeto });
}
