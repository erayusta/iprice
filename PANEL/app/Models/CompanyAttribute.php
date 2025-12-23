<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class CompanyAttribute extends Model
{
    use HasFactory;

    protected $fillable = [
        'company_id',
        'attribute_id',
        'type',
        'value',
    ];

    /**
     * Get the company that owns the attribute.
     */
    public function company()
    {
        return $this->belongsTo(Company::class);
    }

    /**
     * Get the attribute that owns the company attribute.
     */
    public function attribute()
    {
        return $this->belongsTo(Attribute::class);
    }
}