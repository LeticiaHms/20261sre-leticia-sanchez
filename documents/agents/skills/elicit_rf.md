# skills/elicit_rf.md

## Quando usar
Quando o usuario pedir requisitos funcionais e ja existir
`spec/00_problem.md`.

Tambem usar quando:
- existir `documents/01_problem_modeling.md`;
- existir modelagem de stakeholders e fluxos criticos;
- houver necessidade de transformar necessidades do negocio em comportamento do sistema.

## Entrada
- `spec/00_problem.md` (obrigatorio)
- `documents/01_problem_modeling.md` (opcional)
- `documents/02_non_functional_requirements.md` (opcional)

## Passos
1. Ler stakeholders, objetivos de negocio e fluxos criticos.
2. Identificar capacidades do sistema a partir do problema.
3. Converter fluxos criticos em funcionalidades observaveis.
4. Derivar RFs orientados a comportamento do sistema.
5. Garantir rastreabilidade stakeholder -> fluxo -> requisito.
6. Marcar prioridade usando MoSCoW.
7. Relacionar dependencias entre RFs quando existirem.
8. Identificar ambiguidades e premissas.

## Regras de elaboracao
- Requisitos devem descrever comportamento observavel do sistema.
- Usar verbos objetivos:
  - deve validar;
  - deve processar;
  - deve registrar;
  - deve detectar;
  - deve persistir.
- Evitar linguagem vaga:
  - "ser inteligente";
  - "funcionar bem";
  - "ser moderno".
- Todo RF deve possuir criterio verificavel.
- RF deve ser independente de implementacao quando possivel.

Ruim:
> O sistema deve ser confiavel.

Bom:
> RF-03: O sistema deve validar a integridade do CSV antes da ingestao.

## Estrutura do requisito
Cada requisito deve conter:

- ID
- Nome
- Descricao
- Stakeholder relacionado
- Fluxo critico relacionado
- Prioridade (MoSCoW)
- Criterio de aceitacao
- Dependencias
- Riscos associados (quando aplicavel)

## Saida
Arquivo:
`documents/01_functional_requirements.md`

Formato esperado:

```md
# Requisitos Funcionais

## RF-01 - Validar integridade do CSV

### Descricao
O sistema deve validar schema, encoding e integridade do arquivo CSV antes do processamento.

### Stakeholders
- Time de Dados
- Plataforma/SRE

### Fluxo critico relacionado
FC-01 - Ingestao de Arquivos

### Prioridade
Must Have

### Criterios de aceitacao
- rejeitar CSV corrompido;
- registrar erro no log;
- impedir processamento parcial.
```

Ao final incluir:

- matriz de rastreabilidade;
- premissas;
- ambiguidades;
- riscos identificados.

## Criterios de aceitacao
- Todo stakeholder relevante possui RF associado.
- Todo fluxo critico possui pelo menos 1 RF.
- IDs `RF-NN` unicos.
- Nenhum RF e aspiracional.
- Todo RF possui criterio verificavel.
- Existe rastreabilidade stakeholder -> fluxo -> RF.