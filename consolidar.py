"""Junta dados/*.json em eventos.json: valida, normaliza e remove duplicatas.

Uso: python3 -I consolidar.py [AAAA-MM-DD]   (data de referência; padrão = hoje em São Paulo)
"""
import datetime as dt
import glob
import json
import os
import re
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
HOJE = sys.argv[1] if len(sys.argv) > 1 else dt.datetime.now(dt.timezone(dt.timedelta(hours=-3))).date().isoformat()
CATS = {"show", "teatro", "cinema", "infantil", "exposicao", "passeio", "festival",
        "danca", "standup", "esporte", "gastronomia"}
REGIOES = {"Centro", "Zona Sul", "Zona Oeste", "Zona Norte", "Zona Leste", "Grande SP", "Interior/Litoral"}


def chave(texto):
    t = unicodedata.normalize("NFD", str(texto or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def numero(v):
    if v is None or v == "":
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v)
    if "," in s:  # formato brasileiro: 1.200,50
        s = s.replace(".", "").replace(",", ".")
    m = re.search(r"\d+(?:\.\d+)?", s)
    return float(m.group()) if m else None


def promocao_valida(p):
    """Promoção só entra com texto e sem validade vencida."""
    if not isinstance(p, dict) or not p.get("texto"):
        return None
    if p.get("validade") and str(p["validade"]) < HOJE:
        return None
    return {k: p.get(k) for k in ("texto", "validade", "link", "fonte", "verificado_em")}


def limpar(e, origem):
    if not e.get("titulo") or not e.get("link"):
        return None
    e["categoria"] = chave(e.get("categoria")).replace(" ", "") or "festival"
    if e["categoria"] in ("exposicoes", "museu"):
        e["categoria"] = "exposicao"
    if e["categoria"] not in CATS:
        e["categoria"] = "festival"
    if e.get("regiao") not in REGIOES:
        e["regiao"] = None
    e["preco_min"], e["preco_max"] = numero(e.get("preco_min")), numero(e.get("preco_max"))
    e["gratuito"] = bool(e.get("gratuito")) or (e["preco_min"] == 0 and not e["preco_max"])
    e["bom_para_criancas"] = bool(e.get("bom_para_criancas"))
    e["promocao"] = promocao_valida(e.get("promocao"))
    tipo = e.get("tipo_data")
    if tipo == "unica":
        datas = [d for d in e.get("datas") or [] if isinstance(d, dict) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(d.get("data", "")))]
        datas = [d for d in datas if d["data"] >= HOJE]
        if not datas:
            return None
        e["datas"] = sorted(datas, key=lambda d: (d["data"], d.get("hora") or ""))
    elif tipo == "temporada":
        if e.get("fim") and e["fim"] < HOJE:
            return None
    elif tipo != "permanente":
        return None
    e["_origem"] = origem
    return e


def main():
    todos, fontes = [], set()
    promocoes = {}
    caminho_promo = os.path.join(AQUI, "dados", "promocoes.json")
    if os.path.exists(caminho_promo):
        for p in json.load(open(caminho_promo, encoding="utf-8")):
            valida = promocao_valida(p)
            if valida and p.get("titulo"):
                k = chave(p["titulo"])
                if k in promocoes:  # várias promoções no mesmo lugar viram uma linha só
                    atual = promocoes[k]
                    atual["texto"] += " · " + valida["texto"]
                    datas = [v for v in (atual.get("validade"), valida.get("validade")) if v]
                    atual["validade"] = min(datas) if datas else None
                else:
                    promocoes[k] = valida
    for caminho in sorted(glob.glob(os.path.join(AQUI, "dados", "*.json"))):
        origem = os.path.basename(caminho)
        if origem == "promocoes.json":
            continue
        try:
            itens = json.load(open(caminho, encoding="utf-8"))
        except json.JSONDecodeError as erro:
            print(f"{origem}: JSON inválido ({erro})", file=sys.stderr)
            continue
        ok = [x for x in (limpar(dict(i), origem) for i in itens if isinstance(i, dict)) if x]
        print(f"{origem}: {len(itens)} lidos, {len(ok)} válidos")
        todos += ok

    # Duplicata = mesmo título e mesmo local (ou mesma 1ª data). Fica a versão mais completa.
    vistos = {}
    for e in todos:
        k = (chave(e["titulo"]), chave(e.get("local"))[:20] or (e.get("datas") or [{}])[0].get("data"))
        atual = vistos.get(k)
        if atual is not None and e.get("tipo_data") == "unica" and atual.get("tipo_data") == "unica":
            # mesma atração em outra data: junta as datas nas duas versões, para não perder nenhuma
            todas = {(d["data"], d.get("hora")): d for d in atual["datas"] + e["datas"]}
            e["datas"] = atual["datas"] = sorted(todas.values(), key=lambda d: (d["data"], d.get("hora") or ""))
        if atual is None or sum(v not in (None, "", []) for v in e.values()) > sum(v not in (None, "", []) for v in atual.values()):
            vistos[k] = e
    eventos = list(vistos.values())
    for e in eventos:
        e.pop("_origem", None)
        if chave(e["titulo"]) in promocoes:
            e["promocao"] = promocoes[chave(e["titulo"])]
        if e.get("fonte"):
            fontes.add(e["fonte"])

    saida = {"meta": {"atualizado_em": HOJE, "fontes": sorted(fontes)}, "eventos": eventos}
    json.dump(saida, open(os.path.join(AQUI, "eventos.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Total: {len(todos)} → {len(eventos)} após remover duplicatas; {len(fontes)} fontes")
    print(f"Promoções vigentes: {sum(1 for e in eventos if e.get('promocao'))} (de {len(promocoes)} em promocoes.json)")


if __name__ == "__main__":
    main()
