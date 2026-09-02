#!/usr/bin/env python3
"""Arma docs/index.html a partir de la plantilla, las secciones y results/*.json."""
from __future__ import annotations
import datetime, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
RES = os.path.join(ROOT, "results")

def sanitize(o):
    """JSON no admite Infinity ni NaN. Se convierten a null (con una marca
    en el caso de infinito, que en estos datos siempre significa "sin
    límite" y no "error")."""
    if isinstance(o, float):
        if o != o:
            return None
        if o == float("inf"):
            return 1e308
        if o == float("-inf"):
            return -1e308
        return o
    if isinstance(o, dict):
        return {k: sanitize(v) for k, v in o.items()}
    if isinstance(o, list):
        return [sanitize(v) for v in o]
    return o


STUDIES = ["anchors", "damage", "mass_optimum", "accumulators", "freeflight",
           "sensing", "montecarlo", "reliability", "catalog", "lever_baseline",
           "wedge_states", "waveforms", "separability", "mechanisms",
           "wave_return", "wave_return_sim", "mass_sim", "strike_position",
           "sensitivity"]


def main() -> int:
    data = {}
    missing = []
    for name in STUDIES:
        path = os.path.join(RES, name + ".json")
        if not os.path.exists(path):
            missing.append(name)
            continue
        with open(path, encoding="utf-8") as fh:
            data[name] = json.load(fh)
    if missing:
        print("FALTAN estudios:", ", ".join(missing))
    data["_meta"] = {
        "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "estudios": sorted(data.keys()),
    }

    tpl = open(os.path.join(DOCS, "_template.html"), encoding="utf-8").read()
    secs = "\n\n".join(
        open(os.path.join(DOCS, f"_s{i}.html"), encoding="utf-8").read()
        for i in (1, 2, 3, 4))
    app = open(os.path.join(DOCS, "_app.js"), encoding="utf-8").read()

    payload = json.dumps(sanitize(data), ensure_ascii=False,
                         separators=(",", ":"), allow_nan=False)
    # Un "</script>" dentro del JSON cerraría la etiqueta antes de tiempo.
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e")

    html = (tpl.replace("<!--SECTIONS-->", secs)
               .replace("/*__DATA__*/", payload)
               .replace("/*__JS__*/", app))
    out = os.path.join(DOCS, "index.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"docs/index.html  {os.path.getsize(out)/1024:.0f} kB  "
          f"({len(data)-1} estudios)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
