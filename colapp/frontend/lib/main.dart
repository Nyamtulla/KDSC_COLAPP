import 'package:flutter/material.dart';
import 'screens/login_screen.dart';

void main() => runApp(MyApp());

final primaryBlue = Color(0xFF0051BA);
final accentYellow = Color(0xFFEC944A);
final backgroundLight = Color(0xFFEAF3F9);

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Grocery OCR',
      theme: ThemeData(
        primaryColor: primaryBlue,
        colorScheme: ColorScheme.light(
          primary: primaryBlue,
          secondary: accentYellow,
        ),
        scaffoldBackgroundColor: backgroundLight,
        textTheme: TextTheme(
          titleLarge: TextStyle(fontFamily: 'Pacifico', fontSize: 24, color: primaryBlue),
          bodyLarge: TextStyle(fontFamily: 'Roboto', fontSize: 16, color: Colors.black87),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          contentPadding: EdgeInsets.all(16),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide(color: primaryBlue),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide(color: accentYellow),
          ),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: primaryBlue,
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            padding: EdgeInsets.symmetric(vertical: 14),
          ),
        ),
      ),
      home: LoginScreen(),
    );
  }
}
