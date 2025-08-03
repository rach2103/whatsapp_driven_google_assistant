#!/usr/bin/env python3
"""
Court Data Fetcher Setup Script
Automated setup and configuration for the application
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("=" * 60)
    print("🏛️  COURT DATA FETCHER SETUP")
    print("=" * 60)
    print("Setting up your Court Data Fetcher application...")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def create_directories():
    """Create necessary directories"""
    directories = [
        'logs',
        'downloads',
        'downloads/pdfs',
        'tests',
        'nginx',
        'ssl'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}")

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False
    return True

def setup_environment():
    """Set up environment file"""
    if not os.path.exists('.env'):
        print("\n🔧 Setting up environment file...")
        shutil.copy('.env.example', '.env')
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file with your actual configuration values")
    else:
        print("✅ Environment file already exists")

def initialize_database():
    """Initialize the database"""
    print("\n🗄️  Initializing database...")
    try:
        subprocess.check_call([sys.executable, 'init_db.py'])
        print("✅ Database initialized successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to initialize database")
        return False
    return True

def run_tests():
    """Run basic tests"""
    if input("\n🧪 Run tests? (y/N): ").lower() == 'y':
        print("Running tests...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pytest', 'tests/', '-v'])
            print("✅ All tests passed")
        except subprocess.CalledProcessError:
            print("⚠️  Some tests failed")
        except FileNotFoundError:
            print("⚠️  pytest not found, skipping tests")

def create_nginx_config():
    """Create basic Nginx configuration"""
    nginx_config = """
events {
    worker_connections 1024;
}

http {
    upstream court_fetcher {
        server court-fetcher:5000;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://court_fetcher;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
"""
    
    nginx_config_path = Path('nginx/nginx.conf')
    if not nginx_config_path.exists():
        with open(nginx_config_path, 'w') as f:
            f.write(nginx_config.strip())
        print("✅ Created Nginx configuration")

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Edit .env file with your configuration:")
    print("   - Add your 2captcha API key")
    print("   - Set a secure Flask secret key")
    print()
    print("2. Run the application:")
    print("   python app.py")
    print()
    print("3. Or use Docker:")
    print("   docker-compose up -d")
    print()
    print("4. Access the application:")
    print("   http://localhost:5000")
    print()
    print("5. For production deployment:")
    print("   docker-compose --profile production up -d")
    print()
    print("📚 Read README.md for detailed documentation")
    print()

def main():
    """Main setup function"""
    print_banner()
    
    # Check requirements
    check_python_version()
    
    # Setup steps
    create_directories()
    
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        sys.exit(1)
    
    setup_environment()
    create_nginx_config()
    
    if not initialize_database():
        print("❌ Setup failed at database initialization")
        sys.exit(1)
    
    run_tests()
    print_next_steps()

if __name__ == '__main__':
    main()