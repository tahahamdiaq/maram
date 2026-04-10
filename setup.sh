#!/bin/bash
# ═══════════════════════════════════════════════════
#  Maram – Script de démarrage
# ═══════════════════════════════════════════════════

set -e

echo "=== Maram – Setup ==="

# 1. Venv
if [ ! -d "venv" ]; then
  echo "[1/5] Création du virtualenv..."
  python3 -m venv venv
else
  echo "[1/5] Virtualenv existant – OK"
fi

source venv/bin/activate || . venv/bin/activate

# 2. Dépendances
echo "[2/5] Installation des dépendances..."
pip install -r requirements.txt -q

# 3. PostgreSQL via Docker (optionnel)
if command -v docker &> /dev/null; then
  echo "[3/5] Démarrage de PostgreSQL via Docker..."
  docker-compose up -d db
  echo "Attente démarrage PostgreSQL..."
  sleep 5
else
  echo "[3/5] Docker non trouvé – assurez-vous que PostgreSQL est démarré manuellement."
  echo "      Ou modifiez .env pour utiliser SQLite (voir commentaires dans settings.py)"
fi

# 4. Migrations
echo "[4/5] Application des migrations..."
python manage.py migrate

# 5. Superuser (si pas déjà créé)
echo "[5/5] Création du superutilisateur (si nécessaire)..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@maram.tn', 'admin123')
    print('Superutilisateur créé: admin / admin123')
else:
    print('Superutilisateur déjà existant.')
"

# 6. Collecte des fichiers statiques
python manage.py collectstatic --noinput -v 0

echo ""
echo "═══════════════════════════════════════════════"
echo " Maram est prêt !"
echo "═══════════════════════════════════════════════"
echo ""
echo " Démarrer le serveur :  python manage.py runserver"
echo " Interface :            http://127.0.0.1:8000"
echo " Admin Django :         http://127.0.0.1:8000/admin"
echo " Identifiants :         admin / admin123"
echo ""
echo " Vérification des notifications (cron) :"
echo "   python manage.py check_notifications --send-emails"
echo ""
