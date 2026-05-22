# Plano de Teste de Segurança - Batch & Integrity

Focado na integridade dos dados ao longo das camadas Medalhão e no isolamento do ambiente batch.

## 1. Objetivos do Teste
- Garantir que dados maliciosos sejam barrados antes de atingir a camada Bronze.
- Validar a imutabilidade da Landing Zone.
- Verificar a segurança dos logs estruturados (ausência de PII/Segredos).

## 2. Cenários de Segurança Batch

### 2.1 Prevenção de Corrupção em Camadas
- **TC-22: Sanitização de Input (Silver Gate)**
    - **Cenário:** Injetar registros com payloads maliciosos na Bronze.
    - **Resultado esperado:** A transição para a Silver deve detectar e sanitizar ou isolar os registros, logando a ocorrência como `SECURITY_ALERT`.

### 2.2 Integridade do Audit Trail
- **TC-10: Rastreabilidade Bronze -> Gold**
    - **Cenário:** Verificar se o campo `source_file` e o `batch_id` persistem corretamente até a camada Gold.
    - **Resultado esperado:** 100% de linhagem preservada, permitindo auditar a origem de qualquer KPI no dashboard.

### 2.3 Segurança de Observabilidade
- **TC-24: Auditoria de Segredos em Logs**
    - **Cenário:** Varredura automática nos logs JSON gerados durante o processamento batch.
    - **Resultado esperado:** Zero ocorrências de senhas do ClickHouse ou MinIO, conforme ADR-09.

## 3. Critérios de Aceitação
- Nenhum registro da camada Silver ou Gold deve estar desprovido de metadados de auditoria.
- O isolamento entre o Ingestor e o ClickHouse deve ser validado via Docker Network.
