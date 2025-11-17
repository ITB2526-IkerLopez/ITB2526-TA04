import xml.etree.ElementTree as ET
import re
import json
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
FILE = "Incidencies.xml"
OUTPUT = "incidencies_filtrat_valid_invalid.txt"
OUTPUT_JSON = "incidencies_valid_invalid.json"

# Regles de validació
AMBITS_VALIDS = {
    "Equipament Informatic",
    "Equipament audiovisual",
    "Xarxa"
}

TIPUS_EQUIP_VALID = {
    "Ordinador d'escriptori",
    "Projector",
    "Impressora",
    "Xarxa",
    "Sistema de so",
    "Portàtil",
    "Altaveus",
    "Pantalla interactiva"
}

GRAUS_VALIDS = {
    "Baixa (no impedeix el treball)",
    "Mitjana (dificulta parcialment el treball)",
    "Alta (impossibilita el treball)"
}

FREQ_VALIDA = {
    "Només ha passat una vegada",
    "Passa sovint (intermitent)",
    "Sempre que s’utilitza l’equip"
}


# -----------------------------
# VALIDACIONS
# -----------------------------
def validar_nom(nom):
    if not nom or len(nom.split()) < 2:
        return "Nom invàlid: calen mínim nom i cognoms."
    if re.match(r".+@.+\..+", nom):
        return "Nom invàlid: sembla un correu."
    if re.fullmatch(r"[0-9]+", nom):
        return "Nom invàlid: no pot ser només números."
    if len(nom) < 3:
        return "Nom invàlid: massa curt."
    return True


def validar_email(email):
    if not bool(re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", email)):
        return "Email invàlid."
    return True


def validar_data(data):
    try:
        dt = datetime.strptime(data, "%d/%m/%Y")
        if not (2000 <= dt.year <= 2025):
            return "Data fora de rang permès (2000-2025)."
        return True
    except:
        return "Format de data incorrecte (dd/mm/yyyy)."


def validar_hora(hora):
    if not bool(re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d", hora)):
        return "Hora invàlida (hh:mm:ss)."
    return True


def validar_ubicacio(u):
    if not u or len(u) > 50:
        return "Ubicació invàlida o massa llarga (max 50)."
    return True


def validar_ambit(a):
    if a not in AMBITS_VALIDS:
        return "Àmbit no vàlid."
    return True


def validar_tipus(t):
    if t not in TIPUS_EQUIP_VALID:
        return "Tipus d'equip no vàlid."
    return True


def validar_grau(g):
    if g not in GRAUS_VALIDS:
        return "Grau de gravetat no vàlid."
    return True


def validar_text(t, min_len, max_len):
    if not t:
        return "El camp és buit."
    if not (min_len <= len(t) <= max_len):
        return f"Text fora de límits ({min_len}-{max_len} caràcters)."
    return True


def validar_freq(f):
    if f not in FREQ_VALIDA:
        return "Freqüència no vàlida."
    return True


# Nova funció que retorna errors detallats
def validar_registre_detallat(reg):
    errors = {}

    def check(tag, func, *args):
        valor = reg.find(tag).text if reg.find(tag) is not None else ""
        result = func(valor, *args) if args else func(valor)
        if result is not True:
            errors[tag] = result

    check("Nom_i_cognoms", validar_nom)
    check("Adreca_electronica", validar_email)
    check("Data_deteccio_de_la_incidencia", validar_data)
    check("Hora_deteccio_de_la_incidencia", validar_hora)
    check("Ubicacio_equip_afectat", validar_ubicacio)
    check("Quin_ambit_ha_estat_afectat", validar_ambit)
    check("Tipus_d_equip_afectat", validar_tipus)
    check("Grau_de_gravetat", validar_grau)
    check("Descripcio_de_la_incidencia", validar_text, 5, 300)
    check("Possible_motiu_de_l_incident", validar_text, 3, 200)
    check("Frequencia_en_que_es_produeix_el_problema", validar_freq)

    return errors


# -----------------------------
# COLORS (només per a TXT)
# -----------------------------
COLORES = {
    "Nom_i_cognoms": "1;34",
    "Adreca_electronica": "1;35",
    "Data_deteccio_de_la_incidencia": "1;36",
    "Hora_deteccio_de_la_incidencia": "36",
    "Ubicacio_equip_afectat": "33",
    "Quin_ambit_ha_estat_afectat": "32",
    "Tipus_d_equip_afectat": "92",
    "Grau_de_gravetat": "31",
    "Descripcio_de_la_incidencia": "94",
    "Possible_motiu_de_l_incident": "95",
    "Frequencia_en_que_es_produeix_el_problema": "93"
}

def color(c, t):
    return f"\033[{c}m{t}\033[0m"


# -----------------------------
# PROCESSAMENT I SORTIDES
# -----------------------------
tree = ET.parse(FILE)
root = tree.getroot()

resultats_json = []   # ← Guardarem aquí els registres processats

with open(OUTPUT, "w", encoding="utf-8") as f:

    for r in root.findall("Registro"):
        errors = validar_registre_detallat(r)

        registre_dict = {tag: (r.find(tag).text if r.find(tag) is not None else "")
                         for tag in COLORES.keys()}

        if not errors:
            # TXT
            f.write(color("1;33", "==============================\n"))
            f.write(color("1;32", "   REGISTRE D'INCIDÈNCIA VÀLID\n"))
            f.write(color("1;33", "==============================\n"))

            for tag in COLORES.keys():
                valor = registre_dict[tag]
                f.write(color(COLORES[tag], f"{tag.replace('_', ' ')}: {valor}\n"))
            f.write("\n")

            # JSON
            registre_dict["valid"] = True
            registre_dict["errors"] = {}

        else:
            # TXT
            f.write(color("1;31", "==============================\n"))
            f.write(color("1;31", "   REGISTRE D'INCIDÈNCIA INVÀLID\n"))
            f.write(color("1;31", "==============================\n"))
            f.write(color("1;31", "Errors trobats:\n"))
            for tag, msg in errors.items():
                f.write(color("31", f" - {tag.replace('_', ' ')}: {msg}\n"))
            f.write("\n")

            # JSON
            registre_dict["valid"] = False
            registre_dict["errors"] = errors

        resultats_json.append(registre_dict)

# Crear fitxer JSON
with open(OUTPUT_JSON, "w", encoding="utf-8") as fj:
    json.dump(resultats_json, fj, indent=4, ensure_ascii=False)

print("TXT generat correctament:", OUTPUT)
print("JSON generat correctament:", OUTPUT_JSON)