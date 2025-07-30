import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart' show kIsWeb;

class ApiService {
  // Use different URLs for web vs mobile
  static String get baseUrl {
    if (kIsWeb) {
      // Production URL - update this with your actual production API URL
      return 'https://api.nyamshaik.me'; // For production (HTTPS)
      // return 'http://localhost:5000'; // For local testing (HTTP)
    } else {
      // For Android emulator, use 10.0.2.2 to access host machine
      return 'http://10.0.2.2:5000';
    }
  }
  static String? _authToken;
  
  // Public getter for auth token
  static String? get authToken => _authToken;
  
  // Set auth token after login
  static void setAuthToken(String token) {
    _authToken = token;
  }
  
  // Get headers with auth token
  static Map<String, String> get _headers {
    final headers = {
      'Content-Type': 'application/json',
    };
    if (_authToken != null) {
      headers['Authorization'] = 'Bearer $_authToken';
    }
    return headers;
  }
  
  // Register user
  static Future<Map<String, dynamic>> register(Map<String, dynamic> userData) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/register'),
        headers: _headers,
        body: json.encode(userData),
      );

      if (response.statusCode == 200) {
        return {'success': true, 'message': 'Registration successful'};
      } else {
        final error = json.decode(response.body);
        return {'success': false, 'error': error['error'] ?? 'Registration failed'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Login user
  static Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/login'),
        headers: _headers,
        body: json.encode({
          'email': email,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _authToken = data['access_token'];
        return {'success': true, 'token': data['access_token']};
      } else {
        final error = json.decode(response.body);
        return {'success': false, 'error': error['error'] ?? 'Login failed'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Receipt upload with OCR data
  static Future<Map<String, dynamic>> uploadReceipt({
    File? imageFile,
    Uint8List? webImageBytes,
    required String storeName,
    required double totalAmount,
    required List<Map<String, dynamic>> items,
    String parsingMethod = 'auto',
  }) async {
    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/upload-receipt'),
      );
      
      // Add authorization header
      if (_authToken != null) {
        request.headers['Authorization'] = 'Bearer $_authToken';
      }
      
      // Add form fields
      request.fields['store_name'] = storeName;
      request.fields['total_amount'] = totalAmount.toString();
      request.fields['items'] = json.encode(items);
      request.fields['parsing_method'] = parsingMethod;
      
      // Add image file
      if (kIsWeb && webImageBytes != null) {
        // For web, add bytes as file
        request.files.add(
          http.MultipartFile.fromBytes(
            'image',
            webImageBytes,
            filename: 'receipt.jpg',
          ),
        );
      } else if (imageFile != null) {
        // For mobile, add file
        request.files.add(
          await http.MultipartFile.fromPath(
            'image',
            imageFile.path,
          ),
        );
      } else {
        return {'success': false, 'error': 'No image provided'};
      }
      
      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return {'success': true, 'receipt_id': data['receipt_id']};
      } else {
        final error = json.decode(response.body);
        return {'success': false, 'error': error['error'] ?? 'Upload failed'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Get all receipts
  static Future<Map<String, dynamic>> getReceipts() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/receipts'),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return {'success': true, 'receipts': data['receipts']};
      } else {
        final error = json.decode(response.body);
        return {'success': false, 'error': error['error'] ?? 'Failed to fetch receipts'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Get single receipt
  static Future<Map<String, dynamic>> getReceipt(int receiptId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/receipt/$receiptId'),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return {'success': true, 'receipt': data};
      } else {
        final error = json.decode(response.body);
        return {'success': false, 'error': error['error'] ?? 'Failed to fetch receipt'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Update receipt
  static Future<Map<String, dynamic>> updateReceipt(
    int receiptId,
    Map<String, dynamic> receiptData,
  ) async {
    try {
      final response = await http.put(
        Uri.parse('$baseUrl/receipt/$receiptId'),
        headers: _headers,
        body: json.encode(receiptData),
      );

      if (response.statusCode == 200) {
        return {'success': true, 'message': 'Receipt updated successfully'};
      } else {
        final error = json.decode(response.body);
        return {'success': false, 'error': error['error'] ?? 'Failed to update receipt'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Delete receipt
  static Future<Map<String, dynamic>> deleteReceipt(int receiptId) async {
    try {
      final response = await http.delete(
        Uri.parse('$baseUrl/receipt/$receiptId'),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        return {'success': true, 'message': 'Receipt deleted successfully'};
      } else {
        final error = json.decode(response.body);
        return {'success': false, 'error': error['error'] ?? 'Failed to delete receipt'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Get dashboard statistics
  static Future<Map<String, dynamic>> getDashboardStats() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/dashboard-stats'),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return {'success': true, 'stats': data};
      } else {
        final error = json.decode(response.body);
        return {'success': false, 'error': error['error'] ?? 'Failed to fetch dashboard stats'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Get unreviewed receipts
  static Future<Map<String, dynamic>> getUnreviewedReceipts() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/receipts/unreviewed'),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return {'success': true, 'receipts': data['receipts']};
      } else {
        final error = json.decode(response.body);
        return {'success': false, 'error': error['error'] ?? 'Failed to fetch unreviewed receipts'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Add manual expense
  static Future<Map<String, dynamic>> addManualExpense(Map<String, dynamic> expenseData) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/expense/manual'),
        headers: _headers,
        body: json.encode(expenseData),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return {'success': true, 'expense_id': data['expense_id']};
      } else {
        final error = json.decode(response.body);
        return {'success': false, 'error': error['error'] ?? 'Failed to add manual expense'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Save receipt image and metadata (for new upload flow)
  static Future<Map<String, dynamic>> saveReceiptImage({
    File? imageFile,
    Uint8List? webImageBytes,
  }) async {
    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/save-receipt-image'),
      );
      
      // Add authorization header
      if (_authToken != null) {
        request.headers['Authorization'] = 'Bearer $_authToken';
      }
      
      // Add image file
      if (kIsWeb && webImageBytes != null) {
        request.files.add(
          http.MultipartFile.fromBytes(
            'image',
            webImageBytes,
            filename: 'receipt.jpg',
          ),
        );
      } else if (imageFile != null) {
        request.files.add(
          await http.MultipartFile.fromPath(
            'image',
            imageFile.path,
          ),
        );
      } else {
        return {'success': false, 'error': 'No image provided'};
      }
      
      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return {'success': true, 'receipt_id': data['receipt_id']};
      } else {
        final error = json.decode(response.body);
        return {'success': false, 'error': error['error'] ?? 'Failed to save receipt image'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Get BLS categories
  static Future<Map<String, dynamic>> getBLSCategories() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/categories'),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return {'success': true, 'categories': data['categories']};
      } else {
        final error = json.decode(response.body);
        return {'success': false, 'error': error['error'] ?? 'Failed to fetch categories'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Get BLS category hierarchy
  static Future<Map<String, dynamic>> getBLSCategoryHierarchy() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/categories/hierarchy'),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return {'success': true, 'hierarchy': data['hierarchy']};
      } else {
        final error = json.decode(response.body);
        return {'success': false, 'error': error['error'] ?? 'Failed to fetch category hierarchy'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }
} 