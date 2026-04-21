# Seed Data – Maram

Run these SQL blocks in order against your PostgreSQL database.

---

## 1. Engineers

```sql
INSERT INTO projects_engineer (name, email, phone, specialties, user_id) VALUES
('Ahmed Ben Salah',  'a.bensalah@maram.tn', '+216 71 123 456', 'Structure, Béton armé',           NULL),
('Sonia Chaabane',   's.chaabane@maram.tn',  '+216 71 234 567', 'Électricité, HTA/BTA',            NULL),
('Karim Trabelsi',   'k.trabelsi@maram.tn',  '+216 71 345 678', 'Fluide, Climatisation',           NULL),
('Imen Gharbi',      'i.gharbi@maram.tn',    '+216 71 456 789', 'Structure, Charpente métallique', NULL),
('Nizar Hamrouni',   'n.hamrouni@maram.tn',  '+216 71 567 890', 'Électricité, Courants faibles',   NULL);
```

---

## 2. Projects

```sql
INSERT INTO projects_project (
  name, bon_commande_number, bon_commande_date, gouvernorat,
  maitre_ouvrage, maitre_ouvrage_type,
  has_structure, has_electricite, has_fluide,
  planned_visits, completed_visits,
  dao_structure, dao_electricite, dao_fluide, dao_completed_date,
  d0_done, d0_date,
  exe_structure, exe_electricite, exe_fluide, exe_started_date,
  d6_done, d6_date,
  rpro, rpro_date, rdef, rdef_date,
  created_at, updated_at, created_by_id
) VALUES
(
  'Construction école primaire Cité Ettahrir', 'BC-2024-001', '2024-01-15', 'tunis',
  'Ministère de l''Éducation', 'DRE',
  true, true, true, 12, 12,
  'approuve', 'approuve', 'approuve', '2024-03-10',
  true, '2024-04-05',
  'approuve', 'approuve', 'approuve', '2024-05-01',
  true, '2024-11-20',
  true, '2024-12-01', true, '2025-06-01',
  NOW(), NOW(), (SELECT id FROM auth_user WHERE username='admin')
),
(
  'Réhabilitation centre de santé de base Mnihla', 'BC-2024-002', '2024-03-20', 'ariana',
  'Ministère de la Santé', 'CRE',
  true, true, true, 8, 5,
  'approuve', 'approuve', 'en_cours', NULL,
  true, '2024-05-12',
  'en_cours', 'non_recu', 'non_prevu', '2024-07-01',
  false, NULL,
  false, NULL, false, NULL,
  NOW(), NOW(), (SELECT id FROM auth_user WHERE username='admin')
),
(
  'Extension lycée technique Sfax Sud', 'BC-2024-003', '2024-02-08', 'sfax',
  'Ministère de l''Éducation', 'DRE',
  true, true, false, 10, 10,
  'approuve', 'approuve', 'non_prevu', '2024-04-20',
  true, '2024-05-03',
  'approuve', 'approuve', 'non_prevu', '2024-06-01',
  true, '2025-01-15',
  true, '2025-02-01', false, NULL,
  NOW(), NOW(), (SELECT id FROM auth_user WHERE username='admin')
),
(
  'Construction poste de transformation HTA/BTA Sousse', 'BC-2024-004', '2024-06-01', 'sousse',
  'STEG Sousse', 'autre',
  false, true, false, 6, 3,
  'non_prevu', 'approuve', 'non_prevu', '2024-08-05',
  true, '2024-09-10',
  'non_prevu', 'en_cours', 'non_prevu', '2024-10-01',
  false, NULL,
  false, NULL, false, NULL,
  NOW(), NOW(), (SELECT id FROM auth_user WHERE username='admin')
),
(
  'Réhabilitation maison des jeunes Bizerte', 'BC-2024-005', '2024-09-15', 'bizerte',
  'Commissariat Régional de la Jeunesse', 'CRE',
  true, true, true, 6, 0,
  'en_cours', 'non_recu', 'non_recu', NULL,
  false, NULL,
  'non_prevu', 'non_prevu', 'non_prevu', NULL,
  false, NULL,
  false, NULL, false, NULL,
  NOW(), NOW(), (SELECT id FROM auth_user WHERE username='admin')
),
(
  'Construction salle omnisports Kairouan', 'BC-2025-001', '2025-01-10', 'kairouan',
  'Ministère de la Jeunesse et du Sport', 'DRE',
  true, true, true, 15, 2,
  'non_recu', 'non_recu', 'non_recu', NULL,
  false, NULL,
  'non_prevu', 'non_prevu', 'non_prevu', NULL,
  false, NULL,
  false, NULL, false, NULL,
  NOW(), NOW(), (SELECT id FROM auth_user WHERE username='admin')
),
(
  'Réaménagement hôpital régional Nabeul', 'BC-2023-008', '2023-06-05', 'nabeul',
  'Ministère de la Santé', 'CRE',
  true, true, true, 20, 20,
  'approuve', 'approuve', 'approuve', '2023-09-01',
  true, '2023-10-01',
  'approuve', 'approuve', 'approuve', '2023-11-01',
  true, '2024-10-15',
  true, '2024-11-01', true, '2025-05-15',
  NOW(), NOW(), (SELECT id FROM auth_user WHERE username='admin')
);
```

