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
        Schema::create('scan_cronjobs', function (Blueprint $table) {
            $table->id();
            $table->time('time'); // HH:MM formatında saat
            $table->enum('scan_type', ['all', 'company']); // Tarama türü
            $table->unsignedBigInteger('company_id')->nullable(); // Eğer company seçilmişse
            $table->boolean('active')->default(true); // Aktif/pasif durumu
            $table->timestamps();
            
            $table->foreign('company_id')->references('id')->on('companies')->onDelete('cascade');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('scan_cronjobs');
    }
};
