<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Attribute;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Facades\DB;

class AttributeController extends Controller
{
    /**
     * Get all attributes
     */
    public function index(): JsonResponse
    {
        try {
            $attributes = Attribute::orderBy('name')->get();
            
            return response()->json([
                'success' => true,
                'data' => $attributes
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Attribute\'lar yüklenirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Create a new attribute
     */
    public function store(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'name' => 'required|string|max:255|unique:attributes,name',
            'description' => 'nullable|string'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'message' => 'Geçersiz veri',
                'errors' => $validator->errors()
            ], 422);
        }

        try {
            DB::beginTransaction();

            $attribute = Attribute::create([
                'name' => $request->name,
                'description' => $request->description
            ]);

            DB::commit();

            return response()->json([
                'success' => true,
                'message' => 'Attribute başarıyla oluşturuldu',
                'data' => $attribute
            ], 201);
        } catch (\Exception $e) {
            DB::rollBack();
            return response()->json([
                'success' => false,
                'message' => 'Attribute oluşturulurken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get a specific attribute
     */
    public function show($id): JsonResponse
    {
        try {
            $attribute = Attribute::find($id);
            
            if (!$attribute) {
                return response()->json([
                    'success' => false,
                    'message' => 'Attribute bulunamadı'
                ], 404);
            }

            return response()->json([
                'success' => true,
                'data' => $attribute
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Attribute yüklenirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Update an attribute
     */
    public function update(Request $request, $id): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'name' => 'required|string|max:255|unique:attributes,name,' . $id,
            'description' => 'nullable|string'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'message' => 'Geçersiz veri',
                'errors' => $validator->errors()
            ], 422);
        }

        try {
            $attribute = Attribute::find($id);
            
            if (!$attribute) {
                return response()->json([
                    'success' => false,
                    'message' => 'Attribute bulunamadı'
                ], 404);
            }

            DB::beginTransaction();

            $attribute->update([
                'name' => $request->name,
                'description' => $request->description
            ]);

            DB::commit();

            return response()->json([
                'success' => true,
                'message' => 'Attribute başarıyla güncellendi',
                'data' => $attribute
            ]);
        } catch (\Exception $e) {
            DB::rollBack();
            return response()->json([
                'success' => false,
                'message' => 'Attribute güncellenirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Delete an attribute
     */
    public function destroy($id): JsonResponse
    {
        try {
            $attribute = Attribute::find($id);
            
            if (!$attribute) {
                return response()->json([
                    'success' => false,
                    'message' => 'Attribute bulunamadı'
                ], 404);
            }

            DB::beginTransaction();

            // Check if attribute is being used by any company
            $companyAttributeCount = $attribute->companyAttributes()->count();
            if ($companyAttributeCount > 0) {
                return response()->json([
                    'success' => false,
                    'message' => 'Bu attribute kullanımda olduğu için silinemez. Önce ilgili company attribute\'ları silin.'
                ], 400);
            }

            $attribute->delete();

            DB::commit();

            return response()->json([
                'success' => true,
                'message' => 'Attribute başarıyla silindi'
            ]);
        } catch (\Exception $e) {
            DB::rollBack();
            return response()->json([
                'success' => false,
                'message' => 'Attribute silinirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Delete all attributes
     */
    public function deleteAll(): JsonResponse
    {
        try {
            DB::beginTransaction();

            // Check if any attributes are being used by companies
            $usedAttributesCount = DB::table('company_attributes')
                ->whereIn('attribute_id', function($query) {
                    $query->select('id')->from('attributes');
                })
                ->count();

            if ($usedAttributesCount > 0) {
                return response()->json([
                    'success' => false,
                    'message' => 'Bazı attribute\'lar kullanımda olduğu için tümü silinemez. Önce ilgili company attribute\'ları silin.'
                ], 400);
            }

            $deletedCount = Attribute::count();
            Attribute::truncate();

            DB::commit();

            return response()->json([
                'success' => true,
                'message' => "Tüm attribute'lar başarıyla silindi",
                'deleted_count' => $deletedCount
            ]);
        } catch (\Exception $e) {
            DB::rollBack();
            return response()->json([
                'success' => false,
                'message' => 'Attribute\'lar silinirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }
}