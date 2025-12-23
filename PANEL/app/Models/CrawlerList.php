<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class CrawlerList extends Model
{
    use HasFactory;

    protected $table = 'crawler_list';

    protected $fillable = [
        'name',
    ];

    /**
     * Get the companies for the crawler.
     */
    public function companies()
    {
        return $this->hasMany(Company::class, 'crawler_id');
    }
}