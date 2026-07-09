// spda-model.js — enums, rótulos, opções de formulário, fábricas de default e
// projeto de exemplo (porta 1:1 do model Python / Teste.json).

export const ENUM_OPTIONS = {
  Localizacao: [
    ["cercada_mais_altos", "Cercada por objetos mais altos"],
    ["cercada_mesma_altura", "Cercada por objetos da mesma altura ou mais baixos"],
    ["isolada", "Isolada (nenhum objeto nas vizinhanças)"],
    ["topo_colina", "Isolada no topo de uma colina ou monte"],
  ],
  TipoConstrucao: [
    ["simples", "Simples: madeira ou alvenaria simples"],
    ["robusta", "Robusta: estrutura metálica ou concreto armado"],
  ],
  NivelProtecao: [
    ["nenhum", "Sem SPDA"],
    ["IV", "SPDA nível IV"],
    ["III", "SPDA nível III"],
    ["II", "SPDA nível II"],
    ["I", "SPDA nível I"],
    ["I_descida_natural", "SPDA nível I com descida natural (metálica/concreto)"],
    ["captacao_descida_natural", "Cobertura metálica: captação + descida natural"],
  ],
  NivelDPS: [
    ["IV", "DPS para NP IV"],
    ["III", "DPS para NP III"],
    ["II", "DPS para NP II"],
    ["I", "DPS para NP I"],
    ["melhor_I", "DPS melhor que NP I"],
  ],
  TipoSuperficie: [
    ["terra_concreto", "Agricultura, concreto"],
    ["marmore_ceramica", "Mármore, cerâmica"],
    ["brita_carpete", "Cascalho, tapete, carpete"],
    ["asfalto_madeira", "Asfalto, linóleo, madeira"],
  ],
  RiscoIncendio: [
    ["alto", "Risco alto"],
    ["normal", "Risco normal"],
    ["baixo", "Risco baixo"],
    ["sem_risco", "Sem risco de incêndio"],
  ],
  ZonaExplosao: [
    ["nenhuma", "Sem risco de explosão"],
    ["zona_0_20", "Zonas 0, 20 (e explosivos sólidos)"],
    ["zona_1_21", "Zonas 1, 21"],
    ["zona_2_22", "Zonas 2, 22"],
  ],
  TipoOcupacao: [
    ["hospital", "Hospital"],
    ["hotel", "Hotel"],
    ["escola", "Escola"],
    ["edificio_civico", "Edifício cívico / escritório"],
    ["entretenimento", "Entretenimento público"],
    ["igreja", "Igreja"],
    ["museu", "Museu"],
    ["industrial", "Industrial"],
    ["comercial", "Comercial"],
    ["outros", "Outros"],
  ],
  ProvidenciaIncendio: [
    ["nenhuma", "Nenhuma providência"],
    ["extintor", "Manuais (extintores, hidrantes, alarme, rotas de fuga)"],
    ["fixo_automatico", "Instalações fixas automáticas"],
  ],
  ProtecaoToquePasso: [
    ["nenhuma", "Nenhuma medida"],
    ["avisos", "Avisos de alerta"],
    ["isolacao", "Isolação elétrica"],
    ["malha_equipotencial", "Malha de equipotencialização do solo"],
    ["descida_natural", "Estrutura metálica/concreto como descida natural"],
    ["restricoes_fisicas", "Restrições físicas fixas"],
  ],
  ProtecaoToqueEntrada: [
    ["nenhuma", "Nenhuma medida"],
    ["avisos", "Avisos de alerta"],
    ["isolacao", "Isolação elétrica"],
    ["restricoes_fisicas", "Restrições físicas fixas"],
  ],
  InstalacaoLinha: [
    ["aerea", "Aérea"],
    ["enterrada", "Enterrada"],
    ["enterrada_malha", "Enterrada em malha de aterramento"],
  ],
  TipoLinha: [
    ["bt_sinal", "Energia (BT) ou sinal"],
    ["at_trafo", "Energia em AT (com transformador AT/BT)"],
  ],
  AmbienteLinha: [
    ["rural", "Rural"],
    ["suburbano", "Suburbano"],
    ["urbano", "Urbano"],
    ["urbano_alto", "Urbano com edifícios > 20 m"],
  ],
  TipoLinhaExterna: [
    ["aerea_nao_blindada", "Aérea não blindada"],
    ["subterranea_nao_blindada", "Enterrada não blindada"],
    ["energia_neutro_multiaterrado", "Energia com neutro multiaterrado"],
    ["subterranea_blindada_nao_interligada", "Enterrada blindada, blindagem não interligada"],
    ["aerea_blindada_nao_interligada", "Aérea blindada, blindagem não interligada"],
    ["blindada_interligada", "Blindada, blindagem interligada ao barramento"],
    ["eletroduto_metalico", "Cabo em eletroduto/tubo metálico interligado"],
    ["fibra_optica", "Sem linha externa (fibra óptica / sistema independente)"],
    ["interface_isolante", "Interfaces isolantes (NBR 5419-4)"],
  ],
  CategoriaLinha: [
    ["energia", "Linha de energia"],
    ["sinal", "Linha de sinal"],
  ],
  ClasseBlindagemRS: [
    ["nao_blindada", "Não blindada / blindagem não interligada"],
    ["rs_5_20", "Blindada interligada, 5–20 Ω/km"],
    ["rs_1_5", "Blindada interligada, 1–5 Ω/km"],
    ["rs_ate_1", "Blindada interligada, ≤ 1 Ω/km"],
  ],
  FiacaoInterna: [
    ["laco_grande", "Não blindado, sem cuidado no roteamento (laço ≈ 50 m²) — K_S3 1,0"],
    ["laco_medio_25", "Não blindado, evitando grandes laços (≈ 25 m²) — K_S3 0,5"],
    ["laco_medio_10", "Não blindado, evitando laços médios (≈ 10 m²) — K_S3 0,2"],
    ["laco_pequeno", "Não blindado, evitando pequenos laços (≈ 0,5 m²) — K_S3 0,01"],
    ["blindado_conduto", "Blindado ou em conduto metálico — K_S3 0,0001"],
  ],
  RelevanciaAD: [
    ["estrutura_inteira", "Estrutura inteira"],
    ["parte_hmin", "Parte da estrutura (altura mínima)"],
    ["parte_hmax", "Parte da estrutura (altura máxima)"],
  ],
  PerigoEspecial: [
    ["sem_perigo", "Sem perigo especial (h_z = 1)"],
    ["panico_baixo", "Baixo pânico — ≤2 andares, ≤100 pessoas (h_z = 2)"],
    ["panico_medio", "Pânico médio — 100 a 1000 pessoas (h_z = 5)"],
    ["evacuacao_dificil", "Evacuação difícil — imobilizados, hospitais (h_z = 5)"],
    ["panico_alto", "Pânico alto — mais de 1000 pessoas (h_z = 10)"],
  ],
};

