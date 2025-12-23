<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\CrawlerList;
use Illuminate\Http\Request;

class CrawlerController extends Controller
{
    /**
     * Display a listing of the crawlers.
     */
    public function index()
    {
        try {
            $crawlers = CrawlerList::select('id', 'name')->get();
            
            return response()->json([
                'success' => true,
                'data' => $crawlers
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Crawler listesi alınırken bir hata oluştu.',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Store a newly created crawler.
     */
    public function store(Request $request)
    {
        try {
            $request->validate([
                'name' => 'required|string|max:255|unique:crawler_list,name'
            ]);

            $crawler = CrawlerList::create([
                'name' => $request->name
            ]);

            return response()->json([
                'success' => true,
                'message' => 'Crawler başarıyla oluşturuldu.',
                'data' => $crawler
            ], 201);
        } catch (\Illuminate\Validation\ValidationException $e) {
            return response()->json([
                'success' => false,
                'message' => 'Doğrulama hatası.',
                'errors' => $e->errors()
            ], 422);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Crawler oluşturulurken bir hata oluştu.',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Display the specified crawler.
     */
    public function show($id)
    {
        try {
            $crawler = CrawlerList::with('companies')->findOrFail($id);
            
            return response()->json([
                'success' => true,
                'data' => $crawler
            ]);
        } catch (\Illuminate\Database\Eloquent\ModelNotFoundException $e) {
            return response()->json([
                'success' => false,
                'message' => 'Crawler bulunamadı.'
            ], 404);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Crawler bilgileri alınırken bir hata oluştu.',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Update the specified crawler.
     */
    public function update(Request $request, $id)
    {
        try {
            $crawler = CrawlerList::findOrFail($id);
            
            $request->validate([
                'name' => 'required|string|max:255|unique:crawler_list,name,' . $id
            ]);

            $crawler->update([
                'name' => $request->name
            ]);

            return response()->json([
                'success' => true,
                'message' => 'Crawler başarıyla güncellendi.',
                'data' => $crawler
            ]);
        } catch (\Illuminate\Database\Eloquent\ModelNotFoundException $e) {
            return response()->json([
                'success' => false,
                'message' => 'Crawler bulunamadı.'
            ], 404);
        } catch (\Illuminate\Validation\ValidationException $e) {
            return response()->json([
                'success' => false,
                'message' => 'Doğrulama hatası.',
                'errors' => $e->errors()
            ], 422);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Crawler güncellenirken bir hata oluştu.',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Remove the specified crawler.
     */
    public function destroy($id)
    {
        try {
            $crawler = CrawlerList::findOrFail($id);
            
            // Check if crawler has companies
            if ($crawler->companies()->count() > 0) {
                return response()->json([
                    'success' => false,
                    'message' => 'Bu crawler\'a ait firmalar bulunduğu için silinemez.'
                ], 400);
            }
            
            $crawler->delete();

            return response()->json([
                'success' => true,
                'message' => 'Crawler başarıyla silindi.'
            ]);
        } catch (\Illuminate\Database\Eloquent\ModelNotFoundException $e) {
            return response()->json([
                'success' => false,
                'message' => 'Crawler bulunamadı.'
            ], 404);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Crawler silinirken bir hata oluştu.',
                'error' => $e->getMessage()
            ], 500);
        }
    }
}