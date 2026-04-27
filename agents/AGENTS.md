# AGENTS.md — `agents/`

## Finalidade

Esta pasta contém os agentes principais do projeto.

Cada subdiretório dentro de `agents/` representa um agente de alto nível com responsabilidade ampla de coordenação ou execução de uma frente funcional.

## O que pertence aqui

- definição de papel do agente;
- escopo funcional;
- entradas e saídas esperadas;
- dependências em `RAG/`, `subagents/`, `workflows/` e `operations/`;
- regras de orquestração e delegação.

## O que nao pertence aqui

- corpus documental bruto;
- legislação e materiais de indexação;
- runbooks operacionais;
- utilitários genéricos sem vínculo claro com um agente.

## Convenções

- um diretório por agente principal;
- cada agente deve ter `README.md` e `AGENTS.md`;
- nomes de diretório em kebab-case;
- o `README.md` descreve o agente;
- o `AGENTS.md` define instruções para quem for trabalhar naquele diretório.

## Relação com outras áreas

- consulte `RAG/` para base normativa e institucional;
- use `subagents/` para especializações reutilizáveis;
- documente fluxos compostos em `workflows/`;
- documente procedimentos recorrentes em `operations/`.

