"""
AI Portfolio Manager - Automated Setup Script
Sets up project structure, downloads models, configures environment
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def create_directory_structure():
    """Create project directory structure"""
    print_header("📁 Creating Directory Structure")
    
    directories = [
        "backend/models",
        "backend/utils",
        "frontend/src/components",
        "data/historical",
        "logs",
        "config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}/")
    
    print("\n✅ Directory structure created successfully!")


def create_env_file():
    """Create .env file from example"""
    print_header("🔐 Creating Environment Configuration")
    
    env_content = """# Alpaca API Configuration
APCA_API_KEY_ID=your_alpaca_api_key_here
APCA_API_SECRET_KEY=your_alpaca_secret_key_here
APCA_PAPER=true

# Email Notifications (Optional)
SENDGRID_API_KEY=
NOTIFICATION_EMAIL=

# Trading Configuration
INITIAL_CAPITAL=100000
RISK_PER_TRADE=0.02
MAX_POSITION_SIZE=0.25

# Scheduler Configuration
TRADING_SCHEDULE_HOUR=6
TRADING_SCHEDULE_MINUTE=45
TIMEZONE=America/New_York

# Model Configuration
MODEL_PATH=models/
USE_PRETRAINED=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/trading.log
"""
    
    env_path = Path(".env")
    
    if env_path.exists():
        print("⚠️  .env file already exists. Skipping...")
    else:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
        print("\n⚠️  IMPORTANT: Edit .env and add your Alpaca API keys!")


def install_python_dependencies():
    """Install Python dependencies"""
    print_header("📦 Installing Python Dependencies")
    
    try:
        print("Installing packages from requirements.txt...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True
        )
        print("\n✅ Python dependencies installed successfully!")
    
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error installing dependencies: {e}")
        print("Please install manually with: pip install -r requirements.txt")


def download_pretrained_models():
    """Download pretrained RL models from Hugging Face"""
    print_header("🧠 Downloading Pretrained Models")
    
    try:
        from huggingface_hub import hf_hub_download
        
        print("Downloading best_model.zip from Hugging Face...")
        hf_hub_download(
            repo_id="Adilbai/stock-trading-rl-agent",
            filename="best_model.zip",
            local_dir="backend/models/",
            local_dir_use_symlinks=False
        )
        print("✅ Downloaded best_model.zip")
        
        print("\nDownloading scaler.pkl from Hugging Face...")
        hf_hub_download(
            repo_id="Adilbai/stock-trading-rl-agent",
            filename="scaler.pkl",
            local_dir="backend/models/",
            local_dir_use_symlinks=False
        )
        print("✅ Downloaded scaler.pkl")
        
        # Create copies for sector-specific models
        import shutil
        
        model_path = Path("backend/models/best_model.zip")
        if model_path.exists():
            shutil.copy(model_path, "backend/models/tech_model.zip")
            shutil.copy(model_path, "backend/models/energy_model.zip")
            print("\n✅ Created sector-specific model copies")
        
        print("\n✅ Models downloaded and configured successfully!")
        
    except ImportError:
        print("\n⚠️  huggingface-hub not installed. Please install manually:")
        print("    pip install huggingface-hub")
        print("    Then run the download_models() function")
    
    except Exception as e:
        print(f"\n❌ Error downloading models: {e}")
        print("\nManual download instructions:")
        print("1. Visit: https://huggingface.co/Adilbai/stock-trading-rl-agent")
        print("2. Download best_model.zip and scaler.pkl")
        print("3. Place in backend/models/ directory")


def create_sample_data():
    """Create sample data files"""
    print_header("📊 Creating Sample Data Files")
    
    # Create empty trades.csv
    trades_path = Path("data/trades.csv")
    if not trades_path.exists():
        with open(trades_path, 'w') as f:
            f.write("timestamp,symbol,action,qty,price,pnl,order_id,model\n")
        print("✅ Created data/trades.csv")
    
    # Create empty performance.json
    import json
    perf_path = Path("data/performance.json")
    if not perf_path.exists():
        with open(perf_path, 'w') as f:
            json.dump({
                "equity_history": [],
                "daily_returns": [],
                "last_updated": None
            }, f, indent=2)
        print("✅ Created data/performance.json")
    
    print("\n✅ Sample data files created!")


def setup_frontend():
    """Setup React frontend"""
    print_header("⚛️  Setting Up React Frontend")
    
    frontend_path = Path("frontend")
    
    if not frontend_path.exists():
        frontend_path.mkdir(exist_ok=True)
    
    # Create package.json
    package_json = {
        "name": "ai-portfolio-dashboard",
        "version": "1.0.0",
        "type": "module",
        "scripts": {
            "dev": "vite",
            "build": "vite build",
            "preview": "vite preview"
        },
        "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "recharts": "^2.10.3",
            "lucide-react": "^0.263.1"
        },
        "devDependencies": {
            "@vitejs/plugin-react": "^4.2.1",
            "vite": "^5.0.8",
            "tailwindcss": "^3.4.1",
            "autoprefixer": "^10.4.17",
            "postcss": "^8.4.33"
        }
    }
    
    import json
    with open(frontend_path / "package.json", 'w') as f:
        json.dump(package_json, f, indent=2)
    
    print("✅ Created package.json")
    print("\n📝 To complete frontend setup:")
    print("   cd frontend")
    print("   npm install")
    print("   npm run dev")


def check_alpaca_credentials():
    """Check if Alpaca credentials are configured"""
    print_header("🔑 Checking Alpaca Configuration")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("APCA_API_KEY_ID")
        api_secret = os.getenv("APCA_API_SECRET_KEY")
        
        if api_key and api_key != "your_alpaca_api_key_here":
            print("✅ Alpaca API Key configured")
        else:
            print("⚠️  Alpaca API Key not configured")
            print("   Get your keys at: https://alpaca.markets/")
        
        if api_secret and api_secret != "your_alpaca_secret_key_here":
            print("✅ Alpaca Secret Key configured")
        else:
            print("⚠️  Alpaca Secret Key not configured")
        
    except ImportError:
        print("⚠️  python-dotenv not installed")


def print_next_steps():
    """Print next steps for user"""
    print_header("🎯 Next Steps")
    
    print("""
