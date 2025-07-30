import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../widgets/hierarchical_category_picker.dart';

// Import theme colors from main.dart
final primaryBlue = Color(0xFF0051BA);
final accentYellow = Color(0xFFEC944A);
final backgroundLight = Color(0xFFEAF3F9);

// Models
class ReceiptItem {
  String productName;
  double price;
  String category;
  double quantity;
  double unitPrice;
  double totalPrice;
  ReceiptItem({
    required this.productName,
    required this.price,
    required this.category,
    required this.quantity,
    required this.unitPrice,
    required this.totalPrice,
  });

  factory ReceiptItem.fromJson(Map<String, dynamic> json) {
    return ReceiptItem(
      productName: json['product_name'] ?? json['name'] ?? '',
      price: (json['price'] ?? json['total_price'] ?? 0.0).toDouble(),
      category: json['category'] ?? 'Other',
      quantity: (json['quantity'] ?? 1.0).toDouble(),
      unitPrice: (json['unit_price'] ?? 0.0).toDouble(),
      totalPrice: (json['total_price'] ?? json['price'] ?? 0.0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
    'product_name': productName,
    'price': price,
    'category': category,
    'quantity': quantity,
    'unit_price': unitPrice,
    'total_price': totalPrice,
  };
}

// Categories will be loaded from BLS API

class EditReceiptScreen extends StatefulWidget {
  final int receiptId;
  final Map<String, dynamic> initialData;

  EditReceiptScreen({required this.receiptId, required this.initialData});

  @override
  _EditReceiptScreenState createState() => _EditReceiptScreenState();
}

class _EditReceiptScreenState extends State<EditReceiptScreen> {
  late TextEditingController storeController;
  late TextEditingController totalController;
  late List<ReceiptItem> items;
  bool _isSaving = false;
  Map<String, dynamic> _categoryHierarchy = {};
  bool _categoriesLoaded = false;

  @override
  void initState() {
    super.initState();
    
    // Initialize controllers with initial data
    storeController = TextEditingController(text: widget.initialData['store_name'] ?? '');
    totalController = TextEditingController(text: (widget.initialData['total_amount'] ?? 0.0).toStringAsFixed(2));
    
    // Initialize items from initial data
    items = [];
    if (widget.initialData['items'] != null) {
      for (var itemData in widget.initialData['items']) {
        items.add(ReceiptItem.fromJson(itemData));
      }
    }
    
    _loadCategories();
  }

  Future<void> _loadCategories() async {
    try {
      final result = await ApiService.getBLSCategoryHierarchy();
      if (result['success']) {
        setState(() {
          _categoryHierarchy = result['hierarchy'];
          _categoriesLoaded = true;
        });
      }
    } catch (e) {
      print('Error loading categories: $e');
    }
  }

  Future<void> saveAndReturn() async {
    setState(() {
      _isSaving = true;
    });

    try {
      // Convert items to API format
      final itemsData = items.map((item) => item.toJson()).toList();

      // Update receipt data
      final receiptData = {
        'store_name': storeController.text,
        'total_amount': double.tryParse(totalController.text) ?? 0,
        'items': itemsData,
      };

      final result = await ApiService.updateReceipt(widget.receiptId, receiptData);

      if (result['success']) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Receipt updated successfully!'),
            backgroundColor: primaryBlue,
            duration: Duration(seconds: 3),
          ),
        );
        Navigator.pop(context);
      } else {
        _showErrorSnackBar(result['error'] ?? 'Failed to update receipt');
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Edit Receipt Data'),
        backgroundColor: primaryBlue,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(
              maxWidth: 460,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Store Name
                Text("Store Name", style: TextStyle(fontWeight: FontWeight.w500, fontSize: 16)),
                SizedBox(height: 8),
                TextField(
                  controller: storeController,
                  decoration: InputDecoration(
                    border: OutlineInputBorder(),
                    hintText: 'Enter store name',
                  ),
                ),
                SizedBox(height: 20),
                
                // Total Amount
                Text("Total Amount", style: TextStyle(fontWeight: FontWeight.w500, fontSize: 16)),
                SizedBox(height: 8),
                TextField(
                  controller: totalController,
                  keyboardType: TextInputType.numberWithOptions(decimal: true),
                  decoration: InputDecoration(
                    border: OutlineInputBorder(),
                    hintText: '0.00',
                    prefixText: '\$',
                  ),
                ),
                SizedBox(height: 24),
                
                // Items Section
                Text("Items", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                SizedBox(height: 16),
                
                // Items List
                ...List.generate(items.length, (i) {
                  return Card(
                    margin: EdgeInsets.symmetric(vertical: 8),
                    elevation: 2,
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        children: [
                          Row(
                            children: [
                              Expanded(
                                child: TextFormField(
                                  initialValue: items[i].productName,
                                  decoration: InputDecoration(
                                    labelText: "Product Name",
                                    border: OutlineInputBorder(),
                                  ),
                                  onChanged: (v) => items[i].productName = v,
                                ),
                              ),
                              SizedBox(width: 12),
                              Expanded(
                                child: TextFormField(
                                  initialValue: items[i].price.toStringAsFixed(2),
                                  decoration: InputDecoration(
                                    labelText: "Price",
                                    border: OutlineInputBorder(),
                                    prefixText: '\$',
                                  ),
                                  keyboardType: TextInputType.numberWithOptions(decimal: true),
                                  onChanged: (v) => items[i].price = double.tryParse(v) ?? 0,
                                ),
                              ),
                            ],
                          ),
                          SizedBox(height: 12),
                          Row(
                            children: [
                              Expanded(
                                child: _categoriesLoaded
                                    ? HierarchicalCategoryPicker(
                                        selectedCategory: items[i].category,
                                        categoryHierarchy: _categoryHierarchy,
                                        onCategorySelected: (category) => setState(() => items[i].category = category),
                                      )
                                    : Container(
                                        padding: EdgeInsets.all(16),
                                        child: Center(child: CircularProgressIndicator()),
                                      ),
                              ),
                              SizedBox(width: 12),
                              Expanded(
                                child: TextFormField(
                                  initialValue: items[i].quantity.toString(),
                                  decoration: InputDecoration(
                                    labelText: "Quantity",
                                    border: OutlineInputBorder(),
                                  ),
                                  keyboardType: TextInputType.numberWithOptions(decimal: true),
                                  onChanged: (v) => items[i].quantity = double.tryParse(v) ?? 1.0,
                                ),
                              ),
                            ],
                          ),
                          SizedBox(height: 12),
                          Row(
                            children: [
                              Expanded(
                                child: TextFormField(
                                  initialValue: items[i].unitPrice.toStringAsFixed(2),
                                  decoration: InputDecoration(
                                    labelText: "Unit Price",
                                    border: OutlineInputBorder(),
                                    prefixText: '\$',
                                  ),
                                  keyboardType: TextInputType.numberWithOptions(decimal: true),
                                  onChanged: (v) => items[i].unitPrice = double.tryParse(v) ?? 0,
                                ),
                              ),
                              SizedBox(width: 12),
                              Expanded(
                                child: TextFormField(
                                  initialValue: items[i].totalPrice.toStringAsFixed(2),
                                  decoration: InputDecoration(
                                    labelText: "Total Price",
                                    border: OutlineInputBorder(),
                                    prefixText: '\$',
                                  ),
                                  keyboardType: TextInputType.numberWithOptions(decimal: true),
                                  onChanged: (v) => items[i].totalPrice = double.tryParse(v) ?? 0,
                                ),
                              ),
                              SizedBox(width: 12),
                              IconButton(
                                icon: Icon(Icons.delete, color: Colors.red),
                                onPressed: () => setState(() => items.removeAt(i)),
                                tooltip: 'Delete item',
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  );
                }),
                SizedBox(height: 12),
                Center(
                  child: ElevatedButton.icon(
                    icon: Icon(Icons.add),
                    label: Text("Add Item"),
                    onPressed: () => setState(() => items.add(
                        ReceiptItem(productName: "", price: 0, category: "Food and Beverages > Food at home > Other food at home", quantity: 1, unitPrice: 0, totalPrice: 0))),
                  ),
                ),
                
                SizedBox(height: 30),
                
                // Save Button
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: primaryBlue,
                      foregroundColor: Colors.white,
                      padding: EdgeInsets.symmetric(vertical: 16),
                      textStyle: TextStyle(fontSize: 18),
                    ),
                    child: _isSaving 
                      ? SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                          ),
                        )
                      : Text("Save Receipt"),
                    onPressed: _isSaving ? null : saveAndReturn,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
