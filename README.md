# Rolê SP

Agenda cultural de São Paulo e arredores: https://paulonaressi.github.io/role-sp/

## Como a agenda é montada

1. Cada área tem um arquivo em `dados/`, gerado por um "pesquisador" seguindo o `ESQUEMA.md`:
   `cinema.json`, `infantil.json`, `permanentes.json`, `sesc_gratuitos.json`, `shows.json`,
   `teatro_exposicoes.json` e `promocoes.json` (promoções dos lugares fixos, ligadas pelo título).
2. `python3 -I consolidar.py` junta tudo em `eventos.json`: valida, normaliza, descarta o que já passou
   e promoções vencidas, e remove duplicatas. Aceita uma data de referência opcional (`AAAA-MM-DD`).
3. `index.html` lê o `eventos.json`. A página não guarda dado pessoal: o mês de nascimento usado no
   cálculo de gratuidade vem do link (`?nasc=AAAA-MM`) e fica só no navegador.

A atualização roda por tarefa agendada (segunda e quinta de manhã), que refaz os arquivos de `dados/`,
consolida, faz push aqui e republica o artifact privado.

`consolidar.py` é o original do projeto com um ajuste: em duplicata de evento com data única, junta as
datas em vez de descartar a segunda (antes, Hayley Williams 13/11 e New Order 25/11 sumiam).
