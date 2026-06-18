"""
Script d'import des projets depuis les CSVs.
Usage: python3 manage.py shell < import_projects.py
"""
import csv
import os
from datetime import date

from projects.models import Project, Engineer, ProjectObservation

GOUVERNORAT_MAP = {
    'ARIANA':    'ariana',
    'BEJA':      'beja',
    'BEN AROUS': 'ben_arous',
    'BIZERTE':   'bizerte',
    'JENDOUBA':  'jendouba',
    'MANOUBA':   'manouba',
    'SILIANA':   'siliana',
    'EL KEF':    'kef',
    'NABEUL':    'nabeul',
    'TUNIS':     'tunis',
}

CSV_DIR = 'static/img'

def parse_x(val):
    return str(val).strip().upper() == 'X'

def parse_int(val):
    try:
        return int(str(val).strip().replace('F', '').replace('%', ''))
    except:
        return 0

def get_or_create_engineer(name):
    name = name.strip()
    if not name:
        return None
    eng, _ = Engineer.objects.get_or_create(name=name)
    return eng

total_created = 0
total_skipped = 0

for filename in sorted(os.listdir(CSV_DIR)):
    if not filename.endswith('.csv'):
        continue

    # Extract gouvernorat and maitre_ouvrage from filename
    # e.g. "...CRE ARIANA.csv" or "...DRE TUNIS.csv"
    base = filename.replace('SUIVI DES PROJETS Bureau Tunis 01062026-', '').replace('.csv', '')
    parts = base.split(' ', 1)  # ['CRE', 'ARIANA'] or ['DRE', 'TUNIS']
    if len(parts) < 2:
        continue
    org_type = parts[0].strip()   # CRE or DRE
    city = parts[1].strip()       # ARIANA, TUNIS, etc.
    gouvernorat = GOUVERNORAT_MAP.get(city, city.lower().replace(' ', '_'))
    maitre_ouvrage = f'{org_type} {city}'

    filepath = os.path.join(CSV_DIR, filename)
    with open(filepath, encoding='utf-8-sig', errors='replace') as f:
        reader = csv.reader(f)
        rows = list(reader)

    # Data starts at row index 3 (0-based)
    bc_counter = 1
    for row in rows[3:]:
        if len(row) < 2:
            continue
        num = str(row[0]).strip()
        if not num.isdigit():
            continue

        name = str(row[1]).strip()
        if not name:
            continue

        # Engineers (col 2) — split by multiple spaces or newlines
        engineer_raw = str(row[2]).strip()
        engineer_names = [n.strip() for n in engineer_raw.replace('\n', '  ').split('  ') if n.strip()]

        # DAO (cols 3,4,5)
        dao_str  = parse_x(row[3]) if len(row) > 3 else False
        dao_elec = parse_x(row[4]) if len(row) > 4 else False
        dao_fl   = parse_x(row[5]) if len(row) > 5 else False

        # D0 (col 6)
        d0 = parse_x(row[6]) if len(row) > 6 else False

        # EXE (cols 7,8,9)
        exe_str  = parse_x(row[7]) if len(row) > 7 else False
        exe_elec = parse_x(row[8]) if len(row) > 8 else False
        exe_fl   = parse_x(row[9]) if len(row) > 9 else False

        # Visits (cols 10,11)
        planned   = parse_int(row[10]) if len(row) > 10 else 0
        completed = parse_int(row[11]) if len(row) > 11 else 0

        # RPRO (col 13), D6 (col 14), RDEF (col 15)
        rpro = parse_x(row[13]) if len(row) > 13 else False
        d6   = parse_x(row[14]) if len(row) > 14 else False
        rdef = parse_x(row[15]) if len(row) > 15 else False

        # Observations (col 16)
        obs_text = str(row[16]).strip() if len(row) > 16 else ''

        # Bon de commande — temporary placeholder
        bc_number = str(bc_counter).zfill(5)
        bc_counter += 1

        # Skip if already exists
        if Project.objects.filter(name=name, gouvernorat=gouvernorat).exists():
            total_skipped += 1
            continue

        proj = Project.objects.create(
            name=name,
            bon_commande_number=bc_number,
            bon_commande_date=date(2024, 1, 1),  # placeholder
            gouvernorat=gouvernorat,
            maitre_ouvrage=maitre_ouvrage,
            has_structure=dao_str or exe_str,
            has_electricite=dao_elec or exe_elec,
            has_fluide=dao_fl or exe_fl,
            has_securite_incendie=False,
            dao_structure='approuve' if dao_str else 'non_prevu',
            dao_electricite='approuve' if dao_elec else 'non_prevu',
            dao_fluide='approuve' if dao_fl else 'non_prevu',
            dao_securite_incendie='non_prevu',
            d0_done=d0,
            exe_structure='approuve' if exe_str else 'non_prevu',
            exe_electricite='approuve' if exe_elec else 'non_prevu',
            exe_fluide='approuve' if exe_fl else 'non_prevu',
            exe_securite_incendie='non_prevu',
            planned_visits=planned,
            completed_visits=completed,
            rpro=rpro,
            d6_done=d6,
            rdef=rdef,
        )

        # Assign engineers
        for eng_name in engineer_names:
            eng = get_or_create_engineer(eng_name)
            if eng:
                proj.engineers.add(eng)

        # Add observation if exists
        if obs_text:
            ProjectObservation.objects.create(
                project=proj,
                date=date.today(),
                text=obs_text,
                is_auto=False,
            )

        total_created += 1
        print(f'  ✓ [{gouvernorat}] {name[:60]}')

print(f'\n✅ Terminé — {total_created} projets créés, {total_skipped} ignorés (déjà existants)')