const K_S3_TABELA = {
  laco_grande: 1.0, laco_medio_25: 0.5, laco_medio_10: 0.2,
  laco_pequeno: 0.01, blindado_conduto: 0.0001,
};
export function ks3DeFiacao(key) { return K_S3_TABELA[key]; }

const H_Z_TABELA = {
  sem_perigo: 1.0, panico_baixo: 2.0, panico_medio: 5.0,
  evacuacao_dificil: 5.0, panico_alto: 10.0,
};
export function hzDePerigo(key) { return H_Z_TABELA[key]; }

function labelOf(enumName, value) {
  if (value === null || value === undefined) return "nenhum";
  const opts = ENUM_OPTIONS[enumName];
  if (!opts) return String(value);
  const hit = opts.find((o) => o[0] === value);
  return hit ? hit[1] : String(value);
}
export const rotulo = labelOf;

export const COMPONENTE_LABELS = {
  R_A: "Choque elétrico por descarga na estrutura (D1)",
  R_B: "Danos físicos por descarga na estrutura (D2)",
  R_C: "Falha de sistemas internos por descarga na estrutura (D3)",
  R_M: "Falha de sistemas internos por descarga próxima (D3)",
  R_U: "Choque elétrico por descarga em linha conectada (D1)",
  R_V: "Danos físicos por descarga em linha conectada (D2)",
  R_W: "Falha de sistemas por descarga em linha conectada (D3)",
  R_Z: "Falha de sistemas por descarga próxima de linha conectada (D3)",
};

