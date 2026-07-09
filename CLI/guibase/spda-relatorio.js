// spda-relatorio.js — gerador do relatório/memorial de cálculo (HTML imprimível),
// porte fiel de spda/relatorio/{formato,moldes,glossario,notas,diagnostico,
// memorial,html}.py. Função pura: recebe a Memoria + EstudoSolucao (mesmas
// estruturas produzidas por spda-calc.js) e devolve uma string HTML autônoma,
// pronta para abrir/imprimir.

// --------------------------------------------------------------------------
// formato.py — formatação numérica única do relatório + substituição simbólica
// --------------------------------------------------------------------------
export function fmt(x) {
  if (x === null || x === undefined || Number.isNaN(x)) return "—";
  if (x === 0) return "0";
  const ax = Math.abs(x);
  if (ax < 1e-3 || ax >= 1e4) {
    let s = x.toExponential(3);
    s = s.replace(/e([+-])(\d)$/, "e$10$2");
    return s;
  }
  let s = x.toPrecision(4);
  if (s.includes(".")) s = s.replace(/0+$/, "").replace(/\.$/, "");
  if (s.includes("e")) s = fmt(x); // toPrecision pode cair p/ notação científica
  return s;
}

export function substituir(forma, operandos) {
  const keys = Object.keys(operandos || {});
  if (!keys.length) return forma;
  const nomes = keys.sort((a, b) => b.length - a.length).map((k) => k.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
  const re = new RegExp("\\b(" + nomes.join("|") + ")\\b", "g");
  return forma.replace(re, (m) => fmt(operandos[m]));
}

function campo(v) {
  return v === null || v === undefined || v === "" ? "—" : String(v);
}

// --------------------------------------------------------------------------
// moldes.py — formas simbólicas executáveis (mesma álgebra de spda-calc.js)
// --------------------------------------------------------------------------
const MOLDES = {
  A_D: (o) => ("H_min" in o ? "max((L*W + 2*(3*H_min)*(L+W) + pi*(3*H_min)^2), pi*(3*H_max)^2)" : "L*W + 2*(3*H)*(L+W) + pi*(3*H)^2"),
  N_D: () => "N_G*A_D*C_D*1e-6",
  A_M: () => "2*500*(L+W) + pi*500^2",
  N_M: () => "N_G*A_M*1e-6",
  A_L: (o) => ("rho" in o && o.rho > 400 ? "0.6*sqrt(rho)*L_L" : "40*L_L"),
  N_L: () => "N_G*A_L*C_I*C_E*C_T*1e-6",
  A_I: () => "4000*L_L",
  N_I: () => "N_G*A_I*C_I*C_E*C_T*1e-6",
  presenca: (o) => (o.n_t === 0 ? "0" : "(n_z/n_t)*(t_z/8760)"),
  L_A: (o) => `r_t*L_T*${MOLDES.presenca(o)}*r_s`,
  L_B: (o) => `r_p*r_f*h_z*L_F*${MOLDES.presenca(o)}*r_s`,
  L_sis: (o) => `L_O*${MOLDES.presenca(o)}*r_s`,
  L_B3: () => "min(1.0, r_p*r_f*L_F*(c_z/c_t))",
  L4_A: (o) => ("c_a" in o ? "r_t*L_T*(c_a/c_t)" : "r_t*L_T"),
  L4_B: (o) => ("c_a" in o ? "r_p*r_f*L_F*(c_a+c_b+c_c+c_s)/c_t" : "r_p*r_f*L_F"),
  L4_sis: (o) => ("c_s" in o ? "L_O*(c_s/c_t)" : "L_O"),
  P_A: () => "P_TA*P_B",
  P_MS: () => "(K_S1*K_S2*K_S3*K_S4)^2",
  P_C: () => "P_SPD*C_LD",
  P_U: () => "P_TU*P_EB*P_LD*C_LD",
  P_V: () => "P_EB*P_LD*C_LD",
  R_A: () => "N*P*L",
  R_B: () => "N*P*L",
  R_C: () => "N*P*L",
  R_M: () => "N*P*L",
  R_B3: () => "N*P*L",
};

function renderizarOperacao(op) {
  if (!op) return null;
  const temOperandos = op.operandos && Object.keys(op.operandos).length > 0;
  if (MOLDES[op.simbolo] && temOperandos) {
    const forma = MOLDES[op.simbolo](op.operandos);
    return {
      simbolo: op.simbolo, eq: op.eq,
      forma_simbolica: `${op.simbolo} = ${forma}`,
      substituicao: substituir(forma, op.operandos),
      resultado: fmt(op.resultado), origem: op.origem || "",
    };
  }
  return { simbolo: op.simbolo, eq: op.eq, forma_simbolica: null, substituicao: null, resultado: fmt(op.resultado), origem: op.origem || "" };
}

// --------------------------------------------------------------------------
// documento.py — blocos simples (view-models do relatório)
// --------------------------------------------------------------------------
const titulo = (nivel, texto) => ({ t: "titulo", nivel, texto });
const paragrafo = (texto) => ({ t: "paragrafo", texto });
const equacaoBloco = (op) => (op ? { t: "equacao", ...renderizarOperacao(op) } : null);
const tabela = (cabecalho, linhas) => ({ t: "tabela", cabecalho, linhas });
const nota = (nivel, texto) => ({ t: "nota", nivel, texto });
const lista = (itens, ordenada = false) => ({ t: "lista", itens, ordenada });
const glossarioBloco = (itens) => ({ t: "glossario", itens });
const quebra = () => ({ t: "quebra" });
function eqs(...ops) { return ops.filter(Boolean).map(equacaoBloco); }

// --------------------------------------------------------------------------
// glossario.py — dados estáticos + coleta automática de símbolos/equações usados
// --------------------------------------------------------------------------
const GLOSSARIO = {
  N_G: ["densidade de descargas atmosféricas", "1/km²/ano"],
  A_D: ["área de exposição equivalente da estrutura", "m²"],
  A_M: ["área de exposição para descargas perto da estrutura", "m²"],
  A_L: ["área de captação da linha", "m²"],
  A_I: ["área de exposição para descargas perto da linha", "m²"],
  C_D: ["fator de localização da estrutura", "-"],
  C_I: ["fator de instalação da linha", "-"],
  C_E: ["fator ambiental da linha", "-"],
  C_T: ["fator de transformador (AT/BT) da linha", "-"],
  C_LD: ["fator de blindagem/aterramento (dano)", "-"],
  C_LI: ["fator de blindagem/aterramento (indução)", "-"],
  N_D: ["descargas diretas na estrutura", "1/ano"],
  N_M: ["descargas perto da estrutura", "1/ano"],
  N_DJ: ["descargas na estrutura adjacente", "1/ano"],
  N_L: ["descargas na linha", "1/ano"],
  N_I: ["descargas perto da linha", "1/ano"],
  P_TA: ["prob. de choque por toque/passo (estrutura)", "-"],
  P_B: ["prob. de dano físico (nível de SPDA)", "-"],
  P_SPD: ["prob. ligada ao DPS coordenado do sistema", "-"],
  P_EB: ["prob. ligada à ligação equipotencial na entrada", "-"],
  P_TU: ["prob. de choque por toque na entrada da linha", "-"],
  P_LD: ["prob. de falha por surto na linha (dano)", "-"],
  P_LI: ["prob. de falha por surto induzido na linha", "-"],
  K_S1: ["fator de blindagem espacial (interface ZPR0/1)", "-"],
  K_S2: ["fator de blindagem interna", "-"],
  K_S3: ["fator das características da fiação interna", "-"],
  K_S4: ["fator da tensão suportável de impulso (1/U_W)", "-"],
  P_A: ["prob. de choque, descarga na estrutura", "-"],
  P_C: ["prob. de falha de sistemas, descarga na estrutura", "-"],
  P_M: ["prob. de falha de sistemas, descarga perto", "-"],
  P_U: ["prob. de choque por linha", "-"],
  P_V: ["prob. de dano físico por linha", "-"],
  P_W: ["prob. de falha de sistemas por surto na linha", "-"],
  P_Z: ["prob. de falha de sistemas por surto induzido", "-"],
  P_MS: ["prob. de falha de sistemas internos (campo magnético)", "-"],
  r_t: ["fator do tipo de superfície (redução de choque)", "-"],
  r_p: ["fator das providências contra incêndio", "-"],
  r_f: ["fator do risco de incêndio", "-"],
  r_s: ["fator do tipo de construção", "-"],
  L_T: ["perda relativa por choque (valor típico)", "-"],
  L_F: ["perda relativa por dano físico (valor típico)", "-"],
  L_O: ["perda relativa por falha de sistemas (valor típico)", "-"],
  presenca: ["fator de presença de pessoas na zona", "-"],
  L_A: ["perda por choque (descarga na estrutura)", "-"],
  L_B: ["perda por dano físico (descarga na estrutura)", "-"],
  L_sis: ["perda por falha de sistemas internos", "-"],
  L_B3: ["perda de patrimônio (L3)", "-"],
  L4_A: ["perda econômica por choque (L4)", "-"],
  L4_B: ["perda econômica por dano físico (L4)", "-"],
  L4_sis: ["perda econômica por falha de sistemas (L4)", "-"],
  R_A: ["componente de risco: choque (estrutura)", "1/ano"],
  R_B: ["componente de risco: dano físico (estrutura)", "1/ano"],
  R_C: ["componente de risco: falha de sistemas (estrutura)", "1/ano"],
  R_M: ["componente de risco: falha de sistemas (perto)", "1/ano"],
  R_U: ["componente de risco: choque (linha)", "1/ano"],
  R_V: ["componente de risco: dano físico (linha)", "1/ano"],
  R_W: ["componente de risco: falha de sistemas (linha)", "1/ano"],
  R_Z: ["componente de risco: falha de sistemas (indução)", "1/ano"],
  R_B3: ["componente de R3 (patrimônio)", "1/ano"],
  R_V3: ["componente de R3 por linha", "1/ano"],
  R4_total: ["risco econômico da zona (R4)", "1/ano"],
  F_zona: ["frequência de danos da zona", "1/ano"],
  R1: ["risco de vida humana", "1/ano"],
  R3: ["risco de perda de patrimônio cultural", "1/ano"],
  R4: ["risco de perda econômica", "1/ano"],
  F: ["frequência de danos da estrutura", "1/ano"],
};
const EQUACOES = {
  "A.1": ["Área de exposição A_D", "Anexo A"],
  "A.1/A.2": ["Área de exposição A_D (forma complexa)", "Anexo A"],
  "A.3": ["Número de eventos N_D", "Anexo A"],
  "A.4": ["Número de eventos N_DJ (adjacente)", "Anexo A"],
  "A.5": ["Número de eventos N_M", "Anexo A"],
  "A.6": ["Área A_M", "Anexo A"],
  "A.7": ["Número de eventos N_L", "Anexo A"],
  "A.8": ["Área da linha A_L", "Anexo A"],
  "A.9": ["Número de eventos N_I", "Anexo A"],
  "A.10": ["Área perto da linha A_I", "Anexo A"],
  "B.1": ["Probabilidade P_A", "Anexo B"],
  "B.2": ["Probabilidade P_C", "Anexo B"],
  "B.4": ["Probabilidade P_MS", "Anexo B"],
  "B.6": ["Probabilidade P_TU", "Anexo B"],
  "B.7": ["Probabilidade P_EB", "Anexo B"],
  "B.8": ["Probabilidade P_U / P_LD", "Anexo B"],
  "B.9": ["Probabilidade P_V / P_LI", "Anexo B"],
  "B.10": ["Probabilidade P_W", "Anexo B"],
  "B.11": ["Probabilidade P_Z", "Anexo B"],
  "C.1": ["Perda L_A", "Anexo C"],
  "C.3": ["Perda L_B", "Anexo C"],
  "C.4": ["Perda L_sis", "Anexo C"],
  "C.6": ["Fator de presença", "Anexo C"],
  "C.7": ["Perda de patrimônio L_B3", "Anexo C"],
  L3: ["Perda de patrimônio (L3)", "Seção 7"],
  "13.3": ["Perdas econômicas (L4)", "Seção 13"],
  "D.1": ["Perda econômica por choque (L4_A)", "Anexo D"],
  "D.3": ["Perda econômica por dano físico (L4_B)", "Anexo D"],
  "D.4": ["Perda econômica por sistemas (L4_sis)", "Anexo D"],
  "eq.3": ["Componente de risco R = N·P·L", "Seção 8"],
  "eq.4": ["Componente de risco R = N·P·L", "Seção 8"],
  "eq.5": ["Componente de risco R = N·P·L", "Seção 8"],
  "eq.6": ["Componente de risco R = N·P·L", "Seção 8"],
  "eq.8": ["Componente de linha R_U", "Seção 8"],
  "eq.9": ["Componente de linha R_V", "Seção 8"],
  "eq.10": ["Componente de linha R_W", "Seção 8"],
  "eq.11": ["Componente R_Z", "Seção 8"],
  "eq.12": ["Combinação de sistemas (P_C)", "Seção 8"],
  "eq.13": ["Combinação de sistemas (P_M)", "Seção 8"],
  "Secao 8": ["Riscos totais R1/R3/R4", "Seção 8"],
  "Secao 7": ["Frequência de danos F", "Seção 7 (Tabela 7)"],
};
const TABELAS = {
  "Tabela A.1": "Tabela A.1 (C_D, localização)",
  "Tabela A.2": "Tabela A.2 (C_I, instalação)",
  "Tabela A.3": "Tabela A.3 (C_T, transformador)",
  "Tabela A.4": "Tabela A.4 (C_E, ambiente)",
  "Tabela B.1": "Tabela B.1 (P_TA)",
  "Tabela B.2": "Tabela B.2 (P_B)",
  "Tabela B.3": "Tabela B.3 (P_SPD)",
  "Tabela B.4": "Tabela B.4 (C_LD/C_LI)",
  "Tabela B.5": "Tabela B.5 (K_S3)",
  "Tabela B.6": "Tabela B.6 (P_TU)",
  "Tabela B.7": "Tabela B.7 (P_EB)",
  "Tabela B.8": "Tabela B.8 (P_LD)",
  "Tabela B.9": "Tabela B.9 (P_LI)",
  "Tabela C.7": "Tabela C.7 (r_s)",
  "Tabela C.3": "Tabela C.3 (r_t)",
  "Tabela C.4": "Tabela C.4 (r_p)",
  "Tabela C.5": "Tabela C.5 (r_f)",
};

function coletarOperacoes(raiz) {
  const achados = [];
  const vistos = new Set();
  function visita(obj) {
    if (obj === null || obj === undefined || typeof obj !== "object") return;
    if (vistos.has(obj)) return;
    vistos.add(obj);
    if (typeof obj.simbolo === "string" && typeof obj.eq === "string" && typeof obj.resultado === "number") {
      achados.push(obj);
      return;
    }
    if (Array.isArray(obj)) { obj.forEach(visita); return; }
    for (const k in obj) visita(obj[k]);
  }
  visita(raiz);
  return achados;
}
function simbolosUsados(mem) {
  const presentes = new Set(coletarOperacoes(mem).map((o) => o.simbolo));
  return [...presentes].sort().filter((s) => GLOSSARIO[s]).map((s) => [s, GLOSSARIO[s][0], GLOSSARIO[s][1]]);
}
function indiceEquacoes(mem) {
  const eqsSet = new Set(coletarOperacoes(mem).map((o) => o.eq).filter((eq) => !eq.startsWith("Tabela")));
  return [...eqsSet].sort().map((eq) => { const [ti, ref] = EQUACOES[eq] || [eq, ""]; return [eq, ti, ref]; });
}
function indiceTabelas(mem) {
  const vistos = {};
  for (const op of coletarOperacoes(mem)) {
    if (op.eq.startsWith("Tabela") && !(op.eq in vistos)) vistos[op.eq] = op.simbolo;
  }
  return Object.keys(vistos).sort().map((eq) => [eq, vistos[eq], TABELAS[eq] || eq]);
}

// --------------------------------------------------------------------------
// notas.py — notas técnicas automáticas
// --------------------------------------------------------------------------
function notasIdentificacao(mem) {
  const notas = [];
  if (!mem.cidade) notas.push(nota("aviso", "Cidade não informada: é a base do N_G (tabela de municípios da norma) e deve constar no laudo."));
  const ident = mem.identificacao;
  if (!ident) {
    notas.push(nota("aviso", "Bloco de identificação ausente: laudo não assinável sem responsável técnico, ART e registro CREA."));
    return notas;
  }
  const campos = [["responsavel", "responsável técnico"], ["art", "número da ART"], ["registro", "registro CREA"], ["data", "data"]];
  const faltando = campos.filter(([attr]) => !ident[attr]).map(([, label]) => label);
  if (faltando.length) notas.push(nota("aviso", `Identificação incompleta para assinatura: ${faltando.join(", ")}.`));
  return notas;
}
function notasRiscos(mem) {
  const notas = [];
  let algumExcede = false;
  for (const me of mem.estruturas) {
    const checagens = [
      ["R1", me.R1.resultado, mem.rt.R1, "critico", "risco de perda de vida humana"],
      ["R3", me.R3.resultado, mem.rt.R3, "aviso", "risco de perda de patrimônio cultural"],
      ["R4", me.R4.resultado, mem.rt.R4, "aviso", "risco de perda econômica"],
      ["F", me.F.resultado, me.ft, "aviso", "frequência de danos tolerável"],
    ];
    for (const [simbolo, valor, limite, nivel, desc] of checagens) {
      if (valor > limite) {
        algumExcede = true;
        notas.push(nota(nivel, `${me.nome}: ${simbolo} = ${fmt(valor)} excede o limite ${fmt(limite)} (${desc}). Requer medidas de proteção.`));
      }
    }
  }
  if (!algumExcede) notas.push(nota("info", "Todos os riscos calculados estão dentro dos limites da norma."));
  return notas;
}
function notasR4Metodo(mem) {
  if (!mem.estruturas.some((me) => me.R4.resultado > 0)) return [];
  const rtR4 = fmt(mem.rt.R4 || 0);
  if (mem.r4_representativo) {
    return [nota("info", `R4 avaliado com R_T representativo (Tabela 4 = ${rtR4}); as razões c/c_t foram adotadas como 1 (nota das Eqs D.1-D.4).`)];
  }
  return [nota("info", `R4 avaliado pelo método detalhado do Anexo D (razões c/c_t). O gate R4 vs ${rtR4} é indicativo; a justificativa econômica formal é por custo-benefício (C_L vs C_RL + C_PM).`)];
}
function notasHipoteses(mem) {
  const notas = [];
  for (const me of mem.estruturas) {
    for (const mz of me.zonas) {
      for (const ms of mz.sistemas) {
        const onde = `${me.nome}/${mz.nome}/${ms.nome}`;
        if (ms.U_W === null || ms.U_W === undefined) notas.push(nota("info", `${onde}: U_W desconhecido; adotado P_M = 1 (pior caso).`));
        if (!ms.dps) notas.push(nota("info", `${onde}: sem DPS coordenado; adotado P_SPD = 1.`));
      }
    }
  }
  return notas;
}
function gerarNotas(mem) {
  return [...notasIdentificacao(mem), ...notasRiscos(mem), ...notasR4Metodo(mem), ...notasHipoteses(mem)];
}

// --------------------------------------------------------------------------
// diagnostico.py — diagnóstico narrativo por estrutura
// --------------------------------------------------------------------------
const INTERVENCAO = {
  R_A: "proteção contra tensão de toque e passo (P_TA)",
  R_U: "DPS de equipotencialização na entrada e proteção de toque (P_U)",
  R_B: "SPDA e medidas contra incêndio (P_B, r_p)",
  R_V: "SPDA, DPS de entrada e medidas contra incêndio (P_V)",
  R_C: "DPS coordenado e blindagem dos sistemas internos (P_C)",
  R_M: "blindagem espacial e DPS dos sistemas internos (P_M)",
  R_W: "DPS coordenado na linha e blindagem (P_W)",
  R_Z: "blindagem interna e DPS dos sistemas (P_Z)",
};
function gerarDiagnostico(mem) {
  const blocos = [titulo(2, "Diagnóstico por estrutura")];
  for (const me of mem.estruturas) {
    const veredito = me.R1.resultado > mem.rt.R1 ? "INADEQUADA" : "ADEQUADA";
    blocos.push(titulo(3, me.nome));
    blocos.push(paragrafo(`A estrutura **${me.nome}** apresenta R1 = ${fmt(me.R1.resultado)} contra o limite RT = ${fmt(mem.rt.R1)}, sendo considerada **${veredito}** quanto ao risco de vida (R1).`));
    if (me.dominantes && me.dominantes.length) {
      const principal = me.dominantes[0][0];
      const onde = INTERVENCAO[principal] || "as medidas de proteção aplicáveis";
      const itens = me.dominantes.map(([nome, val]) => `${nome} = ${fmt(val)}`).join("; ");
      blocos.push(paragrafo(`Componentes dominantes de R1: ${itens}. Para reduzir R1, recomenda-se atuar prioritariamente sobre ${onde}.`));
    }
  }
  return blocos;
}

// --------------------------------------------------------------------------
// memorial.py — monta o documento completo
// --------------------------------------------------------------------------
function blocoIdentificacao(mem) {
  const ident = mem.identificacao;
  const blocos = [titulo(1, (ident && ident.titulo) || "Análise de Risco — Descargas Atmosféricas")];
  const linhas = ident ? [
    ["Cliente", campo(ident.cliente)],
    ["Endereço", campo(ident.endereco)],
    ["Responsável técnico", campo(ident.responsavel)],
    ["ART", campo(ident.art)],
    ["Registro CREA", campo(ident.registro)],
    ["Norma", `${campo(ident.norma)} (${campo(ident.revisao)})`],
    ["Data", campo(ident.data)],
    ["Observações", campo(ident.observacoes)],
  ] : [["Identificação", "— (não informada)"]];
  blocos.push(tabela(["Campo", "Valor"], linhas));
  blocos.push(paragrafo(`Projeto: **${mem.projeto}** — Cidade: **${campo(mem.cidade)}**.`));
  return blocos;
}
function blocoSumario(mem) {
  const status = (v, l) => (v > l ? "EXCEDE" : "OK");
  const cab = ["Estrutura", "R1", "RT(R1)", "R3", "RT(R3)", "R4", "RT(R4)", "F", "FT"];
  const linhas = mem.estruturas.map((me) => [
    me.nome,
    `${fmt(me.R1.resultado)} (${status(me.R1.resultado, mem.rt.R1)})`, fmt(mem.rt.R1),
    `${fmt(me.R3.resultado)} (${status(me.R3.resultado, mem.rt.R3)})`, fmt(mem.rt.R3),
    `${fmt(me.R4.resultado)} (${status(me.R4.resultado, mem.rt.R4)})`, fmt(mem.rt.R4),
    `${fmt(me.F.resultado)} (${status(me.F.resultado, me.ft)})`, fmt(me.ft),
  ]);
  return [titulo(2, "Sumário executivo"), tabela(cab, linhas)];
}
function blocoLinha(ml) {
  const blocos = [titulo(4, `Linha: ${ml.nome}`)];
  if (ml.nivel_eb) blocos.push(paragrafo(`DPS de entrada (P_EB): ${ml.nivel_eb}.`));
  blocos.push(paragrafo(`U_W usado nas colunas P_LD/P_LI: ${campo(ml.uw_min)}.`));
  blocos.push(...eqs(ml.C_LD, ml.C_LI, ml.P_LD, ml.P_LI, ml.P_TU, ml.P_EB, ml.P_U, ml.P_V, ml.P_W, ml.P_Z));
  for (const t of ml.trechos) {
    blocos.push(titulo(4, `  ${t.nome} (L_L=${fmt(t.L_L)} m)`));
    const ops = [t.C_I, t.C_E, t.C_T, t.A_L, t.N_L, t.A_I, t.N_I];
    if (t.N_DJ) ops.push(t.N_DJ);
    blocos.push(...eqs(...ops));
  }
  return blocos;
}
function blocoZona(mz) {
  const blocos = [titulo(3, `Zona: ${mz.nome}`)];
  blocos.push(paragrafo(`Pessoas n_z=${mz.n_z}, presença t_z=${fmt(mz.t_z)} h/ano.`));
  blocos.push(titulo(4, "Coeficientes"));
  for (const nome of ["r_t", "r_p", "r_f", "r_s", "P_TA", "P_B"]) {
    if (mz.coefs[nome]) blocos.push(equacaoBloco(mz.coefs[nome]));
  }
  blocos.push(titulo(4, "Presença e perdas"));
  blocos.push(...eqs(mz.presenca, mz.L_A, mz.L_B, mz.L_sis));
  blocos.push(...eqs(mz.L_B3, mz.L4_A, mz.L4_B, mz.L4_sis));
  if (mz.sistemas.length) {
    blocos.push(titulo(4, "Sistemas internos"));
    for (const ms of mz.sistemas) {
      blocos.push(paragrafo(`**${ms.nome}** — U_W=${campo(ms.U_W)}, DPS=${campo(ms.dps)}.`));
      blocos.push(...eqs(ms.K_S1, ms.K_S2, ms.K_S3, ms.K_S4, ms.P_SPD, ms.P_MS_i, ms.P_C_i));
    }
  }
  blocos.push(titulo(4, "Probabilidades agregadas"));
  blocos.push(...eqs(mz.P_A, mz.P_C, mz.P_M));
  if (mz.linhas.length) {
    blocos.push(titulo(4, "Linhas e eventos"));
    for (const ml of mz.linhas) blocos.push(...blocoLinha(ml));
  }
  blocos.push(titulo(4, "Componentes de risco da zona"));
  blocos.push(...eqs(mz.R_A, mz.R_B, mz.R_C, mz.R_M, mz.R_U, mz.R_V, mz.R_W, mz.R_Z, mz.R_B3, mz.R_V3, mz.R4_total, mz.F_zona));
  return blocos;
}
function blocoEstrutura(me) {
  const blocos = [quebra(), titulo(2, `Estrutura: ${me.nome}`)];
  blocos.push(titulo(3, "Dados de entrada"));
  blocos.push(tabela(["Parâmetro", "Valor"], Object.entries(me.entradas).map(([k, v]) => [k, campo(v)])));
  blocos.push(titulo(3, "Número de eventos"));
  blocos.push(...eqs(me.A_D, me.C_D, me.N_D, me.A_M, me.N_M));
  for (const mz of me.zonas) blocos.push(...blocoZona(mz));
  blocos.push(titulo(3, "Agregação de riscos"));
  blocos.push(...eqs(me.R1, me.R3, me.R4, me.F));
  if (me.dominantes && me.dominantes.length) {
    blocos.push(paragrafo("**Componentes dominantes de R1:**"));
    blocos.push(lista(me.dominantes.map(([nome, val]) => `${nome} = ${fmt(val)}`), true));
  }
  return blocos;
}
function blocoRecomendacoes(estudo) {
  if (!estudo || !estudo.estruturas || !estudo.estruturas.length) return [];
  const blocos = [quebra(), titulo(2, "Recomendações (Estudo de Solução)")];
  for (const e of estudo.estruturas) {
    blocos.push(titulo(3, e.nome));
    const veredito = e.atingiu_rt && e.atingiu_ft
      ? "R1 ≤ RT e F ≤ FT atingidos com as medidas abaixo."
      : "limites não atingidos; reporta-se o menor R1/F alcançável.";
    blocos.push(paragrafo(
      `R1 inicial = ${fmt(e.R1_inicial)} → final = ${fmt(e.R1_final)} (RT = ${fmt(e.rt_R1)}); ` +
      `F inicial = ${fmt(e.F_inicial)} → final = ${fmt(e.F_final)} (FT = ${fmt(e.ft)}). ${veredito}`
    ));
    const linhas = e.passos.map((p, i) => [String(i + 1), p.medida, p.parametro, `${p.de} → ${p.para}`, fmt(p.R_projetado), fmt(p.F_projetado)]);
    if (linhas.length) blocos.push(tabela(["#", "Medida", "Parâmetro", "De → Para", "R1 projetado", "F projetado"], linhas));
  }
  return blocos;
}
function blocoPropostas(propostas) {
  if (!propostas || !propostas.length) return [];
  const blocos = [
    quebra(), titulo(2, "Propostas registradas (instalação existente — ainda não aplicadas)"),
    paragrafo("As combinações abaixo foram avaliadas e salvas pelo engenheiro como proposta, sem alterar os dados atuais (as-built) da estrutura. Refletem o impacto estimado caso venham a ser implementadas."),
  ];
  for (const p of propostas) {
    blocos.push(titulo(3, p.nome));
    blocos.push(paragrafo(
      `Situação atual: R1 = ${fmt(p.R1_atual)} (limite ${fmt(p.rt_R1)}), F = ${fmt(p.F_atual)} (limite ${fmt(p.ft)}). ` +
      `Com a proposta: R1 = ${fmt(p.R1_proposto)}, F = ${fmt(p.F_proposto)}, R3 = ${fmt(p.R3_proposto)}, R4 = ${fmt(p.R4_proposto)}. ` +
      (p.atinge_rt && p.atinge_ft ? "Atende R1 e F." : "Ainda não atende R1 e/ou F.")
    ));
    blocos.push(lista(p.mudancas.map((m) => `${m.descricao}: ${m.de} → ${m.para}`), true));
  }
  return blocos;
}

function blocoGlossarioIndices(mem) {
  return [
    quebra(), titulo(2, "Glossário e índices"),
    titulo(3, "Glossário de símbolos"), glossarioBloco(simbolosUsados(mem)),
    titulo(3, "Índice de equações"), tabela(["Eq.", "Título", "Referência"], indiceEquacoes(mem)),
    titulo(3, "Índice de tabelas"), tabela(["Tabela", "Coeficiente", "Referência"], indiceTabelas(mem)),
  ];
}

export function gerarDocumento(memoria, estudo, propostas) {
  const blocos = [];
  blocos.push(...blocoIdentificacao(memoria));
  blocos.push(...blocoSumario(memoria));
  const notas = gerarNotas(memoria);
  if (notas.length) blocos.push(titulo(2, "Notas técnicas"), ...notas);
  blocos.push(...gerarDiagnostico(memoria));
  for (const me of memoria.estruturas) blocos.push(...blocoEstrutura(me));
  blocos.push(...blocoRecomendacoes(estudo));
  blocos.push(...blocoPropostas(propostas));
  blocos.push(...blocoGlossarioIndices(memoria));
  return blocos;
}

// --------------------------------------------------------------------------
// html.py — serialização HTML autônoma e imprimível
// --------------------------------------------------------------------------
const PREFIXO_NOTA = { info: "NOTA", aviso: "AVISO", critico: "CRÍTICO" };

function esc(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
function inline(texto) {
  let s = esc(texto);
  s = s.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  s = s.replace(/`(.+?)`/g, "<code>$1</code>");
  return s;
}
function htmlEquacao(e) {
  if (e.substituicao !== null && e.forma_simbolica !== null) {
    const corpo = `<span class="rotulo">${esc(e.simbolo)} (eq. ${esc(e.eq)})</span>\n${esc(e.forma_simbolica)}\n    = ${esc(e.substituicao)}\n    = ${esc(e.resultado)}`;
    return `<div class="equacao">${corpo}</div>`;
  }
  let sufixo = esc(e.eq);
  if (e.origem) sufixo += "; " + esc(e.origem);
  return `<p><span class="rotulo">${esc(e.simbolo)}</span> = ${esc(e.resultado)} (${sufixo})</p>`;
}
function htmlTabela(t) {
  const cab = t.cabecalho.map((c) => `<th>${esc(c)}</th>`).join("");
  const linhas = t.linhas.map((lin) => "<tr>" + lin.map((v) => `<td>${esc(v)}</td>`).join("") + "</tr>").join("");
  return `<table><thead><tr>${cab}</tr></thead><tbody>${linhas}</tbody></table>`;
}
function htmlBloco(b) {
  switch (b.t) {
    case "titulo": { const n = Math.min(Math.max(b.nivel, 1), 4); return `<h${n}>${esc(b.texto)}</h${n}>`; }
    case "paragrafo": return `<p>${inline(b.texto)}</p>`;
    case "equacao": return htmlEquacao(b);
    case "tabela": return htmlTabela(b);
    case "nota": return `<div class="nota ${esc(b.nivel)}"><strong>${PREFIXO_NOTA[b.nivel]}:</strong> ${esc(b.texto)}</div>`;
    case "lista": { const tag = b.ordenada ? "ol" : "ul"; return `<${tag}>${b.itens.map((i) => `<li>${esc(i)}</li>`).join("")}</${tag}>`; }
    case "glossario": {
      const linhas = b.itens.map(([s, n, u]) => `<tr><td>${esc(s)}</td><td>${esc(n)}</td><td>${esc(u)}</td></tr>`).join("");
      return `<table><thead><tr><th>Símbolo</th><th>Descrição</th><th>Unidade</th></tr></thead><tbody>${linhas}</tbody></table>`;
    }
    case "quebra": return '<div class="quebra"></div>';
    default: return "";
  }
}

const CSS = `
:root { --tinta: #1a1a1a; --borda: #999; --aviso: #b35900; --critico: #a40000; }
* { box-sizing: border-box; }
body { font-family: Georgia, 'Times New Roman', serif; color: var(--tinta);
       max-width: 860px; margin: 0 auto; padding: 40px 24px 80px; line-height: 1.55; }
h1, h2, h3, h4 { font-family: Arial, Helvetica, sans-serif; line-height: 1.25; }
h1 { font-size: 1.7rem; border-bottom: 2px solid var(--tinta); padding-bottom: 6px; }
h2 { font-size: 1.35rem; margin-top: 1.8em; }
h3 { font-size: 1.12rem; margin-top: 1.4em; }
h4 { font-size: 0.98rem; color: #333; }
p { margin: 0.6em 0; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 0.92rem; }
th, td { border: 1px solid var(--borda); padding: 5px 9px; text-align: left; vertical-align: top; }
th { background: #eef0f3; }
code { background: #f0f0f0; padding: 1px 5px; border-radius: 3px; font-size: 0.9em; }
.equacao { font-family: 'Courier New', monospace; background: #f7f7f7; font-size: 0.9rem;
           border-left: 3px solid var(--borda); padding: 8px 12px; margin: 10px 0;
           white-space: pre-wrap; overflow-x: auto; }
.equacao .rotulo { font-family: Arial, sans-serif; font-weight: bold; color: #2354a6; }
.nota { border: 1px solid var(--borda); border-left-width: 5px; padding: 7px 11px; margin: 10px 0; font-size: 0.94rem; }
.nota.aviso { border-left-color: var(--aviso); }
.nota.critico { border-left-color: var(--critico); }
.nota.info { border-left-color: #2354a6; }
.toolbar { position: sticky; top: 0; z-index: 10; display: flex; justify-content: flex-end;
           gap: 10px; padding: 10px 24px; background: #f3f5f8; border-bottom: 1px solid #d7dee8; }
.toolbar button { font: 600 13px Arial, sans-serif; padding: 9px 16px; border-radius: 7px;
                  border: 1px solid #2354a6; background: #2354a6; color: #fff; cursor: pointer; }
@media print {
  .toolbar { display: none; }
  body { margin: 0; max-width: none; padding: 0 6mm; font-size: 11pt; }
  h2, h3, h4 { page-break-after: avoid; }
  .equacao, table, .nota { page-break-inside: avoid; }
  .quebra { page-break-before: always; }
  @page { margin: 16mm 14mm; }
}
`;

export function paraHtml(blocos, tituloDoc) {
  const corpo = blocos.map(htmlBloco).join("\n");
  return (
    "<!DOCTYPE html>\n" +
    '<html lang="pt-br">\n<head>\n<meta charset="utf-8">\n' +
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n' +
    `<title>${esc(tituloDoc)}</title>\n<style>${CSS}</style>\n</head>\n<body>\n` +
    '<div class="toolbar"><button onclick="window.print()">Imprimir / Salvar como PDF</button></div>\n' +
    `${corpo}\n</body>\n</html>\n`
  );
}

export function gerarRelatorioHtml(memoria, estudo, propostas) {
  const ident = memoria.identificacao;
  const tituloDoc = (ident && ident.titulo) || `Análise de Risco — ${memoria.projeto}`;
  return paraHtml(gerarDocumento(memoria, estudo, propostas), tituloDoc);
}
