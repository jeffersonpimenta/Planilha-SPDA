// spda-calc.js — motor de cálculo NBR 5419-2:2026, porte fiel do pacote Python
// spda/calc + spda/app.py + spda/solucao. Funções puras sobre objetos JSON simples
// (mesmos nomes de campo do model pydantic original).
import { rotulo } from "./spda-model.js";

const UW_CONSERVADOR_KV = 1.0;

// ---------------------------------------------------------------------------
// Tabelas de referência (ABNT NBR 5419-2:2026)
// ---------------------------------------------------------------------------
export const REF = {
  C_D: { cercada_mais_altos: 0.25, cercada_mesma_altura: 0.5, isolada: 1.0, topo_colina: 2.0 },
  C_I: { aerea: 1.0, enterrada: 0.5, enterrada_malha: 0.01 },
  C_T: { bt_sinal: 1.0, at_trafo: 0.2 },
  C_E: { rural: 1.0, suburbano: 0.5, urbano: 0.1, urbano_alto: 0.01 },
  P_TA: { nenhuma: 1.0, avisos: 0.1, isolacao: 0.01, malha_equipotencial: 0.01, descida_natural: 0.001, restricoes_fisicas: 0.0 },
  P_B: { nenhum: 1.0, IV: 0.2, III: 0.1, II: 0.05, I: 0.02, I_descida_natural: 0.01, captacao_descida_natural: 0.001 },
  P_SPD: { IV: 0.05, III: 0.05, II: 0.02, I: 0.01, melhor_I: 0.005 },
  C_LD: {
    aerea_nao_blindada: 1.0, subterranea_nao_blindada: 1.0, energia_neutro_multiaterrado: 1.0,
    subterranea_blindada_nao_interligada: 1.0, aerea_blindada_nao_interligada: 1.0,
    blindada_interligada: 1.0, eletroduto_metalico: 0.0, fibra_optica: 0.0, interface_isolante: 0.0,
  },
  C_LI: {
    aerea_nao_blindada: 1.0, subterranea_nao_blindada: 1.0, energia_neutro_multiaterrado: 0.2,
    subterranea_blindada_nao_interligada: 0.3, aerea_blindada_nao_interligada: 0.1,
    blindada_interligada: 0.0, eletroduto_metalico: 0.0, fibra_optica: 0.0, interface_isolante: 0.0,
  },
  P_EB: { IV: 0.05, III: 0.05, II: 0.02, I: 0.01, melhor_I: 0.005 },
  P_TU: { nenhuma: 1.0, avisos: 0.1, isolacao: 0.01, restricoes_fisicas: 0.0 },
  K_S3: { laco_grande: 1.0, laco_medio_25: 0.5, laco_medio_10: 0.2, laco_pequeno: 0.01, blindado_conduto: 0.0001 },
  COLUNAS_UW: [1.0, 1.5, 2.5, 4.0, 6.0],
  P_LD: {
    nao_blindada: { 1.0: 1.0, 1.5: 1.0, 2.5: 1.0, 4.0: 1.0, 6.0: 1.0 },
    rs_5_20: { 1.0: 1.0, 1.5: 1.0, 2.5: 0.95, 4.0: 0.9, 6.0: 0.8 },
    rs_1_5: { 1.0: 0.9, 1.5: 0.8, 2.5: 0.6, 4.0: 0.3, 6.0: 0.1 },
    rs_ate_1: { 1.0: 0.6, 1.5: 0.4, 2.5: 0.2, 4.0: 0.04, 6.0: 0.02 },
  },
  P_LI: {
    energia: { 1.0: 1.0, 1.5: 0.6, 2.5: 0.3, 4.0: 0.16, 6.0: 0.1 },
    sinal: { 1.0: 1.0, 1.5: 0.5, 2.5: 0.2, 4.0: 0.08, 6.0: 0.04 },
  },
  R_T: { terra_concreto: 1e-2, marmore_ceramica: 1e-3, brita_carpete: 1e-4, asfalto_madeira: 1e-5 },
  R_P: { nenhuma: 1.0, extintor: 0.5, fixo_automatico: 0.2 },
  R_F: { alto: 0.1, normal: 0.01, baixo: 0.001, sem_risco: 0.0 },
  R_F_EXPLOSAO: { zona_0_20: 1.0, zona_1_21: 0.1, zona_2_22: 0.001 },
  R_S: { simples: 2.0, robusta: 1.0 },
  H_Z: { sem_perigo: 1.0, panico_baixo: 2.0, panico_medio: 5.0, evacuacao_dificil: 5.0, panico_alto: 10.0 },
  L_T: 1e-2,
  L_O_PADRAO: 1e-3,
  L_O_EXPLOSAO: 1e-1,
  L_O_HOSPITAL_CRITICO: 1e-2,
  L_F: { hospital: 0.1, hotel: 0.1, escola: 0.1, edificio_civico: 0.1, entretenimento: 0.05, igreja: 0.05, museu: 0.05, industrial: 0.02, comercial: 0.02, outros: 0.01 },
  L_F_EXPLOSAO: 0.1,
  L_F_L3: 0.1,
  L_F_L4: { hospital: 0.5, industrial: 0.5, museu: 0.5, hotel: 0.2, escola: 0.2, edificio_civico: 0.2, igreja: 0.2, entretenimento: 0.2, comercial: 0.2, outros: 0.1 },
  L_F_L4_EXPLOSAO: 1.0,
  L_O_L4: { hospital: 0.01, industrial: 0.01, hotel: 0.01, comercial: 0.01, edificio_civico: 0.01, museu: 0.001, escola: 0.001, igreja: 0.001, entretenimento: 0.001, outros: 0.0001 },
  L_O_L4_EXPLOSAO: 0.1,
  RT: { R1: 1e-5, R3: 1e-4, R4: 1e-3 },
  FT: { critico: 0.1, nao_critico: 1.0 },
};

export function colunaUW(uw) {
  if (uw === null || uw === undefined) return REF.COLUNAS_UW[0];
  const elegiveis = REF.COLUNAS_UW.filter((c) => c <= uw);
  return elegiveis.length ? Math.max(...elegiveis) : REF.COLUNAS_UW[0];
}
export function pld(classe, uw) { return REF.P_LD[classe][colunaUW(uw)]; }
export function pli(categoria, uw) { return REF.P_LI[categoria][colunaUW(uw)]; }

