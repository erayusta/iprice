<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('custom_profiles_shares', function (Blueprint $table) {
            $table->id();
            $table->foreignId('profiles_id')->constrained('custom_profiles')->onDelete('cascade');
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            $table->timestamps();
            
            // Aynı profili aynı kullanıcıya birden fazla kez paylaşmayı önlemek için unique constraint
            $table->unique(['profiles_id', 'user_id']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('custom_profiles_shares');
    }
};
