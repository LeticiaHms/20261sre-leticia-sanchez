# Especificação Técnica: Pipeline de Dados Olist

## PARTE 1: Contexto do Problema
O negócio Olist atua como um integrador de marketplaces, lidando com um volume expressivo de transações diárias. Atualmente, existe um gap entre a geração do pedido no marketplace e a visibilidade analítica para tomada de decisão. 

**O Desafio:** Processar ~100 mil pedidos diários, garantindo que o dado chegue ao banco analítico de forma confiável, sem duplicidade e com total observabilidade. O sistema não pode "sofrer silenciosamente"; qualquer anomalia deve ser detectada e reportada proativamente.

---

## PARTE 2: Modelagem do Problema (Problem Modeling Canvas)

### 2.1. Stakeholders
*   **Negócio:** Analistas e Gestores que consomem os dashboards.
*   **Operações:** Time de SRE e Engenharia de Dados que mantém o pipeline.
*   **Ecossistema:** Marketplaces parceiros (origem dos dados).

### 2.2. Fluxos Críticos
1.  **Ingestão de Arquivos:** Recebimento do CSV no S3 e validação de integridade.
2.  **Processamento ETL:** Transformação dos dados brutos em formato analítico.
3.  **Carga Idempotente:** Inserção no Postgres garantindo unicidade.
4.  **Telemetria:** Geração de logs e métricas em tempo real.

### 2.3. Requisitos Funcionais (RFs)
*   **RF01:** Ingestão de arquivos CSV via AWS S3.
*   **RF02:** Validação automática de schema e tipos de dados.
*   **RF03:** Persistência em banco de dados Postgres analítico.
*   **RF04:** Tratamento de atualizações de status (Upsert).
*   **RF05:** Isolamento de registros inválidos (Dead Letter Table).
*   **RF06:** Geração de linhagem (timestamp e fonte) para cada registro.

### 2.4. Requisitos Não Funcionais (SWEBOK/ISO 25010)
1.  **Confiabilidade:** Idempotência obrigatória para permitir re-runs sem efeitos colaterais.
2.  **Eficiência:** Processamento de 100k registros em < 5 minutos.
3.  **Escalabilidade:** Arquitetura baseada em containers (ECS Fargate) para elasticidade.
4.  **Segurança:** Dados criptografados e acesso via IAM Roles (Least Privilege).
5.  **Observabilidade:** Dashboards de saúde e alertas proativos via CloudWatch.
6.  **Portabilidade:** Padronização via Docker para consistência entre ambientes.

---

## PARTE 3: Arquitetura de Referência AWS

### 3.1. Visão Geral do Fluxo
O pipeline segue o modelo *Event-Driven Architecture*:
`S3 (Upload) -> EventBridge/S3 Event -> Lambda (Trigger) -> ECS Fargate (Job) -> RDS Postgres`.

### 3.2. Componentes de Infraestrutura
*   **Armazenamento (S3):** Bucket estruturado com pastas `/landing`, `/processed` e `/failed`. Utiliza *Lifecycle Policies* para mover arquivos antigos para Glacier.
*   **Orquestração (Lambda + ECS Fargate):**
    *   **Lambda:** Função leve apenas para disparar o `RunTask` do ECS.
    *   **ECS Fargate:** Executa o container Python com recursos dedicados (CPU/RAM), evitando limites de tempo de execução.
*   **Banco de Dados (RDS Postgres):** Instância em Subnet Privada. O acesso é feito via **VPC Endpoints** para manter o tráfego interno na rede AWS.
*   **Segurança (IAM & Secrets Manager):**
    *   **IAM Task Role:** Permite ao container ler do S3 e escrever no CloudWatch.
    *   **Secrets Manager:** Armazena a string de conexão do banco, injetada no container em tempo de execução.

### 3.3. Estratégia de Dados e Resiliência (Deep Dive)
*   **Bulk Load (COPY):** Em vez de realizar 100.000 comandos de `INSERT` individuais (que saturam o IOPS do banco), o container utiliza o comando nativo `COPY` do Postgres. Isso permite a ingestão de grandes volumes em segundos, enviando o arquivo em "chunks" (pedaços) diretamente para a memória do banco.
*   **Atomic Upsert (Idempotência):** Implementação da lógica `ON CONFLICT (order_id) DO UPDATE`. Isso garante que, caso o pipeline seja re-executado para a mesma carga, o sistema não gere duplicatas, mas sim atualize os registros existentes. Isso torna o pipeline **Idempotente**.
*   **Circuit Breaker (Data Quality Gate):** O script possui um contador de erros. Se a taxa de registros inválidos ultrapassar um limite pré-definido (ex: 5%), o processo realiza um `ROLLBACK` total e aborta a operação. É melhor não ter o dado do que ter um dado não confiável no dashboard.
*   **Staging Area:** Os dados são primeiramente carregados em uma tabela temporária de "Staging" para validação, antes de serem movidos para a tabela final de produção em uma única transação atômica.

