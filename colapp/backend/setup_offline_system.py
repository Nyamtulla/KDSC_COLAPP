#!/usr/bin/env python3
"""
Setup script for offline receipt parsing system
This script helps install and configure all components for zero-cost receipt parsing
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("=" * 60)
    print("🔧 OFFLINE RECEIPT PARSING SYSTEM SETUP")
    print("=" * 60)
    print("This script will help you set up a complete offline receipt parsing")
    print("system with OCR, local LLM, and custom NLP models.")
    print("=" * 60)

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} is compatible")
    return True

def install_system_dependencies():
    """Install system-level dependencies"""
    print("\n📦 Installing system dependencies...")
    
    system = platform.system().lower()
    
    if system == "windows":
        return install_windows_dependencies()
    elif system == "darwin":  # macOS
        return install_macos_dependencies()
    elif system == "linux":
        return install_linux_dependencies()
    else:
        print(f"❌ Unsupported operating system: {system}")
        return False

def install_windows_dependencies():
    """Install Windows dependencies"""
    print("🪟 Installing Windows dependencies...")
    
    # Check if Tesseract is installed
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, check=True)
        print("✅ Tesseract is already installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Tesseract not found. Please install it manually:")
        print("   1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   2. Install to: C:\\Program Files\\Tesseract-OCR")
        print("   3. Add to PATH: C:\\Program Files\\Tesseract-OCR")
        return False
    
    # Check if Poppler is installed (for PDF processing)
    try:
        result = subprocess.run(['pdftoppm', '-h'], 
                              capture_output=True, text=True, check=True)
        print("✅ Poppler is already installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Poppler not found. PDF processing may not work.")
        print("   You can install it via: https://blog.alivate.com.au/poppler-windows/")
    
    return True

def install_macos_dependencies():
    """Install macOS dependencies"""
    print("🍎 Installing macOS dependencies...")
    
    try:
        # Install Homebrew if not available
        subprocess.run(['brew', '--version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("📦 Installing Homebrew...")
        install_script = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        subprocess.run(install_script, shell=True, check=True)
    
    # Install Tesseract
    try:
        subprocess.run(['brew', 'install', 'tesseract'], check=True)
        print("✅ Tesseract installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install Tesseract")
        return False
    
    # Install Poppler
    try:
        subprocess.run(['brew', 'install', 'poppler'], check=True)
        print("✅ Poppler installed")
    except subprocess.CalledProcessError:
        print("⚠️  Failed to install Poppler")
    
    return True

def install_linux_dependencies():
    """Install Linux dependencies"""
    print("🐧 Installing Linux dependencies...")
    
    # Detect package manager
    if os.path.exists('/etc/debian_version'):
        package_manager = 'apt'
    elif os.path.exists('/etc/redhat-release'):
        package_manager = 'yum'
    else:
        print("❌ Unsupported Linux distribution")
        return False
    
    # Install Tesseract
    try:
        if package_manager == 'apt':
            subprocess.run(['sudo', 'apt-get', 'update'], check=True)
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'tesseract-ocr'], check=True)
        else:
            subprocess.run(['sudo', 'yum', 'install', '-y', 'tesseract'], check=True)
        print("✅ Tesseract installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install Tesseract")
        return False
    
    # Install Poppler
    try:
        if package_manager == 'apt':
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'poppler-utils'], check=True)
        else:
            subprocess.run(['sudo', 'yum', 'install', '-y', 'poppler-utils'], check=True)
        print("✅ Poppler installed")
    except subprocess.CalledProcessError:
        print("⚠️  Failed to install Poppler")
    
    return True

def install_python_dependencies():
    """Install Python dependencies"""
    print("\n🐍 Installing Python dependencies...")
    
    try:
        # Upgrade pip
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
        
        # Install requirements
        requirements_file = Path(__file__).parent / 'requirements.txt'
        if requirements_file.exists():
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)], check=True)
            print("✅ Python dependencies installed")
            return True
        else:
            print("❌ requirements.txt not found")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False

def install_ollama():
    """Install and configure Ollama"""
    print("\n🤖 Installing Ollama...")
    
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    try:
        # Check if Ollama is already installed
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, check=True)
        print("✅ Ollama is already installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Install Ollama
    if system == "windows":
        print("📥 Downloading Ollama for Windows...")
        # Windows installation instructions
        print("   Please install Ollama manually:")
        print("   1. Download from: https://ollama.ai/download")
        print("   2. Run the installer")
        print("   3. Restart your terminal")
        return False
    else:
        # Unix-like systems
        install_script = 'curl -fsSL https://ollama.ai/install.sh | sh'
        try:
            subprocess.run(install_script, shell=True, check=True)
            print("✅ Ollama installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install Ollama")
            return False

def download_llm_model():
    """Download a suitable LLM model"""
    print("\n📥 Downloading LLM model...")
    
    try:
        # Check if Ollama is running
        subprocess.run(['ollama', 'list'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Ollama is not running. Please start it first:")
        print("   ollama serve")
        return False
    
    # Download Llama 2 7B model
    model_name = "llama2:7b"
    print(f"📥 Downloading {model_name}...")
    
    try:
        subprocess.run(['ollama', 'pull', model_name], check=True)
        print(f"✅ {model_name} downloaded successfully")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to download {model_name}")
        return False

def test_system():
    """Test the complete system"""
    print("\n🧪 Testing system components...")
    
    tests = []
    
    # Test Tesseract
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, check=True)
        tests.append(("Tesseract OCR", True, result.stdout.split('\n')[0]))
    except:
        tests.append(("Tesseract OCR", False, "Not found"))
    
    # Test Ollama
    try:
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True, check=True)
        tests.append(("Ollama", True, "Running"))
    except:
        tests.append(("Ollama", False, "Not running"))
    
    # Test Python imports
    try:
        import torch
        tests.append(("PyTorch", True, f"v{torch.__version__}"))
    except:
        tests.append(("PyTorch", False, "Not installed"))
    
    try:
        import transformers
        tests.append(("Transformers", True, f"v{transformers.__version__}"))
    except:
        tests.append(("Transformers", False, "Not installed"))
    
    # Print test results
    print("\n📊 System Test Results:")
    print("-" * 50)
    
    all_passed = True
    for component, status, details in tests:
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {component}: {details}")
        if not status:
            all_passed = False
    
    return all_passed

def create_config_file():
    """Create configuration file"""
    print("\n⚙️  Creating configuration file...")
    
    config = {
        "ocr": {
            "engine": "auto",
            "tesseract_config": "--oem 3 --psm 6"
        },
        "llm": {
            "model": "llama2:7b",
            "host": "http://localhost:11434",
            "temperature": 0.1,
            "max_tokens": 2048
        },
        "custom_nlp": {
            "enabled": True,
            "confidence_threshold": 0.7
        },
        "file_processing": {
            "max_file_size": 10485760,  # 10MB
            "supported_formats": [".jpg", ".jpeg", ".png", ".pdf"],
            "temp_dir": "./temp"
        }
    }
    
    config_file = Path(__file__).parent / 'offline_config.json'
    
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Configuration saved to {config_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to create config file: {e}")
        return False

def create_test_script():
    """Create a test script"""
    print("\n📝 Creating test script...")
    
    test_script = '''#!/usr/bin/env python3
"""
Test script for offline receipt parsing system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_receipt_parser import EnhancedReceiptParser

