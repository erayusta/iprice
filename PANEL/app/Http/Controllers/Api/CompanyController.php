<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Company;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;

class CompanyController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        $companies = Company::active()->get();
        
        // Transform data to match frontend expectations
        $transformedCompanies = $companies->map(function ($company) {
            return [
                'id' => $company->id,
                'company_name' => $company->name,
                'company_logo' => $company->company_logo ?? null,
                'company_site' => $company->url,
                'crawler_id' => $company->crawler_id ?? 1,
                'server_id' => $company->server_id ?? 1,
                'is_marketplace' => $company->marketplace === 'true' || $company->marketplace === true,
                'screenshot_required' => $company->screenshot === 'true' || $company->screenshot === true,
                'use_proxy' => $company->use_proxy ?? false,
                'proxy_id' => $company->proxy_id,
                'created_at' => $company->created_at,
                'updated_at' => $company->updated_at,
            ];
        });
        
        return response()->json([
            'success' => true,
            'data' => $transformedCompanies
        ]);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        try {
            // Convert string "0" and "1" to boolean for validation
            $requestData = $request->all();
            if (isset($requestData['screenshot_required'])) {
                $requestData['screenshot_required'] = filter_var($requestData['screenshot_required'], FILTER_VALIDATE_BOOLEAN, FILTER_NULL_ON_FAILURE);
            }
            if (isset($requestData['is_marketplace'])) {
                $requestData['is_marketplace'] = filter_var($requestData['is_marketplace'], FILTER_VALIDATE_BOOLEAN, FILTER_NULL_ON_FAILURE);
            }
            if (isset($requestData['use_proxy'])) {
                $requestData['use_proxy'] = filter_var($requestData['use_proxy'], FILTER_VALIDATE_BOOLEAN, FILTER_NULL_ON_FAILURE);
            }
            
            // Remove company_logo from validation if it's not a valid uploaded file
            if (isset($requestData['company_logo']) && !$request->hasFile('company_logo')) {
                unset($requestData['company_logo']);
            }
            
            $validator = Validator::make($requestData, [
                'company_name' => 'required|string|max:255',
                'company_logo' => 'nullable|image|mimes:jpeg,png,jpg,gif|max:10240', // 10MB max
                'company_site' => 'nullable|url|max:255',
                'crawler_id' => 'nullable|exists:crawler_list,id',
                'server_id' => 'nullable|exists:server_list,id',
                'screenshot_required' => 'nullable|boolean',
                'is_marketplace' => 'nullable|boolean',
                'use_proxy' => 'nullable|boolean',
                'proxy_id' => 'nullable|exists:proxy_settings,id',
            ]);

            if ($validator->fails()) {
                return response()->json([
                    'success' => false,
                    'message' => 'Doğrulama hatası',
                    'errors' => $validator->errors()
                ], 422);
            }

            $screenshotValue = $request->screenshot_required;
            $marketplaceValue = $request->is_marketplace;
            $useProxyValue = $request->use_proxy;
            
            $data = [
                'name' => $request->company_name,
                'url' => $request->company_site,
                'crawler_id' => $request->crawler_id ?? 1,
                'server_id' => $request->server_id ?? 1,
                'screenshot' => ($screenshotValue === '1' || $screenshotValue === 1 || $screenshotValue === true) ? 'true' : 'false',
                'marketplace' => ($marketplaceValue === '1' || $marketplaceValue === 1 || $marketplaceValue === true) ? 'true' : 'false',
                'use_proxy' => ($useProxyValue === '1' || $useProxyValue === 1 || $useProxyValue === true) ? true : false,
                'proxy_id' => $request->proxy_id,
            ];

            // Handle file upload
            if ($request->hasFile('company_logo')) {
                $file = $request->file('company_logo');
                $filename = time() . '_' . $file->getClientOriginalName();
                
                try {
                    $path = $file->storeAs('company-logos', $filename, 'public');
                    if (!$path) {
                        throw new \Exception('Dosya yüklenemedi');
                    }
                    $data['company_logo'] = 'storage/company-logos/' . $filename;
                } catch (\Exception $e) {
                    return response()->json([
                        'success' => false,
                        'message' => 'Dosya yükleme hatası: ' . $e->getMessage(),
                        'error' => $e->getMessage()
                    ], 500);
                }
            }

            $company = Company::create($data);

            // $company = $company->load(['crawler', 'server', 'productUrls', 'attributes.attribute']);
            
            // Transform data to match frontend expectations
            $transformedCompany = [
                'id' => $company->id,
                'company_name' => $company->name,
                'company_logo' => $company->company_logo ?? null,
                'company_site' => $company->url,
                'crawler_id' => $company->crawler_id ?? 1,
                'server_id' => $company->server_id ?? 1,
                'is_marketplace' => $company->marketplace === 'true' || $company->marketplace === true,
                'screenshot_required' => $company->screenshot === 'true' || $company->screenshot === true,
                'use_proxy' => $company->use_proxy ?? false,
                'proxy_id' => $company->proxy_id,
                'created_at' => $company->created_at,
                'updated_at' => $company->updated_at,
            ];
            
            return response()->json([
                'success' => true,
                'message' => 'Firma başarıyla oluşturuldu',
                'data' => $transformedCompany
            ], 201);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Firma oluşturulurken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Display the specified resource.
     */
    public function show($id)
    {
        try {
            $company = Company::active()->findOrFail($id);
            
            // Transform data to match frontend expectations
            $transformedCompany = [
                'id' => $company->id,
                'company_name' => $company->name,
                'company_logo' => $company->company_logo ?? null,
                'company_site' => $company->url,
                'crawler_id' => $company->crawler_id,
                'server_id' => $company->server_id,
                'is_marketplace' => $company->marketplace === 'true' || $company->marketplace === true,
                'screenshot_required' => $company->screenshot === 'true' || $company->screenshot === true,
                'use_proxy' => $company->use_proxy ?? false,
                'proxy_id' => $company->proxy_id,
                'created_at' => $company->created_at,
                'updated_at' => $company->updated_at,
            ];
            
            return response()->json([
                'success' => true,
                'data' => $transformedCompany
            ]);
        } catch (\Illuminate\Database\Eloquent\ModelNotFoundException $e) {
            return response()->json([
                'success' => false,
                'message' => 'Firma bulunamadı veya silinmiş.'
            ], 404);
        }
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, $id)
    {
        try {
            $company = Company::active()->findOrFail($id);
            
            // Convert string "0" and "1" to boolean for validation
            $requestData = $request->all();
            if (isset($requestData['screenshot_required'])) {
                $requestData['screenshot_required'] = filter_var($requestData['screenshot_required'], FILTER_VALIDATE_BOOLEAN, FILTER_NULL_ON_FAILURE);
            }
            if (isset($requestData['is_marketplace'])) {
                $requestData['is_marketplace'] = filter_var($requestData['is_marketplace'], FILTER_VALIDATE_BOOLEAN, FILTER_NULL_ON_FAILURE);
            }
            if (isset($requestData['use_proxy'])) {
                $requestData['use_proxy'] = filter_var($requestData['use_proxy'], FILTER_VALIDATE_BOOLEAN, FILTER_NULL_ON_FAILURE);
            }
            
            // Remove company_logo from validation if it's not a valid uploaded file
            if (isset($requestData['company_logo']) && !$request->hasFile('company_logo')) {
                unset($requestData['company_logo']);
            }
            
            $validator = Validator::make($requestData, [
                'company_name' => 'sometimes|required|string|max:255',
                'company_logo' => 'nullable|image|mimes:jpeg,png,jpg,gif|max:10240', // 10MB max
                'company_site' => 'nullable|url|max:255',
                'crawler_id' => 'nullable|exists:crawler_list,id',
                'server_id' => 'nullable|exists:server_list,id',
                'screenshot_required' => 'nullable|boolean',
                'is_marketplace' => 'nullable|boolean',
                'use_proxy' => 'nullable|boolean',
                'proxy_id' => 'nullable|exists:proxy_settings,id',
            ]);

            if ($validator->fails()) {
                return response()->json([
                    'success' => false,
                    'message' => 'Doğrulama hatası',
                    'errors' => $validator->errors()
                ], 422);
            }

            $data = [];
            if ($request->has('company_name')) {
                $data['name'] = $request->company_name;
            }
            if ($request->has('company_site')) {
                $data['url'] = $request->company_site;
            }
            // Set crawler_id and server_id from request
            if ($request->has('crawler_id')) {
                $data['crawler_id'] = $request->crawler_id;
            }
            if ($request->has('server_id')) {
                $data['server_id'] = $request->server_id;
            }
            if ($request->has('screenshot_required')) {
                $screenshotValue = $request->screenshot_required;
                // Handle string "0"/"1" or boolean
                $data['screenshot'] = ($screenshotValue === '1' || $screenshotValue === 1 || $screenshotValue === true) ? 'true' : 'false';
            }
            if ($request->has('is_marketplace')) {
                $marketplaceValue = $request->is_marketplace;
                // Handle string "0"/"1" or boolean
                $data['marketplace'] = ($marketplaceValue === '1' || $marketplaceValue === 1 || $marketplaceValue === true) ? 'true' : 'false';
            }
            if ($request->has('use_proxy')) {
                $useProxyValue = $request->use_proxy;
                // Handle string "0"/"1" or boolean
                $data['use_proxy'] = ($useProxyValue === '1' || $useProxyValue === 1 || $useProxyValue === true) ? true : false;
            }
            if ($request->has('proxy_id')) {
                $data['proxy_id'] = $request->proxy_id;
            }

            // Handle file upload
            if ($request->hasFile('company_logo')) {
                // Delete old logo if exists
                if ($company->company_logo) {
                    // Get the relative path from the URL
                    $oldLogoPath = str_replace(url('/'), '', $company->company_logo);
                    $oldLogoFullPath = public_path($oldLogoPath);
                    
                    if (file_exists($oldLogoFullPath)) {
                        @unlink($oldLogoFullPath);
                    }
                }
                
                $file = $request->file('company_logo');
                $filename = time() . '_' . $file->getClientOriginalName();
                
                try {
                    $path = $file->storeAs('company-logos', $filename, 'public');
                    if (!$path) {
                        throw new \Exception('Dosya yüklenemedi');
                    }
                    $data['company_logo'] = 'storage/company-logos/' . $filename;
                } catch (\Exception $e) {
                    return response()->json([
                        'success' => false,
                        'message' => 'Dosya yükleme hatası: ' . $e->getMessage(),
                        'error' => $e->getMessage()
                    ], 500);
                }
            }

            $company->update($data);

            // Refresh the model to get updated data
            $company->refresh();

            // $company = $company->load(['crawler', 'server', 'productUrls', 'attributes.attribute']);
            
            // Transform data to match frontend expectations
            $transformedCompany = [
                'id' => $company->id,
                'company_name' => $company->name,
                'company_logo' => $company->company_logo ?? null,
                'company_site' => $company->url,
                'crawler_id' => $company->crawler_id,
                'server_id' => $company->server_id,
                'is_marketplace' => $company->marketplace === 'true' || $company->marketplace === true,
                'screenshot_required' => $company->screenshot === 'true' || $company->screenshot === true,
                'use_proxy' => $company->use_proxy ?? false,
                'proxy_id' => $company->proxy_id,
                'created_at' => $company->created_at,
                'updated_at' => $company->updated_at,
            ];
            
            return response()->json([
                'success' => true,
                'message' => 'Firma başarıyla güncellendi',
                'data' => $transformedCompany
            ]);
        } catch (\Illuminate\Database\Eloquent\ModelNotFoundException $e) {
            return response()->json([
                'success' => false,
                'message' => 'Firma bulunamadı veya silinmiş.'
            ], 404);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Firma güncellenirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy($id)
    {
        try {
            $company = Company::active()->findOrFail($id);
            
            // Soft delete the company
            $company->softDelete();

            return response()->json([
                'success' => true,
                'message' => 'Firma başarıyla silindi'
            ]);
        } catch (\Illuminate\Database\Eloquent\ModelNotFoundException $e) {
            return response()->json([
                'success' => false,
                'message' => 'Firma bulunamadı veya zaten silinmiş.'
            ], 404);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Firma silinirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }
}