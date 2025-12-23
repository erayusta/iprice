<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class CustomProfile extends Model
{
    protected $fillable = [
        'name',
        'description',
        'user_id'
    ];

    protected $casts = [
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function products(): HasMany
    {
        return $this->hasMany(CustomProfileProduct::class)->orderBy('sort_order');
    }

    public function shares(): HasMany
    {
        return $this->hasMany(CustomProfileShare::class, 'profiles_id');
    }

    public function sharedWithUsers(): BelongsToMany
    {
        return $this->belongsToMany(User::class, 'custom_profiles_shares', 'profiles_id', 'user_id')
            ->withTimestamps();
    }

    public function getProductsCountAttribute(): int
    {
        return $this->products()->count();
    }
}
