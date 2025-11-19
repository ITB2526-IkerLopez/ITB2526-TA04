import csv
import xml.etree.ElementTree as ET
import re
import unicodedata
import sys
csv_file = '/home/iker.lopez.7e7/PycharmProjects/ITB2526-TA04/Arxius/Formulari.csv'
xml_file = 'Incidencies.xml'

# Función para limpiar nombres de etiquetas XML
def limpiar_nombre_etiqueta(nombre):
    # Quita acentos
    nombre = ''.join(c for c in unicodedata.normalize('NFD', nombre)
                     if unicodedata.category(c) != 'Mn')
    # Reemplaza caracteres no alfanuméricos por guion bajo
    nombre = re.sub(r'\W+', '_', nombre.strip())
    # Asegura que no empiece con número
    if nombre and nombre[0].isdigit():
        nombre = '_' + nombre
    return nombre

# Función para indentar el XML
def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for e in elem:
            indent(e, level+1)
        if not e.tail or not e.tail.strip():
            e.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

# Crear raíz
root = ET.Element('Registros')

# Leer CSV y construir XML
try:
    with open(csv_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            registro = ET.SubElement(root, 'Registro')
            for key, value in row.items():
                campo_nombre = limpiar_nombre_etiqueta(key)
                campo = ET.SubElement(registro, campo_nombre)
                campo.text = value
except FileNotFoundError:
    print(f"No s'a trobat el fitxer: {csv_file}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Failed to read CSV ` {csv_file} `: {e}", file=sys.stderr)
    sys.exit(1)


# Indentar para que sea legible
indent(root)

# Guardar XML
tree = ET.ElementTree(root)
tree.write(xml_file, encoding='utf-8', xml_declaration=True)
