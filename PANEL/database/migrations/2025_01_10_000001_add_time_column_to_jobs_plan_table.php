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
        Schema::table('jobs_plan', function (Blueprint $table) {
            $table->time('time')->nullable()->after('name');
            $table->string('company')->default('all')->after('time');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('jobs_plan', function (Blueprint $table) {
            $table->dropColumn(['time', 'company']);
        });
    }
};
