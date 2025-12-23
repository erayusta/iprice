<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\AuthController;
use App\Http\Controllers\Api\CompanyController;
use App\Http\Controllers\Api\CrawlerController;
use App\Http\Controllers\Api\AttributeController;
use App\Http\Controllers\Api\CompanyAttributeController;
use App\Http\Controllers\Api\ProductController;
use App\Http\Controllers\Api\UserProductController;
use App\Http\Controllers\Api\BrandController;
use App\Http\Controllers\Api\ScanningController;
use App\Http\Controllers\Api\ServerController;
use App\Http\Controllers\Api\ProxyController;
use App\Http\Controllers\Api\CustomProfileController;
use App\Http\Controllers\Api\RoleController;
use App\Http\Controllers\Api\PermissionController;
use App\Http\Controllers\Api\UserController;
use App\Http\Controllers\Api\ChromeExtensionController;
use App\Http\Controllers\Api\PriceAnalysisController;
use App\Http\Controllers\Api\ProxySettingsController;
use App\Http\Controllers\Api\CronJobController;
use App\Http\Controllers\CompanyAttributeCheckController;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application. These
| routes are loaded by the RouteServiceProvider and all of them will
| be assigned to the "api" middleware group. Make something great!
|
*/

Route::middleware('auth:sanctum')->get('/user', function (Request $request) {
    return $request->user();
});

// Auth routes
Route::prefix('auth')->group(function () {
    Route::post('/register', [AuthController::class, 'register']);
    Route::post('/login', [AuthController::class, 'login']);
    
    Route::middleware('auth:sanctum')->group(function () {
        Route::post('/logout', [AuthController::class, 'logout']);
        Route::get('/me', [AuthController::class, 'me']);
    });
});

// Protected API routes
Route::middleware('auth:sanctum')->group(function () {
    // Companies
    Route::apiResource('companies', CompanyController::class);
    
    // Servers
    Route::get('servers', [ServerController::class, 'index']);
    Route::get('servers/{id}', [ServerController::class, 'show']);
    
    // Crawlers
    Route::apiResource('crawlers', CrawlerController::class);
    
    // Attributes
    Route::delete('attributes/delete-all', [AttributeController::class, 'deleteAll']);
    Route::apiResource('attributes', AttributeController::class);
    
    // Company Attributes
    Route::apiResource('company-attributes', CompanyAttributeController::class);
    
    // Products
    Route::delete('products/delete-all', [ProductController::class, 'deleteAll']);
    Route::get('products/export-urls', [ProductController::class, 'exportUrls']);
    Route::apiResource('products', ProductController::class);
    Route::post('products/batch', [ProductController::class, 'batchStore']);
    Route::post('products/marketplace-urls', [ProductController::class, 'storeMarketplaceUrls']);
    
    // User Products
    Route::delete('user-products/delete-all', [UserProductController::class, 'deleteAll']);
    Route::post('user-products/import-xml', [UserProductController::class, 'importFromXml']);
    Route::post('user-products/xml-info', [UserProductController::class, 'getXmlInfo']);
    Route::apiResource('user-products', UserProductController::class);
    
    // Brands
    Route::delete('brands/delete-all', [BrandController::class, 'deleteAll']);
    Route::apiResource('brands', BrandController::class);
    
    // Scanning
    Route::prefix('scanning')->group(function () {
        Route::get('/scheduled-scans', [ScanningController::class, 'getScheduledScans']);
        Route::post('/scheduled-scans', [ScanningController::class, 'createScheduledScan']);
        Route::delete('/scheduled-scans/{id}', [ScanningController::class, 'deleteScheduledScan']);
        Route::post('/quick-scan', [ScanningController::class, 'startQuickScan']);
        Route::post('/demo-scan', [ScanningController::class, 'startDemoScan']);
        Route::post('/profile-scan', [ScanningController::class, 'startProfileScan']);
        Route::get('/companies', [ScanningController::class, 'getCompanies']);
        Route::get('/operations', [ScanningController::class, 'getScanOperations']);
        Route::get('/job-details/{id}', [ScanningController::class, 'getJobDetails']);
        Route::get('/job-json/{id}', [ScanningController::class, 'getJobJson']);
        Route::get('/job-status/{id}', [ScanningController::class, 'getJobQueueStatus']);
        Route::get('/scraper-data/{jobId}', [ScanningController::class, 'getScraperDataByJobId']);
        Route::post('/retry-scan', [ScanningController::class, 'retryScan']);
        Route::post('/retry-bulk-scan', [ScanningController::class, 'retryBulkScan']);
        Route::post('/quick-scan-product', [ScanningController::class, 'quickScanProduct']);
        Route::post('/purge-queues', [ScanningController::class, 'purgeQueues']);
    });
    
    // Custom Profiles
    Route::apiResource('custom-profiles', CustomProfileController::class);
    Route::get('custom-profiles/{id}/products', [CustomProfileController::class, 'getProducts']);
    Route::post('custom-profiles/{id}/products', [CustomProfileController::class, 'addProduct']);
    Route::post('custom-profiles/{id}/products/batch', [CustomProfileController::class, 'addMultipleProducts']);
    Route::delete('custom-profiles/{profileId}/products/{productId}', [CustomProfileController::class, 'removeProduct']);
    Route::post('custom-profiles/{id}/products/reorder', [CustomProfileController::class, 'reorderProducts']);
    
    // Custom Profile Sharing
    Route::post('custom-profiles/{id}/share', [CustomProfileController::class, 'shareProfile']);
    Route::post('custom-profiles/{id}/unshare', [CustomProfileController::class, 'unshareProfile']);
    Route::get('custom-profiles/{id}/shared-users', [CustomProfileController::class, 'getSharedUsers']);
    Route::get('custom-profiles/{id}/available-users', [CustomProfileController::class, 'getAvailableUsers']);

    // Roles and Permissions
    Route::apiResource('roles', RoleController::class);
    Route::get('roles/{id}/users', [RoleController::class, 'getUsers']);
    Route::apiResource('permissions', PermissionController::class);

    // Users
    Route::apiResource('users', UserController::class);
    Route::get('users/roles/list', [UserController::class, 'getRoles']);
    
    // User profile and token management
    Route::prefix('user')->group(function () {
        Route::get('/profile', [UserController::class, 'profile']);
        Route::post('/generate-token', [UserController::class, 'generateToken']);
        Route::post('/test-token', [UserController::class, 'testToken']);
    });
    
    // Company Attribute Check
    Route::prefix('company-attribute')->group(function () {
        Route::get('/matrix', [CompanyAttributeCheckController::class, 'getMatrix']);
        Route::get('/details', [CompanyAttributeCheckController::class, 'getCompanyAttributeDetails']);
        Route::post('/update', [CompanyAttributeCheckController::class, 'updateCompanyAttribute']);
        Route::delete('/delete', [CompanyAttributeCheckController::class, 'deleteCompanyAttribute']);
        Route::delete('/delete-all-defined', [CompanyAttributeCheckController::class, 'deleteAllDefinedAttributes']);
        Route::get('/export', [CompanyAttributeCheckController::class, 'exportMatrix']);
    });
    
    // Price Analysis
    Route::prefix('price-analysis')->group(function () {
        Route::get('/company-list', [PriceAnalysisController::class, 'companyList']);
        Route::get('/price-summary', [PriceAnalysisController::class, 'priceSummary']);
        Route::get('/company-url-list', [PriceAnalysisController::class, 'companyUrlList']);
        Route::get('/price-history', [PriceAnalysisController::class, 'priceHistory']);
        Route::get('/product-prices', [PriceAnalysisController::class, 'productPrices']);
    });
    
    // Proxy Settings
    Route::delete('proxy-settings/delete-all', [ProxySettingsController::class, 'deleteAll']);
    Route::put('proxy-settings/{id}/toggle-status', [ProxySettingsController::class, 'toggleStatus']);
    Route::apiResource('proxy-settings', ProxySettingsController::class);
    
    // Cron Jobs
    Route::apiResource('cron-jobs', CronJobController::class);
    Route::put('cron-jobs/{id}/toggle', [CronJobController::class, 'toggle']);
    Route::post('cron-jobs/run-scheduled', [CronJobController::class, 'runScheduledJobs']);
});


