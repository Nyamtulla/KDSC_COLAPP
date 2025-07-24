import 'package:flutter/material.dart';
import 'dashboard_screen.dart';
import 'home_screen.dart';
import 'add_expense_screen.dart';
import 'edit_receipt_screen.dart';
import '../services/api_service.dart';
import 'package:google_fonts/google_fonts.dart';

final primaryBlue = Color(0xFF0051BA);
final accentYellow = Color(0xFFEC944A);
final backgroundLight = Color(0xFFEAF3F9);

class ReviewReceiptsScreen extends StatefulWidget {
  @override
  _ReviewReceiptsScreenState createState() => _ReviewReceiptsScreenState();
}

class _ReviewReceiptsScreenState extends State<ReviewReceiptsScreen> {
  bool _isLoading = true;
  String? _error;
  List<Map<String, dynamic>> _receipts = [];

  @override
  void initState() {
    super.initState();
    _loadUnreviewedReceipts();
  }

  Future<void> _loadUnreviewedReceipts() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final result = await ApiService.getUnreviewedReceipts();
      if (result['success']) {
        setState(() {
          _receipts = List<Map<String, dynamic>>.from(result['receipts'] ?? []);
        });
      } else {
        setState(() {
          _error = result['error'] ?? 'Failed to load receipts';
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Error loading receipts: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _editReceipt(Map<String, dynamic> receipt) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => EditReceiptScreen(
          receiptId: receipt['id'],
          initialData: {
            'store_name': receipt['store_name'] ?? 'Unknown Store',
            'total_amount': receipt['total_amount'] ?? 0.0,
            'items': receipt['items'] ?? [],
            'raw_text': receipt['raw_text'] ?? '',
          },
        ),
      ),
    ).then((_) {
      // Refresh the list after editing
      _loadUnreviewedReceipts();
    });
  }

  Widget _buildReceiptCard(Map<String, dynamic> receipt) {
    return Card(
      margin: EdgeInsets.symmetric(vertical: 8, horizontal: 16),
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Receipt Image Preview
            if (receipt['image_url'] != null)
              Container(
                height: 120,
                width: double.infinity,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.grey.shade300),
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image.network(
                    receipt['image_url'],
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) {
                      return Container(
                        color: Colors.grey.shade200,
                        child: Icon(
                          Icons.image_not_supported,
                          size: 40,
                          color: Colors.grey.shade400,
                        ),
                      );
                    },
                  ),
                ),
              ),
            
            SizedBox(height: 12),
            
            // Receipt Details
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        receipt['store_name'] ?? 'Unknown Store',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: primaryBlue,
                        ),
                      ),
                      SizedBox(height: 4),
                      Text(
                        'Date: ${receipt['receipt_date'] ?? 'Unknown'}',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      '\$${(receipt['total_amount'] ?? 0.0).toStringAsFixed(2)}',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: accentYellow,
                      ),
                    ),
                    Text(
                      '${receipt['items']?.length ?? 0} items',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ],
            ),
            
            SizedBox(height: 12),
            
            // Edit Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () => _editReceipt(receipt),
                icon: Icon(Icons.edit),
                label: Text('Edit Receipt'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: primaryBlue,
                  foregroundColor: Colors.white,
                  padding: EdgeInsets.symmetric(vertical: 12),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
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
          'Review Receipts',
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
            onPressed: _loadUnreviewedReceipts,
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: _isLoading
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(color: primaryBlue),
                  SizedBox(height: 16),
                  Text('Loading receipts...'),
                ],
              ),
            )
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.error_outline,
                        size: 64,
                        color: Colors.red,
                      ),
                      SizedBox(height: 16),
                      Text(
                        _error!,
                        style: TextStyle(color: Colors.red),
                        textAlign: TextAlign.center,
                      ),
                      SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: _loadUnreviewedReceipts,
                        child: Text('Retry'),
                      ),
                    ],
                  ),
                )
              : _receipts.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.receipt_long,
                            size: 64,
                            color: Colors.grey[400],
                          ),
                          SizedBox(height: 16),
                          Text(
                            'No receipts to review',
                            style: TextStyle(
                              fontSize: 18,
                              color: Colors.grey[600],
                            ),
                          ),
                          SizedBox(height: 8),
                          Text(
                            'Upload receipts to see them here',
                            style: TextStyle(
                              color: Colors.grey[500],
                            ),
                          ),
                        ],
                      ),
                    )
                  : RefreshIndicator(
                      onRefresh: _loadUnreviewedReceipts,
                      child: ListView.builder(
                        padding: EdgeInsets.symmetric(vertical: 8),
                        itemCount: _receipts.length,
                        itemBuilder: (context, index) {
                          return _buildReceiptCard(_receipts[index]);
                        },
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
        currentIndex: 2,
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
            // Already on Review Receipts
          } else if (index == 3) {
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (_) => AddExpenseScreen()),
            );
          }
        },
      ),
    );
  }
} 