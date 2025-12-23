<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Company extends Model
{
    use HasFactory;

    protected $fillable = [
        'name',
        'url',
        'company_logo',
        'crawler_id',
        'server_id',
        'screenshot',
        'marketplace',
        'use_proxy',
        'proxy_id',
        'deleted',
    ];

    protected $casts = [
        'screenshot' => 'string',
        'marketplace' => 'string',
        'use_proxy' => 'boolean',
        'deleted' => 'boolean',
    ];

    /**
     * Get the is_marketplace attribute.
     */
    public function getIsMarketplaceAttribute()
    {
        return $this->marketplace === 'true' || $this->marketplace === true;
    }

    /**
     * Get the full URL for the company logo.
     */
    public function getCompanyLogoAttribute($value)
    {
        if ($value && !str_starts_with($value, 'http')) {
            return url($value);
        }
        return $value;
    }

    /**
     * Get the crawler that owns the company.
     */
    public function crawler()
    {
        return $this->belongsTo(CrawlerList::class, 'crawler_id');
    }

    /**
     * Get the server that owns the company.
     */
    public function server()
    {
        return $this->belongsTo(Server::class, 'server_id');
    }

    /**
     * Get the proxy setting for the company.
     */
    public function proxy()
    {
        return $this->belongsTo(ProxySetting::class, 'proxy_id');
    }

    /**
     * Get the product URLs for the company.
     */
    public function productUrls()
    {
        return $this->hasMany(CompanyProductsUrl::class);
    }

    /**
     * Get the attributes for the company.
     */
    public function attributes()
    {
        return $this->hasMany(CompanyAttribute::class);
    }

    /**
     * Get the company attributes for the company.
     */
    public function companyAttributes()
    {
        return $this->hasMany(CompanyAttribute::class);
    }

    /**
     * Scope a query to only include non-deleted companies.
     */
    public function scopeActive($query)
    {
        return $query->where('deleted', 0);
    }

    /**
     * Scope a query to only include deleted companies.
     */
    public function scopeDeleted($query)
    {
        return $query->where('deleted', 1);
    }

    /**
     * Soft delete the company.
     */
    public function softDelete()
    {
        $this->update(['deleted' => 1]);
    }

    /**
     * Restore the company.
     */
    public function restore()
    {
        $this->update(['deleted' => 0]);
    }
}