// Public Proxy API routes (token protected)
Route::middleware('proxy.token')->group(function () {
    Route::get('proxies', [ProxyController::class, 'getProxies']);
    Route::post('proxy-fail', [ProxyController::class, 'markProxyAsFailed']);
});

// Chrome Extension API routes (token protected)
Route::prefix('chrome-extension')->group(function () {
    Route::post('/validate-token', [ChromeExtensionController::class, 'validateToken']);
    Route::post('/add-attribute', [ChromeExtensionController::class, 'addAttribute']);
    Route::post('/get-attributes', [ChromeExtensionController::class, 'getAttributes']);
    Route::post('/get-companies', [ChromeExtensionController::class, 'getUserCompanies']);
    Route::post('/test-connection', [ChromeExtensionController::class, 'testConnection']);
    
    // Labels (Attributes) sync endpoints
    Route::post('/sync-labels', [ChromeExtensionController::class, 'syncLabels']);
    Route::post('/get-labels', [ChromeExtensionController::class, 'getLabels']);
    
    // Selectors (Company Attributes) sync endpoints
    Route::post('/sync-selectors', [ChromeExtensionController::class, 'syncSelectors']);
    Route::post('/get-selectors', [ChromeExtensionController::class, 'getSelectors']);
    
    // Scanning endpoints for Chrome Extension
    Route::post('/quick-scan', [ScanningController::class, 'startQuickScanChromeExtension']);
    Route::post('/profile-scan', [ScanningController::class, 'startProfileScanChromeExtension']);
    Route::get('/next-pending-job', [ScanningController::class, 'getNextPendingJob']);
    Route::post('/finish-job', [ScanningController::class, 'finishJob']);
    
    // RabbitMQ queue endpoints (VPN compatible - via backend)
    Route::post('/send-to-queue', [ChromeExtensionController::class, 'sendToQueue']);
});

// Attribute management API routes (temporarily public for testing)
Route::apiResource('attributes', AttributeController::class);