---

## 3. Engineer ↔ Project links

```sql
-- BC-2024-001: Ahmed, Sonia, Karim
INSERT INTO projects_project_engineers (project_id, engineer_id)
SELECT p.id, e.id FROM projects_project p, projects_engineer e
WHERE p.bon_commande_number = 'BC-2024-001'
AND e.email IN ('a.bensalah@maram.tn','s.chaabane@maram.tn','k.trabelsi@maram.tn');

-- BC-2024-002: Ahmed, Sonia, Karim
INSERT INTO projects_project_engineers (project_id, engineer_id)
SELECT p.id, e.id FROM projects_project p, projects_engineer e
WHERE p.bon_commande_number = 'BC-2024-002'
AND e.email IN ('a.bensalah@maram.tn','s.chaabane@maram.tn','k.trabelsi@maram.tn');

-- BC-2024-003: Imen, Sonia
INSERT INTO projects_project_engineers (project_id, engineer_id)
SELECT p.id, e.id FROM projects_project p, projects_engineer e
WHERE p.bon_commande_number = 'BC-2024-003'
AND e.email IN ('i.gharbi@maram.tn','s.chaabane@maram.tn');

-- BC-2024-004: Nizar
INSERT INTO projects_project_engineers (project_id, engineer_id)
SELECT p.id, e.id FROM projects_project p, projects_engineer e
WHERE p.bon_commande_number = 'BC-2024-004'
AND e.email = 'n.hamrouni@maram.tn';

-- BC-2024-005: Ahmed, Karim
INSERT INTO projects_project_engineers (project_id, engineer_id)
SELECT p.id, e.id FROM projects_project p, projects_engineer e
WHERE p.bon_commande_number = 'BC-2024-005'
AND e.email IN ('a.bensalah@maram.tn','k.trabelsi@maram.tn');

-- BC-2025-001: Imen, Sonia, Karim
INSERT INTO projects_project_engineers (project_id, engineer_id)
SELECT p.id, e.id FROM projects_project p, projects_engineer e
WHERE p.bon_commande_number = 'BC-2025-001'
AND e.email IN ('i.gharbi@maram.tn','s.chaabane@maram.tn','k.trabelsi@maram.tn');

-- BC-2023-008: all 5
INSERT INTO projects_project_engineers (project_id, engineer_id)
SELECT p.id, e.id FROM projects_project p, projects_engineer e
WHERE p.bon_commande_number = 'BC-2023-008';
```

---

## 4. Invoices

```sql
-- BC-2024-001 (fully complete — 3 invoices)
INSERT INTO projects_invoice (project_id, invoice_number, establishment_date, transmission_date, notes, created_at)
SELECT p.id, 1, '2024-03-17', '2024-03-24', 'Facture suite à approbation DAO', NOW()
FROM projects_project p WHERE p.bon_commande_number = 'BC-2024-001';

INSERT INTO projects_invoice (project_id, invoice_number, establishment_date, transmission_date, notes, created_at)
SELECT p.id, 2, '2024-07-30', '2024-08-06', 'Facture 50% visites réalisées', NOW()
FROM projects_project p WHERE p.bon_commande_number = 'BC-2024-001';

INSERT INTO projects_invoice (project_id, invoice_number, establishment_date, transmission_date, notes, created_at)
SELECT p.id, 3, '2025-06-11', '2025-06-18', 'Facture finale après RDEF', NOW()
FROM projects_project p WHERE p.bon_commande_number = 'BC-2024-001';

-- BC-2024-003 (RPRO done, no RDEF yet — 2 invoices)
INSERT INTO projects_invoice (project_id, invoice_number, establishment_date, transmission_date, notes, created_at)
SELECT p.id, 1, '2024-04-27', '2024-05-04', 'Facture suite à approbation DAO', NOW()
FROM projects_project p WHERE p.bon_commande_number = 'BC-2024-003';

INSERT INTO projects_invoice (project_id, invoice_number, establishment_date, transmission_date, notes, created_at)
SELECT p.id, 2, '2024-08-30', '2024-09-06', 'Facture 50% visites réalisées', NOW()
FROM projects_project p WHERE p.bon_commande_number = 'BC-2024-003';

-- BC-2023-008 (fully complete — 3 invoices)
INSERT INTO projects_invoice (project_id, invoice_number, establishment_date, transmission_date, notes, created_at)
SELECT p.id, 1, '2023-09-08', '2023-09-15', 'Facture suite à approbation DAO', NOW()
FROM projects_project p WHERE p.bon_commande_number = 'BC-2023-008';

INSERT INTO projects_invoice (project_id, invoice_number, establishment_date, transmission_date, notes, created_at)
SELECT p.id, 2, '2024-01-30', '2024-02-06', 'Facture 50% visites réalisées', NOW()
FROM projects_project p WHERE p.bon_commande_number = 'BC-2023-008';

INSERT INTO projects_invoice (project_id, invoice_number, establishment_date, transmission_date, notes, created_at)
SELECT p.id, 3, '2025-05-25', '2025-06-01', 'Facture finale après RDEF', NOW()
FROM projects_project p WHERE p.bon_commande_number = 'BC-2023-008';
```

