<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Proxy extends Model
{
    protected $fillable = [
        'proxy_id',
        'proxy_string_id',
        'ip',
        'port',
        'country',
        'city',
        'region',
        'anonymity_level',
        'isp',
        'asn',
        'organization',
        'speed',
        'latency',
        'response_time',
        'last_checked',
        'protocols',
        'working_percent',
        'up_time',
        'up_time_success_count',
        'up_time_try_count',
        'created_at_proxy',
        'updated_at_proxy',
        'active'
    ];

    protected $casts = [
        'last_checked' => 'datetime',
        'created_at_proxy' => 'datetime',
        'updated_at_proxy' => 'datetime',
        'active' => 'boolean',
        'latency' => 'decimal:3',
        'working_percent' => 'decimal:2',
        'up_time' => 'decimal:2'
    ];
}
