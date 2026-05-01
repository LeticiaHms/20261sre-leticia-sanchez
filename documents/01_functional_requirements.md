# Requisitos Funcionais (RF) - Pipeline de Dados Olist

Este documento lista os requisitos funcionais para o projeto do Pipeline de Dados Olist, derivados da especificação técnica e refinados utilizando a skill `elicit_rf`.

| ID | Nome do Requisito | Descrição |
| :--- | :--- | :--- |
| **RF01** | Ingestão via S3 | O sistema deve realizar a ingestão automática de arquivos CSV carregados em buckets específicos do AWS S3 (ex: `/landing`). |
| **RF02** | Validação de Schema | O sistema deve validar a presença de cabeçalhos obrigatórios e os tipos de dados corretos para cada coluna no arquivo de entrada. |
| **RF03** | Persistência Analítica | O sistema deve persistir os dados validados e transformados em um banco de dados analítico AWS RDS Postgres. |
| **RF04** | Upsert Idempotente | O sistema deve tratar atualizações de registros com base em um identificador único (`order_id`). Se o registro já existir, deve ser atualizado; caso contrário, inserido. |
| **RF05** | Dead Letter Table (DLT) | Registros que falharem na validação ou transformação devem ser isolados em uma "Dead Letter Table" ou armazenamento de falhas para análise posterior. |
| **RF06** | Linhagem de Dados | Cada registro persistido deve incluir metadados indicando sua fonte (nome do arquivo) e o timestamp preciso da ingestão. |
| **RF07** | Telemetria em Tempo Real | O sistema deve gerar e exportar métricas numéricas em tempo real para o AWS CloudWatch (ex: total de linhas lidas, linhas carregadas, contagem de erros). |
| **RF08** | Circuit Breaker | O processo de ingestão deve ser abortado e realizar um rollback total se a taxa de registros inválidos ultrapassar um limite pré-definido (ex: 5%). |
| **RF09** | Carga em Staging Area | Os dados devem ser carregados em uma área de staging temporária para validação antes de serem movidos para as tabelas finais de produção. |
| **RF10** | Notificação de Falha Crítica | O sistema deve disparar notificações imediatas (via SNS para E-mail/Slack) para o time de SRE sempre que o `Circuit Breaker` for acionado ou o job falhar. |
| **RF11** | Relatório de Sumário de Carga | Ao final de cada execução, o sistema deve gerar um sumário (logs/evento) contendo o total de sucessos, falhas e o tempo de execução para consumo analítico. |
| **RF12** | Alerta de Atraso (SLA) | Se um arquivo esperado não for detectado no bucket S3 até um horário pré-definido, o sistema deve disparar um alerta de "Dados Não Recebidos". |
| **RF13** | Notificação de Recuperação | O sistema deve notificar os stakeholders quando um processo que falhou anteriormente for re-executado com sucesso (resolução do incidente). |
| **RF14** | Validação de Regras de Negócio | O sistema deve validar regras lógicas (ex: valores negativos, datas incoerentes) além da simples conferência de tipos de dados. |
| **RF15** | Tratamento de Sucesso Parcial | O sistema deve permitir a carga de registros válidos enquanto isola os inválidos, desde que a taxa de erro esteja abaixo do limite do Circuit Breaker. |
| **RF16** | Arquivamento Automático | Após o processamento, o arquivo original deve ser movido para as pastas `/processed` ou `/failed` no S3, mantendo a `/landing` limpa. |
| **RF17** | Capacidade de Backfill | O sistema deve permitir o re-processamento manual de arquivos específicos armazenados no S3 sem a necessidade de novo upload. |
| **RF18** | Controle de Concorrência | O pipeline deve gerenciar execuções simultâneas para evitar conflitos de escrita ou deadlocks no banco de dados analítico. |
| **RF19** | Trilha de Auditoria (Audit Log) | Deve haver um registro histórico de todas as execuções, contendo metadados do arquivo, status final e volume de dados processados. |
| **RF20** | Proteção de Dados (PII) | O sistema deve anonimizar ou mascarar dados sensíveis (conforme LGPD) durante o processo de transformação antes da persistência final. |
| **RF21** | Deduplicação Intra-arquivo | O sistema deve identificar e remover registros duplicados dentro do próprio arquivo de entrada antes de iniciar a carga no banco. |
| **RF22** | Padronização e Normalização | O sistema deve aplicar regras de limpeza (ex: trim em strings, conversão de datas para ISO 8601, padronização de nulos) em todos os campos. |
| **RF23** | Enriquecimento de Dados | Durante a transformação, o pipeline deve ser capaz de cruzar dados do CSV com tabelas de referência (ex: converter CEP em Estado/Cidade) se necessário. |
| **RF24** | Atomicidade por Arquivo | O processamento de um arquivo deve ser atômico; em caso de falha crítica, nenhuma parte parcial daquele arquivo deve permanecer nas tabelas de produção. |
| **RF25** | Evolução de Schema (Flexibilidade) | O pipeline deve ser resiliente a pequenas mudanças no arquivo (ex: colunas extras ao final) sem interromper a execução, apenas logando a diferença. |
| **RF26** | Atualização de Status de Metadados | O sistema deve atualizar uma tabela central de controle (`process_control`) com o status de cada arquivo (INICIADO, SUCESSO, FALHA). |
| **RF27** | Limpeza de Recursos Temporários | Após o término (sucesso ou falha), o sistema deve limpar automaticamente tabelas de staging ou arquivos temporários gerados no container. |
| **RF28** | Verificação de Integridade (Checksum) | O sistema deve validar o hash (MD5/SHA256) do arquivo recebido no S3 antes do processamento para garantir que não houve corrupção no upload. |
| **RF29** | Monitoramento de Recência (Data Freshness) | O sistema deve alertar se os dados contidos no arquivo forem excessivamente antigos (ex: pedidos de > 30 dias atrás) para evitar cargas acidentais de dados legados. |
| **RF30** | Suporte à Exclusão (Direito ao Esquecimento) | O pipeline deve possuir um mecanismo para processar solicitações de exclusão de dados específicos (LGPD), garantindo a remoção do banco analítico. |
| **RF31** | Alerta de Volume de DLT | Além do Circuit Breaker, o sistema deve notificar se a Dead Letter Table atingir um volume acumulado anormal (ex: > 1000 registros pendentes). |
