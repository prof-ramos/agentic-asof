# Como Ler as Marcações do Planalto

Este documento explica como interpretar as marcações encontradas nos HTMLs oficiais do Portal do Planalto e refletidas na conversão para Markdown em [README.md](README.md).

## Regra principal

Nem toda tag HTML do Planalto tem significado jurídico.

Ao analisar um trecho, separe sempre:

- marcações estruturais, usadas para navegação;
- marcações visuais, usadas só para apresentação;
- marcações editoriais, usadas para mostrar histórico de redação;
- marcações materiais, que efetivamente sugerem perda de vigência ou superação de texto.

## Marcações que nao indicam invalidade

As marcações abaixo, sozinhas, nao significam que o artigo perdeu vigência:

- `<span id="art20"></span>`
- `<span style="color:black">...</span>`
- `<span style="font-style:normal">...</span>`
- `<span style="font-family:Arial">...</span>`

Significado:

- `id="art20"` cria uma âncora para link interno no artigo.
- `color:black` é apenas cor de fonte.
- `font-style:normal` é apenas ajuste tipográfico.
- `font-family` e estilos semelhantes sao apenas apresentação.

Essas tags podem aparecer tanto em texto vigente quanto em texto historico.

## Marcações que costumam indicar historico ou redacao superada

Os sinais mais importantes sao os de tachado ou substituição editorial. Na prática, eles aparecem de algumas formas:

- `text-decoration: line-through`
- tags HTML como `<strike>`, `<s>` ou blocos equivalentes
- no Markdown convertido, `~~texto~~`

Quando um artigo ou inciso aparece tachado, a leitura padrão deve ser:

- aquele bloco foi preservado por valor historico;
- aquela redação nao é a redação corrente;
- a redação vigente costuma aparecer logo depois, sem tachado.

## Notas editoriais do Planalto

Expressões como estas nao revogam nada por si sós:

- `Redação dada pela Lei ...`
- `Redação dada pela Medida Provisória ...`
- `Incluído pela Lei ...`
- `Revogado pela Lei ...`
- `Vide ...`

Como interpretar:

- `Redação dada pela ...` informa a origem da redação daquele trecho.
- `Incluído pela ...` informa que o dispositivo foi acrescentado por norma posterior.
- `Revogado pela ...` é um forte sinal material de que o trecho nao está vigente.
- `Vide ...` normalmente aponta para outra norma relacionada, sem alterar sozinho a vigência.

## Exemplo pratico: art. 20 da Lei 8.112

No art. 20 da Lei n.º 8.112/1990, o HTML consolidado do Planalto mistura versões historicas e a versão exibida como atual.

O que observar:

- o `span id="art20"` apenas ancora o artigo;
- o texto com tachado representa redação superada;
- a indicação `Redação dada pela Medida Provisória nº 431, de 2008` é uma nota editorial sobre a origem daquela versão;
- a presença de `~~...~~` na conversão para Markdown é o sinal mais confiável de que aquela redação foi mantida apenas para histórico.

## Heuristica recomendada para leitura

Ao analisar qualquer artigo convertido do Planalto, use esta ordem:

1. Verifique se o trecho está tachado.
2. Procure notas como `Revogado pela ...`.
3. Identifique se existe uma versão posterior nao tachada logo abaixo.
4. Trate `id`, `color`, `font-style` e outras propriedades de estilo apenas como suporte visual.

## Limites desta leitura

Mesmo no Portal do Planalto, a consolidação pode misturar:

- redações antigas;
- redações intermediárias;
- observações editoriais;
- remissões para outras normas.

Por isso, para afirmar com segurança qual é a redação vigente, a melhor leitura é:

- localizar o trecho nao tachado;
- conferir as notas `Revogado`, `Redação dada`, `Incluído` e `Vide`;
- quando houver dúvida, confirmar a cadeia de alterações na própria norma apontada pelo link do Planalto.
