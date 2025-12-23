<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class ScraperData extends Model
{
    protected $table = 'scraper_data';

    protected $fillable = [
        'process_id',
        'job_id',
        'data',
        'created_at'
    ];

    protected $casts = [
        'data' => 'array',
        'created_at' => 'datetime'
    ];
}
