#!/bin/bash

# JenMoney Account Restore Script
# Restores account data from a backup JSON file

BASE_URL="http://localhost:8000/api/v1"

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file.json>"
    echo ""
    echo "Available backups:"
    ls -la backups/*.json 2>/dev/null || echo "No backups found in backups/ directory"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "${BACKUP_FILE}" ]; then
    echo "Error: Backup file ${BACKUP_FILE} not found"
    exit 1
fi

echo "Restoring JenMoney data from ${BACKUP_FILE}..."

# Extract data from backup
SETTINGS=$(python3 -c "import json; data = json.load(open('${BACKUP_FILE}')); print(json.dumps(data['settings']))")
RATES=$(python3 -c "import json; data = json.load(open('${BACKUP_FILE}')); print(json.dumps(data['currency_rates']))")
ACCOUNTS=$(python3 -c "import json; data = json.load(open('${BACKUP_FILE}')); print(json.dumps(data['accounts']['items']))")

# Restore settings
echo "1. Restoring user settings..."
DEFAULT_CURRENCY=$(echo "${SETTINGS}" | python3 -c "import json, sys; print(json.load(sys.stdin)['default_currency'])")
curl -s -X PATCH "${BASE_URL}/settings/" \
    -H "Content-Type: application/json" \
    -d "{\"default_currency\": \"${DEFAULT_CURRENCY}\"}" > /dev/null
echo "   ✅ Default currency set to ${DEFAULT_CURRENCY}"

# Restore currency rates
echo "2. Restoring currency rates..."
RATES_IMPORT=$(echo "${RATES}" | python3 -c "
import json, sys
rates = json.load(sys.stdin)
import_data = {'rates': []}
for rate in rates:
    import_data['rates'].append({
        'currency_from': rate['currency_from'],
        'currency_to': rate['currency_to'],
        'rate': rate['rate'],
        'effective_from': rate['effective_from']
    })
print(json.dumps(import_data))
")
curl -s -X POST "${BASE_URL}/currency-rates/import" \
    -H "Content-Type: application/json" \
    -d "${RATES_IMPORT}" > /dev/null
echo "   ✅ $(echo "${RATES}" | python3 -c "import json, sys; print(len(json.load(sys.stdin)))") exchange rates restored"

# Restore accounts
echo "3. Restoring accounts..."
echo "${ACCOUNTS}" | python3 -c "
import json, sys, subprocess

accounts = json.load(sys.stdin)
for acc in accounts:
    account_data = {
        'name': acc['name'],
        'currency': acc['currency'],
        'balance': acc['balance']
    }
    if acc.get('description'):
        account_data['description'] = acc['description']
    
    result = subprocess.run(
        ['curl', '-s', '-X', 'POST', '${BASE_URL}/accounts/',
         '-H', 'Content-Type: application/json',
         '-d', json.dumps(account_data)],
        capture_output=True
    )
    print(f\"   ✅ {acc['name']} ({acc['currency']}): {acc['balance']:,.2f}\")
"

echo ""
echo "✅ Restore complete!"
echo ""
echo "Verification:"
curl -s "${BASE_URL}/accounts/total-balance/" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f\"Total Portfolio Value: {data['total_balance']:,.2f} {data['default_currency']}\")
for curr, amount in data['currency_breakdown'].items():
    print(f\"  {curr}: {amount:,.2f}\")
"