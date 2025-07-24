import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:image_cropper/image_cropper.dart';
import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/foundation.dart' show kIsWeb;
import '../services/ocr_service.dart';
import '../services/api_service.dart';
import 'edit_receipt_screen.dart';
import 'dashboard_screen.dart';
import 'package:google_fonts/google_fonts.dart';
import 'review_receipts_screen.dart';
import 'add_expense_screen.dart';

// Import theme colors from main.dart
final primaryBlue = Color(0xFF0051BA);
final accentYellow = Color(0xFFEC944A);
final backgroundLight = Color(0xFFEAF3F9);

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ImagePicker _picker = ImagePicker();
  File? _selectedImage;
  Uint8List? _webImageBytes;
  bool _isProcessing = false;
  String _processingStatus = '';
  Map<String, dynamic>? _extractedData;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: backgroundLight,
      appBar: AppBar(
        toolbarHeight: 68,
        flexibleSpace: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [primaryBlue, accentYellow],
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
            ),
          ),
        ),
        title: Text(
          'Cost of Living',
          style: GoogleFonts.satisfy(
            fontSize: 28,
            color: Colors.white,
            fontWeight: FontWeight.w400,
          ),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: () {
              setState(() {
                _selectedImage = null;
                _webImageBytes = null;
                _extractedData = null;
              });
            },
            tooltip: 'Clear',
          ),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        backgroundColor: Colors.white,
        selectedItemColor: primaryBlue,
        unselectedItemColor: Colors.grey[600],
        selectedLabelStyle: TextStyle(fontWeight: FontWeight.w600),
        unselectedLabelStyle: TextStyle(fontWeight: FontWeight.w500),
        items: [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.add_a_photo),
            label: 'Upload Receipt',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.receipt_long),
            label: 'Review Receipts',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.edit),
            label: 'Add Expense',
          ),
        ],
        currentIndex: 1, // Upload Receipt is selected
        onTap: (index) {
          if (index == 0) {
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (_) => DashboardScreen()),
            );
          } else if (index == 1) {
            // Already on Upload Receipt (HomeScreen)
          } else if (index == 2) {
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (_) => ReviewReceiptsScreen()),
            );
          } else if (index == 3) {
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (_) => AddExpenseScreen()),
            );
          }
        },
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Header
            Container(
              padding: EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [backgroundLight, primaryBlue.withOpacity(0.1)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: primaryBlue.withOpacity(0.2)),
              ),
              child: Column(
                children: [
                  Icon(
                    Icons.receipt_long,
                    size: 48,
                    color: primaryBlue,
                  ),
                  SizedBox(height: 12),
                  Text(
                    'Upload Receipt',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: primaryBlue,
                    ),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Take a photo or select an image to extract receipt data',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 16,
                      color: primaryBlue.withOpacity(0.8),
                    ),
                  ),
                ],
              ),
            ),
            
            SizedBox(height: 24),
            
            // Image Selection Buttons
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _isProcessing ? null : _pickImageFromCamera,
                    icon: Icon(Icons.camera_alt),
                    label: Text('Camera'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: primaryBlue,
                      foregroundColor: Colors.white,
                      padding: EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
                SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _isProcessing ? null : _pickImageFromGallery,
                    icon: Icon(Icons.photo_library),
                    label: Text('Gallery'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: accentYellow,
                      foregroundColor: Colors.white,
                      padding: EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
              ],
            ),
            
            SizedBox(height: 24),
            
            // Selected Image Display
            if (_selectedImage != null || _webImageBytes != null) ...[
              Container(
                height: 200,
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey.shade300),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: kIsWeb && _webImageBytes != null
                      ? Image.memory(
                          _webImageBytes!,
                          fit: BoxFit.cover,
                          width: double.infinity,
                        )
                      : _selectedImage != null
                          ? Image.file(
                              _selectedImage!,
                              fit: BoxFit.cover,
                              width: double.infinity,
                            )
                          : Container(),
                ),
              ),
              SizedBox(height: 16),
            ],
            
            // Processing Status
            if (_isProcessing) ...[
              Container(
                padding: EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: backgroundLight,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: primaryBlue.withOpacity(0.3)),
                ),
                child: Column(
                  children: [
                    CircularProgressIndicator(
                      valueColor: AlwaysStoppedAnimation<Color>(primaryBlue),
                    ),
                    SizedBox(height: 12),
                    Text(
                      _processingStatus,
                      style: TextStyle(
                        fontSize: 16,
                        color: primaryBlue,
                      ),
                    ),
                  ],
                ),
              ),
              SizedBox(height: 16),
            ],
            
            // Upload and Process Button
            ElevatedButton.icon(
              onPressed: (_selectedImage != null || _webImageBytes != null) && !_isProcessing
                  ? _uploadAndProcess
                  : null,
              icon: Icon(Icons.upload),
              label: Text('Upload and Process'),
              style: ElevatedButton.styleFrom(
                backgroundColor: primaryBlue,
                foregroundColor: Colors.white,
                padding: EdgeInsets.symmetric(vertical: 16),
                textStyle: TextStyle(fontSize: 18),
              ),
            ),
            
            SizedBox(height: 24),
            
            // Instructions
            Container(
              padding: EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: backgroundLight,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: primaryBlue.withOpacity(0.2)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'How it works:',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: primaryBlue,
                    ),
                  ),
                  SizedBox(height: 8),
                  _buildInstructionStep('1', 'Take a photo or select a receipt image.'),
                  _buildInstructionStep('2', 'The app uploads it for background processing (OCR + AI).'),
                  _buildInstructionStep('3', 'You review and edit the extracted data.'),
                  _buildInstructionStep('4', 'Save to track your spending and view analytics.'),
                ],
              ),
            ),
            
            // KSDS Logo at bottom
            SizedBox(height: 24),
            Center(
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: 16.0),
                child: Image.asset(
                  'assets/ksds_logo.jpeg',
                  height: 46,
                  fit: BoxFit.contain,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInstructionStep(String number, String text) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 24,
            height: 24,
            decoration: BoxDecoration(
              color: accentYellow,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Center(
              child: Text(
                number,
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
          SizedBox(width: 12),
          Expanded(
            child: Text(
              text,
              style: TextStyle(
                fontSize: 14,
                color: primaryBlue.withOpacity(0.8),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _pickImageFromCamera() async {
    try {
      final XFile? image = await _picker.pickImage(
        source: ImageSource.camera,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );
      
      if (image != null) {
        setState(() {
          if (kIsWeb) {
            // For web, we need to get bytes
            image.readAsBytes().then((bytes) {
              setState(() {
                _webImageBytes = bytes;
                _selectedImage = null;
              });
            });
          } else {
            _selectedImage = File(image.path);
            _webImageBytes = null;
          }
        });
      }
    } catch (e) {
      _showErrorSnackBar('Error picking image: $e');
    }
  }

  Future<void> _pickImageFromGallery() async {
    try {
      final XFile? image = await _picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );
      
      if (image != null) {
        setState(() {
          if (kIsWeb) {
            // For web, we need to get bytes
            image.readAsBytes().then((bytes) {
              setState(() {
                _webImageBytes = bytes;
                _selectedImage = null;
              });
            });
          } else {
            _selectedImage = File(image.path);
            _webImageBytes = null;
          }
        });
      }
    } catch (e) {
      _showErrorSnackBar('Error picking image: $e');
    }
  }

  Future<void> _uploadAndProcess() async {
    if (_selectedImage == null && _webImageBytes == null) {
      _showErrorSnackBar('Please select an image first');
      return;
    }

    setState(() {
      _isProcessing = true;
      _processingStatus = 'Uploading image...';
    });

    try {
      // Use the async upload endpoint
      final result = await ApiService.uploadReceipt(
        imageFile: _selectedImage,
        webImageBytes: _webImageBytes,
        storeName: '', // Not needed for initial upload
        totalAmount: 0.0, // Not needed for initial upload
        items: [], // Not needed for initial upload
      );

      setState(() {
        _isProcessing = false;
        _processingStatus = '';
      });

      if (result['success']) {
        // Show a message that the receipt is being processed
        await showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: Text('Receipt Uploaded'),
            content: Text('Your receipt is being processed. It will appear in the review list once ready.'),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: Text('OK'),
              ),
            ],
          ),
        );
        // Optionally, navigate to the review receipts screen or refresh
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (_) => ReviewReceiptsScreen()),
        );
      } else {
        _showErrorSnackBar('Error: ${result['error']}');
      }
    } catch (e) {
      setState(() {
        _isProcessing = false;
        _processingStatus = '';
      });
      _showErrorSnackBar('Error: $e');
    }
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  void _showDebugInfo() {
    String debugInfo = '''
Debug Information:
- Platform: ${kIsWeb ? 'Web' : 'Mobile'}
- Selected Image: ${_selectedImage?.path ?? 'None'}
- Web Image Bytes: ${_webImageBytes != null ? '${_webImageBytes!.length} bytes' : 'None'}
- Is Processing: $_isProcessing
- Processing Status: $_processingStatus
- Extracted Data: ${_extractedData != null ? 'Available' : 'None'}
''';

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Debug Information'),
        content: SingleChildScrollView(
          child: Text(debugInfo),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Close'),
          ),
        ],
      ),
    );
  }
}

