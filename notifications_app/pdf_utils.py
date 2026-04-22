"""PDF generation utilities for project/expertise deletion reports."""
import io
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
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
            ("Type maître d'ouvrage",    project.get_maitre_ouvrage_type_display()),
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
