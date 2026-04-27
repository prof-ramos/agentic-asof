# AGENTS.md — `subagents/`

## Finalidade

Esta pasta contém subagentes especializados usados pelos agentes principais.

Subagentes devem ter escopo mais estreito, contexto mais controlado e saídas mais previsíveis do que agentes de topo.

## O que pertence aqui

- especializações por domínio;
- contratos de entrada e saída;
- checklists de uso;
- restrições e limites de atuação;
- critérios de escalonamento para agente principal ou humano.

## O que nao pertence aqui

- orquestração global do sistema;
- corpus bruto de RAG;
- runbooks de manutenção;
- documentação institucional geral sem vínculo funcional.

## Convenções

- um diretório por subagente;
- cada subagente deve ter `README.md` e `AGENTS.md`;
- o foco deve ser tarefa clara e reutilizável;
- sempre explicitar quando o subagente pode responder sozinho e quando deve escalar.

## Critério de desenho

Um bom subagente:

- resolve um tipo reconhecível de problema;
- trabalha com contexto limitado;
- produz saída padronizável;
- evita assumir decisões estratégicas amplas sem validação.

