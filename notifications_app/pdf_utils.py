"""PDF generation utilities for project/expertise deletion reports."""
import io
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A3, landscape as _landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)


_W, _H = A4
_STYLES = getSampleStyleSheet()

_TITLE = ParagraphStyle(
    'Title2', parent=_STYLES['Title'],
    fontSize=18, spaceAfter=6, textColor=colors.HexColor('#0f3460'),
)
_H2 = ParagraphStyle(
    'H2', parent=_STYLES['Heading2'],
    fontSize=12, spaceBefore=14, spaceAfter=4,
    textColor=colors.HexColor('#16213e'),
    borderPad=2,
)
_NORMAL = _STYLES['Normal']
_SMALL = ParagraphStyle('Small', parent=_STYLES['Normal'], fontSize=9, textColor=colors.grey)

_TABLE_STYLE = TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f3460')),
    ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
    ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE',   (0, 0), (-1, 0), 10),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f0f4ff'), colors.white]),
    ('FONTSIZE',   (0, 1), (-1, -1), 9),
    ('GRID',       (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
    ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
    ('LEFTPADDING',  (0, 0), (-1, -1), 6),
    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ('TOPPADDING',   (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING',(0, 0), (-1, -1), 4),
])


def _row(label, value):
    return [Paragraph(f'<b>{label}</b>', _NORMAL), Paragraph(str(value) if value else '–', _NORMAL)]


def _yn(val):
    return 'Oui' if val else 'Non'


def _date(d):
    return d.strftime('%d/%m/%Y') if d else '–'


def build_project_pdf(project):
    """Return a bytes object containing the PDF for the given Project."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )
    story = []

    # ── Header ────────────────────────────────────────────────────────────────
    story.append(Paragraph('MARAM – Fiche Projet (Suppression)', _TITLE))
    story.append(Paragraph(
        f'Généré le {date.today().strftime("%d/%m/%Y")} · Demande de suppression',
        _SMALL,
    ))
    story.append(HRFlowable(width='100%', thickness=1.5, color=colors.HexColor('#0f3460'), spaceAfter=10))

    # ── Identité ──────────────────────────────────────────────────────────────
    story.append(Paragraph('Identité du projet', _H2))
    id_data = [
        ['Champ', 'Valeur'],
        *[_row(*r) for r in [
            ("Nom du projet",            project.name),
            ("N° Bon de commande",       project.bon_commande_number),
            ("Date bon de commande",     _date(project.bon_commande_date)),
            ("Gouvernorat",              project.get_gouvernorat_display()),
            ("Maître d'ouvrage",         project.maitre_ouvrage),
            ("Spécialités",              project.specialties_display),
            ("Créé par",                 project.created_by.get_full_name() or project.created_by.username if project.created_by else '–'),
            ("Date de création",         _date(project.created_at.date()) if project.created_at else '–'),
        ]]
    ]
    story.append(Table(id_data, colWidths=[5*cm, 12*cm], style=_TABLE_STYLE))

    # ── Visites ───────────────────────────────────────────────────────────────
    story.append(Paragraph('Visites', _H2))
    vis_data = [
        ['Champ', 'Valeur'],
        _row('Visites prévues',   project.planned_visits),
        _row('Visites réalisées', project.completed_visits),
        _row('Avancement',        f'{project.visit_percentage} %'),
    ]
    story.append(Table(vis_data, colWidths=[5*cm, 12*cm], style=_TABLE_STYLE))

    # ── DAO ───────────────────────────────────────────────────────────────────
    story.append(Paragraph('Statut DAO', _H2))
    dao_rows = [['Spécialité', 'Statut']]
    if project.has_structure:
        dao_rows.append(_row('Structure', project.get_dao_structure_display()))
    if project.has_electricite:
        dao_rows.append(_row('Électricité', project.get_dao_electricite_display()))
    if project.has_fluide:
        dao_rows.append(_row('Fluide', project.get_dao_fluide_display()))
    if project.has_securite_incendie:
        dao_rows.append(_row('Sécurité incendie', project.get_dao_securite_incendie_display()))
    dao_rows.append(_row('Date complétion DAO', _date(project.dao_completed_date)))
    story.append(Table(dao_rows, colWidths=[5*cm, 12*cm], style=_TABLE_STYLE))

    # ── D0 ────────────────────────────────────────────────────────────────────
    story.append(Paragraph('D0', _H2))
    story.append(Table([
        ['Champ', 'Valeur'],
        _row('D0 réalisé', _yn(project.d0_done)),
        _row('Date D0',    _date(project.d0_date)),
    ], colWidths=[5*cm, 12*cm], style=_TABLE_STYLE))

    # ── EXE ───────────────────────────────────────────────────────────────────
    story.append(Paragraph('Statut EXE', _H2))
    exe_rows = [['Spécialité', 'Statut']]
    if project.has_structure:
        exe_rows.append(_row('Structure', project.get_exe_structure_display()))
    if project.has_electricite:
        exe_rows.append(_row('Électricité', project.get_exe_electricite_display()))
    if project.has_fluide:
        exe_rows.append(_row('Fluide', project.get_exe_fluide_display()))
    if project.has_securite_incendie:
        exe_rows.append(_row('Sécurité incendie', project.get_exe_securite_incendie_display()))
    exe_rows.append(_row('Date début EXE', _date(project.exe_started_date)))
    story.append(Table(exe_rows, colWidths=[5*cm, 12*cm], style=_TABLE_STYLE))

    # ── D6 + Réceptions ───────────────────────────────────────────────────────
    story.append(Paragraph('D6 & Réceptions', _H2))
    story.append(Table([
        ['Champ', 'Valeur'],
        _row('D6 réalisé',  _yn(project.d6_done)),
        _row('Date D6',     _date(project.d6_date)),
        _row('RPRO',        _yn(project.rpro)),
        _row('Date RPRO',   _date(project.rpro_date)),
        _row('RDEF',        _yn(project.rdef)),
        _row('Date RDEF',   _date(project.rdef_date)),
    ], colWidths=[5*cm, 12*cm], style=_TABLE_STYLE))

    # ── Factures ──────────────────────────────────────────────────────────────
    story.append(Paragraph('Factures', _H2))
    inv_data = [['Facture', "Date d'établissement", 'Date de transmission', 'Notes']]
    for inv in project.invoices.all():
        inv_data.append([
            Paragraph(f'N°{inv.invoice_number}', _NORMAL),
            Paragraph(_date(inv.establishment_date), _NORMAL),
            Paragraph(_date(inv.transmission_date), _NORMAL),
            Paragraph(inv.notes[:120] if inv.notes else '–', _NORMAL),
        ])
    if len(inv_data) == 1:
        inv_data.append([Paragraph('Aucune facture', _NORMAL), '', '', ''])
    story.append(Table(inv_data, colWidths=[2.5*cm, 4*cm, 4*cm, 6.5*cm], style=_TABLE_STYLE))

    # ── Ingénieurs ────────────────────────────────────────────────────────────
    story.append(Paragraph('Ingénieurs assignés', _H2))
    eng_data = [['Nom', 'Email', 'Téléphone', 'Spécialités']]
    for eng in project.engineers.all():
        eng_data.append([
            Paragraph(eng.name, _NORMAL),
            Paragraph(eng.email, _NORMAL),
            Paragraph(eng.phone or '–', _NORMAL),
            Paragraph(eng.specialties or '–', _NORMAL),
        ])
    if len(eng_data) == 1:
        eng_data.append([Paragraph('Aucun ingénieur', _NORMAL), '', '', ''])
    story.append(Table(eng_data, colWidths=[4*cm, 5*cm, 3*cm, 5*cm], style=_TABLE_STYLE))

    # ── Observations ──────────────────────────────────────────────────────────
    story.append(Paragraph('Observations', _H2))
    obs_data = [['Date', 'Observation', 'Créé par']]
    for obs in project.observations.all():
        obs_data.append([
            Paragraph(_date(obs.date), _NORMAL),
            Paragraph(obs.text[:200], _NORMAL),
            Paragraph(obs.created_by.username if obs.created_by else '–', _NORMAL),
        ])
    if len(obs_data) == 1:
        obs_data.append([Paragraph('Aucune observation', _NORMAL), '', ''])
    story.append(Table(obs_data, colWidths=[2.5*cm, 12*cm, 2.5*cm], style=_TABLE_STYLE))

    story.append(Spacer(1, 12))
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.grey))
    story.append(Paragraph(
        'Ce document a été généré automatiquement par le système Maram.',
        _SMALL,
    ))

    doc.build(story)
    return buf.getvalue()


def build_expertise_pdf(expertise):
    """Return a bytes object containing the PDF for the given Expertise."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )
    story = []

    # ── Header ────────────────────────────────────────────────────────────────
    story.append(Paragraph('MARAM – Fiche Expertise', _TITLE))
    story.append(Paragraph(
        f'Généré le {date.today().strftime("%d/%m/%Y")}',
        _SMALL,
    ))
    story.append(HRFlowable(width='100%', thickness=1.5, color=colors.HexColor('#0f3460'), spaceAfter=10))

    # ── Identité ──────────────────────────────────────────────────────────────
    story.append(Paragraph("Identité de l'expertise", _H2))
    id_data = [
        ['Champ', 'Valeur'],
        *[_row(*r) for r in [
            ("Intitulé",                 expertise.name),
            ("N° Bon de commande",       expertise.bon_commande_number),
            ("Date bon de commande",     _date(expertise.bon_commande_date)),
            ("Gouvernorat",              expertise.get_gouvernorat_display()),
            ("Maître d'ouvrage",         expertise.maitre_ouvrage),
            ("Spécialités",              expertise.specialties_display if hasattr(expertise, 'specialties_display') else _expertise_specialties(expertise)),
            ("Créé par",                 expertise.created_by.get_full_name() or expertise.created_by.username if expertise.created_by else '–'),
            ("Date de création",         _date(expertise.created_at.date()) if expertise.created_at else '–'),
        ]]
    ]
    story.append(Table(id_data, colWidths=[5*cm, 12*cm], style=_TABLE_STYLE))

    # ── Dossier ───────────────────────────────────────────────────────────────
    story.append(Paragraph('Dossier', _H2))
    story.append(Table([
        ['Champ', 'Valeur'],
        _row('Statut du dossier',       expertise.get_dossier_status_display()),
        _row('Date de complétion',      _date(expertise.dossier_completed_date)),
        _row('Échéance facture (+60j)', _date(expertise.invoice_due_date) if expertise.invoice_due_date else '–'),
        _row('Jours restants',          f'{expertise.invoice_days_remaining} j.' if expertise.invoice_days_remaining is not None else '–'),
    ], colWidths=[5*cm, 12*cm], style=_TABLE_STYLE))

    # ── Facture ───────────────────────────────────────────────────────────────
    story.append(Paragraph('Facture', _H2))
    inv = expertise.get_invoice
    if inv:
        inv_data = [
            ['Champ', 'Valeur'],
            _row("Date d'établissement", _date(inv.establishment_date)),
            _row('Date de transmission', _date(inv.transmission_date)),
            _row('Notes',                inv.notes[:200] if inv.notes else '–'),
        ]
    else:
        inv_data = [['Champ', 'Valeur'], [Paragraph('Aucune facture', _NORMAL), '']]
    story.append(Table(inv_data, colWidths=[5*cm, 12*cm], style=_TABLE_STYLE))

    # ── Ingénieurs ────────────────────────────────────────────────────────────
    story.append(Paragraph('Ingénieurs assignés', _H2))
    eng_data = [['Nom', 'Email', 'Téléphone', 'Spécialités']]
    for eng in expertise.engineers.all():
        eng_data.append([
            Paragraph(eng.name, _NORMAL),
            Paragraph(eng.email, _NORMAL),
            Paragraph(eng.phone or '–', _NORMAL),
            Paragraph(eng.specialties or '–', _NORMAL),
        ])
    if len(eng_data) == 1:
        eng_data.append([Paragraph('Aucun ingénieur', _NORMAL), '', '', ''])
    story.append(Table(eng_data, colWidths=[4*cm, 5*cm, 3*cm, 5*cm], style=_TABLE_STYLE))

    # ── Observations ──────────────────────────────────────────────────────────
    story.append(Paragraph('Observations', _H2))
    obs_data = [['Date', 'Observation', 'Créé par']]
    for obs in expertise.observations.all():
        obs_data.append([
            Paragraph(_date(obs.date), _NORMAL),
            Paragraph(obs.text[:200], _NORMAL),
            Paragraph(obs.created_by.username if obs.created_by else '–', _NORMAL),
        ])
    if len(obs_data) == 1:
        obs_data.append([Paragraph('Aucune observation', _NORMAL), '', ''])
    story.append(Table(obs_data, colWidths=[2.5*cm, 12*cm, 2.5*cm], style=_TABLE_STYLE))

    story.append(Spacer(1, 12))
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.grey))
    story.append(Paragraph(
        'Ce document a été généré automatiquement par le système Maram.',
        _SMALL,
    ))

    doc.build(story)
    return buf.getvalue()


