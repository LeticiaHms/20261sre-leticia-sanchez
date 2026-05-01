# Requisitos Não Funcionais (RNF) - Pipeline de Dados Olist

Este documento detalha os requisitos não funcionais do sistema, focando em performance, segurança, escalabilidade e observabilidade.

| ID | Categoria | Nome do Requisito | Descrição |
| :--- | :--- | :--- | :--- |
| **RNF01** | Confiabilidade | Idempotência Obrigatória | O sistema deve garantir que o processamento repetido do mesmo conjunto de dados não cause duplicidade ou inconsistência no banco de dados. |
| **RNF02** | Eficiência | Tempo de Processamento | O pipeline deve ser capaz de processar uma carga de 100 mil registros em menos de 5 minutos. |
| **RNF03** | Escalabilidade | Escalabilidade Elástica | A arquitetura deve ser baseada em containers (ECS Fargate) para permitir o aumento de recursos (CPU/RAM) conforme o volume de dados cresce. |
| **RNF04** | Segurança | Princípio do Menor Privilégio | O acesso aos recursos AWS (S3, RDS, CloudWatch) deve ser controlado via IAM Roles específicas para cada componente. |
| **RNF05** | Segurança | Isolamento de Rede | Todo o tráfego de dados entre S3, ECS e RDS deve ocorrer dentro da rede privada da AWS via VPC Endpoints, sem exposição à internet. |
| **RNF06** | Observabilidade | Detecção de Anomalias | O sistema deve disparar alertas automáticos (SNS/CloudWatch) caso a taxa de erro ultrapasse 5% ou se houver falha de reconciliação de registros. |
| **RNF07** | Portabilidade | Padronização via Docker | O processo de ETL deve ser encapsulado em containers Docker para garantir paridade entre os ambientes de desenvolvimento, staging e produção. |
| **RNF08** | Disponibilidade | Gerenciamento RDS | O banco de dados deve utilizar as capacidades de backup e alta disponibilidade nativas do AWS RDS. |
| **RNF09** | Segurança | Criptografia em Repouso e Trânsito | Todos os dados no S3 e RDS devem ser criptografados em repouso (AES-256) e em trânsito (TLS 1.2+). |
| **RNF10** | Recuperabilidade | RTO e RPO | O tempo de recuperação (RTO) deve ser < 10 min. O objetivo de ponto de recuperação (RPO) deve ser zero, graças à idempotência. |
| **RNF11** | Manutenibilidade | Cobertura de Testes | A lógica de transformação (Python) deve possuir no mínimo 80% de cobertura de testes unitários. |
| **RNF12** | Eficiência de Custo | Ciclo de Vida de Dados | Arquivos no S3 devem ser movidos para o Glacier após 7 dias e excluídos após 30 dias para otimização de custos. |
| **RNF13** | Operabilidade | Padronização de Logs | Os logs devem seguir o formato JSON estruturado para facilitar a indexação e busca no CloudWatch Logs Insights. |
| **RNF14** | Conformidade | Retenção de Auditoria | Logs de auditoria de acesso aos dados (CloudTrail/RDS Logs) devem ser mantidos por pelo menos 1 ano. |
| **RNF15** | Manutenibilidade | Documentação de Código | O código deve seguir o padrão PEP8 e incluir docstrings em todas as funções de transformação e validação. |
| **RNF16** | FinOps | Tagging de Recursos | Todos os recursos provisionados via Terraform devem possuir tags de `Project`, `Environment` e `CostCenter` para controle orçamentário. |
| **RNF17** | Eficiência | Gestão de Memória (Anti-OOM) | O processamento via container deve utilizar técnicas de *streaming* ou *chunking* para garantir que o uso de RAM seja constante, independentemente do tamanho do arquivo. |
| **RNF18** | Manutenibilidade | Versionamento de Schema (Migrations) | Toda alteração na estrutura das tabelas do RDS deve ser realizada via ferramentas de migração de banco de dados (ex: Alembic, Flyway) e versionada no Git. |
| **RNF19** | Confiabilidade | Pooling de Conexões | O sistema deve utilizar um gestor de conexões (pooling) para evitar a exaustão de conexões no RDS durante picos de concorrência. |
| **RNF20** | Disponibilidade | Recuperação de Desastre (Cross-Region) | Backups críticos do RDS e cópias dos arquivos do S3 devem ser replicados para uma segunda região AWS para garantir continuidade em caso de falha regional. |
