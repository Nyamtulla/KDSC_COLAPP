# Homepage Download Button Integration Guide

## 🎯 **Quick Integration Options**

### **Option 1: Simple Download Button (Recommended)**

Add this HTML to your homepage where you want the download button:

```html
<!-- ColApp Download Button -->
<a href="download/ColApp.apk" class="download-btn" download>
    📱 Download ColApp APK (66.4 MB)
</a>

<style>
.download-btn {
    display: inline-block;
    background: linear-gradient(45deg, #0051BA, #EC944A);
    color: white;
    padding: 15px 30px;
    border-radius: 25px;
    text-decoration: none;
    font-weight: bold;
    font-size: 18px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0, 81, 186, 0.3);
}

.download-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 81, 186, 0.4);
    color: white;
    text-decoration: none;
}
</style>
```

### **Option 2: Advanced Download Section**

Add this complete download section to your homepage:

```html
<!-- ColApp Download Section -->
<section class="download-section">
    <div class="container">
        <h2>📱 Download ColApp</h2>
        <p>Get the smart receipt scanner and expense tracker for Android</p>
        
        <div class="download-card">
            <div class="app-info">
                <div class="app-icon">C</div>
                <div class="app-details">
                    <h3>ColApp</h3>
                    <p>Smart Receipt Scanner & Expense Tracker</p>
                    <ul>
                        <li>✓ OCR Receipt Scanning</li>
                        <li>✓ Automatic Categorization</li>
                        <li>✓ Analytics & Insights</li>
                        <li>✓ Cloud Sync</li>
                    </ul>
                </div>
            </div>
            
            <div class="download-actions">
                <a href="download/ColApp.apk" class="download-btn" download>
                    📱 Download APK
                </a>
                <p class="file-info">Version 1.0.0 • 66.4 MB • Android 5.0+</p>
            </div>
        </div>
    </div>
</section>

<style>
.download-section {
    padding: 60px 0;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
    text-align: center;
}

.download-section h2 {
    font-size: 2.5em;
    color: #333;
    margin-bottom: 10px;
}

.download-section > .container > p {
    font-size: 1.2em;
    color: #666;
    margin-bottom: 40px;
}

.download-card {
    background: white;
    border-radius: 20px;
    padding: 40px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    display: flex;
    align-items: center;
    justify-content: space-between;
    max-width: 800px;
    margin: 0 auto;
}

.app-info {
    display: flex;
    align-items: center;
    text-align: left;
}

.app-icon {
    width: 80px;
    height: 80px;
    background: linear-gradient(45deg, #0051BA, #EC944A);
    border-radius: 15px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    color: white;
    font-weight: bold;
    margin-right: 20px;
}

.app-details h3 {
    font-size: 1.5em;
    color: #333;
    margin-bottom: 5px;
}

.app-details p {
    color: #666;
    margin-bottom: 15px;
}

.app-details ul {
    list-style: none;
    padding: 0;
}

.app-details li {
    color: #666;
    margin: 5px 0;
    font-size: 14px;
}

.download-actions {
    text-align: center;
}

.download-btn {
    display: inline-block;
    background: linear-gradient(45deg, #0051BA, #EC944A);
    color: white;
    padding: 15px 30px;
    border-radius: 25px;
    text-decoration: none;
    font-weight: bold;
    font-size: 18px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0, 81, 186, 0.3);
    margin-bottom: 10px;
}

.download-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 81, 186, 0.4);
    color: white;
    text-decoration: none;
}

.file-info {
    color: #999;
    font-size: 14px;
    margin: 0;
}

@media (max-width: 768px) {
    .download-card {
        flex-direction: column;
        text-align: center;
        padding: 30px 20px;
    }
    
    .app-info {
        flex-direction: column;
        text-align: center;
        margin-bottom: 30px;
    }
    
    .app-icon {
        margin-right: 0;
        margin-bottom: 15px;
    }
}
</style>
```

### **Option 3: Floating Download Button**

