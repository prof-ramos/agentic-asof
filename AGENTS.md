# AGENTS.md — AGENTIC ASOF

Repository for analyzing agentic AI implementation for ASOF (Associação Nacional dos Oficiais de Chancelaria do Serviço Exterior Brasileiro).

## Project Goal

**Primary objective:** Analyze and determine what percentage of ASOF's activities can be automated using AI agents.

This involves:

- Mapping ASOF's operational workflows and processes (documented in `RAG/manual_asof.md`)
- Identifying repetitive, rule-based, or knowledge-intensive tasks
- Assessing automation feasibility across different activity categories
- Providing data-driven estimates of AI automation potential

## Project Structure

```text
├── README.md                 # Basic project description (pt-BR)
├── agents/                   # Main agents
│   └── asof-orchestrator/    # Primary coordinator agent
├── subagents/                # Specialized subagents
│   ├── juridico/             # Legal and normative analysis
│   ├── email/                # Institutional communication triage
│   └── documental/           # Document organization and ingestion
├── workflows/                # Multi-step workflows
├── operations/               # Runbooks and operational routines
└── RAG/                      # Corpus and tooling for retrieval
    ├── manual_asof.md        # Institutional manual for ASOF
    ├── legislacoes/          # Brazilian federal legislation (leis/decretos)
    │   ├── README.md         # Index of all legislation files
    │   ├── marcacoes-planalto.md  # Guide to interpreting Planalto HTML markup
    │   ├── lei-XXXX-YYYY.md  # Laws (Lei n.º XXXX/YYYY)
    │   └── decreto-XXXX-YYYY.md   # Decrees (Decreto n.º XXXX/YYYY)
    ├── .markdownlintrc       # Markdown linting rules
    ├── package.json          # Dev dependencies only
    ├── rag.py                # RAG CLI
    └── setup_rag.py          # RAG setup script
```

## Language

**All content is in Portuguese (pt-BR)** — including documentation, comments, commit messages, and metadata.

## Convenções de Escrita em pt-BR

Ao redigir textos em português brasileiro, seguem-se as normas da ** ABNT NBR 10520** (informações técnicas em documentos) e as convenções estabelecidas pela **Portaria nº 1号, de 23 de outubro de 1995** da Casa Civil, que padronizam a redação oficial.

### Pontuação

| Símbolo | Uso em pt-BR | Exemplo |
| --- | --- | --- |
| `.` (ponto) | Separar decimais, indicar final de frase | `R$ 1.500,00` — vírgula para decimais; ponto para milhares |
| `,` (vírgula) | Separar elementos de enumeração, decimais | `Primeiro, Segundo, Terceiro` |
| `:` (dois-pontos) | Introduzir citação, lista, explicação | `Conforme dispões o artigo 5.º:` |
| `;` (ponto-e-vírgula) | Separar orações coordenadas já separadas por vírgula | `compareceu; contudo, não participou` |
| `—` (travessão) | Indicar mudança de interlocutor em diálogo | `— Pergunto — respondeu o testemunha` |
| `...` (reticências) | Indicar interrupção ou hesitação | `Não sei se devo...` |

### Cifrão e Moeda

- Símbolo monetário precede o número: `R$ 1.500,00`
- Usar vírgula como separador decimal
- Usar ponto como separador de milhar
- Não usar espaço entre símbolo e número: `R$ 1.500,00` (não `R$ 1.500,00`)

### Abreviações e Convenções Legais

| Abreviação | Significado | Uso |
| --- | --- | --- |
| `n.º` | número (com ponto após "o") | `Lei n.º 8.829/1993` |
| `art.` | artigo | `art. 3.º` |
| `§` | parágrafo | `§ 1.º` |
| `cap.` | capítulo | `cap. III` |
| `inc.` | inciso | `inc. I do art. 5.º` |
| `alínea` | alínea | `alínea "a"` |
| `cit.` | obra citada | `Ibidem, op. cit.` |
| `op. cit.` | obra citada | `Fernandes, 2020, op. cit.` |
| `id.` | ibidem (mesma obra) | `Id., ibidem` |
| `s./n.` | sem número | `Rua das Flores, s./n.` |
| `s./l.` | sem local | `s./l.: s./n., 2020` |
| `s./d.` | sem data | `Publicação s./d.` |

