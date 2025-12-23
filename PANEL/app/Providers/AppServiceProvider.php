<?php

namespace App\Providers;

use Illuminate\Support\ServiceProvider;
use Illuminate\Console\Scheduling\Schedule;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        //
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        // Schedule XML import - Her gün saat 03:00'da çalışır
        $this->app->booted(function () {
            $schedule = $this->app->make(Schedule::class);
            
            // XML Import - Her gün saat 03:00'da
            $schedule->command('xml:import')
                ->dailyAt('03:00')
                ->timezone('Europe/Istanbul')
                ->withoutOverlapping()
                ->runInBackground()
                ->emailOutputOnFailure(env('ADMIN_EMAIL'));
        });
    }
}
