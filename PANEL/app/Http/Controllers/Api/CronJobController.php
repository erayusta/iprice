<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\ScanCronjob;
use App\Models\Company;
use App\Services\ScanningService;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Validator;

class CronJobController extends Controller
{
    protected $scanningService;

    public function __construct(ScanningService $scanningService)
    {
        $this->scanningService = $scanningService;
    }

    /**
     * Tüm cron job'ları listele
     */
    public function index(): JsonResponse
    {
        try {
            $cronJobs = ScanCronjob::with('company')
                ->orderBy('time')
                ->get();

            return response()->json([
                'success' => true,
                'data' => $cronJobs
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Cron job\'lar yüklenirken hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Yeni cron job oluştur
     */
    public function store(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'time' => 'required|date_format:H:i',
            'scan_type' => 'required|in:all,company',
            'company_id' => 'nullable|exists:companies,id',
            'active' => 'boolean'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'message' => 'Geçersiz veri',
                'errors' => $validator->errors()
            ], 422);
        }

        try {
            $data = $request->only(['time', 'scan_type', 'company_id', 'active']);
            
            // Eğer scan_type 'all' ise company_id'yi null yap
            if ($data['scan_type'] === 'all') {
                $data['company_id'] = null;
            }

            $cronJob = ScanCronjob::create($data);

            return response()->json([
                'success' => true,
                'message' => 'Cron job başarıyla oluşturuldu',
                'data' => $cronJob->load('company')
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Cron job oluşturulurken hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Cron job güncelle
     */
    public function update(Request $request, $id): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'time' => 'required|date_format:H:i',
            'scan_type' => 'required|in:all,company',
            'company_id' => 'nullable|exists:companies,id',
            'active' => 'boolean'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'message' => 'Geçersiz veri',
                'errors' => $validator->errors()
            ], 422);
        }

        try {
            $cronJob = ScanCronjob::findOrFail($id);
            
            $data = $request->only(['time', 'scan_type', 'company_id', 'active']);
            
            // Eğer scan_type 'all' ise company_id'yi null yap
            if ($data['scan_type'] === 'all') {
                $data['company_id'] = null;
            }

            $cronJob->update($data);

            return response()->json([
                'success' => true,
                'message' => 'Cron job başarıyla güncellendi',
                'data' => $cronJob->load('company')
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Cron job güncellenirken hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Cron job sil
     */
    public function destroy($id): JsonResponse
    {
        try {
            $cronJob = ScanCronjob::findOrFail($id);
            $cronJob->delete();

            return response()->json([
                'success' => true,
                'message' => 'Cron job başarıyla silindi'
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Cron job silinirken hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Cron job aktif/pasif durumunu değiştir
     */
    public function toggle($id): JsonResponse
    {
        try {
            $cronJob = ScanCronjob::findOrFail($id);
            $cronJob->update(['active' => !$cronJob->active]);

            return response()->json([
                'success' => true,
                'message' => 'Cron job durumu güncellendi',
                'data' => $cronJob->load('company')
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Cron job durumu güncellenirken hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Şu anki saatte çalışacak cron job'ları çalıştır
     */
    public function runScheduledJobs(): JsonResponse
    {
        try {
            $currentTime = now()->format('H:i');
            $cronJobs = ScanCronjob::active()
                ->atTime($currentTime)
                ->with('company')
                ->get();

            $results = [];

            foreach ($cronJobs as $cronJob) {
                try {
                    if ($cronJob->scan_type === 'all') {
                        // Chrome Extension için job oluştur
                        $result = $this->scanningService->create_job_chrome_extension('all');
                    } else {
                        // Chrome Extension için job oluştur
                        $result = $this->scanningService->create_job_chrome_extension($cronJob->company_id);
                    }

                    $results[] = [
                        'cron_job_id' => $cronJob->id,
                        'scan_type' => $cronJob->scan_type,
                        'company_id' => $cronJob->company_id,
                        'result' => $result
                    ];
                } catch (\Exception $e) {
                    $results[] = [
                        'cron_job_id' => $cronJob->id,
                        'scan_type' => $cronJob->scan_type,
                        'company_id' => $cronJob->company_id,
                        'error' => $e->getMessage()
                    ];
                }
            }

            return response()->json([
                'success' => true,
                'message' => count($cronJobs) . ' cron job çalıştırıldı',
                'data' => $results
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Cron job\'lar çalıştırılırken hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }
}
