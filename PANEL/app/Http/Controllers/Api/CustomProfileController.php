<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\CustomProfile;
use App\Models\CustomProfileProduct;
use App\Models\CustomProfileShare;
use App\Models\User;
use App\Models\UserProduct;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;

class CustomProfileController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        try {
            $userId = Auth::id();
            
            // Kendi oluşturduğu profiller
            $ownProfiles = CustomProfile::where('user_id', $userId)
                ->withCount('products')
                ->orderBy('created_at', 'desc')
                ->get()
                ->map(function ($profile) {
                    $profile->is_owner = true;
                    $profile->is_shared = false;
                    return $profile;
                });

            // Paylaşılan profiller
            $sharedProfiles = CustomProfile::whereHas('shares', function ($query) use ($userId) {
                $query->where('user_id', $userId);
            })
            ->withCount('products')
            ->orderBy('created_at', 'desc')
            ->get()
            ->map(function ($profile) {
                $profile->is_owner = false;
                $profile->is_shared = true;
                return $profile;
            });

            // İkisini birleştir
            $profiles = $ownProfiles->merge($sharedProfiles);

            return response()->json([
                'success' => true,
                'data' => $profiles
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Profiller yüklenirken hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        try {
            $request->validate([
                'name' => 'required|string|max:255',
                'description' => 'nullable|string'
            ]);

            $profile = CustomProfile::create([
                'name' => $request->name,
                'description' => $request->description,
                'user_id' => Auth::id()
            ]);

            return response()->json([
                'success' => true,
                'message' => 'Profil başarıyla oluşturuldu',
                'data' => $profile
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Profil oluşturulurken hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Display the specified resource.
     */
    public function show($id)
    {
        try {
            $userId = Auth::id();
            
            // Profil sahibi mi veya paylaşılan profiller arasında mı kontrol et
            $profile = CustomProfile::where(function ($query) use ($userId) {
                $query->where('user_id', $userId)
                    ->orWhereHas('shares', function ($q) use ($userId) {
                        $q->where('user_id', $userId);
                    });
            })
            ->where('id', $id)
            ->withCount('products')
            ->first();

            if (!$profile) {
                return response()->json([
                    'success' => false,
                    'message' => 'Profil bulunamadı'
                ], 404);
            }

            // Profil sahibi mi kontrol et
            $profile->is_owner = $profile->user_id === $userId;
            $profile->is_shared = !$profile->is_owner;

            return response()->json([
                'success' => true,
                'data' => $profile
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Profil yüklenirken hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, $id)
    {
        try {
            $profile = CustomProfile::where('id', $id)
                ->where('user_id', Auth::id())
                ->first();

            if (!$profile) {
                return response()->json([
                    'success' => false,
                    'message' => 'Profil bulunamadı'
                ], 404);
            }

            $request->validate([
                'name' => 'required|string|max:255',
                'description' => 'nullable|string'
            ]);

            $profile->update([
                'name' => $request->name,
                'description' => $request->description
            ]);

            return response()->json([
                'success' => true,
                'message' => 'Profil başarıyla güncellendi',
                'data' => $profile
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Profil güncellenirken hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy($id)
    {
        try {
            $profile = CustomProfile::where('id', $id)
                ->where('user_id', Auth::id())
                ->first();

            if (!$profile) {
                return response()->json([
                    'success' => false,
                    'message' => 'Profil bulunamadı'
                ], 404);
            }

            $profile->delete();

            return response()->json([
                'success' => true,
                'message' => 'Profil başarıyla silindi'
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Profil silinirken hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get products for a specific profile
     */
    public function getProducts($id)
    {
        try {
            $userId = Auth::id();
            
            // Profil sahibi mi veya paylaşılan profiller arasında mı kontrol et
            $profile = CustomProfile::where(function ($query) use ($userId) {
                $query->where('user_id', $userId)
                    ->orWhereHas('shares', function ($q) use ($userId) {
                        $q->where('user_id', $userId);
                    });
            })
            ->where('id', $id)
            ->first();

            if (!$profile) {
                return response()->json([
                    'success' => false,
                    'message' => 'Profil bulunamadı'
                ], 404);
            }

            $products = CustomProfileProduct::where('custom_profile_id', $id)
                ->with('product')
                ->orderBy('sort_order')
                ->get();

            return response()->json([
                'success' => true,
                'data' => $products
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Profil ürünleri yüklenirken hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Add product to profile
     */
    public function addProduct(Request $request, $id)
    {
        try {
            $profile = CustomProfile::where('id', $id)
                ->where('user_id', Auth::id())
                ->first();

            if (!$profile) {
                return response()->json([
                    'success' => false,
                    'message' => 'Profil bulunamadı'
                ], 404);
            }

            $request->validate([
                'product_id' => 'required|exists:user_products,id'
            ]);

            // Check if product already exists in profile
            $existingProduct = CustomProfileProduct::where('custom_profile_id', $id)
                ->where('user_product_id', $request->product_id)
                ->first();

            if ($existingProduct) {
                return response()->json([
                    'success' => false,
                    'message' => 'Bu ürün zaten profilde mevcut'
                ], 400);
            }

            // Get the next sort order
            $maxSortOrder = CustomProfileProduct::where('custom_profile_id', $id)
                ->max('sort_order') ?? 0;

            CustomProfileProduct::create([
                'custom_profile_id' => $id,
                'user_product_id' => $request->product_id,
                'sort_order' => $maxSortOrder + 1
            ]);

            return response()->json([
                'success' => true,
                'message' => 'Ürün profile eklendi'
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Ürün eklenirken hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Remove product from profile
     */
    public function removeProduct($profileId, $profileProductId)
    {
        try {
            $profile = CustomProfile::where('id', $profileId)
                ->where('user_id', Auth::id())
                ->first();

            if (!$profile) {
                return response()->json([
                    'success' => false,
                    'message' => 'Profil bulunamadı'
                ], 404);
            }

            $profileProduct = CustomProfileProduct::where('id', $profileProductId)
                ->where('custom_profile_id', $profileId)
                ->first();

            if (!$profileProduct) {
                return response()->json([
                    'success' => false,
                    'message' => 'Profil ürünü bulunamadı'
                ], 404);
            }

            $profileProduct->delete();

            return response()->json([
                'success' => true,
                'message' => 'Ürün profilden çıkarıldı'
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Ürün çıkarılırken hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Reorder products in profile
     */
    public function reorderProducts(Request $request, $id)
    {
        try {
            $profile = CustomProfile::where('id', $id)
                ->where('user_id', Auth::id())
                ->first();

            if (!$profile) {
                return response()->json([
                    'success' => false,
                    'message' => 'Profil bulunamadı'
                ], 404);
            }

            $request->validate([
                'from_index' => 'required|integer|min:0',
                'to_index' => 'required|integer|min:0'
            ]);

            $fromIndex = $request->from_index;
            $toIndex = $request->to_index;

            $products = CustomProfileProduct::where('custom_profile_id', $id)
                ->orderBy('sort_order')
                ->get();

            if ($fromIndex >= $products->count() || $toIndex >= $products->count()) {
                return response()->json([
                    'success' => false,
                    'message' => 'Geçersiz indeks'
                ], 400);
            }

            DB::transaction(function () use ($products, $fromIndex, $toIndex) {
                // Remove the item from its current position
                $item = $products->splice($fromIndex, 1)->first();
                
                // Insert it at the new position
                $products->splice($toIndex, 0, [$item]);
                
                // Update sort orders
                foreach ($products as $index => $product) {
                    $product->update(['sort_order' => $index + 1]);
                }
            });

            return response()->json([
                'success' => true,
                'message' => 'Sıralama güncellendi'
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Sıralama güncellenirken hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }

    public function addMultipleProducts(Request $request, $id)
    {
        try {
            $profile = CustomProfile::where('id', $id)
                ->where('user_id', auth()->id())
                ->firstOrFail();

            $productIds = $request->input('product_ids', []);
            
            if (empty($productIds)) {
                return response()->json([
                    'success' => false,
                    'message' => 'Ürün ID\'leri gerekli'
                ], 400);
            }

            $addedCount = 0;
            $skippedCount = 0;
            $maxSortOrder = $profile->products()->max('sort_order') ?? 0;

            foreach ($productIds as $productId) {
                // Ürünün zaten profilde olup olmadığını kontrol et
                $exists = $profile->products()->where('user_product_id', $productId)->exists();
                
                if (!$exists) {
                    // Ürünü profile ekle
                    $profile->products()->create([
                        'user_product_id' => $productId,
                        'sort_order' => ++$maxSortOrder
                    ]);
                    $addedCount++;
                } else {
                    $skippedCount++;
                }
            }

            return response()->json([
                'success' => true,
                'message' => "{$addedCount} ürün eklendi, {$skippedCount} ürün atlandı",
                'added_count' => $addedCount,
                'skipped_count' => $skippedCount
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Ürünler eklenirken hata: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Share profile with a user
     */
    public function shareProfile(Request $request, $id)
    {
        try {
            $profile = CustomProfile::where('id', $id)
                ->where('user_id', Auth::id())
                ->first();

            if (!$profile) {
                return response()->json([
                    'success' => false,
                    'message' => 'Profil bulunamadı veya bu profili paylaşma yetkiniz yok'
                ], 404);
            }

            $request->validate([
                'user_id' => 'required|exists:users,id'
            ]);

            // Kendi kendine paylaşmayı engelle
            if ($request->user_id == Auth::id()) {
                return response()->json([
                    'success' => false,
                    'message' => 'Kendi profilinizi kendinizle paylaşamazsınız'
                ], 400);
            }

            // Zaten paylaşılmış mı kontrol et
            $existingShare = CustomProfileShare::where('profiles_id', $id)
                ->where('user_id', $request->user_id)
                ->first();

            if ($existingShare) {
                return response()->json([
                    'success' => false,
                    'message' => 'Bu profil zaten bu kullanıcıyla paylaşılmış'
                ], 400);
            }

            CustomProfileShare::create([
                'profiles_id' => $id,
                'user_id' => $request->user_id
            ]);

            return response()->json([
                'success' => true,
                'message' => 'Profil başarıyla paylaşıldı'
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Profil paylaşılırken hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Unshare profile from a user
     */
    public function unshareProfile(Request $request, $id)
    {
        try {
            $profile = CustomProfile::where('id', $id)
                ->where('user_id', Auth::id())
                ->first();

            if (!$profile) {
                return response()->json([
                    'success' => false,
                    'message' => 'Profil bulunamadı veya bu profilin paylaşımını kaldırma yetkiniz yok'
                ], 404);
            }

            $request->validate([
                'user_id' => 'required|exists:users,id'
            ]);

            $share = CustomProfileShare::where('profiles_id', $id)
                ->where('user_id', $request->user_id)
                ->first();

            if (!$share) {
                return response()->json([
                    'success' => false,
                    'message' => 'Bu profil bu kullanıcıyla paylaşılmamış'
                ], 404);
            }

            $share->delete();

            return response()->json([
                'success' => true,
                'message' => 'Profil paylaşımı başarıyla kaldırıldı'
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Profil paylaşımı kaldırılırken hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get users that a profile is shared with
     */
    public function getSharedUsers($id)
    {
        try {
            $profile = CustomProfile::where('id', $id)
                ->where('user_id', Auth::id())
                ->first();

            if (!$profile) {
                return response()->json([
                    'success' => false,
                    'message' => 'Profil bulunamadı veya bu profilin paylaşım bilgilerini görüntüleme yetkiniz yok'
                ], 404);
            }

            $sharedUsers = CustomProfileShare::where('profiles_id', $id)
                ->with('user:id,name,email')
                ->get()
                ->map(function ($share) {
                    return [
                        'id' => $share->user->id,
                        'name' => $share->user->name,
                        'email' => $share->user->email,
                        'shared_at' => $share->created_at
                    ];
                });

            return response()->json([
                'success' => true,
                'data' => $sharedUsers
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Paylaşım bilgileri yüklenirken hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get list of users to share with (excluding current user and already shared users)
     */
    public function getAvailableUsers($id)
    {
        try {
            $profile = CustomProfile::where('id', $id)
                ->where('user_id', Auth::id())
                ->first();

            if (!$profile) {
                return response()->json([
                    'success' => false,
                    'message' => 'Profil bulunamadı'
                ], 404);
            }

            // Zaten paylaşılan kullanıcı ID'leri
            $sharedUserIds = CustomProfileShare::where('profiles_id', $id)
                ->pluck('user_id')
                ->toArray();

            // Kullanılabilir kullanıcıları getir (kendisi ve zaten paylaşılanlar hariç)
            $availableUsers = User::where('id', '!=', Auth::id())
                ->whereNotIn('id', $sharedUserIds)
                ->select('id', 'name', 'email')
                ->get();

            return response()->json([
                'success' => true,
                'data' => $availableUsers
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Kullanıcılar yüklenirken hata oluştu: ' . $e->getMessage()
            ], 500);
        }
    }
}