---

## 5. Projects with active notifications (deadlines around 2026-04-20)

### Projects

```sql
INSERT INTO projects_project (
  name, bon_commande_number, bon_commande_date, gouvernorat,
  maitre_ouvrage, maitre_ouvrage_type,
  has_structure, has_electricite, has_fluide,
  planned_visits, completed_visits,
  dao_structure, dao_electricite, dao_fluide, dao_completed_date,
  d0_done, d0_date,
  exe_structure, exe_electricite, exe_fluide, exe_started_date,
  d6_done, d6_date,
  rpro, rpro_date, rdef, rdef_date,
  created_at, updated_at, created_by_id
) VALUES

-- Facture N°1 en RETARD (critique) — DAO done 2026-03-01, due was 2026-03-22, overdue by 29 days
(
  'Réhabilitation école primaire Hay Hlel', 'BC-2026-N01', '2025-11-10', 'monastir',
  'Ministère de l''Éducation', 'DRE',
  true, true, false, 8, 3,
  'approuve', 'approuve', 'non_prevu', '2026-03-01',
  true, '2026-03-10',
  'en_cours', 'non_recu', 'non_prevu', '2026-03-15',
  false, NULL,
  false, NULL, false, NULL,
  NOW(), NOW(), (SELECT id FROM auth_user WHERE username='admin')
),

-- Facture N°1 J-2 (critique) — DAO done 2026-04-01, due 2026-04-22, 2 days left
(
  'Construction annexe mairie Manouba', 'BC-2026-N02', '2025-12-01', 'manouba',
  'Commune de Manouba', 'autre',
  true, false, false, 6, 2,
  'approuve', 'non_prevu', 'non_prevu', '2026-04-01',
  true, '2026-04-08',
  'en_cours', 'non_prevu', 'non_prevu', '2026-04-10',
  false, NULL,
  false, NULL, false, NULL,
  NOW(), NOW(), (SELECT id FROM auth_user WHERE username='admin')
),

-- Facture N°1 J-7 (important) — DAO done 2026-04-06, due 2026-04-27, 7 days left
-- + D0 not done yet → d0_reminder
(
  'Extension centre de formation professionnelle Gafsa', 'BC-2026-N03', '2026-01-15', 'gafsa',
  'Ministère de la Formation Professionnelle', 'CRE',
  true, true, true, 10, 0,
  'approuve', 'approuve', 'approuve', '2026-04-06',
  false, NULL,
  'non_prevu', 'non_prevu', 'non_prevu', NULL,
  false, NULL,
  false, NULL, false, NULL,
  NOW(), NOW(), (SELECT id FROM auth_user WHERE username='admin')
),

-- Facture N°2 prête (normal) — invoice1 done, 60% visits, no invoice2
(
  'Réhabilitation poste de santé Siliana', 'BC-2026-N04', '2025-09-20', 'siliana',
  'Ministère de la Santé', 'CRE',
  false, true, true, 10, 6,
  'non_prevu', 'approuve', 'approuve', '2025-11-15',
  true, '2025-11-25',
  'non_prevu', 'approuve', 'en_cours', '2025-12-10',
  false, NULL,
  false, NULL, false, NULL,
  NOW(), NOW(), (SELECT id FROM auth_user WHERE username='admin')
),

-- Facture N°3 prête (important) + D6 non fait (normal) — 100% visits, RPRO+RDEF done
(
  'Construction centre culturel Zaghouan', 'BC-2025-N05', '2025-03-01', 'zaghouan',
  'Ministère des Affaires Culturelles', 'DRE',
  true, true, true, 12, 12,
  'approuve', 'approuve', 'approuve', '2025-06-01',
  true, '2025-06-15',
  'approuve', 'approuve', 'approuve', '2025-07-01',
  false, NULL,
  true, '2026-01-10', true, '2026-03-20',
  NOW(), NOW(), (SELECT id FROM auth_user WHERE username='admin')
);
```

### Invoice for BC-2026-N04 (invoice1 established, no invoice2 yet)