Add this floating download button that appears on scroll:

```html
<!-- Floating Download Button -->
<div class="floating-download">
    <a href="download/ColApp.apk" download>
        📱 Download ColApp
    </a>
</div>

<style>
.floating-download {
    position: fixed;
    bottom: 30px;
    right: 30px;
    z-index: 1000;
}

.floating-download a {
    display: block;
    background: linear-gradient(45deg, #0051BA, #EC944A);
    color: white;
    padding: 15px 25px;
    border-radius: 50px;
    text-decoration: none;
    font-weight: bold;
    box-shadow: 0 4px 20px rgba(0, 81, 186, 0.4);
    transition: all 0.3s ease;
}

.floating-download a:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(0, 81, 186, 0.6);
    color: white;
    text-decoration: none;
}

@media (max-width: 768px) {
    .floating-download {
        bottom: 20px;
        right: 20px;
    }
    
    .floating-download a {
        padding: 12px 20px;
        font-size: 14px;
    }
}
</style>
```

## 📁 **File Structure**

Your website should have this structure:

```
your-website/
├── index.html (your homepage)
├── download/
│   ├── index.html (download page)
│   └── ColApp.apk (the APK file)
└── assets/
    └── (your other files)
```

## 🔧 **Server Configuration**

### **For Apache (.htaccess)**
Add this to your `.htaccess` file to enable APK downloads:

```apache
# Enable APK downloads
<Files "*.apk">
    Header set Content-Type application/vnd.android.package-archive
    Header set Content-Disposition "attachment; filename=ColApp.apk"
</Files>
```

### **For Nginx**
Add this to your nginx configuration:

```nginx
# Enable APK downloads
location ~* \.apk$ {
    add_header Content-Type application/vnd.android.package-archive;
    add_header Content-Disposition "attachment; filename=ColApp.apk";
}
```

## 📱 **Mobile Detection (Optional)**

Add this JavaScript to show different content for mobile users:

```html
<script>
// Detect mobile devices
function isMobile() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

// Show mobile-specific download instructions
if (isMobile()) {
    document.addEventListener('DOMContentLoaded', function() {
        const downloadBtn = document.querySelector('.download-btn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', function(e) {
                e.preventDefault();
                alert('To install ColApp:\n\n1. Download the APK\n2. Enable "Install from unknown sources"\n3. Open the APK file\n4. Tap "Install"');
                window.location.href = this.href;
            });
        }
    });
}
</script>
```

## 🎨 **Customization Options**

### **Change Colors**
Update the gradient colors in the CSS:

```css
/* Primary brand colors */
background: linear-gradient(45deg, #0051BA, #EC944A);

/* Alternative color schemes */
/* Blue theme */
background: linear-gradient(45deg, #2196F3, #21CBF3);

/* Green theme */
background: linear-gradient(45deg, #4CAF50, #8BC34A);

/* Purple theme */
background: linear-gradient(45deg, #9C27B0, #E91E63);
```

### **Change Button Text**
Update the button text in the HTML:

```html
<!-- Different button text options -->
<a href="download/ColApp.apk" class="download-btn" download>
    📱 Get ColApp
</a>

<a href="download/ColApp.apk" class="download-btn" download>
    📱 Install Now
</a>

<a href="download/ColApp.apk" class="download-btn" download>
    📱 Download for Android
</a>
```

## ✅ **Integration Checklist**

- ✅ APK file copied to `web/download/ColApp.apk`
- ✅ Download page created at `web/download/index.html`
- ✅ Download button component created
- ✅ Server configuration updated (if needed)
- ✅ Mobile detection added (optional)
- ✅ Colors customized to match your brand
- ✅ Button text updated to match your style

## 🚀 **Testing**

1. **Test the download link** on your website
2. **Verify APK downloads** correctly
3. **Test on mobile devices** to ensure proper behavior
4. **Check file size** displays correctly (66.4 MB)
5. **Verify installation** works on Android devices

Your ColApp download is now ready for your website! 🎉 