1. ✏️  Edit .env file and add your Alpaca API keys:
   - Sign up at https://alpaca.markets/
   - Get Paper Trading API keys
   - Add to APCA_API_KEY_ID and APCA_API_SECRET_KEY

2. 🚀 Start the backend:
   cd backend
   python main.py

3. ⚛️  Start the frontend:
   cd frontend
   npm install
   npm run dev

4. 🌐 Access the application:
   - API: http://localhost:8000
   - Dashboard: http://localhost:5173

5. 📊 Test the system:
   - Check portfolio: http://localhost:8000/api/portfolio
   - View signals: http://localhost:8000/api/signals
   - Trigger strategy: POST http://localhost:8000/api/run-strategy

6. 📅 Daily automation:
   - System runs automatically at 6:45 AM EST (Mon-Fri)
   - Or trigger manually via API

⚠️  IMPORTANT:
   - Start with PAPER TRADING (APCA_PAPER=true)
   - Test thoroughly before considering live trading
   - Never invest more than you can afford to lose
   - Monitor the system regularly

📚 Documentation:
   - See README.md for complete documentation
   - API docs: http://localhost:8000/docs (when backend running)

🐛 Issues?
   - Check logs in logs/trading.log
   - Verify API keys in .env
   - Ensure all dependencies installed
   - Check Alpaca account status
""")


def main():
    """Run complete setup"""
    print("\n" + "🤖" * 30)
    print("  AI Portfolio Manager - Automated Setup")
    print("🤖" * 30)
    
    print("\nThis script will set up your AI Portfolio Manager project.")
    print("It will create directories, download models, and configure the environment.\n")
    
    response = input("Continue with setup? (y/n): ")
    
    if response.lower() != 'y':
        print("\n❌ Setup cancelled.")
        return
    
    try:
        # Run setup steps
        create_directory_structure()
        create_env_file()
        install_python_dependencies()
        download_pretrained_models()
        create_sample_data()
        setup_frontend()
        check_alpaca_credentials()
        
        print_header("✅ Setup Complete!")
        print_next_steps()
        
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        print("Please check the error and try again.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())