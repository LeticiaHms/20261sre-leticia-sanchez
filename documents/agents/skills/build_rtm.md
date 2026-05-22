# skills/build_rtm.md

## Quando usar
Quando existirem requisitos funcionais e/ou nao funcionais documentados.

Usar obrigatoriamente quando existir:

- `spec/00_problem.md`
- `documents/01_functional_requirements.md`
ou
- `documents/02_non_functional_requirements.md`

Usar antes da implementacao.

## Objetivo
Construir uma matriz de rastreabilidade (RTM - Requirements Traceability Matrix) garantindo alinhamento entre:

- problema;
- stakeholders;
- fluxos criticos;
- riscos;
- RFs;
- RNFs;
- testes;
- evidencias;
- componentes arquiteturais.

O objetivo e impedir requisitos orfaos, nao verificaveis ou sem motivacao de negocio.

## Entrada
Obrigatorio:
- `spec/00_problem.md`

Opcional:
- `documents/01_problem_modeling.md`
- `documents/01_functional_requirements.md`
- `documents/02_non_functional_requirements.md`
- `documents/03_architecture.md`
- `documents/adr/`

## Passos

1. Ler stakeholders e fluxos criticos do problema.
2. Identificar objetivos do negocio.
3. Ler RFs existentes.
4. Ler RNFs existentes.
5. Mapear:
   stakeholder -> fluxo critico.
6. Mapear:
   fluxo critico -> requisito.
7. Mapear:
   requisito -> risco mitigado.
8. Mapear:
   requisito -> componente arquitetural.
9. Mapear:
   requisito -> caso de teste.
10. Mapear:
   requisito -> evidencia esperada.
11. Identificar lacunas de rastreabilidade.
12. Criticar inconsistencias.

## Regras
Todo requisito deve possuir pelo menos:

- stakeholder relacionado;
- fluxo critico relacionado;
- criterio verificavel;
- estrategia de teste;
- evidencia observavel.

Nenhum requisito pode ser:

- orfao;
- nao testavel;
- sem stakeholder;
- sem justificativa de negocio.

Se houver requisito sem rastreabilidade:
marcar explicitamente.

## Estrutura obrigatoria da RTM

Cada linha deve rastrear:

| ID | Tipo | Stakeholder | Fluxo Critico | Risco | Componente | Teste | Evidencia | Status |

Onde:

### Tipo
- RF
- RNF

### Status
- Coberto
- Parcial
- Sem cobertura

## Saida
Arquivo:

`documents/03_requirements_traceability_matrix.md`

Formato esperado:

```md
# Requirements Traceability Matrix (RTM)

| ID | Tipo | Stakeholder | Fluxo Critico | Risco | Componente | Teste | Evidencia | Status |
|----|------|--------------|----------------|--------|-------------|--------|------------|--------|
| RF-01 | RF | Time de Dados | FC-01 | CSV corrompido | ETL Python | TC-01 | log de validacao | Coberto |
| RNF-03 | RNF | Plataforma/SRE | FC-04 | falha silenciosa | Observabilidade | TC-08 | logs + metricas | Parcial |
```

Ao final incluir:

## Requisitos orfaos
Requisitos sem rastreabilidade.

## Lacunas detectadas
Exemplo:
- fluxo critico sem teste;
- stakeholder sem requisito;
- RNF sem SLI.

## Riscos sem mitigacao
Riscos do problema ainda nao cobertos.

## Recomendacoes
Sugestoes de melhoria.

## Criterios de aceitacao
- Todo RF rastreado.
- Todo RNF rastreado.
- Todo fluxo critico possui requisito associado.
- Todo stakeholder possui requisito associado.
- Todo requisito possui teste.
- Todo requisito possui evidencia.
- Nenhum requisito orfao.
- Lacunas explicitamente reportadas.