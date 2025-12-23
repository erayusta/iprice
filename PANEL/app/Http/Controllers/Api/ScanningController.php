<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Services\ScanningService;
use App\Models\ScraperData;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

class ScanningController extends Controller
{
    protected $scanningService;

    public function __construct(ScanningService $scanningService)
    {
        $this->scanningService = $scanningService;
    }

    /**
     * Get all scheduled scans
     */
    public function getScheduledScans(): JsonResponse
    {
        $result = $this->scanningService->getScheduledScans();
        
        if ($result['success']) {
            return response()->json([
                'success' => true,
                'data' => $result['job_plans']
            ]);
        }

        return response()->json([
            'success' => false,
            'message' => $result['message']
        ], 400);
    }

    /**
     * Create a new scheduled scan
     */
    public function createScheduledScan(Request $request): JsonResponse
    {
        $request->validate([
            'time' => 'required|string|regex:/^([01]?[0-9]|2[0-3]):[0-5][0-9]$/',
            'company' => 'required|string'
        ]);

        $result = $this->scanningService->createScheduledScan(
            $request->time,
            $request->company
        );

        if ($result['success']) {
            return response()->json([
                'success' => true,
                'message' => $result['message'],
                'data' => $result['job_plan']
            ], 201);
        }

        return response()->json([
            'success' => false,
            'message' => $result['message']
        ], 400);
    }

    /**
     * Start a quick scan
     */
    public function startQuickScan(Request $request): JsonResponse
    {
        $request->validate([
            'company_id' => 'nullable|string'
        ]);

        $result = $this->scanningService->startQuickScan($request->company_id);

        if ($result['success']) {
            return response()->json([
                'success' => true,
                'message' => $result['message'],
                'data' => [
                    'scan_type' => $result['scan_type'],
                    'company_id' => $result['company_id'],
                    'started_at' => $result['started_at'],
                    'queue_stats' => $result['queue_stats'] ?? [],
                    'total_urls' => $result['total_urls'] ?? 0,
                    'companies_count' => $result['companies_count'] ?? 0
                ]
            ]);
        }

        return response()->json([
            'success' => false,
            'message' => $result['message']
        ], 400);
    }

    /**
     * Start a demo scan with custom URLs
     */
    public function startDemoScan(Request $request): JsonResponse
    {
        $request->validate([
            'urls' => 'required|array|min:1',
            'urls.*' => 'required|url',
            'company_id' => 'nullable|integer'
        ]);

        $result = $this->scanningService->startDemoScan(
            $request->urls,
            $request->company_id
        );

        if ($result['success']) {
            return response()->json([
                'success' => true,
                'message' => $result['message'],
                'data' => [
                    'scan_type' => $result['scan_type'],
                    'company_id' => $result['company_id'],
                    'started_at' => $result['started_at'],
                    'queue_stats' => $result['queue_stats'] ?? [],
                    'total_urls' => $result['total_urls'] ?? 0,
                    'companies_count' => $result['companies_count'] ?? 0,
                    'job_id' => $result['job_id'] ?? null
                ]
            ]);
        }

        return response()->json([
            'success' => false,
            'message' => $result['message']
        ], 400);
    }

    /**
     * Start a profile scan
     */
    public function startProfileScan(Request $request): JsonResponse
    {
        $request->validate([
            'profile_id' => 'required|integer|exists:custom_profiles,id'
        ]);

        $result = $this->scanningService->startProfileScan($request->profile_id);

        if ($result['success']) {
            return response()->json([
                'success' => true,
                'message' => $result['message'],
                'data' => [
                    'scan_type' => $result['scan_type'],
                    'profile_id' => $result['profile_id'],
                    'started_at' => $result['started_at'],
                    'queue_stats' => $result['queue_stats'] ?? [],
                    'total_urls' => $result['total_urls'] ?? 0,
                    'companies_count' => $result['companies_count'] ?? 0,
                    'job_id' => $result['job_id'] ?? null
                ]
            ]);
        }

        return response()->json([
            'success' => false,
            'message' => $result['message']
        ], 400);
    }

    /**
     * Delete a scheduled scan
     */
    public function deleteScheduledScan($id): JsonResponse
    {
        $result = $this->scanningService->deleteScheduledScan($id);

        if ($result['success']) {
            return response()->json([
                'success' => true,
                'message' => $result['message']
            ]);
        }

        return response()->json([
            'success' => false,
            'message' => $result['message']
        ], 400);
    }

