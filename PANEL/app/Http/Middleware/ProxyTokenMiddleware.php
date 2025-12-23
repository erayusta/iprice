<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class ProxyTokenMiddleware
{
    /**
     * Handle an incoming request.
     *
     * @param  \Closure(\Illuminate\Http\Request): (\Symfony\Component\HttpFoundation\Response)  $next
     */
    public function handle(Request $request, Closure $next): Response
    {
        $token = $request->header('X-Proxy-Token') ?? $request->query('token');
        $validToken = config('app.proxy_api_token');

        if (!$token || $token !== $validToken) {
            return response()->json([
                'success' => false,
                'message' => 'Geçersiz token'
            ], 401);
        }

        return $next($request);
    }
}