let _uid = 1;
export function uid() { return `id${_uid++}`; }

export function defaultTrecho() {
  return { _id: uid(), L_L: 1000, rho: null, instalacao: null, ambiente: null, tipo: null };
}
export function defaultAdjacente() {
  return { L_J: 10, W_J: 10, H_J: 10, localizacao_J: "isolada" };
}
export function defaultLinha() {
  return {
    _id: uid(), nome: "Linha", tipo: "bt_sinal", categoria: "energia",
    instalacao: "aerea", ambiente: "rural", tipo_externa: "aerea_nao_blindada",
    classe_blindagem: "nao_blindada", nivel_eb: null,
    protecao_toque_entrada: "nenhuma", adjacente: null,
    trechos: [defaultTrecho()],
  };
}
export function defaultSistemaInterno() {
  return {
    _id: uid(), nome: "Sistema", U_W: null, K_S1: 1, K_S2: 1, K_S3: 1,
    K_S4: null, dps: null, em_zpr0a: false,
  };
}
export function defaultZona() {
  return {
    _id: uid(), nome: "Zona", superficie: "terra_concreto", n_z: 1, t_z: 8760,
    h_z: 1, relevancia_AD: "estrutura_inteira",
    c_z: null, c_a: null, c_b: null, c_c: null, c_s: null,
    medidas: { protecao_toque_passo: "nenhuma" },
    sistemas_internos: [],
  };
}
export function defaultEstrutura() {
  return {
    _id: uid(), nome: "Nova estrutura", L: 20, W: 15, H: 8,
    H_min: null, H_max: null, localizacao: "isolada",
    tipo_construcao: "robusta", risco_incendio: "normal",
    providencias_incendio: "nenhuma", ocupacao: "outros",
    zona_explosao: "nenhuma", risco_explosao: false, sistemas_criticos: false,
    nivel_spda: null, descida_natural: false, c_t: null, n_t: 1,
    // proposta: combinação de medidas avaliada e salva pelo engenheiro no
    // Estudo de Solução, sem sobrescrever os campos acima — usado quando a
    // instalação já existe e o "atual" precisa ficar preservado como está.
    proposta: null,
    zonas: [], linhas: [],
  };
}
export function defaultProjeto() {
  return {
    nome: "Novo projeto", cidade: "", N_G: 5, S_M: null,
    rt_override: null, ft_override: null, r4_representativo: false,
    identificacao: {
      titulo: null, cliente: null, endereco: null, responsavel: null,
      art: null, registro: null, norma: "ABNT NBR 5419-2", revisao: "2026",
      data: null, observacoes: null,
    },
    estruturas: [],
  };
}