// ---------------------------------------------------------------------------
// Anexo A — número de eventos perigosos
// ---------------------------------------------------------------------------
export const eventos = {
  areaAD(L, W, H) { return L * W + 2 * (3 * H) * (L + W) + Math.PI * (3 * H) ** 2; },
  areaADComplexa(L, W, H_min, H_max) {
    return Math.max(eventos.areaAD(L, W, H_min), Math.PI * (3 * H_max) ** 2);
  },
  ND(N_G, A_D, C_D) { return N_G * A_D * C_D * 1e-6; },
  NDJ(N_G, A_DJ, C_DJ, C_T) { return N_G * A_DJ * C_DJ * C_T * 1e-6; },
  areaAM(L, W) { return 2 * 500 * (L + W) + Math.PI * 500 ** 2; },
  NM(N_G, A_M) { return N_G * A_M * 1e-6; },
  areaAL(L_L, rho) { return (rho !== null && rho !== undefined && rho > 400) ? 0.6 * Math.sqrt(rho) * L_L : 40 * L_L; },
  NL(N_G, A_L, C_I, C_E, C_T) { return N_G * A_L * C_I * C_E * C_T * 1e-6; },
  areaAI(L_L) { return 4000 * L_L; },
  NI(N_G, A_I, C_I, C_E, C_T) { return N_G * A_I * C_I * C_E * C_T * 1e-6; },
};

// ---------------------------------------------------------------------------
// Anexo B — probabilidades de dano
// ---------------------------------------------------------------------------
export const pr = {
  PA(P_TA, P_B) { return P_TA * P_B; },
  PC(P_SPD, C_LD) { return P_SPD * C_LD; },
  PMS(K_S1, K_S2, K_S3, K_S4) { return (K_S1 * K_S2 * K_S3 * K_S4) ** 2; },
  fatorKS4(U_W) { return Math.min(1.0, 1.0 / U_W); },
  PU(P_TU, P_EB, P_LD, C_LD) { return P_TU * P_EB * P_LD * C_LD; },
  PV(P_EB, P_LD, C_LD) { return P_EB * P_LD * C_LD; },
  PW(P_SPD, P_LD, C_LD) { return P_SPD * P_LD * C_LD; },
  PZ(P_SPD, P_LI, C_LI) { return P_SPD * P_LI * C_LI; },
  combinarSistemas(probs) {
    if (!probs.length) return 0.0;
    return 1 - probs.reduce((acc, p) => acc * (1 - p), 1.0);
  },
  piorCaso(probs) { return probs.length ? Math.max(...probs) : 0.0; },
};

// ---------------------------------------------------------------------------
// Anexo C/D — quantidades relativas de perda
// ---------------------------------------------------------------------------
const HORAS_ANO = 8760.0;
function presenca(n_z, n_t, t_z) { return n_t === 0 ? 0.0 : (n_z / n_t) * (t_z / HORAS_ANO); }

export const perdas = {
  _presenca: presenca,
  L_choque(r_t, L_T, n_z, n_t, t_z, r_s) { return r_t * L_T * presenca(n_z, n_t, t_z) * r_s; },
  L_fisico(r_p, r_f, h_z, L_F, n_z, n_t, t_z, r_s) { return r_p * r_f * h_z * L_F * presenca(n_z, n_t, t_z) * r_s; },
  L_sistemas(L_O, n_z, n_t, t_z, r_s) { return L_O * presenca(n_z, n_t, t_z) * r_s; },
  L3_patrimonio(r_p, r_f, L_F, c_z, c_t) { return c_t === 0 ? 0.0 : Math.min(1.0, r_p * r_f * L_F * (c_z / c_t)); },
  L4_choque(r_t, L_T, c_a = 0.0, c_t = 0.0, representativo = false, animais = true) {
    if (representativo) return animais ? r_t * L_T : 0.0;
    return c_t ? r_t * L_T * (c_a / c_t) : 0.0;
  },
  L4_fisico(r_p, r_f, L_F, c_a = 0.0, c_b = 0.0, c_c = 0.0, c_s = 0.0, c_t = 0.0, representativo = false) {
    if (representativo) return r_p * r_f * L_F;
    return c_t ? r_p * r_f * L_F * (c_a + c_b + c_c + c_s) / c_t : 0.0;
  },
  L4_sistemas(L_O, c_s = 0.0, c_t = 0.0, representativo = false) {
    if (representativo) return L_O;
    return c_t ? L_O * (c_s / c_t) : 0.0;
  },
};

// ---------------------------------------------------------------------------
// Componentes de risco R_x = N * P * L
// ---------------------------------------------------------------------------
export const componentes = {
  componente(N, P, L) { return N * P * L; },
  R_linha(trechos, P, L) { return trechos.reduce((acc, [N, N_DJ]) => acc + (N + N_DJ) * P * L, 0); },
};

// ---------------------------------------------------------------------------
// Frequência de danos F (Seção 7, Tabela 7)
// ---------------------------------------------------------------------------
export const frequencia = {
  F_B(N_D, P_B) { return N_D * P_B; },
  F_C(N_D, P_C) { return N_D * P_C; },
  F_M(N_M, P_M) { return N_M * P_M; },
  F_V(N_L_total, P_EB) { return N_L_total * P_EB; },
  F_W(N_L_total, P_W) { return N_L_total * P_W; },
  F_Z(N_I_total, P_Z) { return N_I_total * P_Z; },
};

export const riscos = { excede(R, RT) { return R > RT; } };

export const economico = {
  custoPerdas(R4, c_t) { return R4 * c_t; },
  custoMedidas(C_P, i, a, m) { return C_P * (i + a + m); },
  poupanca(C_L, C_PM, C_RL) { return C_L - (C_PM + C_RL); },
  viabilidade(C_L, C_RL, C_PM) { return economico.poupanca(C_L, C_PM, C_RL) > 0; },
};

// ---------------------------------------------------------------------------
// Captura da memória de cálculo (porte de spda/app.py)
// ---------------------------------------------------------------------------
function op(simbolo, eq, operandos, fn, opts = {}) {
  const valor = opts.valor !== undefined ? opts.valor : fn(...Object.values(operandos));
  return { simbolo, eq, operandos, resultado: valor, origem: opts.origem ?? null };
}
function coef(simbolo, eq, valor, origem) {
  return { simbolo, eq, operandos: {}, resultado: valor, origem: origem ?? null };
}

function ftEstrutura(projeto, est) {
  if (projeto.ft_override !== null && projeto.ft_override !== undefined) return projeto.ft_override;
  return REF.FT[est.sistemas_criticos ? "critico" : "nao_critico"];
}

