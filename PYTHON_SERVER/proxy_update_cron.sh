#!/bin/bash
###############################################################################
# Proxy Update Cron Script
###############################################################################
# Bu script 6 saatte bir proxy listesini günceller.
#
# Crontab'e ekleme:
# 0 */6 * * * /app/proxy_update_cron.sh >> /var/log/proxy_update.log 2>&1
#
# Açıklama: Her 6 saatte bir (00:00, 06:00, 12:00, 18:00) çalışır
###############################################################################

echo "=================================================="
echo "🔄 Proxy Update Cron - $(date)"
echo "=================================================="

# Docker container içinde çalıştır
docker exec price_analysis_service-app-1 python -m app.tasks.proxy_update

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Proxy güncelleme başarılı - $(date)"
else
    echo "❌ Proxy güncelleme başarısız (Exit: $EXIT_CODE) - $(date)"
fi

echo "=================================================="
echo ""