// ---------------------------------------------------------------------
// Normalização de projeto carregado de JSON externo (mesmo formato salvo por
// salvarProjeto/model_dump_json da engine original, sem os _id internos da UI).
// Preenche _id em cada entidade aninhada e completa defaults ausentes.
// ---------------------------------------------------------------------
function normalizarSistema(s) {
  return { ...defaultSistemaInterno(), ...s, _id: uid() };
}
function normalizarZona(z) {
  const zz = { ...defaultZona(), ...z, _id: uid() };
  zz.medidas = { protecao_toque_passo: "nenhuma", ...(z.medidas || {}) };
  zz.sistemas_internos = (z.sistemas_internos || []).map(normalizarSistema);
  return zz;
}
function normalizarTrecho(t) {
  return { ...defaultTrecho(), ...t, _id: uid() };
}
function normalizarLinha(l) {
  const ll = { ...defaultLinha(), ...l, _id: uid() };
  ll.trechos = (l.trechos && l.trechos.length ? l.trechos : [defaultTrecho()]).map(normalizarTrecho);
  ll.adjacente = l.adjacente ? { ...defaultAdjacente(), ...l.adjacente } : null;
  return ll;
}
function normalizarEstrutura(est) {
  const e = { ...defaultEstrutura(), ...est, _id: uid() };
  e.zonas = (est.zonas || []).map(normalizarZona);
  e.linhas = (est.linhas || []).map(normalizarLinha);
  return e;
}
export function normalizarProjetoCarregado(raw) {
  if (!raw || typeof raw !== "object" || !Array.isArray(raw.estruturas)) {
    throw new Error('JSON inválido: esperado um objeto de projeto com a chave "estruturas".');
  }
  const p = { ...defaultProjeto(), ...raw };
  p.identificacao = { ...defaultProjeto().identificacao, ...(raw.identificacao || {}) };
  p.estruturas = raw.estruturas.map(normalizarEstrutura);
  return p;
}

