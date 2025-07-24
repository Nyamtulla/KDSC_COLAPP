import 'package:flutter/material.dart';
import 'register_screen.dart';
import 'home_screen.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/api_service.dart';

// Import theme colors from main.dart
final primaryBlue = Color(0xFF0051BA);
final accentYellow = Color(0xFFEC944A);
final backgroundLight = Color(0xFFEAF3F9);

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _obscurePassword = true;
  bool _isLoading = false;

  Future<void> _login() async {
    if (_usernameController.text.isEmpty || _passwordController.text.isEmpty) {
      _showErrorSnackBar('Please fill in all fields');
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final result = await ApiService.login(
        _usernameController.text.trim(),
        _passwordController.text,
      );

      if (result['success']) {
        // Store the token (you might want to use shared_preferences or secure_storage)
        ApiService.setAuthToken(result['token']);
        Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => HomeScreen()));
      } else {
        _showErrorSnackBar(result['error']);
      }
    } catch (e) {
      _showErrorSnackBar('An error occurred: $e');
    } finally {
      setState(() {
        _isLoading = false;
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
    final theme = Theme.of(context);
    final double screenWidth = MediaQuery.of(context).size.width;
    final double formMaxWidth = screenWidth < 500 ? screenWidth * 0.95 : 360;

    return Scaffold(
      backgroundColor: theme.colorScheme.surface,
      bottomNavigationBar: Padding(
        padding: const EdgeInsets.only(bottom: 16.0, top: 6),
        child: Image.asset(
          'assets/ksds_logo.jpeg',
          height: 46,
          fit: BoxFit.contain,
        ),
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Gradient + curved header with primary logo on top left
            Stack(
              children: [
                Container(
                  height: 240,
                  width: double.infinity,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [primaryBlue, accentYellow],
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                    ),
                    borderRadius: BorderRadius.vertical(
                      bottom: Radius.circular(180),
                    ),
                  ),
                  child: Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Image.asset(
                          'assets/kansas-commerce-logo.webp', // Make sure asset path is correct!
                          height: 100,
                          fit: BoxFit.contain,
                        ),
                        SizedBox(height: 18),
                        Text(
                            "Cost of Living",
                            style: GoogleFonts.satisfy( // <- wavy, fun, script-like font
                              fontSize: 42,
                              color: Colors.white,
                              fontWeight: FontWeight.w400,
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
              ],
            ),

            SizedBox(height: 32),
            Text(
              "Welcome back",
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.w600, color: primaryBlue),
            ),
            Center(
              child: ConstrainedBox(
                constraints: BoxConstraints(maxWidth: formMaxWidth),
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
                  child: Column(
                    children: [
                      Align(
                        alignment: Alignment.centerLeft,
                        child: Text("User name (Email)", style: TextStyle(fontSize: 14, color: Colors.black54)),
                      ),
                      SizedBox(height: 4),
                      TextField(
                        controller: _usernameController,
                        decoration: InputDecoration(
                          hintText: "User name",
                        ),
                      ),
                      SizedBox(height: 18),
                      Align(
                        alignment: Alignment.centerLeft,
                        child: Text("Password", style: TextStyle(fontSize: 14, color: Colors.black54)),
                      ),
                      SizedBox(height: 4),
                      TextField(
                        controller: _passwordController,
                        obscureText: _obscurePassword,
                        decoration: InputDecoration(
                          hintText: "Password",
                          suffixIcon: IconButton(
                            icon: Icon(
                              _obscurePassword ? Icons.visibility_off : Icons.visibility,
                            ),
                            onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                          ),
                        ),
                      ),
                      SizedBox(height: 28),
                      Center(
                        child: ConstrainedBox(
                          constraints: BoxConstraints(
                            maxWidth: 300,
                          ),
                          child: SizedBox(
                            width: double.infinity,
                            child: ElevatedButton(
                              onPressed: _isLoading ? null : _login,
                              child: _isLoading
                                  ? SizedBox(
                                      height: 20,
                                      width: 20,
                                      child: CircularProgressIndicator(
                                        strokeWidth: 2,
                                        valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                                      ),
                                    )
                                  : Text("Log in", style: TextStyle(fontSize: 16)),
                            ),
                          ),
                        ),
                      ),
                      SizedBox(height: 16),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text("Don't have an Account? "),
                          GestureDetector(
                            child: Text(
                              "Create Account",
                              style: TextStyle(
                                color: accentYellow,
                                fontWeight: FontWeight.w600,
                                decoration: TextDecoration.underline,
                              ),
                            ),
                            onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => RegisterScreen())),
                          )
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
