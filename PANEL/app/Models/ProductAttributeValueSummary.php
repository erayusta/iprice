<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class ProductAttributeValueSummary extends Model
{
    use HasFactory;

    protected $table = 'product_attribute_value_summary';

    protected $fillable = [
        'company_id',
        'value',
        'job_id',
        'product_id',
        'attribute_id',
        'mpn',
    ];

    /**
     * Get the company that owns the product attribute value summary.
     */
    public function company()
    {
        return $this->belongsTo(Company::class);
    }

    /**
     * Get the attribute that owns the product attribute value summary.
     */
    public function attribute()
    {
        return $this->belongsTo(Attribute::class);
    }
}

