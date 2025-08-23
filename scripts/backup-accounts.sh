#!/bin/bash

# JenMoney Account Backup Script
# Backs up current account data to a JSON file

BASE_URL="http://localhost:8000/api/v1"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="backups"
BACKUP_FILE="${BACKUP_DIR}/accounts_backup_${TIMESTAMP}.json"

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

echo "Backing up JenMoney data to ${BACKUP_FILE}..."

# Create JSON backup with all data
cat > "${BACKUP_FILE}" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "settings": $(curl -s "${BASE_URL}/settings/"),
  "currency_rates": $(curl -s "${BASE_URL}/currency-rates/"),
  "accounts": $(curl -s "${BASE_URL}/accounts/")
}
EOF

# Pretty print the JSON
python3 -m json.tool "${BACKUP_FILE}" > "${BACKUP_FILE}.tmp" && mv "${BACKUP_FILE}.tmp" "${BACKUP_FILE}"

echo "✅ Backup complete: ${BACKUP_FILE}"
echo ""
echo "Account Summary:"
echo "----------------"
curl -s "${BASE_URL}/accounts/" | python3 -c "
import json
import sys
data = json.load(sys.stdin)
total_rub = 0
for acc in data['items']:
    print(f\"{acc['name']:20} | {acc['currency']:3} | {acc['balance']:>12,.2f}\")
    if acc['balance_in_default_currency']:
        total_rub += acc['balance_in_default_currency']
    elif acc['currency'] == 'RUB':
        total_rub += acc['balance']

print('-' * 50)
print(f\"{'Total (RUB)':20} |     | {total_rub:>12,.2f}\")
"