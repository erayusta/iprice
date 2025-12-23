<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\User;
use App\Models\Role;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Str;
use Carbon\Carbon;

class UserController extends Controller
{
    /**
     * Display a listing of users.
     */
    public function index(Request $request): JsonResponse
    {
        $query = User::with(['roles']);

        // Search functionality
        if ($request->has('search') && $request->search) {
            $search = $request->search;
            $query->where(function ($q) use ($search) {
                $q->where('name', 'like', "%{$search}%")
                  ->orWhere('email', 'like', "%{$search}%");
            });
        }

        // Role filter
        if ($request->has('role_id') && $request->role_id) {
            $query->whereHas('roles', function ($q) use ($request) {
                $q->where('roles.id', $request->role_id);
            });
        }

        // Pagination
        $perPage = $request->get('per_page', 15);
        $users = $query->paginate($perPage);

        return response()->json([
            'success' => true,
            'data' => $users
        ]);
    }

    /**
     * Store a newly created user.
     */
    public function store(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'name' => 'required|string|max:255',
            'email' => 'required|string|email|max:255|unique:users',
            'password' => 'required|string|min:8|confirmed',
            'role_ids' => 'array',
            'role_ids.*' => 'exists:roles,id'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'message' => 'Validation errors',
                'errors' => $validator->errors()
            ], 422);
        }

        $user = User::create([
            'name' => $request->name,
            'email' => $request->email,
            'password' => Hash::make($request->password),
        ]);

        // Assign roles
        if ($request->has('role_ids')) {
            $user->roles()->sync($request->role_ids);
        }

        $user->load('roles');

        return response()->json([
            'success' => true,
            'message' => 'User created successfully',
            'data' => $user
        ], 201);
    }

    /**
     * Display the specified user.
     */
    public function show(User $user): JsonResponse
    {
        $user->load('roles');
        
        return response()->json([
            'success' => true,
            'data' => $user
        ]);
    }

    /**
     * Update the specified user.
     */
    public function update(Request $request, User $user): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'name' => 'required|string|max:255',
            'email' => 'required|string|email|max:255|unique:users,email,' . $user->id,
            'password' => 'nullable|string|min:8',
            'password_confirmation' => 'nullable|same:password',
            'role_ids' => 'array',
            'role_ids.*' => 'exists:roles,id'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'message' => 'Validation errors',
                'errors' => $validator->errors()
            ], 422);
        }

        $updateData = [
            'name' => $request->name,
            'email' => $request->email,
        ];

        if ($request->has('password') && $request->password) {
            $updateData['password'] = Hash::make($request->password);
        }

        $user->update($updateData);

        // Update roles
        if ($request->has('role_ids')) {
            $user->roles()->sync($request->role_ids);
        }

        $user->load('roles');

        return response()->json([
            'success' => true,
            'message' => 'User updated successfully',
            'data' => $user
        ]);
    }

    /**
     * Remove the specified user.
     */
    public function destroy(User $user): JsonResponse
    {
        // Prevent deleting the current user
        if ($user->id === auth()->id()) {
            return response()->json([
                'success' => false,
                'message' => 'You cannot delete your own account'
            ], 403);
        }

        $user->delete();

        return response()->json([
            'success' => true,
            'message' => 'User deleted successfully'
        ]);
    }

    /**
     * Get all roles for user assignment.
     */
    public function getRoles(): JsonResponse
    {
        $roles = Role::select('id', 'name')->get();
        
        return response()->json([
            'success' => true,
            'data' => $roles
        ]);
    }

    /**
     * Get current user profile with token information.
     */
    public function profile(): JsonResponse
    {
        $user = auth()->user();
        
        // Get user statistics
        $stats = [
            'totalAttributes' => 0, // TODO: Implement attribute counting
            'todayAttributes' => 0, // TODO: Implement today's attribute counting
            'lastActivity' => $user->token_created_at ? $user->token_created_at->format('d.m.Y H:i') : null
        ];
        
        return response()->json([
            'success' => true,
            'user' => $user,
            'stats' => $stats
        ]);
    }

    /**
     * Generate a new iPrice token for the current user.
     */
    public function generateToken(): JsonResponse
    {
        $user = auth()->user();
        
        // Generate a unique token
        $token = 'iprice_' . Str::random(32);
        
        // Update user with new token
        $user->update([
            'iprice_token' => $token,
            'token_created_at' => Carbon::now()
        ]);
        
        return response()->json([
            'success' => true,
            'message' => 'Token başarıyla oluşturuldu',
            'token' => $token
        ]);
    }

    /**
     * Test the current user's iPrice token.
     */
    public function testToken(): JsonResponse
    {
        $user = auth()->user();
        
        if (!$user->iprice_token) {
            return response()->json([
                'success' => false,
                'message' => 'Token bulunamadı'
            ], 404);
        }
        
        // TODO: Implement actual token validation logic
        // For now, just return success if token exists
        return response()->json([
            'success' => true,
            'message' => 'Token geçerli'
        ]);
    }
}
