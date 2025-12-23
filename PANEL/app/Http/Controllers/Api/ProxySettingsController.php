<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\ProxySetting;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Validator;

class ProxySettingsController extends Controller
{
    /**
     * Proxy ayarlarını listele
     */
    public function index(): JsonResponse
    {
        try {
            $proxies = ProxySetting::where('created_by', Auth::id())
                ->orderBy('created_at', 'desc')
                ->get();

            return response()->json([
                'success' => true,
                'data' => $proxies,
                'count' => $proxies->count()
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Proxy ayarları yüklenemedi: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Yeni proxy ayarı oluştur
     */
    public function store(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'name' => 'required|string|max:255',
            'is_active' => 'boolean'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'message' => 'Geçersiz veri',
                'errors' => $validator->errors()
            ], 422);
        }

        try {
            $proxy = ProxySetting::create([
                'name' => $request->name,
                'is_active' => $request->boolean('is_active', true),
                'created_by' => Auth::id()
            ]);

            return response()->json([
                'success' => true,
                'message' => 'Proxy ayarı başarıyla oluşturuldu',
                'data' => $proxy
            ], 201);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Proxy ayarı oluşturulamadı: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Belirli proxy ayarını göster
     */
    public function show($id): JsonResponse
    {
        try {
            $proxy = ProxySetting::where('id', $id)
                ->where('created_by', Auth::id())
                ->first();

            if (!$proxy) {
                return response()->json([
                    'success' => false,
                    'message' => 'Proxy ayarı bulunamadı'
                ], 404);
            }

            return response()->json([
                'success' => true,
                'data' => $proxy
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Proxy ayarı yüklenemedi: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Proxy ayarını güncelle
     */
    public function update(Request $request, $id): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'name' => 'sometimes|required|string|max:255',
            'is_active' => 'boolean'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'message' => 'Geçersiz veri',
                'errors' => $validator->errors()
            ], 422);
        }

        try {
            $proxy = ProxySetting::where('id', $id)
                ->where('created_by', Auth::id())
                ->first();

            if (!$proxy) {
                return response()->json([
                    'success' => false,
                    'message' => 'Proxy ayarı bulunamadı'
                ], 404);
            }

            $updateData = $request->only(['name', 'is_active']);

            $proxy->update($updateData);

            return response()->json([
                'success' => true,
                'message' => 'Proxy ayarı başarıyla güncellendi',
                'data' => $proxy
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Proxy ayarı güncellenemedi: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Proxy ayarını sil
     */
    public function destroy($id): JsonResponse
    {
        try {
            $proxy = ProxySetting::where('id', $id)
                ->where('created_by', Auth::id())
                ->first();

            if (!$proxy) {
                return response()->json([
                    'success' => false,
                    'message' => 'Proxy ayarı bulunamadı'
                ], 404);
            }

            $proxy->delete();

            return response()->json([
                'success' => true,
                'message' => 'Proxy ayarı başarıyla silindi'
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Proxy ayarı silinemedi: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Proxy durumunu toggle et
     */
    public function toggleStatus($id): JsonResponse
    {
        try {
            $proxy = ProxySetting::where('id', $id)
                ->where('created_by', Auth::id())
                ->first();

            if (!$proxy) {
                return response()->json([
                    'success' => false,
                    'message' => 'Proxy ayarı bulunamadı'
                ], 404);
            }

            $proxy->toggleStatus();

            return response()->json([
                'success' => true,
                'message' => $proxy->is_active ? 'Proxy aktifleştirildi' : 'Proxy pasifleştirildi',
                'data' => $proxy
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Proxy durumu değiştirilemedi: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Tüm proxy ayarlarını sil
     */
    public function deleteAll(): JsonResponse
    {
        try {
            $deletedCount = ProxySetting::where('created_by', Auth::id())->count();
            
            ProxySetting::where('created_by', Auth::id())->delete();

            return response()->json([
                'success' => true,
                'message' => 'Tüm proxy ayarları silindi',
                'deleted_count' => $deletedCount
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Proxy ayarları silinemedi: ' . $e->getMessage()
            ], 500);
        }
    }

}