### Números Ordinais

- Usar `.º` / `.ª` após o número: `1.º`, `2.ª`
- Em textos legais: `art. 5.º`, `§ 2.º`, `inc. III`
- Não usar `º` sozinho (sempre com número)

### Numeração de Artigos e Parágrafos

```text
Art. 1.º — Definições...
Art. 2.º...
§ 1.º A...
§ 2.º...
§ 3.º...
Parágrafo único. (quando houver apenas um parágrafo)
```

### Formas de Tratamento

| Tratamento | Abreviatura | Contexto |
| --- | --- | --- |
| Vossa Excelência | V. Ex.ª | Documentos oficiais |
| Senhor | Sr. | Correspondência |
| Senhora | Sra. | Correspondência |
| Doutor | Dr. | Profissionais universitários |
| Ilustríssimo | Ilmo. | Cartas formais |

### Nomes de Leis e Decretos

```text
Lei n.º 8.829, de 27 de janeiro de 1993
Decreto n.º 1.565, de 6 de setembro de 1995
Lei n.º 12.601, de 2012 (pode omitir dia/mes se não relevante)
```

### Citação de Artigos em Referências

- Artigo específico: `art. 5.º, inc. I, da Lei 8.829/1993`
- Múltiplos incisos: `art. 5.º, incs. I e II`
- Parágrafos: `art. 5.º, § 1.º`
- Seção: `art. 5.º, cap. II, seç. 1.ª`

### Conjunções e Conectivos

- Preferir conectivos claros em vez de abreviações
- Evitar uso excessivo de "etc." (usar "entre outros" ou "dentre outros")
- Em documentos legais, preferir formas completas

### Uso de Aspas

- Citação direta: `"texto"` (aspas duplas brasileiras)
- Citação dentro de citação: `'texto dentro de aspas'`
- Termos em destaque: `usar "termo"` com aspas, não itálico

### Hífen em Palavras Compostas

Seguir o **Vocabulário Ortográfico da Língua Portuguesa (VOLP)**:

- Prefixos terminados em vogal + raiz começada por vogal: `anti-inflacionário`, `semi-internacional`
- Prefixos terminados em consoante + raiz começada por vogal: `autoescola`, `superrápido`
- Advérbios terminados em `-mente`: `claramente`, `recentemente`

### Siglas

- Primeira ocorrência: escrever por extenso com sigla entre parênteses
- `Supabase (pgvector)` na primeira menção
- Usar apenas a sigla nas menções subsequentes
- Não pluralizar siglas: "os CPF" não "os CPFs"

## Development Commands

All commands run from `RAG/` directory:

```bash
cd RAG

# Install dependencies
npm install

# Lint markdown files
npx markdownlint-cli "**/*.md" --ignore node_modules

# Lint specific file
npx markdownlint-cli legislacoes/lei-8112-1990.md
```

## Repository Boundaries

Use these directories consistently:

- `RAG/` for retrieval corpus, indexing, chunking, and evaluation artifacts
- `agents/` for definitions of top-level agents
- `subagents/` for specialized worker or helper agents
- `workflows/` for orchestrated multi-step flows
- `operations/` for runbooks, maintenance procedures, and recurring operational tasks

Do not mix new agent specs into `RAG/` unless they are directly part of retrieval or corpus preparation.

## Markdown Conventions

The repository uses `markdownlint-cli` with custom rules (see `.markdownlintrc`):

- **Line length**: 600 characters max (well beyond default 80)
- **MD033** (inline HTML): Disabled — legislation files contain HTML from Portal do Planalto
- **MD041** (first-line heading): Disabled

When editing legislation files, **preserve original HTML structure** from Portal do Planalto — it contains semantic annotations for legal interpretation.

## Legislation File Format

Standard header for new legislation files:

```markdown
# Lei n.º XXXX, de DD de mês de YYYY

**Fonte oficial:** <https://www.planalto.gov.br/ccivil_03/...>

**Ementa:** Brief description of the law's purpose

## Texto integral

[Content from Portal do Planalto]
```

File naming: `{tipo}-{numero}-{ano}.md` where tipo is `lei` or `decreto`.

## Understanding Planalto Markup

Legislation files are converted from Portal do Planalto HTML. Key conventions (documented in `RAG/legislacoes/marcacoes-planalto.md`):

