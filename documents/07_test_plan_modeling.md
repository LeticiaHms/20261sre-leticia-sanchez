# Plano de Teste de Modelagem

Este documento detalha a validação da integridade semântica em cada camada do Northwind Data Pipeline (Bronze, Silver e Gold).

## 1. Objetivos do Teste
- Validar a fidelidade do dado bruto na camada **Bronze**.
- Garantir a precisão da unificação e limpeza na camada **Silver**.
- Verificar a acurácia dos agregados de negócio na camada **Gold**.
- Validar a propagação correta dos metadados de Audit Trail entre camadas.

## 2. Cenários de Teste por Camada

### 2.1 Camada Bronze (Raw Fidelity)
- **TC-26: Acurácia da Carga Bronze**
    - **Objetivo:** Garantir que o ClickHouse (Bronze) seja um espelho fiel do CSV no MinIO.
    - **Resultado esperado:** O número de linhas e o conteúdo das colunas devem ser idênticos ao CSV original.

### 2.2 Camada Silver (Integration & Cleansing)
- **TC-27: Unificação e Enriquecimento Silver**
    - **Objetivo:** Validar o Join entre `Orders` e `Order Details` e a aplicação de tipos.
    - **Regra:** `total_price = unit_price * quantity`.
    - **Resultado esperado:** Registros unificados sem perda de itens de pedido e cálculos matemáticos corretos.

- **TC-09: Sanitização Silver**
    - **Objetivo:** Validar remoção de espaços e padronização.
    - **Resultado esperado:** Dados na Silver devem estar 100% "limpos" conforme RF-09.

### 2.3 Camada Gold (Business Aggregates)
- **TC-28: Consistência dos KPIs Gold**
    - **Objetivo:** Validar se os agregados (ex: vendas por país) batem com a soma manual da camada Silver.
    - **Resultado esperado:** `SUM(Silver.total_price)` agrupado por país deve ser igual ao valor registrado na Gold.

## 3. Testes Transversais (Data Quality)
- **TC-11: Reconciliação em Cascata**
    - **Objetivo:** Garantir que o volume de registros faça sentido ao longo do pipeline.
    - **Resultado esperado:** `Rows(Bronze Orders) <= Rows(Silver Unified)` (devido ao join 1:N com detalhes).

- **TC-04: Idempotência em Camadas**
    - **Ação:** Re-processar o mesmo lote batch.
    - **Resultado esperado:** Nenhuma das três camadas deve apresentar contagem de linhas alterada.
