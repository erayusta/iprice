<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class CustomProfileProduct extends Model
{
    protected $fillable = [
        'custom_profile_id',
        'user_product_id',
        'sort_order'
    ];

    protected $casts = [
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    public function customProfile(): BelongsTo
    {
        return $this->belongsTo(CustomProfile::class);
    }

    public function product(): BelongsTo
    {
        return $this->belongsTo(UserProduct::class, 'user_product_id');
    }
}