function memEventosEstrutura(projeto, est) {
  let A_D;
  if (est.H_min !== null && est.H_min !== undefined && est.H_max !== null && est.H_max !== undefined) {
    A_D = op("A_D", "A.1/A.2", { L: est.L, W: est.W, H_min: est.H_min, H_max: est.H_max },
      (L, W, H_min, H_max) => eventos.areaADComplexa(L, W, H_min, H_max),
      { origem: "forma complexa (A.2.1.3.2): maior entre A_D(H_min) e A'_D = pi*(3*H_max)^2" });
  } else {
    A_D = op("A_D", "A.1", { L: est.L, W: est.W, H: est.H }, (L, W, H) => eventos.areaAD(L, W, H));
  }
  const C_D = coef("C_D", "Tabela A.1", REF.C_D[est.localizacao], rotulo("Localizacao", est.localizacao));
  const N_D = op("N_D", "A.3", { N_G: projeto.N_G, A_D: A_D.resultado, C_D: C_D.resultado },
    (N_G, A_D_, C_D_) => eventos.ND(N_G, A_D_, C_D_));
  const A_M = op("A_M", "A.6", { L: est.L, W: est.W }, (L, W) => eventos.areaAM(L, W));
  const N_M = op("N_M", "A.5", { N_G: projeto.N_G, A_M: A_M.resultado }, (N_G, A_M_) => eventos.NM(N_G, A_M_));
  return { A_D, C_D, N_D, A_M, N_M };
}

function nDjLinha(projeto, linha) {
  if (!linha.adjacente) return 0.0;
  const adj = linha.adjacente;
  const A_DJ = eventos.areaAD(adj.L_J, adj.W_J, adj.H_J);
  return eventos.NDJ(projeto.N_G, A_DJ, REF.C_D[adj.localizacao_J], REF.C_T[linha.tipo]);
}

function memLinha(projeto, linha, uwMin, sistemas, uwLabel) {
  const N_DJ_val = nDjLinha(projeto, linha);
  const ml = {
    nome: linha.nome, nivel_eb: linha.nivel_eb === null ? null : rotulo("NivelDPS", linha.nivel_eb),
    uw_min: uwMin, trechos: [], N_L_total: 0, N_I_total: 0,
  };
  let N_L_total = 0, N_I_total = 0;
  linha.trechos.forEach((tr, i) => {
    const inst = tr.instalacao || linha.instalacao;
    const amb = tr.ambiente || linha.ambiente;
    const tip = tr.tipo || linha.tipo;
    const C_I = coef("C_I", "Tabela A.2", REF.C_I[inst], rotulo("InstalacaoLinha", inst));
    const C_E = coef("C_E", "Tabela A.4", REF.C_E[amb], rotulo("AmbienteLinha", amb));
    const C_T = coef("C_T", "Tabela A.3", REF.C_T[tip], rotulo("TipoLinha", tip));
    const A_L_val = eventos.areaAL(tr.L_L, tr.rho);
    const A_L_ops = (tr.rho === null || tr.rho === undefined) ? { L_L: tr.L_L } : { L_L: tr.L_L, rho: tr.rho };
    const A_L = op("A_L", "A.8", A_L_ops, () => A_L_val, { valor: A_L_val });
    const N_L = op("N_L", "A.7", { N_G: projeto.N_G, A_L: A_L.resultado, C_I: C_I.resultado, C_E: C_E.resultado, C_T: C_T.resultado },
      (N_G, A_L_, C_I_, C_E_, C_T_) => eventos.NL(N_G, A_L_, C_I_, C_E_, C_T_));
    const A_I = op("A_I", "A.10", { L_L: tr.L_L }, (L_L) => eventos.areaAI(L_L));
    const N_I = op("N_I", "A.9", { N_G: projeto.N_G, A_I: A_I.resultado, C_I: C_I.resultado, C_E: C_E.resultado, C_T: C_T.resultado },
      (N_G, A_I_, C_I_, C_E_, C_T_) => eventos.NI(N_G, A_I_, C_I_, C_E_, C_T_));
    let N_DJ = null;
    if (i === 0 && N_DJ_val) {
      N_DJ = { simbolo: "N_DJ", eq: "A.4", operandos: {}, resultado: N_DJ_val,
        origem: `adjacente: ${rotulo("Localizacao", linha.adjacente.localizacao_J)}` };
    }
    ml.trechos.push({ nome: `trecho ${i + 1}`, L_L: tr.L_L, rho: tr.rho, C_I, C_E, C_T, A_L, N_L, A_I, N_I, N_DJ });
    N_L_total += N_L.resultado + (i === 0 ? N_DJ_val : 0.0);
    N_I_total += N_I.resultado;
  });
  ml.N_L_total = N_L_total;
  ml.N_I_total = N_I_total;

  const C_LD = coef("C_LD", "Tabela B.4", REF.C_LD[linha.tipo_externa], rotulo("TipoLinhaExterna", linha.tipo_externa));
  const C_LI = coef("C_LI", "Tabela B.4", REF.C_LI[linha.tipo_externa], rotulo("TipoLinhaExterna", linha.tipo_externa));
  const P_LD = coef("P_LD", "Tabela B.8", pld(linha.classe_blindagem, uwMin), `${rotulo("ClasseBlindagemRS", linha.classe_blindagem)}, U_W=${uwLabel}`);
  const P_LI = coef("P_LI", "Tabela B.9", pli(linha.categoria, uwMin), `${rotulo("CategoriaLinha", linha.categoria)}, U_W=${uwLabel}`);
  const P_TU = coef("P_TU", "Tabela B.6", REF.P_TU[linha.protecao_toque_entrada], rotulo("ProtecaoToqueEntrada", linha.protecao_toque_entrada));
  const P_EB_val = linha.nivel_eb === null ? 1.0 : REF.P_EB[linha.nivel_eb];
  const P_EB = coef("P_EB", "Tabela B.7", P_EB_val, linha.nivel_eb === null ? "sem DPS" : rotulo("NivelDPS", linha.nivel_eb));
  ml.C_LD = C_LD; ml.C_LI = C_LI; ml.P_LD = P_LD; ml.P_LI = P_LI; ml.P_TU = P_TU; ml.P_EB = P_EB;
  ml.P_U = op("P_U", "B.8", { P_TU: P_TU.resultado, P_EB: P_EB.resultado, P_LD: P_LD.resultado, C_LD: C_LD.resultado },
    (a, b, c, d) => pr.PU(a, b, c, d));
  ml.P_V = op("P_V", "B.9", { P_EB: P_EB.resultado, P_LD: P_LD.resultado, C_LD: C_LD.resultado }, (a, b, c) => pr.PV(a, b, c));
  const P_W_val = pr.piorCaso(sistemas.map((s) => pr.PW(s.P_SPD, P_LD.resultado, C_LD.resultado)));
  const P_Z_val = pr.piorCaso(sistemas.map((s) => pr.PZ(s.P_SPD, P_LI.resultado, C_LI.resultado)));
  ml.P_W = { simbolo: "P_W", eq: "B.10", operandos: { P_LD: P_LD.resultado, C_LD: C_LD.resultado }, resultado: P_W_val, origem: "pior caso sobre sistemas (6.9.1.2a/7.4.1.2a)" };
  ml.P_Z = { simbolo: "P_Z", eq: "B.11", operandos: { P_LI: P_LI.resultado, C_LI: C_LI.resultado }, resultado: P_Z_val, origem: "pior caso sobre sistemas (6.9.1.2a/7.4.1.2a)" };
  return ml;
}

