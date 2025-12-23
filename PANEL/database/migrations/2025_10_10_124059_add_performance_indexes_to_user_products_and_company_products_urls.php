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
            // Arama performansı için indeksler
            $table->index('title');
            $table->index('product_type');
            $table->index('availability');
            $table->index('price');
            $table->index('created_at');
            $table->index('brand_id');
            
            // Composite indeksler
            $table->index(['brand_id', 'created_at']);
            $table->index(['availability', 'created_at']);
            $table->index(['price', 'created_at']);
        });

        Schema::table('company_products_urls', function (Blueprint $table) {
            // product_id için indeks (withCount için gerekli)
            $table->index('product_id');
            $table->index('company_id');
            
            // Composite indeks
            $table->index(['product_id', 'company_id']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('user_products', function (Blueprint $table) {
            $table->dropIndex(['title']);
            $table->dropIndex(['product_type']);
            $table->dropIndex(['availability']);
            $table->dropIndex(['price']);
            $table->dropIndex(['created_at']);
            $table->dropIndex(['brand_id']);
            $table->dropIndex(['brand_id', 'created_at']);
            $table->dropIndex(['availability', 'created_at']);
            $table->dropIndex(['price', 'created_at']);
        });

        Schema::table('company_products_urls', function (Blueprint $table) {
            $table->dropIndex(['product_id']);
            $table->dropIndex(['company_id']);
            $table->dropIndex(['product_id', 'company_id']);
        });
    }
};