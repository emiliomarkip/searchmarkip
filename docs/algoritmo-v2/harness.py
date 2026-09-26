"""Réplica exacta del scoring de markip-api/main.py (sin Qdrant) para
analizar el ranking de consultas multi-palabra. El componente semántico
(cosine del embedding) se parametriza porque no hay red para el modelo."""
import re, unicodedata, sys
from difflib import SequenceMatcher
from rapidfuzz import fuzz

def _norm(s):
    s = (s or "").strip().lower()
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn")
def _compact(s):
    s = unicodedata.normalize("NFD", (s or "").lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s)
def _ratio(a, b):
    return SequenceMatcher(None, a, b).ratio() if a and b else 0.0
def phonetic_key(texto):
    t = unicodedata.normalize("NFKD", str(texto or ""))
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^A-Za-z0-9 ]+", " ", t.upper())
    s = re.sub(r"\s+", " ", t).strip().replace(" ", "")
    s = re.sub(r"[0-9]+", "", s)
    if not s: return ""
    s = s.replace("W", "U")
    s = re.sub(r"GU(?=[EI])", "ĝ", s); s = re.sub(r"G(?=[EI])", "J", s); s = s.replace("ĝ", "G")
    s = s.replace("QU", "K").replace("CK", "K").replace("PH", "F")
    s = s.replace("SH", "4").replace("CH", "4"); s = s.replace("X", "KS")
    s = re.sub(r"C(?=[EI])", "S", s); s = s.replace("C", "K")
    s = s.replace("Z", "S").replace("V", "B").replace("LL", "Y"); s = s.replace("HIE", "YE")
    s = s.replace("H", ""); s = re.sub(r"Y(?![AEIOU])", "I", s); s = re.sub(r"(.)\1+", r"\1", s)
    return s

W_LEX, W_PHON, W_SEM = 0.45, 0.35, 0.20
def score_main(q, name, sem, vigente=True, niza_hit=False):
    qn, qphon = _norm(q), phonetic_key(q)
    name_norm = _norm(name)
    lex = _ratio(qn, name_norm)
    qc, nc = _compact(q), _compact(name)
    contain = bool(qc and nc and (qc in nc or nc in qc))
    if contain: lex = max(lex, 0.88)
    cph = phonetic_key(name)
    phon = 1.0 if qphon and qphon == cph else _ratio(qphon, cph)
    base = W_LEX*lex + W_PHON*phon + W_SEM*sem
    if qn == name_norm: base = 1.0
    elif lex >= 0.8 and phon >= 0.8: base = min(1.0, base + 0.05)
    final = base + (0.05 if vigente else -0.05) + (0.10 if niza_hit else 0)
    return max(0, min(1, final)), lex, phon, contain, cph

def score_buscador(q, name):
    """Re-ranking del pipeline antiguo (markip-buscador/buscar_marca.py)."""
    qn = re.sub(r"\s+"," ", re.sub(r"[^A-Za-z0-9 ]+"," ", _norm(q).upper())).strip()
    nn = re.sub(r"\s+"," ", re.sub(r"[^A-Za-z0-9 ]+"," ", _norm(name).upper())).strip()
    return max(fuzz.ratio(qn, nn), fuzz.token_set_ratio(qn, nn), fuzz.partial_ratio(qn, nn)*0.9)

CASES = {
  "Markip Chile": ["MARKIP","MARKIP CHILE","CHILE","BANCO CHILE","CHILE TABACOS","MARCA CHILE","MARKIT","MARKUP",
                   "MARK IP LAW","MERKIP","MARKI","CHILEMARK","MARKIP SPA","VIÑA CHILE","MARQUIP","MARKIPP"],
  "Caro Molina":  ["SOYCARO MOLINA","CARO MOLINA","MOLINA","CARO","CAROLINA","CARO MOLINO","KARO MOLINA","MOLINA CARO",
                   "CARLA MOLINA","CAROLA","VIÑA MOLINA","MOLINARI","CARO Y MOLINA","LA CARO","CARO QUINTANA","MOLINA SPA"],
}
for sem in (0.0, 0.6):
    print(f"\n{'='*78}\n  SCORING ACTUAL (main.py)  —  semántico fijo = {sem}  (todas vigentes, sin filtro Niza)\n{'='*78}")
    for q, cands in CASES.items():
        print(f"\n  Consulta: {q!r}   clave fonética consulta = {phonetic_key(q)}   norm = {_norm(q)!r}")
        rows = []
        for c in cands:
            f, lex, phon, contain, cph = score_main(q, c, sem)
            rows.append((f, c, lex, phon, contain, cph))
        rows.sort(reverse=True)
        print(f"  {'#':>2}  {'score':>5}  {'marca':<16} {'lex':>5} {'phon':>5}  contiene  clave_fon      viejo(rapidfuzz)")
        for i,(f,c,lex,phon,contain,cph) in enumerate(rows,1):
            print(f"  {i:>2}  {f:5.2f}  {c:<16} {lex:5.2f} {phon:5.2f}  {'SÍ' if contain else '  '}        {cph:<14} {score_buscador(q,c):5.1f}")

print("\n\nRECALL exacto (lo único no-semántico que trae candidatos en main.py):")
for q, cands in CASES.items():
    qphon, qname = phonetic_key(q), _norm(q).upper()
    hits = [c for c in cands if phonetic_key(c)==qphon or _norm(c).upper()==qname]
    print(f"  {q!r}: phonetic_key={qphon} brand_name_norm={qname!r} -> recuperados por vía exacta: {hits}")
    print(f"      Todo lo demás depende de que el embedding de MiniLM ponga a la marca en el top-80.")
