<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\CompanyAttribute;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class CompanyAttributeController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
        try {
            $query = CompanyAttribute::with(['company', 'attribute']);

            // Company filter
            if ($request->has('company_id') && $request->company_id) {
                $query->where('company_id', $request->company_id);
            }

            // Attribute filter
            if ($request->has('attribute_id') && $request->attribute_id) {
                $query->where('attribute_id', $request->attribute_id);
            }

            $companyAttributes = $query->orderBy('created_at', 'desc')->get();

            return response()->json([
                'success' => true,
                'data' => $companyAttributes
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Company attributes yüklenirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        try {
            $validator = \Validator::make($request->all(), [
                'company_id' => 'required|exists:companies,id',
                'attributes' => 'required|array',
                'attributes.*.attribute_id' => 'required|exists:attributes,id',
                'attributes.*.type' => 'required|in:class,xpath',
                'attributes.*.value' => 'required|string|max:500',
            ]);

            if ($validator->fails()) {
                return response()->json([
                    'success' => false,
                    'message' => 'Doğrulama hatası',
                    'errors' => $validator->errors()
                ], 422);
            }

            DB::beginTransaction();

            try {
                // Delete existing attributes for this company
                CompanyAttribute::where('company_id', $request->company_id)->delete();

                // Insert new attributes
                $attributesToInsert = [];
                $attributes = $request->input('attributes');
                
                foreach ($attributes as $attr) {
                    $attributesToInsert[] = [
                        'company_id' => $request->company_id,
                        'attribute_id' => $attr['attribute_id'],
                        'type' => $attr['type'],
                        'value' => $attr['value'],
                        'created_at' => now(),
                        'updated_at' => now(),
                    ];
                }

                if (!empty($attributesToInsert)) {
                    CompanyAttribute::insert($attributesToInsert);
                }

                DB::commit();

                return response()->json([
                    'success' => true,
                    'message' => 'Company attributes başarıyla kaydedildi',
                    'data' => CompanyAttribute::where('company_id', $request->company_id)->with('attribute')->get()
                ], 201);
            } catch (\Exception $e) {
                DB::rollback();
                throw $e;
            }
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Company attributes kaydedilirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Display the specified resource.
     */
    public function show(CompanyAttribute $companyAttribute)
    {
        try {
            return response()->json([
                'success' => true,
                'data' => $companyAttribute->load(['company', 'attribute'])
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Company attribute yüklenirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, CompanyAttribute $companyAttribute)
    {
        try {
            $validator = \Validator::make($request->all(), [
                'type' => 'required|in:class,xpath',
                'value' => 'required|string|max:500',
            ]);

            if ($validator->fails()) {
                return response()->json([
                    'success' => false,
                    'message' => 'Doğrulama hatası',
                    'errors' => $validator->errors()
                ], 422);
            }

            $companyAttribute->update($request->only(['type', 'value']));

            return response()->json([
                'success' => true,
                'message' => 'Company attribute başarıyla güncellendi',
                'data' => $companyAttribute->load(['company', 'attribute'])
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Company attribute güncellenirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(CompanyAttribute $companyAttribute)
    {
        try {
            $companyAttribute->delete();

            return response()->json([
                'success' => true,
                'message' => 'Company attribute başarıyla silindi'
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Company attribute silinirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }
}

