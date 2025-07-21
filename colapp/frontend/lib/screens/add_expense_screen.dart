import 'package:flutter/material.dart';
import 'dashboard_screen.dart';
import 'home_screen.dart';
import 'review_receipts_screen.dart';
import 'edit_receipt_screen.dart';
import '../services/api_service.dart';
import 'package:google_fonts/google_fonts.dart';

final primaryBlue = Color(0xFF0051BA);
final accentYellow = Color(0xFFEC944A);
final backgroundLight = Color(0xFFEAF3F9);

class AddExpenseScreen extends StatefulWidget {
  @override
  _AddExpenseScreenState createState() => _AddExpenseScreenState();
}

class _AddExpenseScreenState extends State<AddExpenseScreen> {
  final TextEditingController _storeController = TextEditingController();
  final TextEditingController _totalController = TextEditingController();
  List<Map<String, dynamic>> _items = [];
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    // Add one empty item by default
    _items.add({
      'product_name': '',
      'price': 0.0,
      'category': 'Other',
      'quantity': 1.0,
      'unit_price': 0.0,
      'total_price': 0.0,
    });
  }

  @override
  void dispose() {
    _storeController.dispose();
    _totalController.dispose();
    super.dispose();
  }

  void _addItem() {
    setState(() {
      _items.add({
        'product_name': '',
        'price': 0.0,
        'category': 'Other',
        'quantity': 1.0,
        'unit_price': 0.0,
        'total_price': 0.0,
      });
    });
  }

  void _removeItem(int index) {
    if (_items.length > 1) {
      setState(() {
        _items.removeAt(index);
      });
    }
  }

  void _updateItem(int index, String field, dynamic value) {
    setState(() {
      _items[index][field] = value;
      
      // Auto-calculate total price for the item
      if (field == 'quantity' || field == 'unit_price') {
        double quantity = _items[index]['quantity'] is String 
            ? double.tryParse(_items[index]['quantity']) ?? 1.0 
            : _items[index]['quantity'];
        double unitPrice = _items[index]['unit_price'] is String 
            ? double.tryParse(_items[index]['unit_price']) ?? 0.0 
            : _items[index]['unit_price'];
        _items[index]['total_price'] = quantity * unitPrice;
        _items[index]['price'] = _items[index]['total_price'];
      }
    });
  }

  Future<void> _saveExpense() async {
    if (_storeController.text.trim().isEmpty) {
      _showErrorSnackBar('Please enter a store name');
      return;
    }

    if (_totalController.text.trim().isEmpty) {
      _showErrorSnackBar('Please enter a total amount');
      return;
    }

    double? totalAmount = double.tryParse(_totalController.text);
    if (totalAmount == null || totalAmount <= 0) {
      _showErrorSnackBar('Please enter a valid total amount');
      return;
    }

    setState(() {
      _isSaving = true;
    });

    try {
      final expenseData = {
        'store_name': _storeController.text.trim(),
        'total_amount': totalAmount,
        'items': _items,
        'is_manual': true,
      };

      final result = await ApiService.addManualExpense(expenseData);

      if (result['success']) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Expense added successfully!'),
            backgroundColor: primaryBlue,
            duration: Duration(seconds: 3),
          ),
        );
        
        // Clear the form
        _storeController.clear();
        _totalController.clear();
        setState(() {
          _items = [{
            'product_name': '',
            'price': 0.0,
            'category': 'Other',
            'quantity': 1.0,
            'unit_price': 0.0,
            'total_price': 0.0,
          }];
        });
      } else {
        _showErrorSnackBar(result['error'] ?? 'Failed to add expense');
      }
    } catch (e) {
      _showErrorSnackBar('An error occurred: $e');
    } finally {
      setState(() {
        _isSaving = false;
      });
    }
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
        duration: Duration(seconds: 3),
      ),
    );
  }

  Widget _buildItemCard(int index) {
    final item = _items[index];
    
    return Card(
      margin: EdgeInsets.symmetric(vertical: 8),
      elevation: 2,
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Item ${index + 1}',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                    color: primaryBlue,
                  ),
                ),
                if (_items.length > 1)
                  IconButton(
                    icon: Icon(Icons.delete, color: Colors.red),
                    onPressed: () => _removeItem(index),
                    tooltip: 'Remove item',
                  ),
              ],
            ),
            SizedBox(height: 12),
            
            // Product Name
            TextField(
              decoration: InputDecoration(
                labelText: 'Product Name',
                border: OutlineInputBorder(),
                hintText: 'Enter product name',
              ),
              onChanged: (value) => _updateItem(index, 'product_name', value),
            ),
            SizedBox(height: 12),
            
            // Category
            DropdownButtonFormField<String>(
              decoration: InputDecoration(
                labelText: 'Category',
                border: OutlineInputBorder(),
              ),
              value: item['category'],
              items: [
                'Dairy', 'Bakery', 'Produce', 'Meat', 'Beverages', 
                'Household', 'Frozen', 'Snacks', 'Pantry', 'Seafood', 
                'Personal Care', 'Health', 'Baby', 'Pet', 'Canned Goods', 
                'Condiments', 'Grains', 'Pasta', 'Cleaning', 'Paper Goods', 'Other'
              ].map((category) => DropdownMenuItem(
                value: category,
                child: Text(category),
              )).toList(),
              onChanged: (value) => _updateItem(index, 'category', value ?? 'Other'),
            ),
            SizedBox(height: 12),
            
            // Quantity and Unit Price Row
            Row(
              children: [
                Expanded(
                  child: TextField(
                    decoration: InputDecoration(
                      labelText: 'Quantity',
                      border: OutlineInputBorder(),
                      hintText: '1',
                    ),
                    keyboardType: TextInputType.numberWithOptions(decimal: true),
                    onChanged: (value) => _updateItem(index, 'quantity', value),
                  ),
                ),
                SizedBox(width: 12),
                Expanded(
                  child: TextField(
                    decoration: InputDecoration(
                      labelText: 'Unit Price (\$)',
                      border: OutlineInputBorder(),
                      hintText: '0.00',
                    ),
                    keyboardType: TextInputType.numberWithOptions(decimal: true),
                    onChanged: (value) => _updateItem(index, 'unit_price', value),
                  ),
                ),
              ],
            ),
            SizedBox(height: 12),
            
            // Total Price (read-only)
            Container(
              padding: EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey.shade100,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.grey.shade300),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Total Price:',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  Text(
                    '\$${item['total_price'].toStringAsFixed(2)}',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: primaryBlue,
                      fontSize: 16,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

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
          'Add Expense',
          style: GoogleFonts.satisfy(
            fontSize: 28,
            color: Colors.white,
            fontWeight: FontWeight.w400,
          ),
        ),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
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
                    Icons.edit_note,
                    size: 48,
                    color: primaryBlue,
                  ),
                  SizedBox(height: 12),
                  Text(
                    'Add Expense Manually',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: primaryBlue,
                    ),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Enter your expense details manually',
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
            
            // Store Name
            Text(
              "Store Name",
              style: TextStyle(fontWeight: FontWeight.w500, fontSize: 16),
            ),
            SizedBox(height: 8),
            TextField(
              controller: _storeController,
              decoration: InputDecoration(
                border: OutlineInputBorder(),
                hintText: 'Enter store name',
                prefixIcon: Icon(Icons.store),
              ),
            ),
            SizedBox(height: 20),
            
            // Total Amount
            Text(
              "Total Amount",
              style: TextStyle(fontWeight: FontWeight.w500, fontSize: 16),
            ),
            SizedBox(height: 8),
            TextField(
              controller: _totalController,
              keyboardType: TextInputType.numberWithOptions(decimal: true),
              decoration: InputDecoration(
                border: OutlineInputBorder(),
                hintText: '0.00',
                prefixText: '\$',
                prefixIcon: Icon(Icons.attach_money),
              ),
            ),
            SizedBox(height: 24),
            
            // Items Section
            Text(
              "Items",
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
            ),
            SizedBox(height: 16),
            // Items List
            ...List.generate(_items.length, (index) => _buildItemCard(index)),
            SizedBox(height: 12),
            Center(
              child: ElevatedButton.icon(
                icon: Icon(Icons.add),
                label: Text("Add Item"),
                onPressed: _addItem,
                style: ElevatedButton.styleFrom(
                  backgroundColor: accentYellow,
                  foregroundColor: Colors.white,
                ),
              ),
            ),
            
            SizedBox(height: 24),
            
            // Save Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _isSaving ? null : _saveExpense,
                icon: _isSaving 
                    ? SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                        ),
                      )
                    : Icon(Icons.save),
                label: Text(_isSaving ? 'Saving...' : 'Save Expense'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: primaryBlue,
                  foregroundColor: Colors.white,
                  padding: EdgeInsets.symmetric(vertical: 16),
                  textStyle: TextStyle(fontSize: 18),
                ),
              ),
            ),
            
            SizedBox(height: 24),
            
            // KSDS Logo
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
        currentIndex: 3,
        onTap: (index) {
          if (index == 0) {
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (_) => DashboardScreen()),
            );
          } else if (index == 1) {
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (_) => HomeScreen()),
            );
          } else if (index == 2) {
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (_) => ReviewReceiptsScreen()),
            );
          } else if (index == 3) {
            // Already on Add Expense
          }
        },
      ),
    );
  }
} 