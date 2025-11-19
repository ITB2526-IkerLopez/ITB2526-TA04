import xml.etree.ElementTree as ET
import re
from datetime import datetime
import sys
# -----------------------------
# CONFIG
# -----------------------------
FILE = "Incidencies.xml"
OUTPUT = "incidencies_filtrat.txt"

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
        return False
    if re.match(r".+@.+\..+", nom):
        return False
    if re.fullmatch(r"[0-9]+", nom):
        return False
    if len(nom) < 3:
        return False
    return True


def validar_email(email):
    return bool(re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", email))


def validar_data(data):
    try:
        dt = datetime.strptime(data, "%d/%m/%Y")
        return 2000 <= dt.year <= 2025
    except:
        return False


def validar_hora(hora):
    return bool(re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d", hora))


def validar_ubicacio(u):
    return u and len(u) <= 50


def validar_ambit(a):
    return a in AMBITS_VALIDS


def validar_tipus(t):
    return t in TIPUS_EQUIP_VALID


def validar_grau(g):
    return g in GRAUS_VALIDS


def validar_text(t, min_len, max_len):
    if not t:
        return False
    return min_len <= len(t) <= max_len


def validar_freq(f):
    return f in FREQ_VALIDA



def registre_valid(reg):
    try:
        return (
            validar_nom(reg.find("Nom_i_cognoms").text or "")
            and validar_email(reg.find("Adreca_electronica").text or "")
            and validar_data(reg.find("Data_deteccio_de_la_incidencia").text or "")
            and validar_hora(reg.find("Hora_deteccio_de_la_incidencia").text or "")
            and validar_ubicacio(reg.find("Ubicacio_equip_afectat").text or "")
            and validar_ambit(reg.find("Quin_ambit_ha_estat_afectat").text or "")
            and validar_tipus(reg.find("Tipus_d_equip_afectat").text or "")
            and validar_grau(reg.find("Grau_de_gravetat").text or "")
            and validar_text(reg.find("Descripcio_de_la_incidencia").text or "", 5, 300)
            and validar_text(reg.find("Possible_motiu_de_l_incident").text or "", 3, 200)
            and validar_freq(reg.find("Frequencia_en_que_es_produeix_el_problema").text or "")
        )
    except:
        return False


# -----------------------------
# PALETA DE COLORES POR CAMPO
# -----------------------------
COLORES = {
    "Nom_i_cognoms": "1;34",                         # azul fuerte
    "Adreca_electronica": "1;35",                    # magenta brillante
    "Data_deteccio_de_la_incidencia": "1;36",        # cyan brillante
    "Hora_deteccio_de_la_incidencia": "36",          # cyan
    "Ubicacio_equip_afectat": "33",                  # amarillo
    "Quin_ambit_ha_estat_afectat": "32",             # verde
    "Tipus_d_equip_afectat": "92",                   # verde claro
    "Grau_de_gravetat": "31",                        # rojo
    "Descripcio_de_la_incidencia": "94",             # azul claro
    "Possible_motiu_de_l_incident": "95",            # rosa
    "Frequencia_en_que_es_produeix_el_problema": "93" # amarillo claro
}


def color(c, t):
    return f"\033[{c}m{t}\033[0m"


# -----------------------------
# LECTURA I FILTRAT
# -----------------------------
try:
    tree = ET.parse(FILE)
    root = tree.getroot()
except FileNotFoundError:
    print(f"No s'ha trobat l'arxiu: {FILE} a la ruta: /home/iker.lopez.7e7/PycharmProjects/ITB2526-TA04/Python/Incidencies.xml", file=sys.stderr)
    sys.exit(1)
except ET.ParseError as e:
    print(f"No s'ha trobat l'arxiu: {FILE} a la ruta: /home/iker.lopez.7e7/PycharmProjects/ITB2526-TA04/Python/Incidencies.xml", file=sys.stderr)
    sys.exit(1)
with open(OUTPUT, "w", encoding="utf-8") as f:

    for r in root.findall("Registro"):
        if not registre_valid(r):
            continue

        f.write(color("1;33", "==============================\n"))
        f.write(color("1;32", "   REGISTRE D'INCIDÈNCIA VÀLID\n"))
        f.write(color("1;33", "==============================\n"))

        for tag in COLORES.keys():
            valor = r.find(tag).text or ""
            f.write(color(COLORES[tag], f"{tag.replace('_', ' ')}: {valor}\n"))

        f.write("\n")

print("TXT generat correctament:", OUTPUT)
