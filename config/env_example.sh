# Alpaca API Configuration
APCA_API_KEY_ID=your_alpaca_api_key_here
APCA_API_SECRET_KEY=your_alpaca_secret_key_here
APCA_PAPER=true  # Set to false for live trading

# Email Notifications (Optional - SendGrid)
SENDGRID_API_KEY=your_sendgrid_api_key_here
NOTIFICATION_EMAIL=your_email@example.com

# SMS Notifications (Optional - Twilio)
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
NOTIFICATION_PHONE=+1234567890

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
HUGGINGFACE_MODEL=Adilbai/stock-trading-rl-agent

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/trading.log