# skills/elicit_rnf.md

## Quando usar
Quando o usuario pedir RNFs e ja existir
`spec/00_problem.md`
e/ou
`documents/01_functional_requirements.md`.

Usar especialmente quando:
- existir modelagem do problema;
- houver stakeholders definidos;
- existirem fluxos criticos;
- houver necessidade de estabelecer qualidade do sistema.

## Entrada
- `spec/00_problem.md` (obrigatorio)
- `documents/01_functional_requirements.md` (opcional)
- `documents/01_problem_modeling.md` (opcional)

## Passos
1. Ler stakeholders e fluxos criticos do problema.
2. Identificar riscos operacionais e propriedades emergentes.
3. Mapear os fluxos aos 8 atributos da ISO 25010.
4. Relacionar RNFs aos riscos do sistema.
5. Para cada atributo, propor de 1 a 3 RNFs mensuraveis.
6. Definir:
   - SLI;
   - SLO;
   - unidade;
   - janela;
   - fonte de medicao.
7. Marcar prioridade MoSCoW.
8. Relacionar RNFs aos RFs quando aplicavel.
9. Registrar premissas e ambiguidades.

## Regras de elaboracao
Todo RNF deve ser:

- mensuravel;
- verificavel;
- observavel;
- temporal;
- associado a uma fonte de medicao.

Proibido:

- "o sistema deve ser rapido"
- "o sistema deve ser seguro"
- "o sistema deve ser confiavel"

Obrigatorio explicitar:
- valor;
- unidade;
- janela;
- fonte.

Ruim:
> O sistema deve ser confiavel.

Bom:
> RNF-01: A taxa de falha do pipeline deve ser menor que 1% por dia, medida pelos logs do ETL.

## Atributos obrigatorios (ISO 25010)
Cobrir obrigatoriamente:

1. Adequacao funcional
2. Eficiencia de desempenho
3. Compatibilidade
4. Usabilidade
5. Confiabilidade
6. Seguranca
7. Manutenibilidade
8. Portabilidade

Nao deixar atributo sem avaliacao.
Caso nao aplicavel:
justificar explicitamente.

## Estrutura do requisito
Cada RNF deve conter:

- ID
- Atributo ISO 25010
- Descricao
- Stakeholder impactado
- Fluxo critico relacionado
- SLI
- SLO
- Unidade
- Janela
- Fonte de medicao
- Prioridade (MoSCoW)
- Risco mitigado

Formato esperado:

```md
## RNF-01 - Confiabilidade da ingestao

### Atributo ISO 25010
Confiabilidade

### Descricao
A taxa de falha da ingestao deve permanecer abaixo de 1%.

### Stakeholder impactado
- Time de Dados
- Plataforma/SRE

### Fluxo critico relacionado
FC-01 - Ingestao de Arquivos

### SLI
Taxa de falha da ingestao

### SLO
< 1%

### Unidade
Percentual

### Janela
Diaria

### Fonte
Logs do ETL

### Prioridade
Must Have

### Risco mitigado
Falha silenciosa de ingestao
```

## Saida
Arquivo:
`documents/02_non_functional_requirements.md`

Obrigatorio conter:
- secao por atributo ISO 25010;
- IDs `RNF-NN` unicos;
- tabela consolidada final:

| ID | atributo | SLI | SLO | unidade | janela | fonte | prioridade |

Ao final incluir:
- premissas;
- ambiguidades;
- riscos residuais.

## Criterios de aceitacao
- 8 atributos ISO 25010 cobertos.
- Todo RNF possui unidade.
- Todo RNF possui janela.
- Todo RNF possui fonte de medicao.
- IDs `RNF-NN` unicos.
- Nenhum RNF aspiracional.
- Todo RNF mitiga um risco explicito.
- Existe rastreabilidade fluxo -> risco -> RNF.