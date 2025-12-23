<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class CustomProfileShare extends Model
{
    use HasFactory;

    protected $table = 'custom_profiles_shares';

    protected $fillable = [
        'profiles_id',
        'user_id'
    ];

    protected $casts = [
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    public function profile(): BelongsTo
    {
        return $this->belongsTo(CustomProfile::class, 'profiles_id');
    }

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }
}