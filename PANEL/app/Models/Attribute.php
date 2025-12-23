<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Attribute extends Model
{
    use HasFactory;

    protected $fillable = [
        'name',
        'description',
    ];

    /**
     * Get the company attributes for this attribute.
     */
    public function companyAttributes()
    {
        return $this->hasMany(CompanyAttribute::class);
    }
}