// ---------------------------------------------------------------------
// Projeto de exemplo — porte do Teste.json (usado para popular a demo)
// ---------------------------------------------------------------------
export function exemploProjeto() {
  return JSON.parse(JSON.stringify({
    nome: "Projeto Teste Exaustivo SPDA",
    cidade: "Belo Horizonte",
    N_G: 5.0,
    S_M: 250000.0,
    rt_override: null,
    ft_override: null,
    r4_representativo: false,
    identificacao: {
      titulo: "Análise de Risco NBR 5419-2 — Projeto Teste",
      cliente: "Cliente Exemplo LTDA",
      endereco: "Rua das Descargas, 1000 - Belo Horizonte/MG",
      responsavel: null,
      art: "BR20260012345",
      registro: "CREA-MG 123456/D",
      norma: "ABNT NBR 5419-2",
      revisao: "2026",
      data: "2026-07-01",
      observacoes: "Projeto sintético para cobertura total de parâmetros do programa.",
    },
    estruturas: [
      {
        nome: "E1 Galpão Industrial (explosão zona 1/21, forma complexa)",
        L: 60.0, W: 40.0, H: 12.0, H_min: 8.0, H_max: 16.0,
        localizacao: "isolada", tipo_construcao: "robusta",
        risco_incendio: "alto", providencias_incendio: "fixo_automatico",
        ocupacao: "industrial", zona_explosao: "zona_1_21",
        risco_explosao: false, sistemas_criticos: false, nivel_spda: "I",
        descida_natural: false, c_t: 5000000.0, n_t: 200,
        zonas: [
          {
            nome: "Z1 Área de processo (L3+L4, 2 sistemas)",
            superficie: "terra_concreto", n_z: 30, t_z: 6000.0, h_z: 2.0,
            relevancia_AD: "parte_hmin",
            c_z: 2000000.0, c_a: 50000.0, c_b: 1500000.0, c_c: 400000.0, c_s: 800000.0,
            medidas: { protecao_toque_passo: "nenhuma" },
            sistemas_internos: [
              { nome: "S1 CLP/automação", U_W: 2.5, K_S1: 0.9, K_S2: 0.8, K_S3: 0.2, K_S4: null, dps: "I", em_zpr0a: false },
              { nome: "S2 Instrumentação (U_W desconhecido)", U_W: null, K_S1: 1.0, K_S2: 1.0, K_S3: 1.0, K_S4: 0.5, dps: null, em_zpr0a: true },
            ],
          },
          {
            nome: "Z4 Depósito (L4 sem L3, sem sistemas)",
            superficie: "asfalto_madeira", n_z: 5, t_z: 2000.0, h_z: 5.0,
            relevancia_AD: "parte_hmax",
            c_z: null, c_a: null, c_b: null, c_c: null, c_s: null,
            medidas: { protecao_toque_passo: "malha_equipotencial" },
            sistemas_internos: [],
          },
        ],
        linhas: [
          {
            nome: "L1 Energia BT aérea (adjacente isolada)",
            tipo: "bt_sinal", categoria: "energia", instalacao: "aerea",
            ambiente: "rural", tipo_externa: "aerea_nao_blindada",
            classe_blindagem: "nao_blindada", nivel_eb: null,
            protecao_toque_entrada: "nenhuma",
            adjacente: { L_J: 20.0, W_J: 15.0, H_J: 8.0, localizacao_J: "isolada" },
            trechos: [{ L_L: 800.0, rho: null, instalacao: null, ambiente: null, tipo: null }],
          },
          {
            nome: "L3 Energia multiaterrada (2 trechos)",
            tipo: "bt_sinal", categoria: "energia", instalacao: "enterrada_malha",
            ambiente: "urbano", tipo_externa: "energia_neutro_multiaterrado",
            classe_blindagem: "rs_1_5", nivel_eb: "III",
            protecao_toque_entrada: "isolacao", adjacente: null,
            trechos: [
              { L_L: 300.0, rho: null, instalacao: "aerea", ambiente: "rural", tipo: "bt_sinal" },
              { L_L: 500.0, rho: 500.0, instalacao: null, ambiente: null, tipo: null },
            ],
          },
        ],
      },
      {
        nome: "E2 Hospital (sistemas críticos)",
        L: 45.0, W: 30.0, H: 20.0, H_min: null, H_max: null,
        localizacao: "topo_colina", tipo_construcao: "simples",
        risco_incendio: "normal", providencias_incendio: "extintor",
        ocupacao: "hospital", zona_explosao: "nenhuma",
        risco_explosao: false, sistemas_criticos: true, nivel_spda: "II",
        descida_natural: false, c_t: 10000000.0, n_t: 500,
        zonas: [
          {
            nome: "Z2 UTI (evacuação difícil)",
            superficie: "marmore_ceramica", n_z: 40, t_z: 8760.0, h_z: 5.0,
            relevancia_AD: "estrutura_inteira",
            c_z: null, c_a: 20000.0, c_b: 3000000.0, c_c: 1000000.0, c_s: 2000000.0,
            medidas: { protecao_toque_passo: "avisos" },
            sistemas_internos: [
              { nome: "S3 Equipamentos UTI", U_W: 6.0, K_S1: 1.0, K_S2: 1.0, K_S3: 0.01, K_S4: null, dps: "II", em_zpr0a: false },
            ],
          },
          {
            nome: "Z3 Recepção (L3+L4)",
            superficie: "brita_carpete", n_z: 60, t_z: 5000.0, h_z: 1.0,
            relevancia_AD: "estrutura_inteira",
            c_z: 500000.0, c_a: null, c_b: null, c_c: null, c_s: null,
            medidas: { protecao_toque_passo: "isolacao" },
            sistemas_internos: [
              { nome: "S4 TI recepção", U_W: 4.0, K_S1: 1.0, K_S2: 1.0, K_S3: 1.0, K_S4: 0.8, dps: "III", em_zpr0a: false },
            ],
          },
        ],
        linhas: [
          {
            nome: "L2 Sinal subterrâneo (rho)",
            tipo: "at_trafo", categoria: "sinal", instalacao: "enterrada",
            ambiente: "suburbano", tipo_externa: "subterranea_nao_blindada",
            classe_blindagem: "rs_5_20", nivel_eb: "IV",
            protecao_toque_entrada: "avisos",
            adjacente: { L_J: 25.0, W_J: 18.0, H_J: 10.0, localizacao_J: "cercada_mesma_altura" },
            trechos: [{ L_L: 400.0, rho: 250.0, instalacao: null, ambiente: null, tipo: null }],
          },
          {
            nome: "L4 Sinal subterrâneo blindado",
            tipo: "at_trafo", categoria: "sinal", instalacao: "aerea",
            ambiente: "urbano_alto", tipo_externa: "subterranea_blindada_nao_interligada",
            classe_blindagem: "rs_ate_1", nivel_eb: "II",
            protecao_toque_entrada: "restricoes_fisicas",
            adjacente: { L_J: 30.0, W_J: 22.0, H_J: 6.0, localizacao_J: "cercada_mais_altos" },
            trechos: [{ L_L: 600.0, rho: null, instalacao: null, ambiente: null, tipo: null }],
          },
        ],
      },
      {
        nome: "E3 Residência",
        L: 12.0, W: 10.0, H: 6.0, H_min: null, H_max: null,
        localizacao: "cercada_mais_altos", tipo_construcao: "robusta",
        risco_incendio: "baixo", providencias_incendio: "nenhuma",
        ocupacao: "outros", zona_explosao: "nenhuma",
        risco_explosao: false, sistemas_criticos: false, nivel_spda: "nenhum",
        descida_natural: false, c_t: null, n_t: 4,
        zonas: [{
          nome: "Z6 Residência única", superficie: "marmore_ceramica",
          n_z: 4, t_z: 8760.0, h_z: 1.0, relevancia_AD: "estrutura_inteira",
          c_z: null, c_a: null, c_b: null, c_c: null, c_s: null,
          medidas: { protecao_toque_passo: "restricoes_fisicas" },
          sistemas_internos: [],
        }],
        linhas: [{
          nome: "L5 Rede BT aérea blindada",
          tipo: "bt_sinal", categoria: "energia", instalacao: "enterrada",
          ambiente: "rural", tipo_externa: "aerea_blindada_nao_interligada",
          classe_blindagem: "nao_blindada", nivel_eb: "I",
          protecao_toque_entrada: "nenhuma",
          adjacente: { L_J: 15.0, W_J: 12.0, H_J: 20.0, localizacao_J: "topo_colina" },
          trechos: [{ L_L: 1000.0, rho: null, instalacao: null, ambiente: null, tipo: null }],
        }],
      },
      {
        nome: "E4 Data Center (forma complexa)",
        L: 50.0, W: 35.0, H: 6.0, H_min: 4.0, H_max: 9.0,
        localizacao: "cercada_mesma_altura", tipo_construcao: "robusta",
        risco_incendio: "sem_risco", providencias_incendio: "fixo_automatico",
        ocupacao: "comercial", zona_explosao: "nenhuma",
        risco_explosao: false, sistemas_criticos: true, nivel_spda: "IV",
        descida_natural: false, c_t: 20000000.0, n_t: 300,
        zonas: [{
          nome: "Z5 Sala de servidores (L3+L4)",
          superficie: "terra_concreto", n_z: 20, t_z: 8760.0, h_z: 2.0,
          relevancia_AD: "parte_hmin",
          c_z: 8000000.0, c_a: 10000.0, c_b: 5000000.0, c_c: 3000000.0, c_s: 6000000.0,
          medidas: { protecao_toque_passo: "descida_natural" },
          sistemas_internos: [
            { nome: "S5 Servidores", U_W: 1.5, K_S1: 1.0, K_S2: 1.0, K_S3: 1.0, K_S4: null, dps: "melhor_I", em_zpr0a: false },
          ],
        }],
        linhas: [
          {
            nome: "L6 Sinal blindado interligado",
            tipo: "bt_sinal", categoria: "sinal", instalacao: "aerea",
            ambiente: "suburbano", tipo_externa: "blindada_interligada",
            classe_blindagem: "rs_5_20", nivel_eb: null,
            protecao_toque_entrada: "avisos", adjacente: null,
            trechos: [{ L_L: 350.0, rho: null, instalacao: null, ambiente: null, tipo: null }],
          },
          {
            nome: "L7 Energia eletroduto metálico",
            tipo: "at_trafo", categoria: "energia", instalacao: "enterrada_malha",
            ambiente: "urbano", tipo_externa: "eletroduto_metalico",
            classe_blindagem: "rs_1_5", nivel_eb: "IV",
            protecao_toque_entrada: "isolacao", adjacente: null,
            trechos: [{ L_L: 450.0, rho: null, instalacao: null, ambiente: null, tipo: null }],
          },
        ],
      },
      {
        nome: "E5 Subestação (explosão via bool legado)",
        L: 20.0, W: 20.0, H: 5.0, H_min: null, H_max: null,
        localizacao: "isolada", tipo_construcao: "robusta",
        risco_incendio: "alto", providencias_incendio: "extintor",
        ocupacao: "industrial", zona_explosao: "nenhuma",
        risco_explosao: true, sistemas_criticos: false, nivel_spda: "III",
        descida_natural: false, c_t: null, n_t: 10,
        zonas: [{
          nome: "Z7 Pátio", superficie: "brita_carpete", n_z: 2, t_z: 1000.0, h_z: 1.0,
          relevancia_AD: "estrutura_inteira",
          c_z: null, c_a: null, c_b: null, c_c: null, c_s: null,
          medidas: { protecao_toque_passo: "nenhuma" },
          sistemas_internos: [],
        }],
        linhas: [
          {
            nome: "L8 Sinal fibra óptica",
            tipo: "bt_sinal", categoria: "sinal", instalacao: "aerea",
            ambiente: "urbano_alto", tipo_externa: "fibra_optica",
            classe_blindagem: "rs_ate_1", nivel_eb: "II",
            protecao_toque_entrada: "restricoes_fisicas", adjacente: null,
            trechos: [{ L_L: 700.0, rho: null, instalacao: null, ambiente: null, tipo: null }],
          },
          {
            nome: "L9 Energia interface isolante",
            tipo: "bt_sinal", categoria: "energia", instalacao: "enterrada",
            ambiente: "rural", tipo_externa: "interface_isolante",
            classe_blindagem: "nao_blindada", nivel_eb: "III",
            protecao_toque_entrada: "nenhuma", adjacente: null,
            trechos: [{ L_L: 900.0, rho: null, instalacao: null, ambiente: null, tipo: null }],
          },
        ],
      },
      {
        nome: "E6 Escola (NP I descida natural, sem linhas)",
        L: 40.0, W: 25.0, H: 10.0, H_min: null, H_max: null,
        localizacao: "topo_colina", tipo_construcao: "simples",
        risco_incendio: "normal", providencias_incendio: "nenhuma",
        ocupacao: "escola", zona_explosao: "nenhuma",
        risco_explosao: false, sistemas_criticos: false,
        nivel_spda: "I_descida_natural", descida_natural: true,
        c_t: null, n_t: 300,
        zonas: [{
          nome: "Z8 Salas de aula", superficie: "terra_concreto",
          n_z: 200, t_z: 3000.0, h_z: 1.0, relevancia_AD: "estrutura_inteira",
          c_z: null, c_a: null, c_b: null, c_c: null, c_s: null,
          medidas: { protecao_toque_passo: "avisos" },
          sistemas_internos: [],
        }],
        linhas: [],
      },
      {
        nome: "E7 Depósito (mínimo, sem linhas)",
        L: 8.0, W: 6.0, H: 3.0, H_min: null, H_max: null,
        localizacao: "cercada_mais_altos", tipo_construcao: "simples",
        risco_incendio: "baixo", providencias_incendio: "extintor",
        ocupacao: "outros", zona_explosao: "nenhuma",
        risco_explosao: false, sistemas_criticos: false,
        nivel_spda: "captacao_descida_natural", descida_natural: false,
        c_t: null, n_t: 2,
        zonas: [{
          nome: "Z9 Galpão único", superficie: "asfalto_madeira",
          n_z: 1, t_z: 500.0, h_z: 1.0, relevancia_AD: "estrutura_inteira",
          c_z: null, c_a: null, c_b: null, c_c: null, c_s: null,
          medidas: { protecao_toque_passo: "nenhuma" },
          sistemas_internos: [],
        }],
        linhas: [],
      },
    ],
  }));
}
