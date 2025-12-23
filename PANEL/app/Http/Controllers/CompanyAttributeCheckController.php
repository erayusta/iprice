<?php

namespace App\Http\Controllers;

use App\Models\Company;
use App\Models\Attribute;
use App\Models\CompanyAttribute;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

class CompanyAttributeCheckController extends Controller
{
    /**
     * Get company attribute matrix data
     */
    public function getMatrix(): JsonResponse
    {
        try {
            // Tüm firmaları al
            $companies = Company::with(['crawler', 'server'])->get();
            
            // Tüm attribute'ları al
            $attributes = Attribute::all();
            
            // Company attribute'ları al
            $companyAttributes = CompanyAttribute::all();
            
            // Matrix oluştur
            $matrix = [];
            
            foreach ($companies as $company) {
                $matrix[$company->id] = [];
                
                foreach ($attributes as $attribute) {
                    $companyAttribute = $companyAttributes->where('company_id', $company->id)
                                                          ->where('attribute_id', $attribute->id)
                                                          ->first();
                    
                    if ($companyAttribute) {
                        $matrix[$company->id][$attribute->id] = [
                            'status' => $this->determineStatus($companyAttribute->value),
                            'value' => $companyAttribute->value,
                            'type' => $companyAttribute->type,
                            'enabled' => true
                        ];
                    } else {
                        $matrix[$company->id][$attribute->id] = [
                            'status' => 'undefined',
                            'value' => null,
                            'type' => null,
                            'enabled' => false
                        ];
                    }
                }
            }
            
            return response()->json([
                'success' => true,
                'data' => $matrix,
                'summary' => $this->calculateSummary($matrix, $companies, $attributes)
            ]);
            
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Matrix verisi alınırken hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }
    
    /**
     * Get detailed company attribute data
     */
    public function getCompanyAttributeDetails(Request $request): JsonResponse
    {
        try {
            $companyId = $request->get('company_id');
            $attributeId = $request->get('attribute_id');
            
            if (!$companyId || !$attributeId) {
                return response()->json([
                    'success' => false,
                    'message' => 'Company ID ve Attribute ID gerekli'
                ], 400);
            }
            
            $companyAttribute = CompanyAttribute::where('company_id', $companyId)
                                                ->where('attribute_id', $attributeId)
                                                ->first();
            
            if (!$companyAttribute) {
                return response()->json([
                    'success' => false,
                    'message' => 'Attribute bulunamadı'
                ], 404);
            }
            
            return response()->json([
                'success' => true,
                'data' => [
                    'id' => $companyAttribute->id,
                    'company_id' => $companyAttribute->company_id,
                    'attribute_id' => $companyAttribute->attribute_id,
                    'type' => $companyAttribute->type,
                    'value' => $companyAttribute->value,
                    'status' => $this->determineStatus($companyAttribute->value),
                    'created_at' => $companyAttribute->created_at,
                    'updated_at' => $companyAttribute->updated_at
                ]
            ]);
            
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Detay verisi alınırken hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }
    
    /**
     * Update company attribute
     */
    public function updateCompanyAttribute(Request $request): JsonResponse
    {
        try {
            $request->validate([
                'company_id' => 'required|integer|exists:companies,id',
                'attribute_id' => 'required|integer|exists:attributes,id',
                'type' => 'required|in:class,xpath',
                'value' => 'required|string|max:500'
            ]);
            
            $companyAttribute = CompanyAttribute::updateOrCreate(
                [
                    'company_id' => $request->company_id,
                    'attribute_id' => $request->attribute_id
                ],
                [
                    'type' => $request->type,
                    'value' => $request->value
                ]
            );
            
            return response()->json([
                'success' => true,
                'message' => 'Attribute başarıyla güncellendi',
                'data' => [
                    'id' => $companyAttribute->id,
                    'company_id' => $companyAttribute->company_id,
                    'attribute_id' => $companyAttribute->attribute_id,
                    'type' => $companyAttribute->type,
                    'value' => $companyAttribute->value,
                    'status' => $this->determineStatus($companyAttribute->value)
                ]
            ]);
            
        } catch (\Illuminate\Validation\ValidationException $e) {
            return response()->json([
                'success' => false,
                'message' => 'Validation hatası',
                'errors' => $e->errors()
            ], 422);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Attribute güncellenirken hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }
    
    /**
     * Delete company attribute
     */
    public function deleteCompanyAttribute(Request $request): JsonResponse
    {
        try {
            $companyId = $request->get('company_id');
            $attributeId = $request->get('attribute_id');
            
            if (!$companyId || !$attributeId) {
                return response()->json([
                    'success' => false,
                    'message' => 'Company ID ve Attribute ID gerekli'
                ], 400);
            }
            
            $deleted = CompanyAttribute::where('company_id', $companyId)
                                     ->where('attribute_id', $attributeId)
                                     ->delete();
            
            if ($deleted) {
                return response()->json([
                    'success' => true,
                    'message' => 'Attribute başarıyla silindi'
                ]);
            } else {
                return response()->json([
                    'success' => false,
                    'message' => 'Attribute bulunamadı'
                ], 404);
            }
            
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Attribute silinirken hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }
    
    /**
     * Delete all defined attributes for all companies
     */
    public function deleteAllDefinedAttributes(): JsonResponse
    {
        try {
            // Sadece tanımlı attribute'ları sil (value'su -1 olmayan ve boş olmayan)
            $deletedCount = CompanyAttribute::where('value', '!=', '-1')
                                          ->whereNotNull('value')
                                          ->where('value', '!=', '')
                                          ->delete();
            
            return response()->json([
                'success' => true,
                'message' => "Tüm firmalardan {$deletedCount} tanımlı attribute başarıyla silindi",
                'deleted_count' => $deletedCount
            ]);
            
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Tanımlı attribute\'lar silinirken hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }
    
    /**
     * Get export data for Excel/CSV
     */
    public function exportMatrix(Request $request): JsonResponse
    {
        try {
            $format = $request->get('format', 'json'); // json, csv, excel
            
            // Matrix verisini al
            $companies = Company::with(['crawler', 'server'])->get();
            $attributes = Attribute::all();
            $companyAttributes = CompanyAttribute::all();
            
            $exportData = [];
            
            // Header row
            $header = ['Firma Adı', 'Web Sitesi', 'Crawler', 'Server'];
            foreach ($attributes as $attribute) {
                $header[] = $attribute->name;
            }
            $exportData[] = $header;
            
            // Data rows
            foreach ($companies as $company) {
                $row = [
                    $company->company_name,
                    $company->company_site ?? '',
                    $company->crawler?->name ?? 'Bilinmiyor',
                    $company->server?->name ?? 'Local'
                ];
                
                foreach ($attributes as $attribute) {
                    $companyAttribute = $companyAttributes->where('company_id', $company->id)
                                                          ->where('attribute_id', $attribute->id)
                                                          ->first();
                    
                    if ($companyAttribute) {
                        $status = $this->determineStatus($companyAttribute->value);
                        $row[] = $status === 'defined' ? '✓' : ($status === 'disabled' ? '✗' : '?');
                    } else {
                        $row[] = '?';
                    }
                }
                
                $exportData[] = $row;
            }
            
            return response()->json([
                'success' => true,
                'data' => $exportData,
                'format' => $format,
                'filename' => 'company_attribute_matrix_' . date('Y-m-d_H-i-s') . '.' . $format
            ]);
            
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Export verisi oluşturulurken hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }
    
    /**
     * Determine attribute status based on value
     */
    private function determineStatus(?string $value): string
    {
        if (is_null($value) || trim($value) === '') {
            return 'undefined';
        }
        
        if ($value === '-1') {
            return 'disabled';
        }
        
        return 'defined';
    }
    
    /**
     * Calculate summary statistics
     */
    private function calculateSummary(array $matrix, $companies, $attributes): array
    {
        $defined = 0;
        $disabled = 0;
        $undefined = 0;
        $total = 0;
        
        foreach ($companies as $company) {
            foreach ($attributes as $attribute) {
                $total++;
                $status = $matrix[$company->id][$attribute->id]['status'] ?? 'undefined';
                
                switch ($status) {
                    case 'defined':
                        $defined++;
                        break;
                    case 'disabled':
                        $disabled++;
                        break;
                    default:
                        $undefined++;
                        break;
                }
            }
        }
        
        return [
            'total' => $total,
            'defined' => $defined,
            'disabled' => $disabled,
            'undefined' => $undefined,
            'defined_percentage' => $total > 0 ? round(($defined / $total) * 100, 2) : 0,
            'disabled_percentage' => $total > 0 ? round(($disabled / $total) * 100, 2) : 0,
            'undefined_percentage' => $total > 0 ? round(($undefined / $total) * 100, 2) : 0
        ];
    }
}