function temExplosao(est) { return est.risco_explosao || est.zona_explosao !== "nenhuma"; }
function zonaExplosaoEfetiva(est) {
  if (est.zona_explosao !== "nenhuma") return est.zona_explosao;
  return est.risco_explosao ? "zona_0_20" : "nenhuma";
}
function resolverRfRp(est) {
  if (temExplosao(est)) {
    const ze = zonaExplosaoEfetiva(est);
    const r_f = coef("r_f", "Tabela C.5", REF.R_F_EXPLOSAO[ze], rotulo("ZonaExplosao", ze));
    const r_p = coef("r_p", "C.3.4", 1.0, "risco de explosão → r_p = 1");
    return [r_f, r_p];
  }
  const r_f = coef("r_f", "Tabela C.5", REF.R_F[est.risco_incendio], rotulo("RiscoIncendio", est.risco_incendio));
  const r_p = coef("r_p", "Tabela C.4", REF.R_P[est.providencias_incendio], rotulo("ProvidenciaIncendio", est.providencias_incendio));
  return [r_f, r_p];
}
function resolverLF(est) { return temExplosao(est) ? REF.L_F_EXPLOSAO : REF.L_F[est.ocupacao]; }
function resolverLO(est) {
  if (temExplosao(est)) return REF.L_O_EXPLOSAO;
  if (est.sistemas_criticos) return REF.L_O_HOSPITAL_CRITICO;
  return REF.L_O_PADRAO;
}
function resolverLF_L4(est) { return temExplosao(est) ? REF.L_F_L4_EXPLOSAO : REF.L_F_L4[est.ocupacao]; }
function resolverLO_L4(est) { return temExplosao(est) ? REF.L_O_L4_EXPLOSAO : REF.L_O_L4[est.ocupacao]; }
function CLDZona() { return 1.0; }

