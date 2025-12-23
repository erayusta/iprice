<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class JobPlan extends Model
{
    use HasFactory;

    protected $table = 'jobs_plan';

    protected $fillable = [
        'company',
        'time',
        'active',
    ];

    protected $casts = [
        'time' => 'datetime:H:i',
        'active' => 'boolean',
    ];

    /**
     * Get the company relationship if company is not 'all'
     */
    public function companyRelation()
    {
        if ($this->company !== 'all') {
            return $this->belongsTo(Company::class, 'company', 'id');
        }
        return null;
    }

    /**
     * Check if this is a general scan (not company specific)
     */
    public function isGeneral()
    {
        return $this->company === 'all';
    }

    /**
     * Get company name for display
     */
    public function getCompanyNameAttribute()
    {
        if ($this->isGeneral()) {
            return 'Genel';
        }
        
        $company = $this->companyRelation;
        return $company ? $company->company_name : 'Bilinmeyen Firma';
    }

    /**
     * Scope for active jobs
     */
    public function scopeActive($query)
    {
        return $query->where('active', true);
    }

    /**
     * Scope for general jobs
     */
    public function scopeGeneral($query)
    {
        return $query->where('company', 'all');
    }

    /**
     * Scope for company specific jobs
     */
    public function scopeCompanySpecific($query)
    {
        return $query->where('company', '!=', 'all');
    }
}
