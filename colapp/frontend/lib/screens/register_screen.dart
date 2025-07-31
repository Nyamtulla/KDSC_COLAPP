import 'package:flutter/material.dart';
import 'package:dropdown_search/dropdown_search.dart';
import 'login_screen.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/api_service.dart';
import '../utils/kansas_data.dart';

// === Theme Colors ===
final primaryBlue = Color(0xFF0051BA);
final accentYellow = Color(0xFFEC944A);
const List<String> sexes = [
  'Male', 'Female', 'Other', 'Prefer not to say'
];

class RegisterScreen extends StatefulWidget {
  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final TextEditingController firstNameController = TextEditingController();
  final TextEditingController lastNameController = TextEditingController();
  final TextEditingController emailController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();
  final TextEditingController rePasswordController = TextEditingController();
  final TextEditingController ageController = TextEditingController();
  final TextEditingController zipController = TextEditingController();

  String? selectedSex;
  String? selectedCounty;
  String? selectedCity;

  bool isPasswordVisible = false;
  bool isRePasswordVisible = false;
  bool _isLoading = false;

  final _formKey = GlobalKey<FormState>();

  Future<void> _tryRegister() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final userData = {
        'email': emailController.text.trim(),
        'password': passwordController.text,
        'first_name': firstNameController.text.trim(),
        'last_name': lastNameController.text.trim(),
        'age': int.parse(ageController.text),
        'sex': selectedSex!,
        'city': selectedCity!,
        'county': selectedCounty!,
        'state': 'Kansas',
        'zip_code': zipController.text.trim(),
      };

      final result = await ApiService.register(userData);