function memZona(projeto, est, zona, eventosEst) {
  const { N_D: N_D_op, N_M: N_M_op } = eventosEst;
  const N_D = N_D_op.resultado, N_M = N_M_op.resultado;

  const r_t = coef("r_t", "Tabela C.3", REF.R_T[zona.superficie], rotulo("TipoSuperficie", zona.superficie));
  const [r_f, r_p] = resolverRfRp(est);
  const r_s = coef("r_s", "Tabela C.7", REF.R_S[est.tipo_construcao], rotulo("TipoConstrucao", est.tipo_construcao));
  const L_F_val = resolverLF(est);
  const P_TA = coef("P_TA", "Tabela B.1", REF.P_TA[zona.medidas.protecao_toque_passo], rotulo("ProtecaoToquePasso", zona.medidas.protecao_toque_passo));
  const P_B_val = est.nivel_spda === null ? 1.0 : REF.P_B[est.nivel_spda];
  const P_B = coef("P_B", "Tabela B.2", P_B_val, est.nivel_spda === null ? "sem SPDA" : rotulo("NivelProtecao", est.nivel_spda));

  const mz = { nome: zona.nome, n_z: zona.n_z, t_z: zona.t_z, coefs: { r_t, r_p, r_f, r_s, P_TA, P_B }, sistemas: [], linhas: [] };

  const L_O = resolverLO(est);
  mz.presenca = op("presenca", "C.6", { n_z: zona.n_z, n_t: est.n_t, t_z: zona.t_z }, (n_z, n_t, t_z) => presenca(n_z, n_t, t_z));
  mz.L_A = op("L_A", "C.1", { r_t: r_t.resultado, L_T: REF.L_T, n_z: zona.n_z, n_t: est.n_t, t_z: zona.t_z, r_s: r_s.resultado },
    (rt_, LT_, nz_, nt_, tz_, rs_) => perdas.L_choque(rt_, LT_, nz_, nt_, tz_, rs_));
  mz.L_B = op("L_B", "C.3", { r_p: r_p.resultado, r_f: r_f.resultado, h_z: zona.h_z, L_F: L_F_val, n_z: zona.n_z, n_t: est.n_t, t_z: zona.t_z, r_s: r_s.resultado },
    (rp_, rf_, hz_, LF_, nz_, nt_, tz_, rs_) => perdas.L_fisico(rp_, rf_, hz_, LF_, nz_, nt_, tz_, rs_));
  mz.L_sis = op("L_sis", "C.4", { L_O, n_z: zona.n_z, n_t: est.n_t, t_z: zona.t_z, r_s: r_s.resultado },
    (LO_, nz_, nt_, tz_, rs_) => perdas.L_sistemas(LO_, nz_, nt_, tz_, rs_));

  const temL3 = (zona.c_z !== null && zona.c_z !== undefined) && (est.c_t !== null && est.c_t !== undefined && est.c_t > 0);
  if (temL3) {
    mz.L_B3 = op("L_B3", "C.7", { r_p: r_p.resultado, r_f: r_f.resultado, L_F: REF.L_F_L3, c_z: zona.c_z, c_t: est.c_t },
      (rp_, rf_, LF_, cz_, ct_) => perdas.L3_patrimonio(rp_, rf_, LF_, cz_, ct_));
  } else { mz.L_B3 = null; }
  const temL4 = est.c_t !== null && est.c_t !== undefined && est.c_t > 0;
  if (temL4) {
    const L_F_L4_val = resolverLF_L4(est);
    const L_O_L4_val = resolverLO_L4(est);
    if (projeto.r4_representativo) {
      const org = "R_T representativo (Tabela 4) -> razão = 1 (nota Eqs D.1-D.4)";
      const temAnimais = !!zona.c_a;
      if (temAnimais) {
        mz.L4_A = op("L4_A", "D.1", { r_t: r_t.resultado, L_T: REF.L_T }, () => 0, {
          valor: perdas.L4_choque(r_t.resultado, REF.L_T, 0, 0, true, true), origem: org });
      } else {
        mz.L4_A = { simbolo: "L4_A", eq: "D.1", operandos: {}, resultado: 0.0,
          origem: "sem animais na zona -> L_T não se aplica (Tabela C.12) -> L4_A = 0" };
      }
      mz.L4_B = op("L4_B", "D.3", { r_p: r_p.resultado, r_f: r_f.resultado, L_F: L_F_L4_val }, () => 0, {
        valor: perdas.L4_fisico(r_p.resultado, r_f.resultado, L_F_L4_val, 0, 0, 0, 0, 0, true), origem: org });
      mz.L4_sis = op("L4_sis", "D.4", { L_O: L_O_L4_val }, () => 0, {
        valor: perdas.L4_sistemas(L_O_L4_val, 0, 0, true), origem: org });
    } else {
      mz.L4_A = op("L4_A", "D.1", { r_t: r_t.resultado, L_T: REF.L_T, c_a: zona.c_a || 0.0, c_t: est.c_t },
        (rt_, LT_, ca_, ct_) => perdas.L4_choque(rt_, LT_, ca_, ct_, false));
      mz.L4_B = op("L4_B", "D.3", { r_p: r_p.resultado, r_f: r_f.resultado, L_F: L_F_L4_val, c_a: zona.c_a || 0.0, c_b: zona.c_b || 0.0, c_c: zona.c_c || 0.0, c_s: zona.c_s || 0.0, c_t: est.c_t },
        (rp_, rf_, LF_, ca_, cb_, cc_, cs_, ct_) => perdas.L4_fisico(rp_, rf_, LF_, ca_, cb_, cc_, cs_, ct_, false));
      mz.L4_sis = op("L4_sis", "D.4", { L_O: L_O_L4_val, c_s: zona.c_s || 0.0, c_t: est.c_t },
        (LO_, cs_, ct_) => perdas.L4_sistemas(LO_, cs_, ct_, false));
    }
  } else { mz.L4_A = null; mz.L4_B = null; mz.L4_sis = null; }

  const sistemasCalc = [];
  const P_C_list = [], P_M_list = [];
  for (const sis of zona.sistemas_internos) {
    const P_SPD_val = sis.dps === null ? 1.0 : REF.P_SPD[sis.dps];
    const k_s4_val = sis.K_S4 !== null && sis.K_S4 !== undefined ? sis.K_S4 : (sis.U_W !== null && sis.U_W !== undefined ? pr.fatorKS4(sis.U_W) : 1.0);
    let P_MS_val;
    if (sis.U_W === null || sis.U_W === undefined) P_MS_val = 1.0;
    else P_MS_val = pr.PMS(sis.K_S1, sis.K_S2, sis.K_S3, k_s4_val);
    const P_C_val = pr.PC(P_SPD_val, CLDZona());
    const k_s4_origem = sis.K_S4 !== null && sis.K_S4 !== undefined ? "informado" : (sis.U_W !== null && sis.U_W !== undefined ? "1/U_W" : "default 1.0");
    let p_ms_op;
    if (sis.U_W === null || sis.U_W === undefined) {
      p_ms_op = coef("P_MS", "B.4", P_MS_val, "U_W desconhecido -> 1 (pior caso)");
    } else {
      p_ms_op = op("P_MS", "B.4", { K_S1: sis.K_S1, K_S2: sis.K_S2, K_S3: sis.K_S3, K_S4: k_s4_val }, () => 0, { valor: P_MS_val });
    }
    const ms = {
      nome: sis.nome, U_W: sis.U_W, dps: sis.dps === null ? null : rotulo("NivelDPS", sis.dps),
      K_S1: coef("K_S1", "Tabela B.5", sis.K_S1, "informado"),
      K_S2: coef("K_S2", "Tabela B.5", sis.K_S2, "informado"),
      K_S3: coef("K_S3", "Tabela B.5", sis.K_S3, "informado"),
      K_S4: coef("K_S4", "Tabela B.5", k_s4_val, k_s4_origem),
      P_SPD: coef("P_SPD", "Tabela B.3", P_SPD_val, sis.dps === null ? "sem DPS" : rotulo("NivelDPS", sis.dps)),
      P_MS_i: p_ms_op,
      P_C_i: op("P_C", "B.2", { P_SPD: P_SPD_val, C_LD: CLDZona() }, (a, b) => pr.PC(a, b)),
    };
    mz.sistemas.push(ms);
    const P_M_i = (sis.U_W === null || sis.U_W === undefined) ? P_MS_val : P_SPD_val * P_MS_val;
    sistemasCalc.push({ P_SPD: P_SPD_val });
    P_C_list.push(P_C_val);
    P_M_list.push(P_M_i);
  }
  const P_C_comb = pr.combinarSistemas(P_C_list);
  const P_M_comb = pr.combinarSistemas(P_M_list);
  mz.P_A = op("P_A", "B.1", { P_TA: P_TA.resultado, P_B: P_B.resultado }, (a, b) => pr.PA(a, b));
  mz.P_C = { simbolo: "P_C", eq: "eq.12", operandos: {}, resultado: P_C_comb, origem: "1 - prod(1 - P_C_i) sobre sistemas" };
  mz.P_M = { simbolo: "P_M", eq: "eq.13", operandos: {}, resultado: P_M_comb, origem: "1 - prod(1 - P_M_i) sobre sistemas; P_M_i = P_SPD x P_MS (B.4.9)" };

  mz.R_A = op("R_A", "eq.3", { N: N_D, P: mz.P_A.resultado, L: mz.L_A.resultado }, (n, p, l) => componentes.componente(n, p, l));
  mz.R_B = op("R_B", "eq.4", { N: N_D, P: P_B.resultado, L: mz.L_B.resultado }, (n, p, l) => componentes.componente(n, p, l));
  mz.R_C = op("R_C", "eq.5", { N: N_D, P: P_C_comb, L: mz.L_sis.resultado }, (n, p, l) => componentes.componente(n, p, l));
  mz.R_M = op("R_M", "eq.6", { N: N_M, P: P_M_comb, L: mz.L_sis.resultado }, (n, p, l) => componentes.componente(n, p, l));
  if (temL3) {
    mz.R_B3 = op("R_B3", "L3", { N: N_D, P: P_B.resultado, L: mz.L_B3.resultado }, (n, p, l) => componentes.componente(n, p, l));
  } else { mz.R_B3 = null; }

  const uws = zona.sistemas_internos.map((s) => s.U_W);
  const uwMin = (!uws.length || uws.some((u) => u === null || u === undefined)) ? null : Math.min(...uws);
  const uwLabel = uwMin === null ? `${UW_CONSERVADOR_KV.toFixed(0)} kV (conservador)` : `${uwMin} kV`;
  let R_U = 0, R_V = 0, R_W = 0, R_Z = 0, R_V3 = 0, R4_total = 0;
  if (temL4) {
    R4_total += componentes.componente(N_D, mz.P_A.resultado, mz.L4_A.resultado)
      + componentes.componente(N_D, P_B.resultado, mz.L4_B.resultado)
      + componentes.componente(N_D, P_C_comb, mz.L4_sis.resultado)
      + componentes.componente(N_M, P_M_comb, mz.L4_sis.resultado);
  }
  const F_B_val = zona.sistemas_internos.some((s) => s.em_zpr0a) ? frequencia.F_B(N_D, P_B.resultado) : 0.0;
  let F_zona_val = F_B_val + frequencia.F_C(N_D, P_C_comb) + frequencia.F_M(N_M, P_M_comb);

  for (const linha of est.linhas) {
    const ml = memLinha(projeto, linha, uwMin, sistemasCalc, uwLabel);
    const mzTrechos = ml.trechos.map((t) => [t.N_L.resultado, t.N_DJ ? t.N_DJ.resultado : 0.0]);
    R_U += componentes.R_linha(mzTrechos, ml.P_U.resultado, mz.L_A.resultado);
    R_V += componentes.R_linha(mzTrechos, ml.P_V.resultado, mz.L_B.resultado);
    R_W += componentes.R_linha(mzTrechos, ml.P_W.resultado, mz.L_sis.resultado);
    R_Z += componentes.componente(ml.N_I_total, ml.P_Z.resultado, mz.L_sis.resultado);
    if (temL3) R_V3 += componentes.R_linha(mzTrechos, ml.P_V.resultado, mz.L_B3.resultado);
    if (temL4) {
      R4_total += componentes.R_linha(mzTrechos, ml.P_U.resultado, mz.L4_A.resultado)
        + componentes.R_linha(mzTrechos, ml.P_V.resultado, mz.L4_B.resultado)
        + componentes.R_linha(mzTrechos, ml.P_W.resultado, mz.L4_sis.resultado)
        + componentes.componente(ml.N_I_total, ml.P_Z.resultado, mz.L4_sis.resultado);
    }
    F_zona_val += frequencia.F_V(ml.N_L_total, ml.P_EB.resultado) + frequencia.F_W(ml.N_L_total, ml.P_W.resultado) + frequencia.F_Z(ml.N_I_total, ml.P_Z.resultado);
    mz.linhas.push(ml);
  }

  mz.R_U = { simbolo: "R_U", eq: "eq.8", operandos: {}, resultado: R_U, origem: "soma sobre linhas/trechos" };
  mz.R_V = { simbolo: "R_V", eq: "eq.9", operandos: {}, resultado: R_V, origem: "soma sobre linhas/trechos" };
  mz.R_W = { simbolo: "R_W", eq: "eq.10", operandos: {}, resultado: R_W, origem: "soma sobre linhas/trechos" };
  mz.R_Z = { simbolo: "R_Z", eq: "eq.11", operandos: {}, resultado: R_Z, origem: "soma sobre linhas (N_I)" };
  mz.R_V3 = temL3 ? { simbolo: "R_V3", eq: "L3", operandos: {}, resultado: R_V3, origem: "soma sobre linhas/trechos" } : null;
  mz.R4_total = temL4 ? { simbolo: "R4_total", eq: "13.3", operandos: {}, resultado: R4_total, origem: "soma D1+D2+D3 (L4)" } : null;
  mz.F_zona = { simbolo: "F_zona", eq: "Seção 7", operandos: {}, resultado: F_zona_val, origem: "F_B+F_C+F_M+F_V+F_W+F_Z (F_V com P_EB; F_B só com equipamento em ZPR 0A)" };
  return mz;
}

