# Requisitos Não Funcionais - Northwind Data Pipeline

Este documento estabelece as metas de qualidade, desempenho e confiabilidade do Northwind Data Pipeline, baseando-se na especificação do problema (`spec/00_problem.md`) e nos requisitos funcionais (`documents/01_functional_requirements.md`), seguindo o padrão ISO 25010.

## 1. Adequação Funcional
### RNF-01 - Completude dos Dados
- **Descrição:** O sistema deve garantir que 100% dos registros válidos presentes no CSV sejam carregados no ClickHouse.
- **Stakeholder impactado:** Time de Dados, Negócio.
- **Fluxo crítico:** Carga Idempotente.
- **SLI:** Percentual de registros carregados vs. registros válidos no CSV.
- **SLO:** 100%.
- **Unidade:** Percentual.
- **Janela:** Por lote de carga.
- **Fonte:** Logs do ETL e contagem de linhas no ClickHouse.
- **Prioridade:** Must Have.
- **Risco mitigado:** Perda de dados durante o processamento.

---

## 2. Eficiência de Desempenho
### RNF-02 - Vazão de Processamento (Throughput)
- **Descrição:** O pipeline deve ser capaz de processar 100.000 pedidos em menos de 2 horas.
- **Stakeholder impactado:** Time de Dados, SRE.
- **Fluxo crítico:** Processamento ETL.
- **SLI:** Tempo total de processamento do lote diário.
- **SLO:** < 120 minutos.
- **Unidade:** Minutos.
- **Janela:** Diária.
- **Fonte:** Métricas de telemetria do container ETL.
- **Prioridade:** Must Have.
- **Risco mitigado:** Atraso na visibilidade analítica.

### RNF-09 - Escalabilidade Horizontal
- **Descrição:** O design do ETL deve permitir a execução de múltiplas instâncias em paralelo de forma stateless para acelerar o processamento.
- **Stakeholder impactado:** SRE, Time de Dados.
- **Fluxo crítico:** Processamento ETL.
- **SLI:** Redução linear do tempo de processamento ao dobrar workers.
- **SLO:** > 80% de eficiência na paralelização.
- **Unidade:** Percentual.
- **Janela:** Por teste de carga / batch volumoso.
- **Fonte:** Métricas de orquestração Docker.
- **Prioridade:** Could Have.
- **Risco mitigado:** Gargalo computacional devido a picos inesperados de dados.

---

## 3. Compatibilidade
### RNF-03 - Interoperabilidade com MinIO e ClickHouse
- **Descrição:** O ETL deve utilizar protocolos padrão (S3 API e HTTP/Native ClickHouse) para garantir compatibilidade sem modificações no código em caso de troca de provedor.
- **Stakeholder impactado:** Plataforma / SRE.
- **Fluxo crítico:** Ingestão e Carga.
- **SLI:** Taxa de sucesso de conexão com os serviços.
- **SLO:** 100%.
- **Unidade:** Percentual.
- **Janela:** Contínua.
- **Fonte:** Logs de erro de conexão.
- **Prioridade:** Should Have.
- **Risco mitigado:** Lock-in técnico e falhas de integração.

---

## 4. Usabilidade
### RNF-04 - Tempo de Resposta do Dashboard
- **Descrição:** O dashboard Streamlit deve carregar os KPIs principais em menos de 5 segundos.
- **Stakeholder impactado:** Consumidores dos dashboards, Negócio.
- **Fluxo crítico:** Visualização Analítica.
- **SLI:** Tempo de carregamento da página (First Contentful Paint).
- **SLO:** < 5 segundos.
- **Unidade:** Segundos.
- **Janela:** Por acesso.
- **Fonte:** Logs do Streamlit / Browser DevTools.
- **Prioridade:** Should Have.
- **Risco mitigado:** Baixa adoção da ferramenta analítica.

---

## 5. Confiabilidade
### RNF-05 - Detecção Proativa de Falhas (Observabilidade)
- **Descrição:** 100% das falhas críticas (ex: erro de conexão, esquema inválido) devem gerar um alerta/log estruturado imediatamente.
- **Stakeholder impactado:** Plataforma / SRE.
- **Fluxo crítico:** Telemetria.
- **SLI:** Taxa de falhas capturadas por logs/métricas vs. falhas ocorridas.
- **SLO:** 100%.
- **Unidade:** Percentual.
- **Janela:** Tempo real.
- **Fonte:** Logs estruturados.
- **Prioridade:** Must Have.
- **Risco mitigado:** "Sofrimento silencioso" do sistema.

### RNF-10 - Disponibilidade da Camada Analítica
- **Descrição:** Os dados carregados no ClickHouse e o Dashboard devem se manter consultáveis, suportando falhas temporárias do componente de ingestão.
- **Stakeholder impactado:** Negócio, Consumidores dos dashboards.
- **Fluxo crítico:** Camada Analítica.
- **SLI:** Uptime de resposta HTTP 200 do Streamlit e ClickHouse.
- **SLO:** > 99.5%.
- **Unidade:** Percentual.
- **Janela:** Mensal.
- **Fonte:** Monitoramento de healthcheck (Ping).
- **Prioridade:** Must Have.
- **Risco mitigado:** Indisponibilidade de acesso a dados históricos.