      if (result['success']) {
        _showSuccessSnackBar(result['message']);
        // Navigate to login screen after successful registration
        Future.delayed(Duration(seconds: 2), () {
          Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => LoginScreen()));
        });
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

  void _showSuccessSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: primaryBlue,
        duration: Duration(seconds: 3),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    double screenWidth = MediaQuery.of(context).size.width;
    double formMaxWidth = screenWidth < 600 ? screenWidth * 0.97 : 430;

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
            // Top curved gradient
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
            SizedBox(height: 18),
            Text("Create Account",
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.w600, color: primaryBlue)),
            SizedBox(height: 10),
            Center(
              child: ConstrainedBox(
                constraints: BoxConstraints(maxWidth: formMaxWidth),
                child: Card(
                  elevation: 2,
                  margin: EdgeInsets.symmetric(vertical: 18, horizontal: 10),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
                  child: Padding(
                    padding: const EdgeInsets.all(14.0),
                    child: Form(
                      key: _formKey,
                      child: Column(
                        children: [
                          // First and Last Name
                          Row(
                            children: [
                              Expanded(
                                child: TextFormField(
                                  controller: firstNameController,
                                  decoration: InputDecoration(
                                    labelText: "First Name",
                                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                                  ),
                                  validator: (v) => v == null || v.isEmpty ? 'First name required' : null,
                                ),
                              ),
                              SizedBox(width: 10),
                              Expanded(
                                child: TextFormField(
                                  controller: lastNameController,
                                  decoration: InputDecoration(
                                    labelText: "Last Name",
                                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                                  ),
                                  validator: (v) => v == null || v.isEmpty ? 'Last name required' : null,
                                ),
                              ),
                            ],
                          ),
                          SizedBox(height: 10),

                          // Email (User ID)
                          TextFormField(
                            controller: emailController,
                            keyboardType: TextInputType.emailAddress,
                            decoration: InputDecoration(
                              labelText: "Email (User ID)",
                              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                            ),
                            validator: (v) =>
                                v == null || v.isEmpty
                                    ? 'Email required'
                                    : !RegExp(r"^[\w\.\-]+@[\w\-]+\.[a-zA-Z]+").hasMatch(v)
                                    ? 'Enter valid email'
                                    : null,
                          ),
                          SizedBox(height: 10),

                          // Password
                          TextFormField(
                            controller: passwordController,
                            obscureText: !isPasswordVisible,
                            decoration: InputDecoration(
                              labelText: "Password (Min 6 characters)",
                              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                              suffixIcon: IconButton(
                                icon: Icon(
                                  isPasswordVisible ? Icons.visibility : Icons.visibility_off,
                                ),
                                onPressed: () => setState(() => isPasswordVisible = !isPasswordVisible),
                              ),
                            ),
                            validator: (v) =>
                                v == null || v.length < 6 ? 'Min 6 chars required' : null,
                          ),
                          SizedBox(height: 10),

                          // Re-enter Password
                          TextFormField(
                            controller: rePasswordController,
                            obscureText: !isRePasswordVisible,
                            decoration: InputDecoration(
                              labelText: "Re-enter Password",
                              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                              suffixIcon: IconButton(
                                icon: Icon(
                                  isRePasswordVisible ? Icons.visibility : Icons.visibility_off,
                                ),
                                onPressed: () => setState(() => isRePasswordVisible = !isRePasswordVisible),
                              ),
                            ),
                            validator: (v) =>
                                v != passwordController.text ? 'Passwords do not match' : null,
                          ),
                          SizedBox(height: 10),

                          // Age
                          TextFormField(
                            controller: ageController,
                            keyboardType: TextInputType.number,
                            decoration: InputDecoration(
                              labelText: "Age",
                              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                            ),
                            validator: (v) =>
                                v == null || v.isEmpty
                                    ? 'Age required'
                                    : int.tryParse(v) == null
                                    ? 'Enter a valid number'
                                    : null,
                          ),
                          SizedBox(height: 10),

                          // Sex Dropdown
                          DropdownButtonFormField<String>(
                            value: selectedSex,
                            items: sexes
                                .map((sex) => DropdownMenuItem(
                              value: sex,
                              child: Text(sex),
                            ))
                                .toList(),
                            decoration: InputDecoration(
                              labelText: "Gender",
                              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                            ),
                            onChanged: (v) => setState(() => selectedSex = v),
                            validator: (v) => v == null || v.isEmpty ? 'Select Gender' : null,
                          ),
                          SizedBox(height: 10),

                          // State: Read-only, always "Kansas"
                          TextFormField(
                            initialValue: "Kansas",
                            readOnly: true,
                            decoration: InputDecoration(
                              labelText: "State",
                              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                            ),
                          ),
                          SizedBox(height: 10),

                          // County: Searchable Dropdown
                          DropdownSearch<String>(
                            items: kansasCounties,
                            selectedItem: selectedCounty,
                            dropdownDecoratorProps: DropDownDecoratorProps(
                              dropdownSearchDecoration: InputDecoration(
                                labelText: "County",
                                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                              ),
                            ),
                            onChanged: (county) {
                              setState(() {
                                selectedCounty = county;
                                selectedCity = null;
                              });
                            },
                            validator: (v) => v == null || v.isEmpty ? 'Select county' : null,
                            popupProps: PopupProps.menu(
                              showSearchBox: true,
                              searchFieldProps: TextFieldProps(
                                decoration: InputDecoration(
                                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                                  labelText: 'Search County',
                                ),
                              ),
                            ),
                          ),
                          SizedBox(height: 10),

                          // City: Searchable Dropdown, only show if county selected
                          if (selectedCounty != null && selectedCounty!.isNotEmpty)
                            DropdownSearch<String>(
                              items: kansasCountiesAndCities[selectedCounty] ?? [],
                              selectedItem: selectedCity,
                              dropdownDecoratorProps: DropDownDecoratorProps(
                                dropdownSearchDecoration: InputDecoration(
                                  labelText: "City",
                                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                                ),
                              ),
                              onChanged: (city) {
                                setState(() {
                                  selectedCity = city;
                                });
                              },
                              validator: (v) => v == null || v.isEmpty ? 'Select city' : null,
                              popupProps: PopupProps.menu(
                                showSearchBox: true,
                                searchFieldProps: TextFieldProps(
                                  decoration: InputDecoration(
                                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                                    labelText: 'Search City',
                                  ),
                                ),
                              ),
                            ),
                          if (selectedCounty != null && selectedCounty!.isNotEmpty)
                            SizedBox(height: 10),

                          // ZIP Code
                          TextFormField(
                            controller: zipController,
                            keyboardType: TextInputType.number,
                            decoration: InputDecoration(
                              labelText: "ZIP Code",
                              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                            ),
                            validator: (v) =>
                                v == null || v.isEmpty
                                    ? 'ZIP Code required'
                                    : int.tryParse(v) == null
                                    ? 'Enter valid ZIP code'
                                    : null,
                          ),
                          SizedBox(height: 14),

                          // Register Button, also responsive
                          Center(
                            child: ConstrainedBox(
                              constraints: BoxConstraints(maxWidth: 280),
                              child: SizedBox(
                                width: double.infinity,
                                child: ElevatedButton(
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: primaryBlue,
                                    foregroundColor: Colors.white,
                                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                                    padding: EdgeInsets.symmetric(vertical: 14),
                                  ),
                                  onPressed: _isLoading ? null : _tryRegister,
                                  child: _isLoading 
                                    ? SizedBox(
                                        height: 20,
                                        width: 20,
                                        child: CircularProgressIndicator(
                                          strokeWidth: 2,
                                          valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                                        ),
                                      )
                                    : Text("Create Account", style: TextStyle(fontSize: 16)),
                                ),
                              ),
                            ),
                          ),
                          SizedBox(height: 10),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text("Already have an Account? "),
                              GestureDetector(
                                onTap: () => Navigator.pushReplacement(
                                    context, MaterialPageRoute(builder: (_) => LoginScreen())),
                                child: Text(
                                  "Log in",
                                  style: TextStyle(
                                    color: accentYellow,
                                    fontWeight: FontWeight.w600,
                                    decoration: TextDecoration.underline,
                                  ),
                                ),
                              )
                            ],
                          ),
                        ],
                      ),
                    ),
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