function memEstrutura(projeto, est) {
  const eventosEst = memEventosEstrutura(projeto, est);
  const zonas = est.zonas.map((z) => memZona(projeto, est, z, eventosEst));

  const incluirD3 = temExplosao(est) || est.sistemas_criticos || est.ocupacao === "hospital";
  const me = {
    nome: est.nome,
    ft: ftEstrutura(projeto, est),
    entradas: {
      L: est.L, W: est.W, H: est.H, localizacao: rotulo("Localizacao", est.localizacao),
      tipo_construcao: rotulo("TipoConstrucao", est.tipo_construcao),
      risco_incendio: rotulo("RiscoIncendio", est.risco_incendio),
      providencias_incendio: rotulo("ProvidenciaIncendio", est.providencias_incendio),
      ocupacao: rotulo("TipoOcupacao", est.ocupacao), zona_explosao: rotulo("ZonaExplosao", est.zona_explosao),
      risco_explosao: est.risco_explosao, sistemas_criticos: est.sistemas_criticos,
      nivel_spda: est.nivel_spda === null ? null : rotulo("NivelProtecao", est.nivel_spda),
      n_t: est.n_t, c_t: est.c_t,
    },
    A_D: eventosEst.A_D, C_D: eventosEst.C_D, N_D: eventosEst.N_D, A_M: eventosEst.A_M, N_M: eventosEst.N_M,
    zonas,
  };

  const comps1 = ["R_A", "R_B", "R_U", "R_V"];
  const r1_parcelas = {};
  for (const c of comps1) r1_parcelas[c] = zonas.reduce((acc, z) => acc + z[c].resultado, 0);
  if (incluirD3) {
    for (const c of ["R_C", "R_M", "R_W", "R_Z"]) r1_parcelas[c] = zonas.reduce((acc, z) => acc + z[c].resultado, 0);
  }
  const R1_val = Object.values(r1_parcelas).reduce((a, b) => a + b, 0);
  const R3_val = zonas.reduce((acc, z) => acc + (z.R_B3 ? z.R_B3.resultado : 0) + (z.R_V3 ? z.R_V3.resultado : 0), 0);
  const R4_val = zonas.reduce((acc, z) => acc + (z.R4_total ? z.R4_total.resultado : 0), 0);
  const F_val = zonas.reduce((acc, z) => acc + z.F_zona.resultado, 0);

  me.R1 = { simbolo: "R1", eq: "Seção 8", operandos: r1_parcelas, resultado: R1_val, origem: "soma das parcelas por zona" };
  me.R3 = { simbolo: "R3", eq: "Seção 8", operandos: {}, resultado: R3_val, origem: "soma (R_B3+R_V3)" };
  me.R4 = { simbolo: "R4", eq: "Seção 8", operandos: {}, resultado: R4_val, origem: "soma R4_total" };
  me.F = { simbolo: "F", eq: "Seção 7", operandos: {}, resultado: F_val, origem: "soma F_zona" };
  me.dominantes = Object.entries(r1_parcelas).sort((a, b) => b[1] - a[1]);
  return me;
}

function projetarZona(mz) {
  const rz = { nome: mz.nome };
  for (const c of ["R_A", "R_B", "R_C", "R_M", "R_U", "R_V", "R_W", "R_Z"]) rz[c] = mz[c].resultado;
  rz.R_B3 = mz.R_B3 ? mz.R_B3.resultado : 0.0;
  rz.R_V3 = mz.R_V3 ? mz.R_V3.resultado : 0.0;
  rz.R4_total = mz.R4_total ? mz.R4_total.resultado : 0.0;
  rz.F_zona = mz.F_zona.resultado;
  return rz;
}
function projetarEstrutura(me, rt) {
  const linhas0 = me.zonas.length ? me.zonas[0].linhas : [];
  const N_DJ = linhas0.reduce((acc, l) => acc + l.trechos.reduce((a, t) => a + (t.N_DJ ? t.N_DJ.resultado : 0), 0), 0);
  return {
    nome: me.nome, N_D: me.N_D.resultado, N_M: me.N_M.resultado, N_DJ,
    R1: me.R1.resultado, R3: me.R3.resultado, R4: me.R4.resultado, F: me.F.resultado, ft: me.ft,
    excede_R1: riscos.excede(me.R1.resultado, rt.R1), excede_R3: riscos.excede(me.R3.resultado, rt.R3),
    excede_R4: riscos.excede(me.R4.resultado, rt.R4), excede_F: riscos.excede(me.F.resultado, me.ft),
    dominantes: me.dominantes, zonas: me.zonas.map(projetarZona),
  };
}

