import 'dart:io';
import 'dart:typed_data';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart' show kIsWeb;
import 'api_service.dart';

class OcrService {
  /// Unified OCR for both web and mobile: sends image to backend for OCR.
  /// Pass [imageFile] for mobile, [webImageBytes] for web.
  /// [parsingMethod] can be: 'auto', 'heuristic', 'google', 'openai', 'azure', 'hybrid'
  static Future<Map<String, dynamic>> extractReceiptData({
    File? imageFile,
    Uint8List? webImageBytes,
    String parsingMethod = 'auto',
  }) async {
    try {
      final uri = Uri.parse('${ApiService.baseUrl}/api/ocr-receipt');
      var request = http.MultipartRequest('POST', uri);
      final authToken = ApiService.authToken;
      if (authToken != null) {
        request.headers['Authorization'] = 'Bearer $authToken';
      }
      
      // Add parsing method parameter
      request.fields['parsing_method'] = parsingMethod;
      
      if (kIsWeb && webImageBytes != null) {
        request.files.add(http.MultipartFile.fromBytes('image', webImageBytes, filename: 'receipt.jpg'));
      } else if (imageFile != null) {
        request.files.add(await http.MultipartFile.fromPath('image', imageFile.path));
      } else {
        return {'success': false, 'error': 'No image provided'};
      }
      
      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        // Add null checks and defaults
        return {
          'success': data['success'] ?? false,
          'store_name': data['store_name'] ?? 'Unknown Store',
          'total_amount': data['total_amount'] ?? 0.0,
          'items': data['items'] ?? [],
          'raw_text': data['raw_text'] ?? '',
          'method': data['method'] ?? 'unknown',
          'error': data['error'],
        };
      } else {
        return {'success': false, 'error': 'OCR failed: ${response.body}'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }
  
  /// Get available parsing methods
  static List<Map<String, String>> getAvailableParsingMethods() {
    return [
      {
        'value': 'auto',
        'label': 'Auto (Best Available)',
        'description': 'Automatically choose the best parsing method available'
      },
      {
        'value': 'heuristic',
        'label': 'Heuristic (Legacy)',
        'description': 'Use traditional OCR with rule-based parsing'
      },
      {
        'value': 'google',
        'label': 'Google Cloud Vision',
        'description': 'Use Google Cloud Vision API for advanced OCR'
      },
      {
        'value': 'openai',
        'label': 'OpenAI GPT-4 Vision',
        'description': 'Use OpenAI GPT-4 Vision for intelligent parsing'
      },
      {
        'value': 'azure',
        'label': 'Azure Form Recognizer',
        'description': 'Use Azure Form Recognizer (specialized for receipts)'
      },
      {
        'value': 'custom_nlp',
        'label': 'Custom NLP Model',
        'description': 'Use your own trained NLP models for parsing'
      },
      {
        'value': 'hybrid',
        'label': 'Hybrid (Multiple APIs)',
        'description': 'Combine multiple APIs for maximum accuracy'
      },
    ];
  }
} 