- **`~~texto~~`** (strikethrough): Indicates superseded/historical text, not current law
- **`<span id="artX">`**: Anchor for internal navigation only — no legal significance
- **`Redação dada pela Lei...`**: Editorial note indicating origin of text version
- **`Revogado pela Lei...`**: Strong indicator the provision is no longer in force
- **Style attributes** (`color`, `font-style`): Presentation only — ignore for legal analysis

When analyzing legislation programmatically, prioritize non-strikethrough text and verify current status through cross-references.

## Adding New Legislation

1. Download/consolidate from [Portal do Planalto](https://www.planalto.gov.br/legislacao)
2. Convert to Markdown preserving HTML structure
3. Add entry to `legislacoes/README.md` index
4. Run linter: `npx markdownlint-cli legislacoes/novo-arquivo.md`

## Development Workflow

### Branch Strategy

- `main` — production-ready documentation
- Feature branches for new legislation or analysis: `feat/descricao-breve`
- Fix branches for corrections: `fix/nome-do-arquivo`

### Commit Conventions

**All commit messages in Portuguese (pt-BR):**

```text
<type>: <descrição curta>

<corpo opcional com detalhes>
```

Types:

- `docs` — adiciona ou atualiza documentação
- `feat` — nova funcionalidade ou análise
- `fix` — correção de erro
- `refactor` — reorganização sem mudança de conteúdo
- `chore` — tarefas de manutenção

Examples:

```text
docs: adiciona Lei 15.141/2025

Inclui texto integral da lei sobre promoções na carreira
de Oficial de Chancelaria.
```

### Code Review Process

1. **Self-review before PR** — verifique:
   - Markdown lint passa (`npx markdownlint-cli`)
   - Links para Portal do Planalto estão corretos
   - Ementa está presente e precisa
   - Estrutura HTML original foi preservada

2. **Review checklist for legislation**:
   - [ ] Cabeçalho segue o formato padrão
   - [ ] Fonte oficial é URL válida do Planalto
   - [ ] Nome do arquivo segue convenção `{tipo}-{numero}-{ano}.md`
   - [ ] Entrada adicionada ao `legislacoes/README.md`
   - [ ] Não há informações sensíveis (CPFs, dados pessoais de associados)

### Analysis Workflow

For automation feasibility analysis (the main project goal):

1. Document activity in `RAG/manual_asof.md` or dedicated analysis file
2. Categorize by automation potential:
   - **High** — repetitive, rule-based, data-heavy
   - **Medium** — requires some judgment, but structured
   - **Low** — creative, interpersonal, regulatory interpretation
3. Link to supporting legislation
4. Estimate time/effort savings if automated

### File Organization

```text
RAG/
├── manual_asof.md              # Institutional context (read-only reference)
├── legislacoes/                # Official legislation (authoritative source)
│   ├── README.md              # Master index
│   └── lei-XXXX-YYYY.md       # Individual laws
├── analises/                   # [Future] Automation analysis outputs
│   └── categoria-atividade.md
└── templates/                  # [Future] Reusable templates
    └── legislacao-template.md
```

## Integrations

### Database (Supabase)

Supabase project configured for data persistence and real-time features.

**Project Reference:** `aerkqudrangsqrdsfsys`

Setup commands:
```bash
supabase login          # Authenticate with Supabase CLI
supabase init           # Initialize local Supabase project
supabase link --project-ref aerkqudrangsqrdsfsys  # Link to remote project
```

**Note:** Run these commands to connect your local environment to the Supabase project for database access, edge functions, and real-time subscriptions.

**MCP Integration:**
The Supabase MCP server is configured in `~/.config/opencode/opencode.json`:

```json
{
  "mcp": {
    "supabase": {
      "type": "remote",
      "url": "https://mcp.supabase.com/mcp?project_ref=aerkqudrangsqrdsfsys",
      "enabled": true
    }
  }
}
```

Authenticate with: `opencode mcp auth supabase`

**Agent Skills:**
Installed Supabase skills for enhanced AI assistance:

- `supabase` — Core Supabase operations
- `supabase-postgres-best-practices` — PostgreSQL best practices

Install with: `npx skills add supabase/agent-skills --yes --global`

### Email (Google Workspace)

The project uses `gogcli` (Google CLI for Terminal) for email automation and Google Workspace integration.

**Reference documentation:** <https://context7.com/steipete/gogcli/llms.txt?tokens=10000>

Key capabilities for ASOF automation:

- **Gmail**: Search, send, label management, drafts, watch/webhook setup
- **Gmail**: Search, send, label management, drafts, watch/webhook setup
- **Calendar**: Event creation, availability checking, meeting management
- **Drive**: File upload/download, permissions, organization
- **Docs/Sheets/Slides**: Document creation and manipulation

Authentication requires OAuth2 setup via Google Cloud Console. Credentials stored in OS keychain or encrypted file.

### Slack

Slack app integration configured for notifications and bot interactions.

**App ID:** `your-app-id`

Environment variables (stored in `.env` — never commit this file):
```bash
SLACK_APP_ID=your-app-id
SLACK_CLIENT_ID=your-client-id
SLACK_CLIENT_SECRET=your-client-secret
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_VERIFICATION_TOKEN=your-verification-token
```

**Security notes:**
- Use `SLACK_SIGNING_SECRET` to verify requests come from Slack (recommended)
- `SLACK_VERIFICATION_TOKEN` is deprecated but still functional
- Store credentials in `.env` only — never in code or public repos

## RAG System (Legal Document Search)

Retrieval-Augmented Generation system for semantic search over ASOF legal documents.

**Stack:**

- **Vector DB**: Supabase pgvector (PostgreSQL extension)
- **Embeddings**: OpenAI text-embedding-3-small (1536 dimensions)
- **Chunking**: MarkdownHeaderTextSplitter (by headers #, ##, ###)
- **Similarity**: Cosine distance with HNSW index

**Setup:**
```bash
# 1. Install dependencies
uv add -r requirements.txt
# or: pip install -r requirements.txt

# 2. Set environment variables
export SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
export OPENAI_API_KEY=your-openai-key

# 3. Apply database migration
python rag.py migrate

# 4. Index documents
python rag.py index

# 5. Query
python rag.py query --query "direitos dos oficiais de chancelaria"
```

**Files:**
- `rag.py` — Main CLI (migrate, index, query commands)
- `supabase/migrations/20250427020000_create_documents.sql` — Database schema
- `requirements.txt` — Python dependencies

**Database Schema:**
```sql
documents (
  id SERIAL PRIMARY KEY,
  content TEXT NOT NULL,
  metadata JSONB,
  embedding VECTOR(1536),
  created_at TIMESTAMP
)
```

### RAG Quality Evaluation

Evaluate and optimize RAG performance:

```bash

Evaluate and optimize RAG performance:

```bash
# Analyze chunk statistics
python rag_eval.py analyze

# Run quality evaluation
python rag_eval.py evaluate

# Reindex with optimized chunking
python rag_optimize.py reindex
```

**Current Metrics (Baseline):**
- Retrieval Precision: 53% — Moderate (room for improvement)
- Retrieval Recall: 70% — Good coverage
- Context Relevance: 100% — Excellent relevance

**Optimization Recommendations:**
1. **Chunk Size**: Current average ~44KB is too large. Target: 1000 tokens (~4000 chars)
2. **Chunk Overlap**: Use 200 tokens overlap for context continuity
3. **Separators**: Prioritize `\n## `, `\n### `, `\n\n`, `\n`, `. `, ` `
4. **Embedding Model**: text-embedding-3-small is cost-effective; upgrade to -large for better accuracy
5. **Index Type**: HNSW with cosine similarity (already optimal)

**Files:**
- `rag_eval.py` — Evaluation metrics and test cases
- `rag_optimize.py` — Reindexing with token-based chunking
- `rag_evaluation_results.json` — Evaluation results

## No Build/Test Pipeline

This is a documentation repository — no build step, tests, or deployment. Validation is markdown linting only.

## ASOF Context

ASOF represents ~763 associates (active, retired, and pensioner chancery officers). Key facts for context:
- CNPJ: 26.989.392/0001-57
- Founded: April 1991
- Mission: Represent career interests before MRE (Ministério das Relações Exteriores) and Congress
- Legal basis: Lei 8.829/1993 (creates Chancery Officer career)

Full institutional details in `RAG/manual_asof.md`.