export function analisarMemoria(projeto) {
  const rt = { ...REF.RT, ...(projeto.rt_override || {}) };
  const estruturas = projeto.estruturas.map((est) => memEstrutura(projeto, est));
  return { projeto: projeto.nome, cidade: projeto.cidade, identificacao: projeto.identificacao, rt, r4_representativo: projeto.r4_representativo, estruturas };
}
export function analisar(projeto) {
  const mem = analisarMemoria(projeto);
  return { projeto: mem.projeto, rt: mem.rt, estruturas: mem.estruturas.map((me) => projetarEstrutura(me, mem.rt)) };
}

// ---------------------------------------------------------------------------
// Estudo de Solução (Seção 11) — porte de spda/solucao
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
const ESC_TP = ["nenhuma", "avisos", "isolacao"];
const ESC_INC = ["nenhuma", "extintor", "fixo_automatico"];

function labelOrNone(campo, v) { return v === null || v === undefined ? "nenhum" : rotulo(campo, v); }

// Catálogo de medidas: cada uma sabe seu nível atual na estrutura e como
// aplicar um valor absoluto da escada (não mais "avançar 1 nível" — o
// otimizador escolhe qualquer combinação de níveis simultaneamente).
export const MEDIDAS = [
  {
    id: "spda", descricao: "SPDA (nível de proteção)", parametro: "P_B", componentes: ["R_B", "R_V"],
    escada: ESC_SPDA, rotuloValor: (v) => labelOrNone("NivelProtecao", v),
    aplicavel() { return true; },
    indiceAtual(est) { return idxOf(est.nivel_spda, ESC_SPDA); },
    aplicar(est, valor) { const copia = structuredClone(est); copia.nivel_spda = valor; return copia; },
  },
  {
    id: "toque_passo", descricao: "Proteção contra tensão de toque e passo", parametro: "P_TA", componentes: ["R_A", "R_U"],
    escada: ESC_TP, rotuloValor: (v) => rotulo("ProtecaoToquePasso", v),
    aplicavel(est) { return est.zonas.length > 0; },
    indiceAtual(est) { return idxZonas(est, "protecao_toque_passo", ESC_TP); },
    aplicar(est, valor) { const copia = structuredClone(est); copia.zonas.forEach((z) => { z.medidas.protecao_toque_passo = valor; }); return copia; },
  },
  {
    id: "dps", descricao: "Sistema coordenado de DPS", parametro: "P_SPD", componentes: ["R_C", "R_W", "R_Z"],
    escada: ESC_DPS, rotuloValor: (v) => labelOrNone("NivelDPS", v),
    aplicavel(est) { return est.zonas.some((z) => z.sistemas_internos.length > 0); },
    indiceAtual(est) { return idxSistemas(est, ESC_DPS); },
    aplicar(est, valor) { const copia = structuredClone(est); copia.zonas.forEach((z) => z.sistemas_internos.forEach((s) => { s.dps = valor; })); return copia; },
  },
  {
    id: "incendio", descricao: "Sistema de combate a incêndio", parametro: "r_p", componentes: ["R_B", "R_V"],
    escada: ESC_INC, rotuloValor: (v) => rotulo("ProvidenciaIncendio", v),
    aplicavel() { return true; },
    indiceAtual(est) { return idxOf(est.providencias_incendio, ESC_INC); },
    aplicar(est, valor) { const copia = structuredClone(est); copia.providencias_incendio = valor; return copia; },
  },
];

// Medidas cuja escada atual da estrutura é reconhecida (indiceAtual !== null)
// e que fazem sentido para ela (ex.: toque/passo exige zonas, DPS exige
// sistemas internos). Só essas entram na busca combinatória.
export function medidasDisponiveis(est) {
  return MEDIDAS.filter((m) => m.aplicavel(est) && m.indiceAtual(est) !== null);
}

function metricasEstrutura(projeto, est) {
  const p = {
    nome: projeto.nome, N_G: projeto.N_G, rt_override: projeto.rt_override,
    ft_override: projeto.ft_override, r4_representativo: projeto.r4_representativo, estruturas: [est],
  };
  return analisar(p).estruturas[0];
}
function rtR1De(projeto) {
  return (projeto.rt_override && projeto.rt_override.R1 !== undefined) ? projeto.rt_override.R1 : REF.RT.R1;
}
function aplicarCombo(est, medidas, combo) {
  let atual = est;
  for (const m of medidas) atual = m.aplicar(atual, combo[m.id]);
  return atual;
}
// Limita a busca combinatória a no máximo N alvos por medida (amostra
// uniforme incluindo o nível atual e o máximo), mantendo o espaço de busca
// tratável mesmo com 4 escadas independentes sendo testadas ao mesmo tempo.
const MAX_ALVOS_POR_MEDIDA = 4;
function amostrarAlvos(escada, iAtual) {
  const total = escada.length - iAtual;
  if (total <= MAX_ALVOS_POR_MEDIDA) return escada.slice(iAtual);
  const passo = (total - 1) / (MAX_ALVOS_POR_MEDIDA - 1);
  const idxs = new Set();
  for (let k = 0; k < MAX_ALVOS_POR_MEDIDA; k++) idxs.add(iAtual + Math.round(k * passo));
  return [...idxs].sort((a, b) => a - b).map((idx) => escada[idx]);
}