def test_parser():
    """Test the receipt parser"""
    print("🧪 Testing Enhanced Receipt Parser...")
    
    # Initialize parser
    parser = EnhancedReceiptParser()
    
    # Test available methods
    methods = parser.get_available_methods()
    print("\\n📋 Available parsing methods:")
    for method, info in methods.items():
        status = "✅" if info['available'] else "❌"
        print(f"{status} {method}: {info['description']}")
    
    # Test services
    services = parser.test_services()
    print("\\n🔧 Service status:")
    for service, info in services.items():
        status = "✅" if info['available'] else "❌"
        print(f"{status} {service}: {'Available' if info['available'] else 'Not available'}")
    
    print("\\n✅ Test completed!")

if __name__ == "__main__":
    test_parser()
'''
    
    test_file = Path(__file__).parent / 'test_offline_system.py'
    
    try:
        with open(test_file, 'w') as f:
            f.write(test_script)
        
        # Make executable on Unix systems
        if platform.system() != "windows":
            os.chmod(test_file, 0o755)
        
        print(f"✅ Test script created: {test_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to create test script: {e}")
        return False

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # # Install system dependencies
    # if not install_system_dependencies():
    #     print("\n❌ System dependency installation failed")
    #     print("Please install the required system packages manually and run this script again.")
    #     sys.exit(1)
    
    # # Install Python dependencies
    # if not install_python_dependencies():
    #     print("\n❌ Python dependency installation failed")
    #     sys.exit(1)
    
    # # Install Ollama
    # if not install_ollama():
    #     print("\n⚠️  Ollama installation failed or requires manual setup")
    #     print("You can still use the system with OCR-only parsing")
    
    # Download LLM model (optional)
    if install_ollama():
        download_llm_model()
    
    # Create configuration
    create_config_file()
    
    # Create test script
    create_test_script()
    
    # Test system
    if test_system():
        print("\n🎉 Setup completed successfully!")
        print("\n📖 Next steps:")
        print("1. Start Ollama: ollama serve")
        print("2. Test the system: python test_offline_system.py")
        print("3. Run the Flask app: python app.py")
    else:
        print("\n⚠️  Setup completed with some issues")
        print("Please check the test results above and fix any problems")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main() 