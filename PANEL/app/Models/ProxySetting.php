<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class ProxySetting extends Model
{
    protected $table = 'proxy_settings';
    
    protected $fillable = [
        'name',
        'is_active',
        'created_by'
    ];

    protected $casts = [
        'is_active' => 'boolean'
    ];

    /**
     * Proxy ayarını oluşturan kullanıcı
     */
    public function creator()
    {
        return $this->belongsTo(User::class, 'created_by');
    }


    /**
     * Proxy durumunu toggle et
     */
    public function toggleStatus()
    {
        $this->update(['is_active' => !$this->is_active]);
        return $this;
    }
}
