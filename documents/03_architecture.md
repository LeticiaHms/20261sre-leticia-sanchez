# Arquitetura Detalhada: Pipeline de Dados Olist

Esta documentação detalha a arquitetura técnica, ferramentas e protocolos, mapeando-os aos Requisitos Funcionais (RF) e Não Funcionais (RNF).

---

## 1. Enterprise Viewpoint (Visão de Negócio)
Foca no propósito e conformidade.

- **Objetivo:** Processamento de 100k pedidos/dia para dashboard analítico.
- **Conformidade (PII):** Mascaramento de dados sensíveis via **Python Hashlib** ou substituição de strings. (RF20)
- **Gestão de Custos:** Monitoramento de créditos do Learner Lab via **AWS Budgets** (apenas visualização). (RNF16)
- **Governança:** Trilha de auditoria gravada em tabela `audit_log` no RDS. (RF19)

**RFs:** RF19, RF20, RF30 | **RNFs:** RNF12, RNF14, RNF16.

---

## 2. Information Viewpoint (Visão de Informação)
Foca no ciclo de vida e estrutura do dado.

- **Ingestão:** Arquivos `.csv` com encoding `UTF-8`. (RF01)
- **Estrutura de Armazenamento (AWS S3):**
    - `s3://[BUCKET_NAME]/landing/`: Destino de upload inicial; gatilho para a Lambda.
    - `s3://[BUCKET_NAME]/processed/`: Destino de arquivos processados com sucesso.
    - `s3://[BUCKET_NAME]/failed/`: Destino de arquivos que falharam na integridade ou validação inicial.
- **Esquemas de Banco de Dados (Postgres 16):**
    - `raw_zone`: Tabelas temporárias de staging (Unlogged tables para performance). (RF09)
    - `analytics_zone`: Tabelas finais indexadas por `order_id`. (RF03, RF04)
    - `error_zone`: Tabelas de Dead Letter (DLT) com colunas de erro e stacktrace. (RF05, RF31)
- **Qualidade:** Validação de tipos e regras de negócio via **Pydantic** ou **Pandas Validation**. (RF02, RF14, RF29)

**RFs:** RF02, RF04, RF05, RF06, RF14, RF15, RF21, RF22, RF28, RF31 | **RNFs:** RNF01, RNF18.

---

## 3. Computational Viewpoint (Visão Computacional)
Foca nos módulos de processamento e bibliotecas Python.

- **Trigger (AWS Lambda):** Código em Python 3.12 usando **Boto3** para disparar o `ecs.run_task`. (RF01)
- **ETL Engine (ECS Fargate):**
    - **Extract:** **Boto3** para streaming de arquivos do S3. (RNF17)
    - **Transform:** **Pandas** para limpeza, deduplicação e normalização. (RF21, RF22, RF23)
    - **Load:** **Psycopg2** com o método `copy_expert` para Bulk Load via stdin. (RNF02, RNF19)
- **Observabilidade:** **Python Logging** com formatador JSON para CloudWatch. (RNF13)
- **Migrações:** **Alembic** para versionamento de schema. (RNF18)

**RFs:** RF07, RF08, RF10, RF21, RF22, RF23, RF24, RF26, RF27 | **RNFs:** RNF06, RNF11, RNF13, RNF15, RNF17, RNF18.

---

## 4. Engineering Viewpoint (Visão de Engenharia)
Foca na infraestrutura AWS e conectividade.

- **Rede (VPC):**
    - **Subnets Privadas:** Onde residem o ECS Fargate e o RDS. (RNF05)
    - **S3 Gateway Endpoint:** Acesso gratuito e interno ao S3. (RNF05)
    - **Interface Endpoints (PrivateLink):** Para Secrets Manager, CloudWatch e ECR. (RNF05)
- **Segurança:** 
    - **Secrets Manager:** Armazena JSON com credenciais do DB (host, user, pwd). (RNF04, RNF09)
    - **Security Groups:** Regras de ingresso restritas ao tráfego do ECS para o RDS (Porta 5432). (RNF05)
- **Notificações:** **AWS SNS** para disparar e-mails em falhas críticas. (RF10, RF13)

**RFs:** RF01, RF03, RF10, RF12, RF16, RF18 | **RNFs:** RNF02, RNF03, RNF04, RNF05, RNF08, RNF09, RNF10, RNF19, RNF20.

---

## 5. Technology Viewpoint (Visão de Tecnologia)
Especificação exata das versões e ferramentas.

- **Linguagem:** Python 3.12.
- **Bibliotecas Principais:** `pandas==2.2.0`, `psycopg2-binary==2.9.9`, `boto3==1.34.0`, `pydantic==2.6.0`, `alembic==1.13.0`.
- **Infrastructure as Code:** Terraform 1.7+.
- **Database:** Amazon RDS for PostgreSQL 16.1-R1 (Single-AZ para custo Learner Lab).
- **Container:** Docker Engine 25.0 (Alpine-based image para leveza).
- **Protocolos:** TLS 1.2 para todas as conexões (JDBC/S3 API).

---

## ADRs (Architecture Decision Records)

### ADR 01: Processamento em Chunks com Pandas/Psycopg2
- **Contexto:** Arquivos de 100k podem ocupar muita RAM no container Fargate.
- **Decisão:** Usar `pandas.read_csv(chunksize=10000)` e carregar no Postgres via buffer `io.StringIO` com o comando `COPY`.
- **Consequências:** Uso de memória estável (< 512MB) e alta velocidade de carga, atendendo RNF02 e RNF17.

### ADR 02: Validação de Schema com Pydantic
- **Contexto:** Necessidade de garantir integridade dos dados (tipos e regras) antes de tocar no banco.
- **Decisão:** Utilizar Pydantic Models para validar cada linha do DataFrame.
- **Consequências:** Erros de validação capturados precocemente e enviados para a DLT de forma estruturada (RF02, RF05, RF14).

### ADR 03: VPC Interface Endpoints para Secrets e CloudWatch
- **Contexto:** O Learner Lab não permite NAT Gateways de alto custo para acesso à internet a partir de subnets privadas.
- **Decisão:** Utilizar VPC Endpoints (Interface) para serviços críticos da AWS.
- **Consequências:** Segurança aumentada e custo de tráfego reduzido, garantindo que o ECS possa buscar segredos e enviar logs sem sair da rede AWS (RNF05).

---
*Restrições Academy Lab: Sem Glue, Sem Redshift, Sem NAT Gateway (custo), Sem Kinesis.*
