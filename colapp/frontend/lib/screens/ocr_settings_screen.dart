import 'package:flutter/material.dart';
import '../services/ocr_service.dart';

class OcrSettingsScreen extends StatefulWidget {
  @override
  _OcrSettingsScreenState createState() => _OcrSettingsScreenState();
}

class _OcrSettingsScreenState extends State<OcrSettingsScreen> {
  String selectedMethod = 'auto';
  final primaryBlue = Color(0xFF0051BA);
  final accentYellow = Color(0xFFEC944A);

  @override
  Widget build(BuildContext context) {
    final methods = OcrService.getAvailableParsingMethods();
    
    return Scaffold(
      appBar: AppBar(
        title: Text('OCR Settings', style: TextStyle(color: Colors.white)),
        backgroundColor: primaryBlue,
        iconTheme: IconThemeData(color: Colors.white),
      ),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Card(
              elevation: 4,
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Parsing Method',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: primaryBlue,
                      ),
                    ),
                    SizedBox(height: 12),
                    Text(
                      'Choose how your receipts should be parsed. Machine learning methods provide better accuracy but may require API keys.',
                      style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                    ),
                    SizedBox(height: 16),
                    ...methods.map((method) => _buildMethodOption(method)).toList(),
                  ],
                ),
              ),
            ),
            SizedBox(height: 20),
            Card(
              elevation: 4,
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'API Configuration',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: primaryBlue,
                      ),
                    ),
                    SizedBox(height: 12),
                    _buildApiInfo('Google Cloud Vision', 'Requires Google Cloud API key'),
                    _buildApiInfo('OpenAI GPT-4 Vision', 'Requires OpenAI API key'),
                    _buildApiInfo('Azure Form Recognizer', 'Requires Azure subscription'),
                    _buildApiInfo('Custom NLP Model', 'Requires trained models in models/ folder'),
                    SizedBox(height: 12),
                    Text(
                      'Configure API keys in your backend .env file to enable ML-based parsing.',
                      style: TextStyle(fontSize: 12, color: Colors.grey[500]),
                    ),
                  ],
                ),
              ),
            ),
            SizedBox(height: 20),
            Card(
              elevation: 4,
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Method Comparison',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: primaryBlue,
                      ),
                    ),
                    SizedBox(height: 12),
                    _buildComparisonRow('Heuristic', 'Fast', 'Basic', 'Free'),
                    _buildComparisonRow('Google Vision', 'Very Good', 'Advanced', 'Paid'),
                    _buildComparisonRow('OpenAI Vision', 'Excellent', 'Slow', 'Paid'),
                    _buildComparisonRow('Azure Form', 'Excellent', 'Medium', 'Paid'),
                    _buildComparisonRow('Custom NLP', 'Very Good', 'Fast', 'Free'),
                    _buildComparisonRow('Hybrid', 'Best', 'Slow', 'Paid'),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMethodOption(Map<String, String> method) {
    final isSelected = selectedMethod == method['value'];
    
    return Container(
      margin: EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        border: Border.all(
          color: isSelected ? primaryBlue : Colors.grey[300]!,
          width: isSelected ? 2 : 1,
        ),
        borderRadius: BorderRadius.circular(8),
        color: isSelected ? primaryBlue.withOpacity(0.1) : Colors.white,
      ),
      child: RadioListTile<String>(
        value: method['value']!,
        groupValue: selectedMethod,
        onChanged: (value) {
          setState(() {
            selectedMethod = value!;
          });
        },
        title: Text(
          method['label']!,
          style: TextStyle(
            fontWeight: FontWeight.w600,
            color: isSelected ? primaryBlue : Colors.black87,
          ),
        ),
        subtitle: Text(
          method['description']!,
          style: TextStyle(fontSize: 12, color: Colors.grey[600]),
        ),
        activeColor: primaryBlue,
        contentPadding: EdgeInsets.symmetric(horizontal: 8),
      ),
    );
  }

  Widget _buildApiInfo(String name, String description) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(Icons.info_outline, size: 16, color: Colors.grey[600]),
          SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  name,
                  style: TextStyle(fontWeight: FontWeight.w600),
                ),
                Text(
                  description,
                  style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildComparisonRow(String method, String accuracy, String features, String cost) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Expanded(
            flex: 2,
            child: Text(
              method,
              style: TextStyle(fontWeight: FontWeight.w600),
            ),
          ),
          Expanded(
            child: Text(
              accuracy,
              style: TextStyle(fontSize: 12, color: Colors.grey[600]),
            ),
          ),
          Expanded(
            child: Text(
              features,
              style: TextStyle(fontSize: 12, color: Colors.grey[600]),
            ),
          ),
          Expanded(
            child: Text(
              cost,
              style: TextStyle(fontSize: 12, color: Colors.grey[600]),
            ),
          ),
        ],
      ),
    );
  }
} 