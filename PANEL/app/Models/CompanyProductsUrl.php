<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class CompanyProductsUrl extends Model
{
    use HasFactory;

    protected $table = 'company_products_urls';

    protected $fillable = [
        'company_id',
        'product_id',
        'url',
    ];

    /**
     * Get the company that owns the product URL.
     */
    public function company()
    {
        return $this->belongsTo(Company::class);
    }

    /**
     * Get the user product that owns the URL.
     */
    public function userProduct()
    {
        return $this->belongsTo(UserProduct::class, 'product_id');
    }
}