### RNF-11 - Retenção de Dados Brutos (Capacidade/Confiabilidade)
- **Descrição:** Os arquivos originais ingeridos no MinIO devem ser mantidos por 1 semana (7 dias) para viabilizar reprocessamento de lotes recentes e expurgados após este prazo para poupar storage.
- **Stakeholder impactado:** Plataforma / SRE.
- **Fluxo crítico:** Armazenamento.
- **SLI:** Presença de arquivos com idade entre 0 e 7 dias; Ausência de arquivos > 7 dias.
- **SLO:** 100%.
- **Unidade:** Percentual.
- **Janela:** Auditoria diária.
- **Fonte:** Listagem de objetos do MinIO.
- **Prioridade:** Must Have.
- **Risco mitigado:** Esgotamento de disco e perda de capacidade de auditoria de curto prazo.

---

## 6. Segurança
### RNF-06 - Integridade na Gravação (Staging Area)
- **Descrição:** Nenhuma carga deve ser feita diretamente na tabela de produção sem passar por uma tabela de staging para validação atômica.
- **Stakeholder impactado:** SRE, Time de Dados.
- **Fluxo crítico:** Carga Idempotente.
- **SLI:** Percentual de cargas que ignoram o staging.
- **SLO:** 0%.
- **Unidade:** Percentual.
- **Janela:** Por carga.
- **Fonte:** Auditoria de queries no ClickHouse.
- **Prioridade:** Must Have.
- **Risco mitigado:** Corrupção da tabela analítica final.

---

## 7. Manutenibilidade
### RNF-07 - Documentação de Decisões (ADR)
- **Descrição:** Todas as decisões arquiteturais e trade-offs devem estar registrados no README.md.
- **Stakeholder impactado:** Time de Dados, SRE.
- **Fluxo crítico:** Todos.
- **SLI:** Existência de justificativa para tecnologias adotadas/descartadas.
- **SLO:** 100%.
- **Unidade:** Binário (Sim/Não).
- **Janela:** Vitalícia do projeto.
- **Fonte:** Revisão do repositório.
- **Prioridade:** Must Have.
- **Risco mitigado:** Perda de contexto técnico (Dívida técnica).

---

## 8. Portabilidade
### RNF-08 - Padronização via Docker
- **Descrição:** O sistema deve ser executável em qualquer ambiente Linux/macOS com Docker e Docker Compose instalado, sem necessidade de configuração manual de libs no host.
- **Stakeholder impactado:** Plataforma / SRE.
- **Fluxo crítico:** Portabilidade.
- **SLI:** Taxa de sucesso de `docker-compose up` em ambiente limpo.
- **SLO:** 100%.
- **Unidade:** Percentual.
- **Janela:** Por deploy/setup.
- **Fonte:** Testes de CI/CD.
- **Prioridade:** Must Have.
- **Risco mitigado:** Inconsistência entre ambientes ("Na minha máquina funciona").

---

## Tabela Consolidada de RNFs

| ID | Atributo ISO 25010 | SLI | SLO | Unidade | Janela | Fonte | Prioridade |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RNF-01** | Adequação Funcional | Taxa de carregamento de registros válidos | 100% | % | Por Lote | Logs/DB | Must Have |
| **RNF-02** | Eficiência | Tempo de processamento do lote | < 120 | min | Diária | Telemetria | Must Have |
| **RNF-03** | Compatibilidade | Sucesso de conexão (protocolos padrão) | 100% | % | Contínua | Logs | Should Have |
| **RNF-04** | Usabilidade | Tempo de carga do Dashboard | < 5 | seg | Por acesso | Streamlit | Should Have |
| **RNF-05** | Confiabilidade | Falhas capturadas vs. ocorridas | 100% | % | Real-time | Logs | Must Have |
| **RNF-06** | Segurança | Cargas ignorando staging | 0% | % | Por carga | Auditoria | Must Have |
| **RNF-07** | Manutenibilidade | Decisões registradas no README | 100% | Binário | Projeto | Repo | Must Have |
| **RNF-08** | Portabilidade | Sucesso do Docker Compose | 100% | % | Deploy | CI/CD | Must Have |
| **RNF-09** | Eficiência | Escala linear de performance via paralelismo | > 80% | % | Carga | Docker Metrics | Could Have |
| **RNF-10** | Confiabilidade | Uptime do Analytics (Streamlit/ClickHouse) | > 99.5%| % | Mensal | Ping | Must Have |
| **RNF-11** | Confiabilidade | Arquivos originais expurgados após 7 dias | 100% | % | Diária | MinIO audit | Must Have |

## Premissas
1. A infraestrutura onde o Docker será executado possui recursos (CPU/RAM) suficientes para suportar o ClickHouse e o ETL simultaneamente.
2. O MinIO e o ClickHouse estarão na mesma rede Docker para minimizar latência de rede interna.

## Ambiguidades
1. **Segurança de Acesso:** Não foi especificado se o acesso ao MinIO/ClickHouse exige autenticação forte ou se chaves simples em ambiente isolado são suficientes.

## Riscos Residuais
1. **Burst de Carga:** Se o volume exceder significativamente 100k pedidos, o SLO de 120 minutos (RNF-02) pode ser violado sem escalonamento horizontal adequado.
2. **Indisponibilidade do ClickHouse:** O pipeline não prevê comportamento de "backoff" ou "retry" em caso de indisponibilidade temporária do banco.
