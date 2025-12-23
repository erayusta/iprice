<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class MultipartFormDataParser
{
    /**
     * Handle an incoming request.
     *
     * @param  \Closure(\Illuminate\Http\Request): (\Symfony\Component\HttpFoundation\Response)  $next
     */
    public function handle(Request $request, Closure $next): Response
    {
        // Check if this is a multipart form data request with PUT method
        if ($request->isMethod('PUT') && 
            str_contains($request->header('Content-Type', ''), 'multipart/form-data')) {
            
            // Parse the raw input manually
            $rawInput = $request->getContent();
            $boundary = $this->extractBoundary($request->header('Content-Type'));
            
            if ($boundary && $rawInput) {
                $parsedData = $this->parseMultipartData($rawInput, $boundary);
                
                // Merge parsed data into request
                $request->merge($parsedData);
            }
        }
        
        return $next($request);
    }
    
    /**
     * Extract boundary from Content-Type header
     */
    private function extractBoundary($contentType)
    {
        if (preg_match('/boundary=(.+)$/', $contentType, $matches)) {
            return '--' . trim($matches[1]);
        }
        return null;
    }
    
    /**
     * Parse multipart form data
     */
    private function parseMultipartData($rawInput, $boundary)
    {
        $data = [];
        $parts = explode($boundary, $rawInput);
        
        foreach ($parts as $part) {
            if (empty(trim($part)) || $part === '--') {
                continue;
            }
            
            // Split headers and content
            $part = trim($part);
            if (strpos($part, "\r\n\r\n") !== false) {
                list($headers, $content) = explode("\r\n\r\n", $part, 2);
                
                // Extract field name from Content-Disposition header
                if (preg_match('/name="([^"]+)"/', $headers, $matches)) {
                    $fieldName = $matches[1];
                    $data[$fieldName] = trim($content);
                }
            }
        }
        
        return $data;
    }
}
