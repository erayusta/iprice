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
        Schema::table('user_products', function (Blueprint $table) {
            // Önce mevcut brand_id kolonunu sil
            $table->dropColumn('brand_id');
        });
        
        Schema::table('user_products', function (Blueprint $table) {
            // Yeni brand_id kolonunu bigint olarak ekle ve foreign key constraint ekle
            $table->unsignedBigInteger('brand_id')->nullable()->after('product_url');
            $table->foreign('brand_id')->references('id')->on('brands')->onDelete('set null');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('user_products', function (Blueprint $table) {
            // Foreign key constraint'i kaldır
            $table->dropForeign(['brand_id']);
            // brand_id kolonunu sil
            $table->dropColumn('brand_id');
        });
        
        Schema::table('user_products', function (Blueprint $table) {
            // Eski string tipinde brand_id kolonunu geri ekle
            $table->string('brand_id')->nullable()->after('product_url');
        });
    }
};
