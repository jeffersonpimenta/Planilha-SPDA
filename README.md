# Planilha-SPDA

Planilha para análise do risco de descargas atmosféricas segundo a **ABNT NBR 5419-2:2026**


# Importante

- O autor não se responsabiliza por erros decorrentes do uso da tabela
- O laudo de SPDA precisa ser acompanhado de uma ART assinada exclusivamente por engenheiro habilitado e qualificado
- Todo estudo deve ser realizado após a revisão da norma atualizada
- Todos os resultados oriundos da tabela devem ser checados manualmente

# Funcionamento

- A tabela considera duas áreas de risco Z0 e Z1, respectivamente fora e dentro da estrutura.

- O risco R4 (perda econômica) na região Z0 está presente e o risco R1 (perda de vida humana) não está presente.

- O risco R4 (perda econômica) na região Z1 não está presente e o risco R1 (perda de vida humana) está presente.

- Os parâmetros a serem alterados exibem uma opção de lista suspensa
![alt text](https://github.com/jeffersonpimenta/Planilha-SPDA/blob/master/Imagens/imagem1.JPG)

- Os resultados acima dos valores toleráveis são destacados em vermelho
![alt text](https://github.com/jeffersonpimenta/Planilha-SPDA/blob/master/Imagens/imagem2.JPG)

- A planilha relatório contem o estudo inicial, a planilha estudo contem a solução para adequação da estrutura e a planilha dados contem todas as tabelas necessárias

![alt text](https://github.com/jeffersonpimenta/Planilha-SPDA/blob/master/Imagens/imagem3.JPG)

- Uma vez inadequada, um estudo de medidas pode ser adotado
![alt text](https://github.com/jeffersonpimenta/Planilha-SPDA/blob/master/Imagens/imagem4.JPG)

- O memorial de cálculo pode ser diretamente impresso
![alt text](https://github.com/jeffersonpimenta/Planilha-SPDA/blob/master/Imagens/imagem5.JPG)

![alt text](https://github.com/jeffersonpimenta/Planilha-SPDA/blob/master/Imagens/imagem6.JPG)


# Resumo das mudanças ABNT NBR 5419-2:2015 para a versão 2026

A tabela abaixo resume as principais alterações normativas incorporadas nesta versão da planilha.

| Tema | NBR 5419-2:2015 | NBR 5419-2:2026 |
|---|---|---|
| **Risco R2** (perda de serviço ao público) | Risco obrigatório, com perdas L2 e risco tolerável R_T = 10⁻³ | **Eliminado.** Substituído pelo conceito de **Frequência de Danos F** (Seção 7), com F_T = 0,1/ano para sistemas críticos e 1/ano para não-críticos |
| **Risco R4** (perda econômica) | Risco normativo, obrigatório quando aplicável | **Informativo e opcional** (Anexo D). R_T não é normalizado (sugestão 10⁻³) |
| **Frequência de Danos F** | Não existia | **Nova Seção 7:** F = F_B + F_C + F_M + F_V + F_W + F_Z (ainda em implementação) |
| **Tabela B.1 — P_TA** (medidas contra tensão de toque/passo) | 5 opções | **6 opções** — adicionadas "Malha de equipotencialização do solo" (10⁻²) e "Estrutura metálica/concreto armado como descida natural" (10⁻³) |
| **Tabela B.2 — P_B** (danos físicos por SPDA) | 6 linhas (não protegida + NP I–IV) | **9 linhas** — adicionadas opções para SPDA NP I + descida natural (P_B = 0,01) e cobertura metálica como captação natural (P_B = 0,001) |
| **Tabela B.3 — P_SPD** (DPS coordenado) | 6 opções | Adicionada opção **"Melhor que NP I"** (P_SPD = 0,005–0,001) para DPS de desempenho superior |
| **Tabela B.5 — K_S3** (roteamento interno) | 4 opções | **5 opções** — adicionado nível intermediário "Evitar grandes laços" (K_S3 = 0,5) entre "sem preocupação" (1) e "evitar laços médios" (0,2) |
| **Tabela A.2 — C_I** (instalação da linha) | Fator fixo de 0,01 para linha em malha | Incluída **nota normativa**: para solos com ρ > 400 Ω·m, usar A_L = 0,6 × √ρ × L_L |
| **Tabela B.4 — C_LD/C_LI** | 6 tipos de linha | Reformulada com **9 tipos**, incluindo cabos de proteção contra descargas e interfaces isolantes |
| **Tabela C.8 — L2** | Valores de perda L2 por tipo de estrutura | **Removida** (perda L2 não existe mais) |
| **Perda L_FT** | L_F apenas | **L_FT = L_F + L_E** (opcional, quando danos envolvem estruturas vizinhas ou meio ambiente) |
| **Densidade N_G** | Mapa isoceráunico / valores calculados por T_d | **Anexo F normativo** — valores de N_G por município, obtidos de dados do satélite TRMM/LIS (1998–2013) tratados pelo INPE. Dados de outras fontes são **proibidos** |
| **Período de transição** | — | Norma vigente a partir de **10/03/2026** (versão corrigida 02/04/2026), com 180 dias de transição para adequação |


# Atualização para ABNT NBR 5419-2:2026

O arquivo "Análise de Risco - Versão 2026.xlsx" atualiza a planilha da edição **2015** para a edição **2026** da norma. As modificações
seguem a norma publicada em 10/03/2026 (versão corrigida 02/04/2026) e estão descritas abaixo.

## Eliminação do Risco R2

O risco R2 (perda de serviço ao público) foi **eliminado** da norma 2026 e substituído pelo conceito
de **Frequência de Danos F** (Seção 7 da norma). Na planilha:

- A **Tabela 5 (Perdas L2)** da aba *Relatório* foi removida, com nota explicativa no lugar.
- As linhas de **R2** nas tabelas de análise final (*Relatório* e *Estudo*) foram marcadas como
  substituídas, com referência à Seção 7 da NBR 5419-2:2026.
- Inclusão da análise frequência de danos F.

## Atualizações nas tabelas de lookup (aba *Dados*)

| Tabela | Mudança |
|--------|---------|
| **B.1 — P_TA** | Adicionadas duas novas opções de medida de proteção: "Malha de equipotencialização do solo" (1×10⁻²) e "Estrutura metálica contínua ou concreto armado atuando como descida natural" (1×10⁻³). A tabela passa de 5 para **6 opções**. |
| **B.2 — P_B** | Adicionadas duas novas linhas para SPDA com captação NPI + descida natural (P_B = 0,01) e cobertura metálica + descida natural (P_B = 0,001). |
| **B.3 — P_SPD** | Adicionada opção "Melhor que Nível I" com P_SPD = 0,005–0,001. |
| **B.5 — K_S3** | Adicionada opção intermediária "Evitar grandes laços" (K_S3 = 0,5), entre "sem preocupação" (1) e "evitar laços médios" (0,2). A tabela passa de 4 para **5 opções**. |
| **A.2 — C_I** | Adicionada nota normativa: para solos com resistividade ρ > 400 Ω·m, a área de exposição equivalente de linha enterrada deve ser calculada como A_L = 0,6 × √ρ × L_L (conforme Nota 1 da Tabela A.2). |
| **C.8 — L2** | Tabela removida, pois a perda L2 não existe mais na norma 2026. |


# Licença

<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Licença Creative Commons" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br />Este obra está licenciado com uma Licença <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Atribuição-NãoComercial-CompartilhaIgual 4.0 Internacional</a>.

- Você é livre para compartilhar e modificar, entretanto deve dar os créditos do autor, não pode haver fins comerciais e todo material derivado deste deve ser registrado sob a mesma licença.
- Os infratores estarão sujeitos às penas cominadas no código penal brasileiro.