    /**
     * Get all companies for selection
     */
    public function getCompanies(): JsonResponse
    {
        $result = $this->scanningService->getCompanies();

        if ($result['success']) {
            return response()->json([
                'success' => true,
                'data' => $result['companies']
            ]);
        }

        return response()->json([
            'success' => false,
            'message' => $result['message']
        ], 400);
    }

    /**
     * Get scan operations history with pagination
     */
    public function getScanOperations(Request $request): JsonResponse
    {
        $page = $request->get('page', 1);
        $perPage = $request->get('per_page', 10);
        
        $result = $this->scanningService->getScanOperations($page, $perPage);

        if ($result['success']) {
            return response()->json([
                'success' => true,
                'data' => $result['operations'],
                'pagination' => $result['pagination']
            ]);
        }

        return response()->json([
            'success' => false,
            'message' => $result['message']
        ], 400);
    }

    /**
     * Get job details
     */
    public function getJobDetails($id): JsonResponse
    {
        $result = $this->scanningService->getJobDetails($id);

        if ($result['success']) {
            return response()->json([
                'success' => true,
                'data' => $result
            ]);
        }

        return response()->json([
            'success' => false,
            'message' => $result['message']
        ], 400);
    }

    /**
     * Get job JSON content by job id (fallback viewer)
     */
    public function getJobJson($id): JsonResponse
    {
        $result = $this->scanningService->getJobJson($id);

        if ($result['success']) {
            return response()->json([
                'success' => true,
                'data' => $result
            ]);
        }

        return response()->json([
            'success' => false,
            'message' => $result['message']
        ], 400);
    }

    /**
     * Purge all RabbitMQ queues (stop all scans)
     * Tüm RabbitMQ queue'lerini temizler ve taramaları durdurur
     */
    public function purgeQueues(Request $request): JsonResponse
    {
        $environment = $request->get('environment'); // 'local', 'azure', veya null (tüm server'lar)
        
        $result = $this->scanningService->purgeQueues($environment);

        if ($result['success']) {
            return response()->json([
                'success' => true,
                'message' => $result['message'],
                'data' => $result['stats']
            ]);
        }

        return response()->json([
            'success' => false,
            'message' => $result['message']
        ], 400);
    }

    /**
     * Get job queue status by job ID
     * Job ID'ye göre RabbitMQ queue'lardaki mesaj durumlarını döner
     */
    public function getJobQueueStatus($id): JsonResponse
    {
        $result = $this->scanningService->getJobQueueStatus($id);

        if ($result['success']) {
            return response()->json([
                'success' => true,
                'data' => $result
            ]);
        }

        return response()->json([
            'success' => false,
            'message' => $result['message']
        ], 400);
    }

    /**
     * Start a quick scan for Chrome Extension
     */
    public function startQuickScanChromeExtension(Request $request): JsonResponse
    {
        $request->validate([
            'company_id' => 'nullable|string',
            'token' => 'required|string'
        ]);

        // Token validation
        $user = \App\Models\User::where('iprice_token', $request->token)->first();
        if (!$user) {
            return response()->json([
                'success' => false,
                'message' => 'Geçersiz token'
            ], 401);
        }

        $companyId = $request->company_id ?: 'all';
        $result = $this->scanningService->create_job_chrome_extension($companyId);

        if ($result['success']) {
            return response()->json([
                'success' => true,
                'message' => 'Chrome extension hızlı tarama başarıyla başlatıldı',
                'data' => [
                    'scan_type' => $companyId === 'all' ? 'Genel' : 'Firma Özel',
                    'company_id' => $companyId,
                    'started_at' => now()->toISOString(),
                    'queue_stats' => $result['queue_stats'] ?? [],
                    'total_urls' => $result['total_urls'] ?? 0,
                    'companies_count' => $result['companies_count'] ?? 0,
                    'job_id' => $result['job_id'] ?? null
                ]
            ]);
        }

        return response()->json([
            'success' => false,
            'message' => $result['message']
        ], 400);
    }

