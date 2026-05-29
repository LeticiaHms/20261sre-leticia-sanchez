# AGENTS.md · northwind-sre-pipeline

## Contexto
Pipeline de dados Northwind.

Fluxo esperado:

`CSV Northwind -> ETL Python -> DuckDB/ClickHouse -> Streamlit`

Orientacao principal:
- SRE-first;
- arquitetura documentada;
- reproducibilidade;
- evidencias reais de execucao;
- decisao arquitetural explicita.

---

## Objetivo do agente
Projetar, documentar, implementar e validar uma stack analitica baseada no dataset Northwind, seguindo praticas de engenharia de software, SRE, arquitetura de software (Bass) e avaliacao arquitetural (ATAM).

O agente deve priorizar:
1. modelagem antes de implementacao;
2. reproducibilidade;
3. clareza documental;
4. validacao automatizada;
5. justificativa tecnica de decisoes.

Nao pular etapas.

---

## Restricoes duras

### Seguranca
- Sem secrets em codigo.
- Tudo via variaveis de ambiente.
- Quando necessario, assumir `SSM Parameter Store` como origem de configuracao.
- Nunca hardcodar credenciais.
- Sempre fornecer `.env.example`.

### Infraestrutura
- Nao provisionar infraestrutura cloud nesta disciplina.
- Apenas artefatos declarativos:
  - Markdown;
  - Mermaid;
  - Docker Compose;
  - templates quando solicitado.

### Arquitetura
- Nao inventar nomes de servico.
- Nao assumir componentes inexistentes.
- Toda escolha arquitetural deve ser justificada.

### Evidencias
- Nao criar imagens, screenshots ou prints como evidencia padrao.
- Priorizar evidencias textuais e reproduziveis.

---

# Processo obrigatorio

## Regra principal
Antes de codar, modelar o problema.

Nunca iniciar implementacao sem modelagem minima.

A ordem obrigatoria e:

1. entendimento do problema;
2. modelagem conceitual;
3. modelagem logica;
4. modelagem fisica;
5. arquitetura da stack;
6. ADRs e trade-offs;
7. implementacao;
8. testes;
9. evidencias;
10. revisao final.

Nao inverter a ordem.

---

# Modelagem obrigatoria

## Modelo conceitual
Produzir modelo conceitual do dataset Northwind contendo:

- entidades;
- atributos;
- relacionamentos;
- cardinalidades;
- regras de negocio.

Explicitar:
- o que representa cada entidade;
- dependencias entre entidades.

---

## Modelo logico
Produzir modelo logico contendo:

- tabelas;
- atributos;
- PK;
- FK;
- cardinalidades;
- normalizacao;
- relacionamentos.

Explicitar:
- decisoes de modelagem;
- desnormalizacoes quando existirem;
- trade-offs adotados.

---

## Modelo fisico
Produzir modelo fisico contendo:

- tipos de dados;
- constraints;
- PK;
- FK;
- indices quando relevantes;
- estrategia de particionamento quando aplicavel.

Explicitar:
- compatibilidade com ClickHouse;
- compatibilidade com DuckDB;
- justificativa dos tipos escolhidos.

---

# Arquitetura obrigatoria

## Diagrama de arquitetura
Produzir diagrama arquitetural obrigatorio usando:

- Mermaid no `README.md`

ou

- arquivo em `docs/diagrams/`

O diagrama deve mostrar explicitamente:

### Ingestao
- origem CSV Northwind;
- leitura dos arquivos;
- validacoes iniciais.

### Armazenamento
- `MinIO` ou S3-like;
- persistencia intermediaria quando existir.

### Processamento
- ETL Python;
- transformacoes;
- limpeza;
- enriquecimento;
- validacao.

### Camada analitica
- `DuckDB`;
- `ClickHouse`.

### Visualizacao
- `Streamlit`.

### Operacao/SRE
Quando aplicavel, mostrar:
- logs;
- observabilidade;
- retries;
- health checks;
- configuracao externa.

---

# Decisoes arquiteturais obrigatorias

Registrar no `README.md`:

## Decisoes tomadas
Explicar:
- o que foi escolhido;
- por que foi escolhido;
- impacto tecnico.

---

## Trade-offs
Explicar:
- alternativas consideradas;
- alternativas descartadas;
- motivo tecnico do descarte.

Sempre justificar tecnicamente.

Evitar frases vagas como:
- "foi escolhido porque e melhor"
- "mais facil"

Explicar criterios tecnicos.

---

## ADRs
Usar IDs estaveis:

- `ADR-01`
- `ADR-02`

Formato esperado:

```md
# ADR-01 - Escolha do ClickHouse

## Contexto

## Decisao

## Consequencias

## Alternativas descartadas