<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Brand;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Facades\Log;

class BrandController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
        try {
            $query = Brand::query();

            // Search filter
            if ($request->has('search') && $request->search) {
                $search = $request->search;
                $query->where('name', 'LIKE', "%{$search}%");
            }

            // Active filter
            if ($request->has('is_active') && $request->is_active !== null) {
                $query->where('is_active', $request->is_active);
            }

            $brands = $query->withCount('userProducts')->orderBy('name', 'asc')->get();

            return response()->json([
                'success' => true,
                'data' => $brands,
                'total' => $brands->count()
            ]);
        } catch (\Exception $e) {
            Log::error('Brands index error: ' . $e->getMessage());
            return response()->json([
                'success' => false,
                'message' => 'Markalar yüklenirken bir hata oluştu',
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
            $validator = Validator::make($request->all(), [
                'name' => 'required|string|max:255|unique:brands,name',
                'slug' => 'nullable|string|max:255|unique:brands,slug',
                'description' => 'nullable|string',
                'logo' => 'nullable|string',
                'is_active' => 'boolean'
            ]);

            if ($validator->fails()) {
                return response()->json([
                    'success' => false,
                    'message' => 'Doğrulama hatası',
                    'errors' => $validator->errors()
                ], 422);
            }

            $data = $request->all();
            
            // Auto-generate slug if not provided
            if (empty($data['slug'])) {
                $data['slug'] = \Illuminate\Support\Str::slug($data['name']);
            }
            
            $brand = Brand::create($data);

            return response()->json([
                'success' => true,
                'message' => 'Marka başarıyla oluşturuldu',
                'data' => $brand
            ], 201);

        } catch (\Exception $e) {
            Log::error('Brand store error: ' . $e->getMessage());
            return response()->json([
                'success' => false,
                'message' => 'Marka oluşturulurken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Display the specified resource.
     */
    public function show(string $id)
    {
        try {
            $brand = Brand::with('userProducts')->findOrFail($id);

            return response()->json([
                'success' => true,
                'data' => $brand
            ]);

        } catch (\Exception $e) {
            Log::error('Brand show error: ' . $e->getMessage());
            return response()->json([
                'success' => false,
                'message' => 'Marka bulunamadı',
                'error' => $e->getMessage()
            ], 404);
        }
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, string $id)
    {
        try {
            $brand = Brand::findOrFail($id);

            $validator = Validator::make($request->all(), [
                'name' => 'required|string|max:255|unique:brands,name,' . $id,
                'slug' => 'nullable|string|max:255|unique:brands,slug,' . $id,
                'description' => 'nullable|string',
                'logo' => 'nullable|string',
                'is_active' => 'boolean'
            ]);

            if ($validator->fails()) {
                return response()->json([
                    'success' => false,
                    'message' => 'Doğrulama hatası',
                    'errors' => $validator->errors()
                ], 422);
            }

            $data = $request->all();
            
            // Auto-generate slug if not provided
            if (empty($data['slug'])) {
                $data['slug'] = \Illuminate\Support\Str::slug($data['name']);
            }
            
            $brand->update($data);

            return response()->json([
                'success' => true,
                'message' => 'Marka başarıyla güncellendi',
                'data' => $brand
            ]);

        } catch (\Exception $e) {
            Log::error('Brand update error: ' . $e->getMessage());
            return response()->json([
                'success' => false,
                'message' => 'Marka güncellenirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(string $id)
    {
        try {
            $brand = Brand::findOrFail($id);

            // Check if brand has products
            if ($brand->userProducts()->count() > 0) {
                return response()->json([
                    'success' => false,
                    'message' => 'Bu markaya ait ürünler bulunduğu için silinemez'
                ], 422);
            }

            $brand->delete();

            return response()->json([
                'success' => true,
                'message' => 'Marka başarıyla silindi'
            ]);

        } catch (\Exception $e) {
            Log::error('Brand destroy error: ' . $e->getMessage());
            return response()->json([
                'success' => false,
                'message' => 'Marka silinirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Delete all brands.
     */
    public function deleteAll()
    {
        try {
            $deletedCount = Brand::count();
            Brand::truncate();

            return response()->json([
                'success' => true,
                'message' => 'Tüm markalar başarıyla silindi',
                'deleted_count' => $deletedCount
            ]);

        } catch (\Exception $e) {
            Log::error('Delete all brands error: ' . $e->getMessage());
            return response()->json([
                'success' => false,
                'message' => 'Markalar silinirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }
}