    /**
     * Start a profile scan for Chrome Extension
     */
    public function startProfileScanChromeExtension(Request $request): JsonResponse
    {
        $request->validate([
            'profile_id' => 'required|integer|exists:custom_profiles,id',
            'token' => 'required|string'
        ]);

        // Token validation
        $user = \App\Models\User::where('iprice_token', $request->token)->first();
        if (!$user) {
            return response()->json([
                'success' => false,
                'message' => 'Geçersiz token'
            ], 401);
        }

        $result = $this->scanningService->create_profile_job_chrome_extension($request->profile_id);

        if ($result['success']) {
            return response()->json([
                'success' => true,
                'message' => $result['message'],
                'data' => [
                    'scan_type' => 'Profil Tarama (Chrome Extension)',
                    'profile_id' => $request->profile_id,
                    'started_at' => now()->toISOString(),
                    'queue_stats' => $result['queue_stats'] ?? [],
                    'total_urls' => $result['total_urls'] ?? 0,
                    'companies_count' => $result['companies_count'] ?? 0,
                    'job_id' => $result['job_id'] ?? null
                ]
            ]);
        }

        return response()->json([
            'success' => false,
            'message' => $result['message']
        ], 400);
    }

    /**
     * Get next pending job for Chrome Extension
     * Chrome Extension için pending durumundaki ilk job'ı getirir
     */
    public function getNextPendingJob(Request $request): JsonResponse
    {
        try {
            // Token validation (optional, can be removed if not needed)
            if ($request->has('token')) {
                $user = \App\Models\User::where('iprice_token', $request->token)->first();
                if (!$user) {
                    return response()->json([
                        'success' => false,
                        'message' => 'Geçersiz token'
                    ], 401);
                }
            }

            // Get first pending job
            $job = \Illuminate\Support\Facades\DB::table('jobs_data')
                ->where('status', 'pending')
                ->whereNotNull('json_path')
                ->where('json_path', '!=', '')
                ->orderBy('id', 'asc')
                ->first();

            if (!$job) {
                return response()->json([
                    'success' => false,
                    'message' => 'Pending durumunda job bulunamadı'
                ], 404);
            }

            // Read JSON file from storage
            $jsonPath = $job->json_path;
            if (!\Illuminate\Support\Facades\Storage::disk('public')->exists($jsonPath)) {
                return response()->json([
                    'success' => false,
                    'message' => 'JSON dosyası bulunamadı: ' . $jsonPath
                ], 404);
            }

            $jsonContent = \Illuminate\Support\Facades\Storage::disk('public')->get($jsonPath);
            $jobData = json_decode($jsonContent, true);

            if (json_last_error() !== JSON_ERROR_NONE) {
                return response()->json([
                    'success' => false,
                    'message' => 'JSON parse hatası: ' . json_last_error_msg()
                ], 500);
            }

            // Chrome Extension için sadece application_id = 4 (chrome.queue) olanları filtrele
            // Eğer jobData bir array ise ve içinde application_id field'ı varsa filtrele
            $filteredData = [];
            if (is_array($jobData)) {
                foreach ($jobData as $item) {
                    // application_id = 4 (chrome.queue) olanları al
                    // Eğer application_id yoksa, varsayılan olarak chrome extension için kabul et
                    if (isset($item['application_id'])) {
                        if ($item['application_id'] == 4) {
                            $filteredData[] = $item;
                        }
                    } else {
                        // application_id yoksa, eski format için kontrol et
                        // Eğer server_id = 3 (chrome) ise veya hiç yoksa kabul et
                        if (!isset($item['server_id']) || $item['server_id'] == 3) {
                            $filteredData[] = $item;
                        }
                    }
                }
            } else {
                // Eğer jobData array değilse, olduğu gibi kullan
                $filteredData = $jobData;
            }

            // Eğer filtrelenmiş veri boşsa, tüm veriyi döndür (geriye dönük uyumluluk)
            if (empty($filteredData) && !empty($jobData)) {
                $filteredData = $jobData;
            }

            // Update status to 'worker'
            \Illuminate\Support\Facades\DB::table('jobs_data')
                ->where('id', $job->id)
                ->update([
                    'status' => 'worker',
                    'updated_at' => now()
                ]);

            // Count değerini filtrelenmiş verinin uzunluğuna göre güncelle
            $filteredCount = is_array($filteredData) ? count($filteredData) : (is_array($jobData) ? count($jobData) : $job->count);

            return response()->json([
                'success' => true,
                'data' => $filteredData,
                'job_id' => $job->id,
                'job_name' => $job->job_name,
                'count' => $filteredCount
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Finish job - Update job status to 'finish'
     * Chrome Extension taraması tamamlandığında job'ın status'unu 'finish' olarak günceller
     */
    public function finishJob(Request $request): JsonResponse
    {
        try {
            // Token validation (optional, can be removed if not needed)
            if ($request->has('token')) {
                $user = \App\Models\User::where('iprice_token', $request->token)->first();
                if (!$user) {
                    return response()->json([
                        'success' => false,
                        'message' => 'Geçersiz token'
                    ], 401);
                }
            }

            // Validate job_id
            $validator = \Illuminate\Support\Facades\Validator::make($request->all(), [
                'job_id' => 'required|integer|exists:jobs_data,id'
            ]);

            if ($validator->fails()) {
                return response()->json([
                    'success' => false,
                    'message' => 'Doğrulama hatası',
                    'errors' => $validator->errors()
                ], 422);
            }

            $jobId = $request->input('job_id');

            // Check if job exists and is in 'worker' status
            $job = \Illuminate\Support\Facades\DB::table('jobs_data')
                ->where('id', $jobId)
                ->first();

            if (!$job) {
                return response()->json([
                    'success' => false,
                    'message' => 'Job bulunamadı'
                ], 404);
            }

            // Update status to 'finish'
            \Illuminate\Support\Facades\DB::table('jobs_data')
                ->where('id', $jobId)
                ->update([
                    'status' => 'finish',
                    'updated_at' => now()
                ]);

            return response()->json([
                'success' => true,
                'message' => 'Job başarıyla tamamlandı olarak işaretlendi',
                'data' => [
                    'job_id' => $jobId,
                    'status' => 'finish'
                ]
            ]);

        } catch (\Exception $e) {
            \Log::error('Finish job error: ' . $e->getMessage(), [
                'job_id' => $request->input('job_id'),
                'trace' => $e->getTraceAsString()
            ]);
            
            return response()->json([
                'success' => false,
                'message' => 'Hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get scraper data by job_id
     */
    public function getScraperDataByJobId($jobId): JsonResponse
    {
        try {
            $scraperData = ScraperData::where('job_id', $jobId)
                ->orderBy('created_at', 'desc')
                ->get();

            return response()->json([
                'success' => true,
                'data' => $scraperData->map(function ($item) {
                    return [
                        'id' => $item->id,
                        'process_id' => $item->process_id,
                        'job_id' => $item->job_id,
                        'data' => is_string($item->data) ? json_decode($item->data, true) : $item->data,
                        'created_at' => $item->created_at
                    ];
                })
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Retry scan with prepared data
     */
    public function retryScan(Request $request): JsonResponse
    {
        $request->validate([
            'data' => 'required|array',
            'data.url' => 'required|string',
            'data.company_id' => 'required|integer',
            'data.product_id' => 'required|integer',
            'data.attributes' => 'required|array'
        ]);

        try {
            $result = $this->scanningService->retryScanWithData($request->data);

            if ($result['success']) {
                return response()->json([
                    'success' => true,
                    'message' => $result['message'],
                    'job_id' => $result['job_id'],
                    'data_id' => $result['data_id'] ?? null
                ]);
            }

            return response()->json([
                'success' => false,
                'message' => $result['message']
            ], 400);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Retry bulk scan with prepared data array
     */
    public function retryBulkScan(Request $request): JsonResponse
    {
        $request->validate([
            'data' => 'required|array|min:1',
            'data.*.url' => 'required|string',
            'data.*.company_id' => 'required|integer',
            'data.*.product_id' => 'required|integer',
            'data.*.attributes' => 'required|array'
        ]);

        try {
            $result = $this->scanningService->retryBulkScanWithData($request->data);

            if ($result['success']) {
                return response()->json([
                    'success' => true,
                    'message' => $result['message'],
                    'job_id' => $result['job_id'],
                    'total_items' => $result['total_items']
                ]);
            }

            return response()->json([
                'success' => false,
                'message' => $result['message']
            ], 400);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Quick scan for a single product
     * Belirli bir ürün için hızlı tarama başlatır
     */
    public function quickScanProduct(Request $request): JsonResponse
    {
        $request->validate([
            'product_id' => 'required|integer'
        ]);

        try {
            $result = $this->scanningService->quickScanProduct($request->product_id);

            if ($result['success']) {
                return response()->json([
                    'success' => true,
                    'message' => $result['message'],
                    'job_id' => $result['job_id'],
                    'total_items' => $result['total_items']
                ]);
            }

            return response()->json([
                'success' => false,
                'message' => $result['message']
            ], 400);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }
}
