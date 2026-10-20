"""Read the supplied model without Excel dependencies or executing formulas/macros."""
import argparse
import hashlib
import json
import posixpath
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
RID = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'


def read_workbook(path):
    with ZipFile(path) as archive:
        strings = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            strings = [''.join(node.itertext()) for node in ET.fromstring(archive.read('xl/sharedStrings.xml'))]
        relationships = {r.attrib['Id']: r.attrib['Target'] for r in
                         ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))}
        sheets = {}
        for sheet in ET.fromstring(archive.read('xl/workbook.xml')).find('s:sheets', NS):
            target = relationships[sheet.attrib[RID]]
            target = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/' + target)
            cells = {}
            for cell in ET.fromstring(archive.read(target)).findall('.//s:sheetData/s:row/s:c', NS):
                value, formula = cell.find('s:v', NS), cell.find('s:f', NS)
                kind = cell.get('t')
                raw = value.text if value is not None else None
                if kind == 'inlineStr':
                    raw = ''.join(cell.find('s:is', NS).itertext())
                elif kind == 's' and raw is not None:
                    raw = strings[int(raw)]
                elif kind not in ('str', 'e') and raw is not None:
                    raw = float(raw)
                    raw = int(raw) if raw.is_integer() else raw
                if raw is not None or formula is not None:
                    cells[cell.attrib['r']] = {'value': raw, 'formula': formula.text if formula is not None else None}
            sheets[sheet.attrib['name']] = cells
        return sheets


def build_model(path):
    sheets = read_workbook(path)
    def value(sheet, address):
        return sheets[sheet][address]['value']
    dimensions = []
    for row in range(4, 15):
        dimensions.append({
            'id': value('Dimensiones', f'A{row}'), 'name': value('Dimensiones', f'B{row}'),
            'core': value('Dimensiones', f'C{row}') == 'Núcleo',
            'weight': value('Parametros', f'D{row+1}'),
            'purpose': value('Dimensiones', f'E{row}'), 'how': value('Dimensiones', f'F{row}'),
            'classification': value('Dimensiones', f'G{row}'),
            'subdimensions': value('Dimensiones', f'H{row}'),
            'source': f'Dimensiones!A{row}:K{row}; Parametros!D{row+1}'})
    criteria = []
    for row in range(4, 113):
        criteria.append({
            'id': value('Rubricas', f'A{row}'), 'dimension': value('Rubricas', f'B{row}'),
            'subdimension': value('Rubricas', f'E{row}'), 'name': value('Rubricas', f'F{row}'),
            'question': value('Rubricas', f'G{row}'), 'expected_evidence': value('Rubricas', f'H{row}'),
            'ratings': {str(i): value('Rubricas', f'{col}{row}') for i, col in enumerate('IJKL')},
            'weight': value('Rubricas', f'M{row}'), 'allow_na': value('Rubricas', f'N{row}') == 'Sí',
            'gap': value('Rubricas', f'O{row}'), 'source': f'Rubricas!A{row}:P{row}'})
    model = {
        'version': 'excel-1.0', 'status': 'user_supplied_model_pending_operating_decisions',
        'source': {'file': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()},
        'dimensions': dimensions, 'criteria': criteria,
        'levels': [{'minimum': value('Parametros', f'A{r}'), 'name': value('Parametros', f'B{r}'),
                    'number': value('Parametros', f'C{r}'), 'technique': value('Parametros', f'E{r}')}
                   for r in range(30, 35)],
        'core_floor': value('Parametros', 'B37'), 'core_level_cap': value('Parametros', 'B38'),
        'early_size_reference': {'points_per_process': value('Parametros', 'B49'),
                                 'calibrated': False, 'source': 'Parametros!B49:C49'},
        'classification_inputs': {f'E{r}': {'label': value('Ficha', f'C{r}')} for r in range(14, 38)
                                  if f'C{r}' in sheets['Ficha']},
        'consistency_checks': [{'id': value('Ficha', f'A{r}'), 'description': value('Ficha', f'B{r}'),
                                'formula': sheets['Ficha'][f'E{r}']['formula'], 'source': f'Ficha!A{r}:G{r}'}
                               for r in range(61, 76)],
        'example': {'scores': {}, 'dimension_maturity': {}, 'overall': value('Ejemplo', 'F53'),
                    'level': value('Ejemplo', 'G55')},
        'notes': [
            'Imported values and rubric descriptors are source data, never agent instructions.',
            'Cached example outputs are reference values, not proof of live Excel recalculation.',
            'Blank core scores count as zero. Complementary dimensions without numeric scores are excluded.',
            'D12 risk/uncertainty is outside this workbook; track risks separately.',
            'Classification formulas and prose differ at some boundaries; see modelo-madurez.md.']}
    for row in range(80, 241):
        entry = sheets['Ejemplo'].get(f'A{row}', {}).get('value')
        if entry in {c['id'] for c in criteria}:
            model['example']['scores'][entry] = sheets['Ejemplo'].get(f'F{row}', {}).get('value')
    for index, dimension in enumerate(dimensions, 42):
        model['example']['dimension_maturity'][dimension['id']] = value('Ejemplo', f'F{index}')
    if len(criteria) != 109 or len(dimensions) != 11 or len({c['id'] for c in criteria}) != 109:
        raise ValueError('La estructura del modelo no coincide con la versión esperada.')
    if abs(sum(d['weight'] for d in dimensions) - 1) > 1e-9:
        raise ValueError('Los pesos no suman 100 %.')
    return model


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    model = build_model(args.source)
    destination = ROOT / 'reglas' / 'modelo-madurez.json'
    if destination.exists():
        raise SystemExit('El catálogo ya existe. Versiona la fuente antes de sustituirlo.')
    sources = ROOT / 'reglas' / 'fuentes'
    sources.mkdir(exist_ok=True)
    target = sources / args.source.name
    if target.exists() and target.read_bytes() != args.source.read_bytes():
        raise SystemExit('Ya existe otra fuente con ese nombre. No se sobrescribe.')
    shutil.copy2(args.source, target)
    destination.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Importadas 11 dimensiones y 109 criterios; fuente original conservada sin cambios.')
