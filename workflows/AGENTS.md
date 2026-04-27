# AGENTS.md — `workflows/`

## Finalidade

Esta pasta contém fluxos multi-etapas do sistema.

Workflows descrevem a sequência entre agente principal, subagentes, pontos de validação humana, insumos de RAG e critérios de conclusão.

## O que pertence aqui

- fluxos ponta a ponta;
- handoffs entre componentes;
- estados intermediários;
- critérios de sucesso, retry e fallback;
- checkpoints de revisão humana.

## O que nao pertence aqui

- instruções internas detalhadas de um único agente;
- runbooks de manutenção;
- legislação ou corpus base;
- notas soltas sem fluxo definido.

## Convenções

- um diretório por workflow quando ele justificar desdobramento;
- workflows curtos podem começar com um `README.md`;
- workflows mais robustos devem incluir `inputs.md`, `outputs.md` ou artefatos equivalentes.

## Regra prática

Se o conteúdo responde “como vários componentes cooperam?”, ele tende a pertencer em `workflows/`.