### 3.4. Observabilidade e SRE (Métricas Detalhadas)
O sistema não apenas gera logs, mas expõe **Métricas Numéricas** via CloudWatch para monitoramento em tempo real:
*   **Volume de Ingestão (`records_in`):** Total de linhas lidas do CSV.
*   **Sucesso de Carga (`records_out`):** Total de linhas persistidas no Postgres.
*   **Taxa de Erro (`error_rate`):** Percentual de falhas na transformação/validação.
*   **Latência de Fase (`phase_duration`):** Tempo gasto em cada etapa (Download, Transform, Load).
*   **Check de Reconciliação:** Uma métrica binária (0 ou 1) que indica se `records_in` é igual a `records_out` + `records_failed`. Se for 0, o alerta dispara imediatamente.

### 3.5. Delivery e Governança
*   **IaC:** Provisionamento 100% via **Terraform**.
*   **CI/CD:** Pipeline automatizado que executa testes unitários, constrói a imagem Docker e atualiza a Task Definition no ECS.
*   **Compliance:** Logs de auditoria ativados para rastrear quem acessou ou modificou os dados.

---

## PARTE 4: Justificativa Técnica dos Recursos (Rationale)

Nesta seção, detalhamos a escolha de cada componente da AWS e como ele endereça os requisitos de confiabilidade, performance e custo do projeto.

### 4.1. AWS S3 (Simple Storage Service)
*   **Por que usar:** É o padrão ouro para durabilidade e custo-benefício. Atua como um *Data Lake* inicial.
*   **No Contexto Olist:** Permite que os arquivos de 100k registros sejam depositados de forma assíncrona. O uso de *S3 Event Notifications* elimina a necessidade de um processo "polling" (ficar perguntando se o arquivo chegou), economizando recursos e garantindo que o processamento comece instantaneamente após o upload.

### 4.2. AWS Lambda (Trigger)
*   **Por que usar:** Modelo *Serverless* com custo zero enquanto não está sendo executada.
*   **No Contexto Olist:** A Lambda atua apenas como um "maestro". Ela recebe o sinal do S3, valida se o arquivo é o esperado e dispara a tarefa no ECS. Usamos a Lambda aqui porque disparar uma tarefa leva milissegundos, sendo muito mais barato do que manter um servidor ligado esperando o arquivo.

### 4.3. AWS ECS Fargate (Elastic Container Service)
*   **Por que usar:** Permite rodar containers sem gerenciar servidores (EC2). Oferece isolamento total de CPU e Memória.
*   **No Contexto Olist:** Processar 100k linhas pode levar mais de 15 minutos (limite da Lambda). O **Fargate** não tem esse limite. Se amanhã o Olist crescer para 1 milhão de linhas, basta aumentar a vCPU/RAM na configuração da Task, sem mudar uma linha de código, garantindo a **Escalabilidade**.

### 4.4. AWS RDS Postgres (Relational Database Service)
*   **Por que usar:** Gerenciamento automatizado de backups, patches e alta disponibilidade.
*   **No Contexto Olist:** Como precisamos gerar dashboards diários, a integridade referencial (ACID) é crucial. O Postgres lida nativamente com o comando `COPY` para cargas em massa e permite a técnica de `UPSERT` (On Conflict), essencial para garantir a **Idempotência** do pipeline.

### 4.5. AWS CloudWatch (Observability Suite)
*   **Por que usar:** Centraliza logs, métricas e alertas em um único lugar.
*   **No Contexto Olist:** Resolve o problema do "sofrimento silencioso". Se o pipeline falhar ou se apenas 50k registros forem carregados em vez de 100k, o CloudWatch detecta essa anomalia através de *Metric Filters* e dispara um alarme via SNS, garantindo que o SRE seja avisado antes do Analista de Negócio abrir o dashboard.

### 4.6. AWS Secrets Manager
*   **Por que usar:** Segurança e conformidade (LGPD/Segurança da Informação).
*   **No Contexto Olist:** Evita o erro comum de deixar senhas do banco de dados expostas no código ou em variáveis de ambiente visíveis no console da AWS. O container do ECS busca a senha de forma dinâmica, e podemos rotacionar essa senha periodicamente sem derrubar o serviço.

### 4.7. VPC Endpoints (Gateway & Interface)
*   **Por que usar:** Segurança e economia de tráfego de rede.
*   **No Contexto Olist:** Permite que o tráfego de 100k registros entre o S3, ECS e RDS trafegue 100% dentro da rede privada da AWS. Isso impede ataques via internet e elimina custos de saída de dados (*NAT Gateway*), tornando o pipeline mais barato e seguro.