def _expertise_specialties(expertise):
    parts = []
    if expertise.has_structure:
        parts.append('STR')
    if expertise.has_electricite:
        parts.append('ELEC')
    if expertise.has_fluide:
        parts.append('FL')
    if expertise.has_securite_incendie:
        parts.append('SI')
    return ' / '.join(parts) if parts else '–'


def build_expertise_list_pdf(expertises):
    """Return a bytes object containing a landscape A3 PDF table of expertises."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=_landscape(A3),
        leftMargin=1*cm, rightMargin=1*cm,
        topMargin=1*cm, bottomMargin=1*cm,
    )

    styles = getSampleStyleSheet()
    TITLE_S = ParagraphStyle('ELTitle', parent=styles['Title'],
        fontSize=13, spaceAfter=4, textColor=colors.HexColor('#0f3460'))
    META_S  = ParagraphStyle('ELMeta', parent=styles['Normal'],
        fontSize=8, spaceAfter=6, textColor=colors.grey)
    HDR_S   = ParagraphStyle('ELHdr', parent=styles['Normal'],
        fontSize=7, leading=9, fontName='Helvetica-Bold',
        textColor=colors.white, alignment=1)
    CELL_S  = ParagraphStyle('ELCell', parent=styles['Normal'], fontSize=7, leading=9)
    CELL_C  = ParagraphStyle('ELCellC', parent=styles['Normal'], fontSize=7, leading=9, alignment=1)

    _ST_SHORT = {
        'non_prevu': '—', 'non_recu': 'N.Reçu', 'non_approuve': 'N.App.',
        'en_cours': 'En cours', 'approuve': 'Approuvé',
    }
    _ST_COLOR = {
        'non_prevu': '#aaaaaa', 'non_recu': '#dc3545', 'non_approuve': '#fd7e14',
        'en_cours': '#0066cc', 'approuve': '#198754',
    }

    def _st(val):
        c   = _ST_COLOR.get(val, '#333333')
        lbl = _ST_SHORT.get(val, val or '—')
        return Paragraph(f'<font color="{c}"><b>{lbl}</b></font>', CELL_C)

    def _yn(val):
        return (Paragraph('<font color="#198754"><b>✓</b></font>', CELL_C)
                if val else Paragraph('<font color="#cccccc">—</font>', CELL_C))

    def _spec(e):
        parts = []
        if e.has_structure:         parts.append('STR')
        if e.has_electricite:       parts.append('ELEC')
        if e.has_fluide:            parts.append('FL')
        if e.has_securite_incendie: parts.append('SI')
        return Paragraph(' / '.join(parts) if parts else '—', CELL_C)

    def _invoice_status(e):
        inv = e.get_invoice
        if inv and inv.is_complete:
            return Paragraph('<font color="#198754"><b>Transmise</b></font>', CELL_C)
        if inv and inv.is_established:
            return Paragraph('<font color="#0066cc"><b>Établie</b></font>', CELL_C)
        days = e.invoice_days_remaining
        if days is None:
            return Paragraph('<font color="#aaaaaa">—</font>', CELL_C)
        if days < 0:
            return Paragraph(f'<font color="#dc3545"><b>RETARD {abs(days)}j</b></font>', CELL_C)
        if days <= 10:
            return Paragraph(f'<font color="#fd7e14"><b>J-{days}</b></font>', CELL_C)
        return Paragraph('<font color="#0066cc">À faire</font>', CELL_C)

    def _h(text):
        return Paragraph(text, HDR_S)

    headers = [
        _h('#'), _h('N°BC'), _h('Expertise'), _h('Gouv.'), _h('M.O.'), _h('Spéc.'),
        _h('Statut\ndossier'), _h('Complétion'), _h('Échéance\nfacture'), _h('Facture'),
    ]

    expertises = list(expertises)
    rows = [headers]
    for i, e in enumerate(expertises, 1):
        rows.append([
            Paragraph(str(i), CELL_C),
            Paragraph(e.bon_commande_number or '—', CELL_C),
            Paragraph(e.name[:50], CELL_S),
            Paragraph(e.get_gouvernorat_display()[:12], CELL_S),
            Paragraph((e.maitre_ouvrage or '—')[:22], CELL_S),
            _spec(e),
            _st(e.dossier_status),
            Paragraph(_date(e.dossier_completed_date), CELL_C),
            Paragraph(_date(e.invoice_due_date), CELL_C),
            _invoice_status(e),
        ])

    col_widths = [
        0.7*cm,   # #
        1.5*cm,   # N°BC
        7.0*cm,   # Expertise
        2.5*cm,   # Gouv.
        4.0*cm,   # M.O.
        2.5*cm,   # Spéc.
        2.5*cm,   # Statut dossier
        2.5*cm,   # Complétion
        2.5*cm,   # Échéance facture
        2.5*cm,   # Facture
    ]

    table = Table(rows, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0),  colors.HexColor('#0f3460')),
        ('ROWBACKGROUNDS',(0, 1), (-1, -1), [colors.HexColor('#eef2ff'), colors.white]),
        ('GRID',          (0, 0), (-1, -1), 0.3, colors.HexColor('#cccccc')),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 3),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 3),
        ('TOPPADDING',    (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LINEAFTER', (5, 0), (5, -1), 1.0, colors.HexColor('#0f3460')),
        ('LINEAFTER', (6, 0), (6, -1), 1.0, colors.HexColor('#0f3460')),
    ]))

    story = [
        Paragraph('Expertises – Maram', TITLE_S),
        Paragraph(f'Exporté le {date.today().strftime("%d/%m/%Y")}  –  {len(expertises)} expertise(s)', META_S),
        table,
    ]
    doc.build(story)
    buf.seek(0)
    return buf.getvalue()


def build_project_list_pdf(projects):
    """Return a bytes object containing a landscape A3 PDF table of projects."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=_landscape(A3),
        leftMargin=1*cm, rightMargin=1*cm,
        topMargin=1*cm, bottomMargin=1*cm,
    )

    styles = getSampleStyleSheet()
    TITLE_S = ParagraphStyle('LTitle', parent=styles['Title'],
        fontSize=13, spaceAfter=4, textColor=colors.HexColor('#0f3460'))
    META_S  = ParagraphStyle('LMeta', parent=styles['Normal'],
        fontSize=8, spaceAfter=6, textColor=colors.grey)
    HDR_S   = ParagraphStyle('LHdr', parent=styles['Normal'],
        fontSize=7, leading=9, fontName='Helvetica-Bold',
        textColor=colors.white, alignment=1)
    CELL_S  = ParagraphStyle('LCell', parent=styles['Normal'],
        fontSize=7, leading=9)
    CELL_C  = ParagraphStyle('LCellC', parent=styles['Normal'],
        fontSize=7, leading=9, alignment=1)

    _ST_SHORT = {
        'non_prevu': '—', 'non_recu': 'N.Reçu', 'non_approuve': 'N.App.',
        'en_cours': 'En cours', 'approuve': 'Approuvé',
    }
    _ST_COLOR = {
        'non_prevu': '#aaaaaa', 'non_recu': '#dc3545', 'non_approuve': '#fd7e14',
        'en_cours': '#0066cc', 'approuve': '#198754',
    }

    def _st(has_flag, val):
        if not has_flag:
            return Paragraph('<font color="#cccccc">—</font>', CELL_C)
        c = _ST_COLOR.get(val, '#333333')
        lbl = _ST_SHORT.get(val, val or '—')
        return Paragraph(f'<font color="{c}"><b>{lbl}</b></font>', CELL_C)

    def _yn(val):
        return (Paragraph('<font color="#198754"><b>✓</b></font>', CELL_C)
                if val else Paragraph('<font color="#cccccc">—</font>', CELL_C))

    def _spec(p):
        parts = []
        if p.has_structure:        parts.append('STR')
        if p.has_electricite:      parts.append('ELEC')
        if p.has_fluide:           parts.append('FL')
        if p.has_securite_incendie: parts.append('SI')
        return Paragraph(' / '.join(parts) if parts else '—', CELL_C)

    def _h(text):
        return Paragraph(text, HDR_S)

    headers = [
        _h('#'), _h('N°BC'), _h('Projet'), _h('Gouv.'), _h('M.O.'), _h('Spéc.'),
        _h('DAO\nSTR'), _h('DAO\nELEC'), _h('DAO\nFL'), _h('DAO\nSI'),
        _h('D0'),
        _h('EXE\nSTR'), _h('EXE\nELEC'), _h('EXE\nFL'), _h('EXE\nSI'),
        _h('Vis.'), _h('D6'), _h('RPRO'), _h('RDEF'),
    ]

    rows = [headers]
    projects = list(projects)
    for i, p in enumerate(projects, 1):
        rows.append([
            Paragraph(str(i), CELL_C),
            Paragraph(p.bon_commande_number or '—', CELL_C),
            Paragraph(p.name[:50], CELL_S),
            Paragraph(p.get_gouvernorat_display()[:12], CELL_S),
            Paragraph((p.maitre_ouvrage or '—')[:22], CELL_S),
            _spec(p),
            _st(p.has_structure,          p.dao_structure),
            _st(p.has_electricite,        p.dao_electricite),
            _st(p.has_fluide,             p.dao_fluide),
            _st(p.has_securite_incendie,  p.dao_securite_incendie),
            _yn(p.d0_done),
            _st(p.has_structure,          p.exe_structure),
            _st(p.has_electricite,        p.exe_electricite),
            _st(p.has_fluide,             p.exe_fluide),
            _st(p.has_securite_incendie,  p.exe_securite_incendie),
            Paragraph(f'{p.completed_visits}/{p.planned_visits}', CELL_C),
            _yn(p.d6_done),
            _yn(p.rpro),
            _yn(p.rdef),
        ])

    col_widths = [
        0.7*cm,  # #
        1.5*cm,  # N°BC
        5.5*cm,  # Projet
        2.5*cm,  # Gouv.
        3.0*cm,  # M.O.
        2.0*cm,  # Spéc.
        2.0*cm,  # DAO STR
        2.0*cm,  # DAO ELEC
        2.0*cm,  # DAO FL
        2.0*cm,  # DAO SI
        1.0*cm,  # D0
        2.0*cm,  # EXE STR
        2.0*cm,  # EXE ELEC
        2.0*cm,  # EXE FL
        2.0*cm,  # EXE SI
        1.3*cm,  # Vis.
        1.0*cm,  # D6
        1.0*cm,  # RPRO
        1.0*cm,  # RDEF
    ]

    table = Table(rows, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0),  colors.HexColor('#0f3460')),
        ('ROWBACKGROUNDS',(0, 1), (-1, -1), [colors.HexColor('#eef2ff'), colors.white]),
        ('GRID',          (0, 0), (-1, -1), 0.3, colors.HexColor('#cccccc')),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 3),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 3),
        ('TOPPADDING',    (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        # Group separators
        ('LINEAFTER', (5,  0), (5,  -1), 1.0, colors.HexColor('#0f3460')),
        ('LINEAFTER', (9,  0), (9,  -1), 1.0, colors.HexColor('#0f3460')),
        ('LINEAFTER', (10, 0), (10, -1), 1.0, colors.HexColor('#0f3460')),
        ('LINEAFTER', (14, 0), (14, -1), 1.0, colors.HexColor('#0f3460')),
        ('LINEAFTER', (15, 0), (15, -1), 1.0, colors.HexColor('#0f3460')),
    ]))

    story = [
        Paragraph('Tableau de bord – Maram', TITLE_S),
        Paragraph(f'Exporté le {date.today().strftime("%d/%m/%Y")}  –  {len(projects)} projet(s)', META_S),
        table,
    ]
    doc.build(story)
    buf.seek(0)
    return buf.getvalue()
