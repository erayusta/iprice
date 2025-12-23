<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Proxy;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

class ProxyController extends Controller
{
    /**
     * Aktif proxy'lerden rastgele 100 tane döndür
     */
    public function getProxies(): JsonResponse
    {
        $proxies = Proxy::where('active', true)
            ->inRandomOrder()
            ->limit(100)
            ->get();

        return response()->json([
            'success' => true,
            'data' => $proxies,
            'count' => $proxies->count()
        ]);
    }

    /**
     * Belirtilen proxy'yi inactive yap
     */
    public function markProxyAsFailed(Request $request): JsonResponse
    {
        $request->validate([
            'id' => 'required|integer|exists:proxies,id'
        ]);

        $proxy = Proxy::find($request->id);
        
        if (!$proxy) {
            return response()->json([
                'success' => false,
                'message' => 'Proxy bulunamadı'
            ], 404);
        }

        $proxy->update(['active' => false]);

        return response()->json([
            'success' => true,
            'message' => 'Proxy başarıyla inactive yapıldı',
            'data' => $proxy
        ]);
    }
}
