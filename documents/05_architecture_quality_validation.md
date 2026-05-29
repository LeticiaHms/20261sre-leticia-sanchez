# Validação de Qualidade Arquitetural e RNFs

Este documento descreve as validações e implementações de Requisitos Não Funcionais (RNFs) realizadas na arquitetura do Northwind Data Pipeline. Tudo o que está descrito aqui foi **efetivamente implementado no código-fonte**.

## 1. Requisitos Não Funcionais (RNFs) Atendidos

| ID | Requisito Não Funcional | Tática de Bass Utilizada | Meta Mensurável | Status de Implementação |
| :--- | :--- | :--- | :--- | :--- |
| **RNF-01** | **Confiabilidade:** Tolerância a falhas temporárias do banco analítico. | **Retry (Fault Recovery)** | Suportar até 3 falhas transitórias de conexão com backoff exponencial. | Implementado via decorator `@retry_db_operation` e aplicado na Camada Silver e Gold. |
| **RNF-02** | **Desempenho (Throughput):** Prevenção de gargalos de memória na ingestão de arquivos. | **Chunking / Resource Pooling** | Uso máximo da memória estabilizado, ingerindo arquivos em chunks de 10.000 linhas. | Implementado no `BronzeLoader` (`chunksize=10000`). |
| **RNF-03** | **Disponibilidade / Desempenho:** O frontend deve suportar picos de usuários (leituras pesadas) sem derrubar o ClickHouse. | **Caching** | P95 < 500ms com 50 VUs (Usuários Virtuais) simultâneos. | Implementado no `app.py` usando `@st.cache_data(ttl=60)` para as queries do ClickHouse. |
| **RNF-04** | **Observabilidade:** Monitoramento do tempo de execução de cada pipeline. | **Instrumentação (Metrics/Logging)** | Todo ciclo de batch deve registrar os milissegundos totais decorridos. | Implementado no `BatchManager` (registro da variável `elapsed_ms` em logs estruturados). |
| **RNF-05** | **Robustez (Prevenção de Falhas):** O sistema não deve falhar devido a linhas completamente vazias injetadas acidentalmente nos CSVs. | **Data Validation / Filtering** | 0 falhas decorrentes de instâncias DataFrame vazias. | Implementado no `BronzeLoader` (`df_chunk.dropna(how='all')`). |

---

## 2. Análise ATAM Aplicada

A tabela abaixo reflete as decisões arquiteturais reais tomadas e ativas no código:

| Cenário | Atributo de Qualidade | Sensibilidade | Trade-off | Risco | Decisão Arquitetural (Implementada) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| O ClickHouse falha por 5s devido a um reinício do container durante o processamento Silver/Gold. | Confiabilidade / Disponibilidade | Conexão HTTP/Native DB | **Confiabilidade vs Latência:** O retry atrasa o pipeline, mas garante a entrega. | Pipeline crachar e exigir reprocessamento manual. | Criação do decorator `@retry_db_operation(max_retries=3, backoff_factor=2)` no código. |
| Dashboard recebe 50 acessos simultâneos solicitando a evolução de receita. | Desempenho (Latência) | Camada ClickHouse Queries | **Performance vs Consistência:** Dados no dashboard podem ter até 60s de atraso em troca de velocidade. | Gargalo de IO e indisponibilidade do Streamlit. | Adição da anotação de Caching (`@st.cache_data(ttl=60)`) no conector. |
| O arquivo CSV de ingestão possui 500 mil linhas, excedendo a RAM do container ETL. | Desempenho (Throughput) | Leitura do Pandas na Ingestão (Bronze) | **Throughput vs Latência:** O processamento em chunks consome menos RAM, mas pode levar levemente mais tempo por IOPS repetido. | *Out Of Memory* (OOM) Kill pelo Docker. | Leitura particionada (`pd.read_csv(chunksize=10000)`). |
| Equipe de SRE precisa saber qual etapa ou qual batch demora mais ao longo do tempo. | Observabilidade | Log do Pipeline | **Observabilidade vs Complexidade:** Enriquecimento do log aumenta a clareza, mas exige gestão manual do tempo. | Falta de baselines para capacity planning. | Cálculo explícito de `elapsed_ms` via `time.time()` injetado na lib `structlog` (`BatchManager`). |

---

## 3. Pontos de Sensibilidade (Sensitivity Points) Consolidados

| Ponto Sensível | Componente Afetado | Impacto | RNF Afetado | Mitigação Implementada no Código |
| :--- | :--- | :--- | :--- | :--- |
| Conexão ClickHouse | `SilverTransformer`, `GoldAggregator` | Falha na agregação (UNKNOWN_TABLE, timeouts). | Confiabilidade | Decorator `@retry_db_operation` adicionado em volta das funções `transform_and_load` e `aggregate_and_load`. |
| Leitura Pandas (RAM) | `BronzeLoader` | Container Crash (OOM). | Desempenho | Processamento alterado para laço `for chunk in pd.read_csv` mitigando pico de RAM. |
| WebSockets do Streamlit | `app.py` (Frontend) | Degradação da latência quando em concorrência. | Disponibilidade | Decorator `@st.cache_data` impede múltiplas execuções redundantes da mesma query no DB. |
| Sujeira Inesperada (CSV) | `BronzeLoader` | Exceções de tipagem ou falhas no JSON. | Robustez | Remoção de linhas vazias com `dropna(how='all')` pré-conversão. |

---

## 4. Estratégia de Testes de Performance (K6)

Para comprovar a estabilidade sob carga das decisões listadas (principalmente o Cache), implementamos scripts de testes com **K6**.

**Localização dos Scripts:** `/tests/performance/`
**Execução:** Expostos via `package.json` (Ex: `npm run test:load`)

### Testes Implementados e Métricas/Critérios:

1. **Load Test (`load-test.js`):**
   * **Objetivo:** Simular uso contínuo no pico normal.
   * **Carga:** Ramp-up para 50 VUs (Usuários Virtuais) mantido por 30s.
   * **Critério de Aprovação:** `p(95) < 500ms` e taxa de erro `< 1%`.
   * **Validação RNF:** Valida a eficiência do Cache implementado (RNF-03).

2. **Stress Test (`stress-test.js`):**
   * **Objetivo:** Identificar ponto de degradação e quebra.
   * **Carga:** Picos forçados de 100 para 200 VUs em escadas.
   * **Critério de Aprovação:** `p(95) < 2000ms` (aceita-se degradação) e erro `< 5%`.
   * **Validação RNF:** Demonstra limite físico do container do Dashboard.

3. **Spike Test (`spike-test.js`):**
   * **Objetivo:** Validar a resiliência a eventos súbitos (ex: envio de e-mail marketing).
   * **Carga:** Salto instantâneo de 20 para 300 VUs em 10s.
   * **Critério de Aprovação:** Taxa de erro mantida `< 5%` sem indisponibilidade total.
   * **Validação RNF:** Teste de robustez da camada web/caching.

4. **Endurance Test (`endurance-test.js`):**
   * **Objetivo:** Identificar vazamentos de memória (Memory Leaks) sob carga contínua.
   * **Carga:** 50 VUs sustentados de forma plana por 2 minutos (tempo reduzido para lab).
   * **Critério de Aprovação:** `p(95) < 500ms` sem aumento progressivo do tempo com o passar dos minutos.
   * **Validação RNF:** Confirma estabilidade estrutural (RNF-03).
