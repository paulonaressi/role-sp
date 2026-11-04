# Esquema dos eventos (um arquivo JSON por pesquisador: um array de objetos)

Janela: da data da execução até 4 semanas depois (eventos com data), mais temporadas/exposições em cartaz nesse período e atrações permanentes (parques, fazendinhas).

Campos (todos em português; use null quando não souber, nunca invente):

```json
{
  "titulo": "Nome do evento",
  "categoria": "show | teatro | cinema | infantil | exposicao | passeio | festival | danca | standup | esporte | gastronomia",
  "subcategoria": "ex.: MPB, musical, stand-up, fazendinha, mostra de cinema",
  "descricao": "1-2 frases curtas, escritas por você (não copie o texto do site), máx. 220 caracteres",
  "tipo_data": "unica | temporada | permanente",
  "datas": [{"data": "2026-11-07", "hora": "20:00"}],
  "inicio": "2026-11-01",
  "fim": "2026-12-14",
  "dias_horarios": "texto livre p/ temporada ou permanente, ex.: 'qui a sáb 20h, dom 18h' ou 'sáb, dom e feriados 9h-17h'",
  "local": "Nome do local",
  "endereco": "Rua, número",
  "bairro": "Bairro",
  "cidade": "São Paulo",
  "regiao": "Centro | Zona Sul | Zona Oeste | Zona Norte | Zona Leste | Grande SP | Interior/Litoral",
  "preco_min": 0,
  "preco_max": 180,
  "gratuito": false,
  "faixa_etaria": "Livre | 10 anos | 14 anos | 16 anos | 18 anos | a partir de 2 anos ...",
  "bom_para_criancas": true,
  "link": "URL da página do evento ou da compra",
  "fonte": "Nome do site onde achou (Sympla, Sesc SP, etc.)"
}
```

Regras:
- `datas` preenchido para tipo_data "unica" (pode ter várias datas). Para "temporada" use inicio/fim + dias_horarios. Para "permanente", só dias_horarios.
- Só inclua o que você viu numa fonte. Preço em reais, número (sem "R$"). Se só tem "a partir de", preencha só preco_min.
- `bom_para_criancas`: true quando é feito para crianças pequenas (até ~6 anos) ou claramente adequado a elas.
- Datas em ISO (AAAA-MM-DD), horas HH:MM.
- Salve o arquivo como JSON válido (valide com `python3 -I -c "import json,sys;json.load(open(sys.argv[1]))" ARQUIVO`).

## Promoções
- Em qualquer item, se a fonte mostrar uma promoção vigente (desconto, cupom, combo família, criança não paga, compra antecipada mais barata, Black Friday), preencha `"promocao": {"texto": "máx. 140 caracteres, com o valor", "validade": "AAAA-MM-DD ou null", "link": "URL da promoção", "fonte": "site", "verificado_em": "AAAA-MM-DD"}`. Senão, `null`. Meia-entrada de lei e gratuidade fixa não são promoção.
- Promoções dos lugares fixos (fazendinhas, parques, museus) ficam em `dados/promocoes.json`: array de objetos com os mesmos campos mais `"titulo"` igual ao título do lugar em `permanentes.json`. O `consolidar.py` liga a promoção ao lugar e descarta as vencidas.

## Gratuidade para crianças (lugares fixos)
Em `permanentes.json`, cada lugar pago pode ter `"gratis_crianca": {"regra": "texto curto, ex.: até 3 anos e 11 meses não pagam", "idade_max_meses": 47, "verificado_em": "AAAA-MM-DD"}`. `idade_max_meses` é a última idade, em meses, que ainda entra grátis (menores de 2 anos = 23; até 3 anos = 47 se a regra é "até 3 anos e 11 meses", 35 se é "menores de 3"). Use `null` quando a visita é grátis para todos. O painel usa isso para dizer até quando a Nina não paga.
