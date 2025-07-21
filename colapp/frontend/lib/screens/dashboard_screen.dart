import 'package:flutter/material.dart';
import 'home_screen.dart';
import 'login_screen.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/api_service.dart';
import 'package:fl_chart/fl_chart.dart';
import 'review_receipts_screen.dart';
import 'add_expense_screen.dart';

// Theme colors
final primaryBlue = Color(0xFF0051BA);
final accentYellow = Color(0xFFEC944A);
final backgroundLight = Color(0xFFEAF3F9);

class DashboardScreen extends StatefulWidget {
  @override
  _DashboardScreenState createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  bool _isLoading = true;
  String? _error;
  Map<String, dynamic> _stats = {};
  List<Map<String, dynamic>> _receipts = [];

  @override
  void initState() {
    super.initState();
    _loadDashboardData();
  }

  Future<void> _loadDashboardData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final statsResult = await ApiService.getDashboardStats();
      final receiptsResult = await ApiService.getReceipts();
      if (statsResult['success'] && receiptsResult['success']) {
        setState(() {
          _stats = statsResult['stats'] ?? {};
          _receipts = List<Map<String, dynamic>>.from(receiptsResult['receipts'] ?? []);
        });
      } else {
        setState(() {
          _error = statsResult['error'] ?? receiptsResult['error'] ?? 'Failed to load data.';
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Error loading dashboard data: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _logout(BuildContext context) {
    Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => LoginScreen()));
  }

  Widget _buildStatCards() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        _buildStatCard('Total Spent', '\$${(_stats['total_spent'] ?? 0).toStringAsFixed(2)}', Icons.attach_money, Colors.green),
        _buildStatCard('Total Receipts', '${_stats['total_receipts'] ?? 0}', Icons.receipt_long, Colors.blue),
      ],
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 40, color: color),
            SizedBox(height: 12),
            Text(value, style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: primaryBlue)),
            SizedBox(height: 8),
            Text(title, style: TextStyle(fontSize: 14, color: Colors.grey[600]), textAlign: TextAlign.center),
          ],
        ),
      ),
    );
  }

  Widget _buildCategoryPieChart() {
    final categoryData = _stats['category_breakdown'] ?? {};
    if (categoryData.isEmpty) {
      return _emptyCard('No category data available');
    }
    final entries = (categoryData as Map<String, dynamic>)
        .entries
        .where((e) => e.value is num)
        .map((e) => MapEntry(e.key, (e.value as num).toDouble()))
        .toList();
    final total = entries.fold<double>(0, (sum, e) => sum + e.value);
    if (total == 0) {
      return _emptyCard('No category data available');
    }
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Spending by Category', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryBlue)),
            SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: PieChart(
                PieChartData(
                  sections: entries.asMap().entries.map((entry) {
                    final idx = entry.key;
                    final label = entry.value.key;
                    final value = entry.value.value;
                    final percent = (value / total * 100).toStringAsFixed(1);
                    return PieChartSectionData(
                      color: _pieColors[idx % _pieColors.length],
                      value: value,
                      title: '$label\n$percent%',
                      radius: 60,
                      titleStyle: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white),
                    );
                  }).toList(),
                  sectionsSpace: 2,
                  centerSpaceRadius: 32,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMonthlyBarChart() {
    final monthlyData = _stats['monthly_spending'] ?? {};
    if (monthlyData.isEmpty) {
      return _emptyCard('No monthly data available');
    }
    final entries = (monthlyData as Map<String, dynamic>)
        .entries
        .where((e) => e.value is num)
        .map((e) => MapEntry(e.key, (e.value as num).toDouble()))
        .toList()
      ..sort((a, b) => a.key.compareTo(b.key));
    if (entries.isEmpty) {
      return _emptyCard('No monthly data available');
    }
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Monthly Spending', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryBlue)),
            SizedBox(height: 16),
            SizedBox(
              height: 220,
              child: BarChart(
                BarChartData(
                  alignment: BarChartAlignment.spaceAround,
                  barTouchData: BarTouchData(enabled: true),
                  titlesData: FlTitlesData(
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(showTitles: true, reservedSize: 40),
                    ),
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        getTitlesWidget: (double value, TitleMeta meta) {
                          final idx = value.toInt();
                          if (idx < 0 || idx >= entries.length) return Container();
                          return SideTitleWidget(
                            axisSide: meta.axisSide,
                            child: Text(entries[idx].key, style: TextStyle(fontSize: 10)),
                          );
                        },
                        reservedSize: 40,
                      ),
                    ),
                    rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  ),
                  borderData: FlBorderData(show: false),
                  barGroups: List.generate(entries.length, (idx) {
                    return BarChartGroupData(
                      x: idx,
                      barRods: [
                        BarChartRodData(
                          toY: entries[idx].value,
                          color: accentYellow,
                          width: 18,
                          borderRadius: BorderRadius.circular(4),
                        ),
                      ],
                    );
                  }),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentReceipts() {
    if (_receipts.isEmpty) {
      return _emptyCard('No receipts available');
    }
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Recent Receipts', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryBlue)),
            SizedBox(height: 16),
            ..._receipts.take(5).map((receipt) => ListTile(
                  leading: CircleAvatar(
                    backgroundColor: accentYellow,
                    child: Icon(Icons.receipt, color: Colors.white),
                  ),
                  title: Text(receipt['store_name'] ?? 'Unknown Store', style: TextStyle(fontWeight: FontWeight.w500)),
                  subtitle: Text(receipt['receipt_date'] ?? ''),
                  trailing: Text(
                    '\$${(receipt['total_amount'] ?? 0).toStringAsFixed(2)}',
                    style: TextStyle(fontWeight: FontWeight.bold, color: primaryBlue),
                  ),
                )),
          ],
        ),
      ),
    );
  }

  Widget _emptyCard(String text) {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(20),
        child: Text(text),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: backgroundLight,
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
        currentIndex: 0, // Dashboard is selected
        onTap: (index) {
          if (index == 0) {
            // Already on Dashboard
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
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (_) => AddExpenseScreen()),
            );
          }
        },
      ),
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
        leading: GestureDetector(
          onTap: () {
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (_) => HomeScreen()),
            );
          },
          child: Padding(
            padding: const EdgeInsets.only(left: 4.0),
            child: Image.asset(
              'assets/kansas-commerce-logo.webp',
            ),
          ),
        ),
        title: Text(
          "Cost of Living",
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
            onPressed: _loadDashboardData,
            tooltip: 'Refresh',
          ),
          IconButton(
            icon: Icon(Icons.logout),
            onPressed: () => _logout(context),
            tooltip: 'Logout',
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
                  Text('Loading dashboard data...'),
                ],
              ),
            )
          : _error != null
              ? Center(child: Text(_error!, style: TextStyle(color: Colors.red)))
              : RefreshIndicator(
                  onRefresh: _loadDashboardData,
                  child: SingleChildScrollView(
                    padding: EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _buildStatCards(),
                        SizedBox(height: 24),
                        _buildCategoryPieChart(),
                        SizedBox(height: 24),
                        _buildMonthlyBarChart(),
                        SizedBox(height: 24),
                        _buildRecentReceipts(),
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
                ),
    );
  }
}

const List<Color> _pieColors = [
  Color(0xFF0051BA),
  Color(0xFFEC944A),
  Color(0xFF4CAF50),
  Color(0xFF9C27B0),
  Color(0xFFFFC107),
  Color(0xFF00BCD4),
  Color(0xFFE91E63),
  Color(0xFF607D8B),
];