```sql
INSERT INTO projects_invoice (project_id, invoice_number, establishment_date, transmission_date, notes, created_at)
SELECT p.id, 1, '2025-11-22', '2025-11-29', 'Facture N°1 établie suite à approbation DAO', NOW()
FROM projects_project p WHERE p.bon_commande_number = 'BC-2026-N04';
```

### Invoices for BC-2025-N05 (invoice1 + invoice2 done, no invoice3 yet)

```sql
INSERT INTO projects_invoice (project_id, invoice_number, establishment_date, transmission_date, notes, created_at)
SELECT p.id, 1, '2025-06-08', '2025-06-15', 'Facture N°1 établie', NOW()
FROM projects_project p WHERE p.bon_commande_number = 'BC-2025-N05';

INSERT INTO projects_invoice (project_id, invoice_number, establishment_date, transmission_date, notes, created_at)
SELECT p.id, 2, '2025-10-01', '2025-10-08', 'Facture N°2 établie – 50% visites atteintes', NOW()
FROM projects_project p WHERE p.bon_commande_number = 'BC-2025-N05';
```

### Notifications

```sql
-- BC-2026-N01: Facture N°1 en retard (critique)
INSERT INTO notifications_app_notification (project_id, notification_type, priority, message, status, email_sent, email_error, created_at, updated_at)
SELECT p.id, 'facture1_overdue', 'critique',
  'RETARD – Facture N°1 en retard de 29 jour(s) pour le projet "Réhabilitation école primaire Hay Hlel".',
  'unread', false, '', NOW(), NOW()
FROM projects_project p WHERE p.bon_commande_number = 'BC-2026-N01';

-- BC-2026-N02: Facture N°1 J-2 (critique)
INSERT INTO notifications_app_notification (project_id, notification_type, priority, message, status, email_sent, email_error, created_at, updated_at)
SELECT p.id, 'facture1_j2', 'critique',
  'URGENT – Il ne reste que 2 jour(s) pour établir la Facture N°1 du projet "Construction annexe mairie Manouba" (échéance : 22/04/2026).',
  'unread', false, '', NOW(), NOW()
FROM projects_project p WHERE p.bon_commande_number = 'BC-2026-N02';

-- BC-2026-N03: Facture N°1 J-7 (important) + D0 reminder (normal)
INSERT INTO notifications_app_notification (project_id, notification_type, priority, message, status, email_sent, email_error, created_at, updated_at)
SELECT p.id, 'facture1_j7', 'important',
  'Rappel – Il vous reste 7 jour(s) pour établir la Facture N°1 du projet "Extension centre de formation professionnelle Gafsa" (échéance : 27/04/2026).',
  'unread', false, '', NOW(), NOW()
FROM projects_project p WHERE p.bon_commande_number = 'BC-2026-N03';

INSERT INTO notifications_app_notification (project_id, notification_type, priority, message, status, email_sent, email_error, created_at, updated_at)
SELECT p.id, 'd0_reminder', 'normal',
  'Rappel – Le dossier D0 doit être réalisé avant le lancement de la phase EXE pour le projet "Extension centre de formation professionnelle Gafsa".',
  'unread', false, '', NOW(), NOW()
FROM projects_project p WHERE p.bon_commande_number = 'BC-2026-N03';

-- BC-2026-N04: Facture N°2 prête (normal)
INSERT INTO notifications_app_notification (project_id, notification_type, priority, message, status, email_sent, email_error, created_at, updated_at)
SELECT p.id, 'facture2_ready', 'normal',
  'Facture N°2 à établir – 50 % des visites prévues sont réalisées pour le projet "Réhabilitation poste de santé Siliana" (6/10 visites).',
  'unread', false, '', NOW(), NOW()
FROM projects_project p WHERE p.bon_commande_number = 'BC-2026-N04';

-- BC-2025-N05: Facture N°3 prête (important) + D6 reminder (normal)
INSERT INTO notifications_app_notification (project_id, notification_type, priority, message, status, email_sent, email_error, created_at, updated_at)
SELECT p.id, 'facture3_ready', 'important',
  'Facture N°3 à établir – toutes les conditions sont remplies pour le projet "Construction centre culturel Zaghouan" (100 % visites, RPRO et RDEF validées).',
  'unread', false, '', NOW(), NOW()
FROM projects_project p WHERE p.bon_commande_number = 'BC-2025-N05';

INSERT INTO notifications_app_notification (project_id, notification_type, priority, message, status, email_sent, email_error, created_at, updated_at)
SELECT p.id, 'd6_reminder', 'normal',
  'Rappel – Le dossier D6 doit être réalisé avec la Facture N°3 pour le projet "Construction centre culturel Zaghouan".',
  'unread', false, '', NOW(), NOW()
FROM projects_project p WHERE p.bon_commande_number = 'BC-2025-N05';
```
