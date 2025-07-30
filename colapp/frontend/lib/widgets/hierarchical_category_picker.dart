import 'package:flutter/material.dart';

class HierarchicalCategoryPicker extends StatefulWidget {
  final String? selectedCategory;
  final Function(String) onCategorySelected;
  final Map<String, dynamic> categoryHierarchy;

  const HierarchicalCategoryPicker({
    Key? key,
    required this.selectedCategory,
    required this.onCategorySelected,
    required this.categoryHierarchy,
  }) : super(key: key);

  @override
  State<HierarchicalCategoryPicker> createState() => _HierarchicalCategoryPickerState();
}

class _HierarchicalCategoryPickerState extends State<HierarchicalCategoryPicker> {
  String? selectedLevel1;
  String? selectedLevel2;
  String? selectedLevel3;

  @override
  void initState() {
    super.initState();
    _initializeSelection();
  }

  void _initializeSelection() {
    if (widget.selectedCategory != null) {
      final parts = widget.selectedCategory!.split(' > ');
      if (parts.isNotEmpty) {
        selectedLevel1 = parts[0];
        if (parts.length > 1) {
          selectedLevel2 = parts[1];
          if (parts.length > 2) {
            selectedLevel3 = parts[2];
          }
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Category',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 8),
        Container(
          decoration: BoxDecoration(
            border: Border.all(color: Colors.grey.shade300),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Column(
            children: [
              // Level 1 Selection
              _buildLevelSelector(
                'Level 1',
                selectedLevel1,
                widget.categoryHierarchy.keys.toList(),
                (value) {
                  setState(() {
                    selectedLevel1 = value;
                    selectedLevel2 = null;
                    selectedLevel3 = null;
                  });
                  _updateSelectedCategory();
                },
              ),
              
              // Level 2 Selection
              if (selectedLevel1 != null && 
                  widget.categoryHierarchy[selectedLevel1] is Map)
                _buildLevelSelector(
                  'Level 2',
                  selectedLevel2,
                  (widget.categoryHierarchy[selectedLevel1] as Map<String, dynamic>).keys.toList(),
                  (value) {
                    setState(() {
                      selectedLevel2 = value;
                      selectedLevel3 = null;
                    });
                    _updateSelectedCategory();
                  },
                ),
              
              // Level 3 Selection
              if (selectedLevel2 != null && 
                  widget.categoryHierarchy[selectedLevel1] is Map &&
                  (widget.categoryHierarchy[selectedLevel1] as Map<String, dynamic>)[selectedLevel2] is List)
                _buildLevelSelector(
                  'Level 3',
                  selectedLevel3,
                  (widget.categoryHierarchy[selectedLevel1] as Map<String, dynamic>)[selectedLevel2] as List<String>,
                  (value) {
                    setState(() {
                      selectedLevel3 = value;
                    });
                    _updateSelectedCategory();
                  },
                )
              else if (selectedLevel2 != null)
                // If no level 3, just show the selected level 2
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    border: Border(
                      bottom: BorderSide(color: Colors.grey.shade200),
                    ),
                  ),
                  child: Row(
                    children: [
                      SizedBox(
                        width: 80,
                        child: Text(
                          'Selected:',
                          style: const TextStyle(fontWeight: FontWeight.w500),
                        ),
                      ),
                      Expanded(
                        child: Text(
                          '$selectedLevel1 > $selectedLevel2',
                          style: const TextStyle(fontWeight: FontWeight.w500),
                        ),
                      ),
                    ],
                  ),
                ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildLevelSelector(
    String label,
    String? selectedValue,
    List<String> options,
    Function(String?) onChanged,
  ) {
    // Handle empty options
    if (options.isEmpty) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          border: Border(
            bottom: BorderSide(color: Colors.grey.shade200),
          ),
        ),
        child: Row(
          children: [
            SizedBox(
              width: 80,
              child: Text(
                label,
                style: const TextStyle(fontWeight: FontWeight.w500),
              ),
            ),
            Expanded(
              child: Text(
                'No options available',
                style: TextStyle(color: Colors.grey.shade600),
              ),
            ),
          ],
        ),
      );
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        border: Border(
          bottom: BorderSide(color: Colors.grey.shade200),
        ),
      ),
      child: Row(
        children: [
          SizedBox(
            width: 80,
            child: Text(
              label,
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
          Expanded(
            child: DropdownButton<String>(
              value: selectedValue,
              hint: Text('Select $label'),
              isExpanded: true,
              underline: const SizedBox(),
              items: [
                DropdownMenuItem<String>(
                  value: null,
                  child: Text('Select $label'),
                ),
                ...options.map((option) => DropdownMenuItem<String>(
                  value: option,
                  child: Text(option),
                )),
              ],
              onChanged: onChanged,
            ),
          ),
        ],
      ),
    );
  }

  void _updateSelectedCategory() {
    final parts = <String>[];
    if (selectedLevel1 != null) {
      parts.add(selectedLevel1!);
      if (selectedLevel2 != null) {
        parts.add(selectedLevel2!);
        if (selectedLevel3 != null) {
          parts.add(selectedLevel3!);
        }
      }
    }
    
    if (parts.isNotEmpty) {
      widget.onCategorySelected(parts.join(' > '));
    }
  }
} 