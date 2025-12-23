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
        Schema::table('permissions', function (Blueprint $table) {
            // guard_name sütununu kaldır
            $table->dropColumn('guard_name');
            
            // description ve group sütunlarını ekle
            $table->text('description')->nullable();
            $table->string('group')->nullable();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('permissions', function (Blueprint $table) {
            // description ve group sütunlarını kaldır
            $table->dropColumn(['description', 'group']);
            
            // guard_name sütununu geri ekle
            $table->string('guard_name');
        });
    }
};
