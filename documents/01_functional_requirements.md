# Requisitos Funcionais - Northwind Data Pipeline

Este documento detalha as capacidades comportamentais do sistema Northwind Data Pipeline, estruturado para processamento em **Batch** e seguindo a **Arquitetura Medalhão**, conforme derivado da especificação do problema e diretrizes de design.

## RF-01 - Validar Integridade e Esquema do CSV (Inbound)

### Descrição
O sistema deve validar o esquema, o encoding e a integridade estrutural dos arquivos CSV recebidos em lote (batch) antes de qualquer processamento.

### Critérios de Aceitação
- Rejeitar arquivos com colunas incorretas ou corrompidos.
- Registrar log detalhado da falha (sem notificações externas).

---

## RF-02 - Persistência em Landing Zone (Storage)

### Descrição
O sistema deve persistir os arquivos brutos recebidos no MinIO, servindo como a fonte imutável para a camada Bronze.

### Critérios de Aceitação
- Garantir que o dado bruto permaneça inalterado.
- Confirmar gravação via log de sucesso.

---

## RF-03 - Camada Bronze (Raw Data no DB)

### Descrição
O sistema deve carregar os dados brutos do MinIO para tabelas **Bronze** no ClickHouse sem transformações complexas, preservando o estado original do arquivo.

### Stakeholders
- Time de Dados

### Fluxo Crítico Relacionado
- Processamento Batch (Ingestão Bronze)

### Prioridade
Must Have

### Critérios de Aceitação
- Réplica exata das colunas do CSV no ClickHouse.
- Inclusão de metadados de auditoria básica (timestamp de carga).

---

## RF-04 - Camada Silver (Cleaned & Unified)

### Descrição
O sistema deve ler os dados da camada Bronze, realizar a sanitização (RF-09), unificar as entidades `Orders` e `Order Details` e aplicar a lógica de negócio, persistindo na camada **Silver**.

### Stakeholders
- Time de Dados

### Fluxo Crítico Relacionado
- Transformação Medalhão

### Prioridade
Must Have

### Critérios de Aceitação
- Dados limpos (trim, tratamento de nulos).
- Join realizado entre pedidos e itens.
- Injeção de Audit Trail (RF-10).

---

## RF-05 - Camada Gold (Business/Aggregated)

### Descrição
O sistema deve gerar agregados de negócio a partir da camada Silver e persistir na camada **Gold**, otimizada para consumo pelo dashboard.

### Stakeholders
- Operação Northwind (negócio)
- Consumidores dos dashboards

### Fluxo Crítico Relacionado
- Camada Analítica Final

### Prioridade
Must Have

### Critérios de Aceitação
- Tabelas com KPIs agregados (ex: vendas por dia, por categoria).
- Performance de consulta otimizada para o Streamlit.

---

## RF-06 - Carga Idempotente em Camadas

### Descrição
O sistema deve garantir que o processamento batch de um mesmo lote não gere duplicidades em nenhuma das camadas (Bronze, Silver ou Gold).

### Critérios de Aceitação
- Uso de `ReplacingMergeTree` ou lógica de delete/insert atômica.
- Verificação via logs de reconciliação.

---

## RF-07 - Monitoramento via Logs Estruturados

### Descrição
Toda a saúde do pipeline, anomalias e estatísticas de carga batch devem ser acompanhadas exclusivamente através de logs estruturados (JSON). Nenhuma notificação externa (e-mail/Slack) será utilizada.

### Stakeholders
- Plataforma / SRE

### Prioridade
Must Have

### Critérios de Aceitação
- Logs em todos os estágios do modelo Medalhão.
- Níveis de log adequados (INFO para progresso, ERROR/CRITICAL para anomalias).

---

## RF-08 - Mecanismo de Reprocessamento (Replay Batch)

### Descrição
O sistema deve permitir disparar o reprocessamento de um lote específico a partir da Landing Zone, reconstruindo as camadas Bronze, Silver e Gold conforme necessário.

---

## RF-09 - Sanitização e Padronização (Camada Silver)
*(Mantido conforme definição anterior, agora focado na transição Bronze -> Silver)*

---

## RF-10 - Registro de Linhagem (Audit Trail)
*(Mantido conforme definição anterior, presente nas camadas Silver e Gold)*

---

## Matriz de Rastreabilidade (Resumo)

| Requisito | Camada Medalhão | Fluxo | Prioridade |
| :--- | :--- | :--- | :--- |
| RF-01 | Inbound | Batch Ingest | Must Have |
| RF-02 | Landing Zone | Storage | Must Have |
| RF-03 | Bronze | Raw Load | Must Have |
| RF-04 | Silver | Transformation | Must Have |
| RF-05 | Gold | Aggregation | Must Have |
| RF-06 | Todas | Idempotency | Must Have |
| RF-07 | Todas | Observability | Must Have |
| RF-08 | Todas | Replay | Should Have |
| RF-09 | Silver | Data Quality | Must Have |
| RF-10 | Silver/Gold | Audit | Must Have |
