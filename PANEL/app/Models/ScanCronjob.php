<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class ScanCronjob extends Model
{
    protected $fillable = [
        'time',
        'scan_type',
        'company_id',
        'active'
    ];

    protected $casts = [
        'active' => 'boolean'
    ];

    /**
     * İlişkili firma
     */
    public function company(): BelongsTo
    {
        return $this->belongsTo(Company::class);
    }

    /**
     * Aktif cron job'ları getir
     */
    public function scopeActive($query)
    {
        return $query->where('active', true);
    }

    /**
     * Belirli saatteki cron job'ları getir
     * PostgreSQL time field'i için format düzeltmesi
     */
    public function scopeAtTime($query, $time)
    {
        // Time field'ini HH:MM formatına çevirip karşılaştır
        // PostgreSQL time field'i '12:30:00' formatında saklanır, biz '12:30' ile karşılaştırıyoruz
        return $query->whereRaw("TO_CHAR(time, 'HH24:MI') = ?", [$time]);
    }

    /**
     * Genel tarama cron job'ları
     */
    public function scopeGeneral($query)
    {
        return $query->where('scan_type', 'all');
    }

    /**
     * Firma bazlı tarama cron job'ları
     */
    public function scopeCompany($query)
    {
        return $query->where('scan_type', 'company');
    }
}