// Busca combinatória: testa combinações simultâneas de níveis de todas as
// medidas aplicáveis (não uma de cada vez) e retorna os pacotes válidos
// (atendem R1 e F ao mesmo tempo) que alteram menos medidas / menores saltos
// de nível — os "mais enxutos" primeiro. O engenheiro escolhe um pacote como
// ponto de partida e pode ajustar cada medida manualmente antes de decidir.
export function pacotesParaEstrutura(projeto, est, maxPacotes = 3) {
  const base = metricasEstrutura(projeto, est);
  const medidas = medidasDisponiveis(est);
  const medidasInfo = medidas.map((m) => {
    const iAtual = m.indiceAtual(est);
    return {
      id: m.id, descricao: m.descricao,
      opcoes: m.escada.map((v, idx) => ({ valor: v, rotulo: m.rotuloValor(v), disponivel: idx >= iAtual })),
      valorAtual: m.escada[iAtual],
    };
  });
  const identidade = Object.fromEntries(medidas.map((m) => [m.id, m.escada[m.indiceAtual(est)]]));
  if (!(base.excede_R1 || base.excede_F)) {
    return { nome: est.nome, jaConforme: true, R1: base.R1, F: base.F, rt_R1: null, ft: base.ft, medidas: medidasInfo, identidade, pacotes: [], semSolucao: false };
  }
  const rtR1 = rtR1De(projeto);
  const opcoesPorMedida = medidas.map((m) => ({ medida: m, alvos: amostrarAlvos(m.escada, m.indiceAtual(est)) }));
  let combos = [{}];
  for (const { medida, alvos } of opcoesPorMedida) {
    const novo = [];
    for (const c of combos) for (const alvo of alvos) novo.push({ ...c, [medida.id]: alvo });
    combos = novo;
  }
  const avaliados = combos.map((combo) => {
    const estMod = aplicarCombo(est, medidas, combo);
    const re = metricasEstrutura(projeto, estMod);
    let mudancas = 0, saltos = 0;
    const detalhes = medidas.map((m) => {
      const iAtual = m.indiceAtual(est);
      const iAlvo = m.escada.indexOf(combo[m.id]);
      const mudou = iAlvo !== iAtual;
      if (mudou) { mudancas++; saltos += Math.abs(iAlvo - iAtual); }
      return { id: m.id, descricao: m.descricao, de: m.rotuloValor(m.escada[iAtual]), para: m.rotuloValor(combo[m.id]), mudou };
    });
    return { combo, re, mudancas, saltos, detalhes, valido: re.R1 <= rtR1 && re.F <= re.ft };
  });
  const validos = avaliados.filter((a) => a.valido && a.mudancas > 0);
  validos.sort((a, b) => a.mudancas - b.mudancas || a.saltos - b.saltos || a.re.R1 - b.re.R1);
  const vistos = new Set();
  const top = [];
  for (const a of validos) {
    const chave = JSON.stringify(a.combo);
    if (vistos.has(chave)) continue;
    vistos.add(chave);
    top.push(a);
    if (top.length >= maxPacotes) break;
  }
  return {
    nome: est.nome, jaConforme: false, R1: base.R1, F: base.F, rt_R1: rtR1, ft: base.ft,
    medidas: medidasInfo, identidade,
    pacotes: top.map((a, i) => ({
      indice: i + 1, combo: a.combo, mudancas: a.detalhes.filter((d) => d.mudou),
      R1: a.re.R1, R3: a.re.R3, R4: a.re.R4, F: a.re.F, ft: a.re.ft,
    })),
    semSolucao: validos.length === 0,
  };
}

// Avalia uma combinação arbitrária (ex.: escolhida manualmente no simulador)
// sem gravar nada — usado para feedback ao vivo enquanto o engenheiro ajusta.
export function avaliarCombinacao(projeto, est, combo) {
  const medidas = medidasDisponiveis(est);
  const estMod = aplicarCombo(est, medidas, combo);
  const re = metricasEstrutura(projeto, estMod);
  return { R1: re.R1, R3: re.R3, R4: re.R4, F: re.F, ft: re.ft, excede_R1: re.excede_R1, excede_R3: re.excede_R3, excede_R4: re.excede_R4, excede_F: re.excede_F };
}

// Retorna a estrutura com a combinação aplicada diretamente aos seus campos
// (sobrescreve nivel_spda/dps/etc. — usar só quando não há distinção entre
// "situação atual" e "proposta", ex.: projeto novo ou medida já implementada).
export function aplicarCombinacaoEmEstrutura(est, combo) {
  const medidas = medidasDisponiveis(est);
  return aplicarCombo(est, medidas, combo);
}

// Grava a combinação escolhida no projeto (só chamado quando o engenheiro
// confirma com "Aplicar ao projeto" — nada é persistido antes disso).
export function aplicarCombinacaoAoProjeto(projeto, estIndex, combo) {
  const p = structuredClone(projeto);
  p.estruturas[estIndex] = aplicarCombinacaoEmEstrutura(p.estruturas[estIndex], combo);
  return p;
}

// Propostas registradas via "Salvar proposta": combinações avaliadas e
// guardadas em est.proposta.combo SEM alterar os campos reais da estrutura —
// o caminho certo para instalação existente, onde a situação atual (as-built)
// precisa ficar preservada enquanto se documenta o impacto de uma melhoria
// ainda não implementada. Usado pelo relatório para mostrar atual vs proposto.
export function propostasRegistradas(projeto) {
  const linhas = [];
  const rtR1 = rtR1De(projeto);
  for (const est of projeto.estruturas) {
    if (!est.proposta || !est.proposta.combo) continue;
    const atual = metricasEstrutura(projeto, est);
    const avaliado = avaliarCombinacao(projeto, est, est.proposta.combo);
    const medidas = medidasDisponiveis(est);
    const mudancas = medidas
      .map((m) => {
        const iAtual = m.indiceAtual(est);
        const valor = est.proposta.combo[m.id];
        if (valor === undefined || valor === m.escada[iAtual]) return null;
        return { descricao: m.descricao, de: m.rotuloValor(m.escada[iAtual]), para: m.rotuloValor(valor) };
      })
      .filter(Boolean);
    if (!mudancas.length) continue;
    linhas.push({
      nome: est.nome, mudancas,
      R1_atual: atual.R1, F_atual: atual.F, rt_R1: rtR1, ft: atual.ft,
      R1_proposto: avaliado.R1, R3_proposto: avaliado.R3, R4_proposto: avaliado.R4, F_proposto: avaliado.F,
      atinge_rt: avaliado.R1 <= rtR1, atinge_ft: avaliado.F <= avaliado.ft,
    });
  }
  return linhas;
}

// Usado pelo memorial/relatório: para cada estrutura pendente, reporta o
// melhor pacote (1º da lista ranqueada) como recomendação, com uma linha por
// medida alterada (mudança simultânea, não mais passo a passo).
export function estudoSolucao(projeto) {
  const estruturas = [];
  for (const est of projeto.estruturas) {
    const pac = pacotesParaEstrutura(projeto, est, 1);
    if (pac.jaConforme) continue;
    const melhor = pac.pacotes[0];
    estruturas.push({
      nome: est.nome,
      R1_inicial: pac.R1, rt_R1: pac.rt_R1, R1_final: melhor ? melhor.R1 : pac.R1,
      atingiu_rt: melhor ? melhor.R1 <= pac.rt_R1 : false,
      F_inicial: pac.F, ft: pac.ft, F_final: melhor ? melhor.F : pac.F,
      atingiu_ft: melhor ? melhor.F <= melhor.ft : false,
      passos: melhor ? melhor.mudancas.map((m) => ({
        medida: m.descricao, parametro: "", componentes: [], de: m.de, para: m.para,
        R_projetado: melhor.R1, F_projetado: melhor.F,
        atingiu_rt: melhor.R1 <= pac.rt_R1, atingiu_ft: melhor.F <= melhor.ft,
      })) : [],
    });
  }
  return { projeto: projeto.nome, estruturas };
}
