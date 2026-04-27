# Agentic ASOF

Agente de IA para análise e documentação institucional da ASOF.

## Sobre a ASOF

A **Associação Nacional dos Oficiais de Chancelaria do Serviço Exterior Brasileiro** (ASOF) é a entidade representativa da carreira de Oficial de Chancelaria do Ministério das Relações Exteriores.

| | |
|---|---|
| **Sigla** | ASOF |
| **Fundação** | 1993 |
| **Sede** | Brasília, DF |
| **Missão** | Representar os interesses da carreira perante o MRE e o Congresso |
| **Base legal** | Lei 8.829/1993 (cria a carreira de Oficial de Chancelaria) |

## Estrutura do Projeto

```text
agentic-asof/
├── README.md                    # Este arquivo
├── AGENTS.md                    # Diretrizes para agentes de IA
├── requirements.txt             # Dependências Python
├── .env.example                 # Exemplo de variáveis de ambiente
├── .gitignore                   # Arquivos ignorados pelo git
├── agents/                      # Agentes principais do sistema
│   ├── AGENTS.md
│   ├── README.md
│   └── asof-orchestrator/
│       ├── AGENTS.md
│       └── README.md
├── subagents/                   # Subagentes especializados
│   ├── AGENTS.md
│   ├── README.md
│   ├── documental/
│   │   ├── AGENTS.md
│   │   └── README.md
│   ├── email/
│   │   ├── AGENTS.md
│   │   └── README.md
│   └── juridico/
│       ├── AGENTS.md
│       └── README.md
├── workflows/                   # Fluxos multi-etapas
│   ├── AGENTS.md
│   └── README.md
├── operations/                  # Runbooks e rotinas operacionais
│   ├── AGENTS.md
│   └── README.md
└── RAG/
    ├── legal_splitter.py        # Utilitário para dividir documentos legais
    ├── rag.py                   # CLI do sistema RAG
    ├── rag_eval.py              # Avaliação do sistema RAG
    ├── rag_evaluation_results.json
    ├── rag_optimize.py          # Otimização do RAG
    ├── setup_rag.py             # Script de configuração do RAG
    ├── .markdownlintrc          # Regras de linting Markdown
    ├── package.json             # Dependências de desenvolvimento
    ├── package-lock.json
    ├── manual_asof.md           # Manual institucional
    └── legislacoes/             # Legislação federal relevante
        ├── README.md            # Índice de legislação
        ├── marcacoes-planalto.md # Guia de interpretação do Planalto
        ├── lei-XXXX-YYYY.md     # Leis federais
        └── decreto-XXXX-YYYY.md # Decretos federais
```

## Desenvolvimento

## Organização do Repositório

O projeto agora separa explicitamente:

- `RAG/` para corpus, ingestão, avaliação e tooling de recuperação;
- `agents/` para os agentes principais;
- `subagents/` para especializações reutilizáveis;
- `workflows/` para fluxos compostos;
- `operations/` para runbooks e procedimentos operacionais.

Essa separação deixa a raiz pronta para crescer sem misturar base de conhecimento com orquestração e operação.

Estrutura inicial criada:

- `agents/asof-orchestrator/` como agente principal;
- `subagents/juridico/` para base normativa;
- `subagents/email/` para comunicação institucional;
- `subagents/documental/` para organização e ingestão documental.

### Comandos

```bash
# Instalar dependências Node.js
cd RAG && npm install

# Lint em todos os arquivos Markdown do RAG
cd RAG && npx markdownlint-cli "**/*.md" --ignore node_modules

# Lint em arquivo específico
cd RAG && npx markdownlint-cli legislacoes/lei-8112-1990.md
```

### Convenções de Markdown

O projeto usa `markdownlint-cli` com regras personalizadas:

- **Linha máxima**: 600 caracteres
- **MD033** (HTML inline): Desativado para documentos legais
- **MD041** (primeira linha de heading): Desativado

### Estrutura de Legislação

Os arquivos de legislação seguem o formato:

```markdown
# Lei n.º XXXX, de DD de mês de YYYY

**Fonte oficial:** <https://www.planalto.gov.br/ccivil_03/...>

**Ementa:** Breve descrição do propósito da lei

## Texto integral

[Conteúdo do Portal do Planalto]
```

Nome do arquivo: `{tipo}-{numero}-{ano}.md` (ex: `lei-8112-1990.md`)

### Estratégia de Branches

- `main` — documentação pronta para produção
- `feat/descricao-breve` — novas funcionalidades ou análises
- `fix/nome-do-arquivo` — correções

### Convenções de Commit

Mensagens de commit em português (pt-BR):

```
<tipo>: <descrição curta>

<corpo opcional com detalhes>
```

Tipos:
- `docs` — adiciona ou atualiza documentação
- `feat` — nova funcionalidade ou análise
- `fix` — correção de erro
- `refactor` — reorganização sem mudança de conteúdo
- `chore` — tarefas de manutenção

### Workflow de Análise

1. Documentar atividades em `RAG/manual_asof.md` ou arquivos de análise
2. Categorizar por potencial de automação:
   - **Alta** — repetitivas, baseadas em regras, intensivas em dados
   - **Média** — requerem julgamento, mas estruturadas
   - **Baixa** — criativas, interpessoais, interpretação regulatória
3. Vincular a legislação de apoio
4. Estimar economia de tempo/esforço se automatizado

### Expansão do Agente

Para novos componentes:

1. Coloque conhecimento-base e corpus em `RAG/`
2. Coloque definições de agentes em `agents/`
3. Coloque especializações em `subagents/`
4. Coloque fluxos compostos em `workflows/`
5. Coloque procedimentos recorrentes em `operations/`

## Começando

### Variáveis de Ambiente

Copie `.env.example` para `.env` e configure as variáveis necessárias:

```bash
cp .env.example .env
```

### Configuração do RAG

```bash
# Configurar variáveis de ambiente no arquivo .env
# Executar o script de configuração
python RAG/setup_rag.py
```

## License

Este projeto é para fins de análise e documentação institucional.

## Contato

ASOF — Associação Nacional dos Oficiais de Chancelaria do Serviço Exterior Brasileiro
