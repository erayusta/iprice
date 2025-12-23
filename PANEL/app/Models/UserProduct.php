<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class UserProduct extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id',
        'name',
        'image',
        'title',
        'mpn',
        'gtin',
        'availability',
        'price',
        'sale_price',
        'web_price',
        'web_stock',
        'brand_id',
        'link',
        'product_type',
        'is_active',
    ];

    protected $casts = [
        'price' => 'decimal:2',
        'sale_price' => 'decimal:2',
        'web_price' => 'decimal:2',
    ];

    /**
     * Get the brand for this user product.
     */
    public function brand()
    {
        return $this->belongsTo(Brand::class);
    }

    /**
     * Get the company product URLs for this user product.
     */
    public function companyProductUrls()
    {
        return $this->hasMany(CompanyProductsUrl::class, 'product_id');
    }
}