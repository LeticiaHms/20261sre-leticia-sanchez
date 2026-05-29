# Especificação Técnica: Pipeline de Dados Northwind

## PARTE 1: Contexto do Problema
O negócio Northwind atua como um conjunto relacional de pedidos e itens de pedido, de domínio de distribuição de alimentos e bebidas, lidando com um volume expressivo de transações diárias. Atualmente, existe um gap entre a geração do pedido e a visibilidade analítica para tomada de decisão. 

**O Desafio:** Processar ~100 mil pedidos diários, garantindo que o dado chegue ao banco analítico de forma confiável, sem duplicidade e com total observabilidade. O sistema não pode "sofrer silenciosamente"; qualquer anomalia deve ser detectada e reportada proativamente.

**Esperado:** (i) modelo conceitual, lógico e físico das tabelas do dataset Northwind (entidades, atributos, relacionamentos, tipos e chaves); (ii) diagrama de arquitetura da stack adotada (Mermaid no próprio README), mostrando ingestão, armazenamento (MinIO), processamento e camada analítica (ClickHouse, Streamlit); (iii) registro, no README.md, das decisões e trade-offs considerados — quais alternativas foram descartadas e por quê.

## PARTE 2: Modelagem do Problema (Problem Modeling Canvas)

### 2.1. Stakeholders
- Operação Northwind (negócio)
- Time de dados
- Consumidores dos dashboards
- Plataforma / SRE

### 2.2. Fluxos Críticos
1.  **Ingestão de Arquivos:** Recebimento do CSV e validação de integridade.
2.  **Processamento ETL:** Transformação dos dados brutos em formato analítico.
3.  **Carga Idempotente:** Inserção em um banco analitico garantindo unicidade.
4.  **Telemetria:** Geração de logs e métricas em tempo real.
5.  **Portabilidade:** Padronização via Docker para consistência entre ambientes.
