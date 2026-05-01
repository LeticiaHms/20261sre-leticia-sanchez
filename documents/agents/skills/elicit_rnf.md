# Skill: Elicit Non-Functional Requirements (RNF)

Esta skill orienta o agente na identificação e documentação dos requisitos não funcionais para o Pipeline de Dados Olist, focando em atributos de qualidade como performance, segurança e observabilidade.

## Objetivo
Capturar as restrições e qualidades do sistema que garantem sua operação eficiente e segura, seguindo padrões como SWEBOK e ISO 25010.

## Fluxo de Trabalho
1. **Análise Técnica:** Revisar a arquitetura e restrições descritas em `00_problem.md`.
2. **Categorização:** Dividir os requisitos em categorias (ex: Confiabilidade, Eficiência, Segurança, Observabilidade).
3. **Escrita Técnica:** Formular os RNFs com métricas claras e testáveis.
4. **Validação:** Garantir que cada RNF apoia os objetivos de SRE do projeto.

## Categorias Padrão para este Projeto
- **Confiabilidade:** Garantia de idempotência e recuperação de falhas.
- **Eficiência de Performance:** Limites de tempo de processamento e volume de dados.
- **Escalabilidade:** Capacidade de crescimento horizontal (ECS Fargate).
- **Segurança:** Criptografia, controle de acesso (IAM) e rede privada.
- **Observabilidade:** Métricas, logs e alertas proativos.

## Formato de Saída
Os requisitos devem ser adicionados ao arquivo `documents/02_non_functional_requirements.md`.
