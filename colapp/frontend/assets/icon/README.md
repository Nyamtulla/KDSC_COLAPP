# Icon Setup Instructions

## 📁 **Place Your Icon Here**

1. **Create your icon**: Design a 1024x1024 px PNG icon
2. **Save as**: `icon.png` in this directory
3. **Run commands**: See steps below

## 🎨 **Icon Requirements**

- **Size**: 1024x1024 pixels
- **Format**: PNG with transparency
- **Design**: Square format (system will round it)
- **Colors**: Use ColApp brand colors (#0051BA, #EC944A)

## 🚀 **Quick Setup**

### **Step 1: Add Your Icon**
Save your 1024x1024 icon as `icon.png` in this folder.

### **Step 2: Generate All Sizes**
```bash
cd colapp/frontend
flutter pub get
flutter pub run flutter_launcher_icons:main
```

### **Step 3: Rebuild App**
```bash
flutter clean
flutter build apk --debug
```

## 🎯 **Icon Ideas for ColApp**

### **Simple Design Options:**
1. **Blue "C"** - Stylized "C" on blue background
2. **Receipt Icon** - Receipt with scan lines
3. **Camera + Receipt** - Camera icon with receipt corner
4. **Smart Scanner** - Abstract scanner design

### **Color Scheme:**
- **Primary**: #0051BA (Blue)
- **Accent**: #EC944A (Orange)
- **Background**: #EAF3F9 (Light Blue)

## 🛠️ **Online Icon Generators**

If you need help creating an icon:

1. **Figma** (Free): https://figma.com
2. **Canva** (Free): https://canva.com
3. **App Icon Generator**: https://appicon.co/

## ✅ **After Adding Icon**

1. ✅ Save as `icon.png` (1024x1024)
2. ✅ Run `flutter pub run flutter_launcher_icons:main`
3. ✅ Test on Android device
4. ✅ Test on web browser
5. ✅ Deploy to production

Your new icon will appear on:
- Android home screen
- Web browser tab
- App launcher
- PWA installation 