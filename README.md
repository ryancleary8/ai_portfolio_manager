
# 🤖 AI Portfolio Manager

A complete autonomous stock-trading system powered by **Reinforcement Learning** that updates daily, fetches market data, runs predictions, places trades via **Alpaca**, and displays everything in a live **React dashboard**.

---

## 🎯 Features

- **🧠 Reinforcement Learning Trading**: PPO models trained for Tech and Energy/Finance sectors
- **📊 Automated Daily Updates**: Runs at 6:45 AM EST every weekday
- **💹 Alpaca Integration**: Paper & live trading support
- **📈 Real-time Dashboard**: React frontend with live portfolio tracking
- **📉 Technical Analysis**: 17+ indicators (SMA, EMA, RSI, MACD, Bollinger Bands)
- **📧 Daily Reports**: Email/SMS notifications with performance summary
- **🔄 Multi-Model Support**: Separate models for different market sectors
- **📝 Complete Logging**: Trade history, P&L tracking, performance metrics

---

## 🏗️ Architecture

```
ai_portfolio_manager/
├── backend/
│   ├── main.py                 # FastAPI server + scheduler
│   ├── models/
│   │   ├── tech_model.zip      # Tech sector RL model
│   │   ├── energy_model.zip    # Energy/Finance RL model
│   │   └── scaler.pkl          # Feature scaler
│   └── utils/
│       ├── data_fetch.py       # Yahoo Finance data fetching
│       ├── indicators.py       # Technical indicator calculations
│       ├── trader.py           # Alpaca trading interface
│       └── logger.py           # Trade & performance logging
├── frontend/
│   ├── src/
│   │   └── App.jsx             # React dashboard
│   └── package.json
├── data/
│   ├── trades.csv              # Trade log
│   ├── performance.json        # Portfolio metrics
│   └── historical/             # Market data cache
├── config/
│   └── .env                    # API keys & configuration
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd ai_portfolio_manager
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your Alpaca API keys
```

### 3. Download Models

**Option A: Use Pretrained Models**

```python
# Download from Hugging Face
from huggingface_hub import hf_hub_download

# Download best_model.zip and scaler.pkl
hf_hub_download(
    repo_id="Adilbai/stock-trading-rl-agent",
    filename="best_model.zip",
    local_dir="backend/models/"
)

hf_hub_download(
    repo_id="Adilbai/stock-trading-rl-agent",
    filename="scaler.pkl",
    local_dir="backend/models/"
)

# Rename for sector-specific models
# tech_model.zip, energy_model.zip
```

**Option B: Train Your Own Models**

```bash
# Edit backend/training/training_config.yaml to list the tickers for each model
# Then launch the trainer (downloads data from Yahoo Finance automatically)
python -m backend.training.train_models --config backend/training/training_config.yaml
```

The YAML file ships with sample `tech`, `energy`, and `finance` model
definitions.  You can freely add new models or adjust the ticker lists, PPO
hyperparameters, training horizon, or output paths.  Each model saves its
trained weights and feature scaler into `backend/models/` by default, keeping
them ready for the backend server to load.

### 4. Get Alpaca API Keys

1. Sign up at [Alpaca](https://alpaca.markets/)
2. Generate API keys (Paper Trading recommended for testing)
3. Add keys to `.env` file:

```bash
APCA_API_KEY_ID=your_key_here
APCA_API_SECRET_KEY=your_secret_here
APCA_PAPER=true
```

### 5. Start Backend

```bash
cd backend
python main.py

# Or with uvicorn:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`

### 6. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Dashboard will open at `http://localhost:5173`

---

## 📅 Daily Automation

The system automatically runs at **6:45 AM EST** every weekday:

1. **Fetch Market Data**: Downloads latest OHLCV from Yahoo Finance
2. **Calculate Indicators**: Computes SMA, EMA, RSI, MACD, Bollinger Bands
3. **Run RL Models**: Tech and Energy/Finance agents make predictions
4. **Execute Trades**: Places orders via Alpaca based on signals
5. **Log Results**: Records trades, updates performance metrics
6. **Send Report**: Emails/SMS daily summary

### Manual Trigger

```bash
curl -X POST http://localhost:8000/api/run-strategy
```

---

## 🧠 How It Works

### RL Model Architecture

- **Algorithm**: Proximal Policy Optimization (PPO)
- **Observation Space**: 17 features per stock
  - OHLCV (Open, High, Low, Close, Volume)
  - SMA (20, 50-day)
  - EMA (12, 26-day)
  - RSI (14-day)
  - MACD, MACD Signal, MACD Histogram
  - Bollinger Bands (Upper, Middle, Lower)
  - Daily Returns

- **Action Space**: 
  - `action[0]`: 0=HOLD, 1=BUY, 2=SELL
  - `action[1]`: Position size (0-1 fraction of portfolio)

### Trading Logic

```python
def run_daily_strategy():
    # 1. Fetch data for all tickers
    market_data = fetch_market_data(tickers, days=60)
    
    # 2. For each model (Tech / Energy)
    for model_name, tickers in MODEL_GROUPS.items():
        model = MODELS[model_name]
        
        for ticker in tickers:
            # 3. Calculate indicators
            obs = calculate_indicators(data[ticker])
            
            # 4. Get model prediction
            action, _ = model.predict(obs)
            
            # 5. Execute trade
            if action != HOLD:
                trader.execute_trade(ticker, action, size)
```

---

## 📊 API Endpoints

### Portfolio

```bash
GET /api/portfolio
# Returns current portfolio summary

GET /api/positions
# Returns all open positions

GET /api/performance
# Returns performance metrics & equity curve
```

### Trading

```bash
GET /api/signals?model=tech
# Returns latest AI signals

GET /api/trades?limit=50
# Returns recent trades

POST /api/manual-trade
# Body: {ticker, action, quantity}
# Execute manual override trade

POST /api/run-strategy
# Manually trigger daily strategy
```

### Models

```bash
GET /api/models
# Returns loaded models and ticker groups
```

---

## 📈 Dashboard Features

### Portfolio Overview
- Total Equity
- Day P&L
- Open Positions Count
- Buying Power

### Equity Curve
- Historical portfolio value chart
- 7-day rolling view

### AI Signals Panel
- Real-time model predictions
- Confidence scores
- Position size recommendations
- Prediction explanations

### Open Positions Table
- Symbol, Quantity, Avg Price
- Current Price, P&L, P&L %

### Trade Log
- Complete trade history
- Timestamp, Action, Quantity, Price
- P&L per trade

### Model Selector
- Switch between Tech / Energy models
- View sector-specific signals

---

## 🔧 Configuration

### Trading Parameters

Edit `backend/main.py`:

```python
MODEL_GROUPS = {
    "tech": ["AAPL", "MSFT", "NVDA", "GOOGL", "TSLA"],
    "energy": ["XOM", "CVX", "JPM", "BAC"]
}

# Add more tickers or models as needed
```

### Scheduler

Edit schedule in `main.py`:

```python
scheduler.add_job(
    run_daily_strategy,
    trigger=CronTrigger(
        day_of_week='mon-fri',
        hour=6,  # Change hour
        minute=45,  # Change minute
        timezone=pytz.timezone('America/New_York')
    )
)
```

### Risk Management

Edit `.env`:

```bash
INITIAL_CAPITAL=100000
RISK_PER_TRADE=0.02  # 2% risk per trade
MAX_POSITION_SIZE=0.25  # Max 25% of portfolio per position
```

---

## 📧 Notifications Setup

### Email (SendGrid)

1. Get API key from [SendGrid](https://sendgrid.com/)
2. Add to `.env`:

```bash
SENDGRID_API_KEY=your_key
NOTIFICATION_EMAIL=your_email@example.com
```

3. Implement in `main.py`:

```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_daily_notification(report):
    message = Mail(
        from_email='trading@yourapp.com',
        to_emails=os.getenv('NOTIFICATION_EMAIL'),
        subject='Daily Trading Report',
        html_content=f'<strong>P&L: ${report["pnl"]}</strong>'
    )
    
    sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
    sg.send(message)
```

### SMS (Twilio)

Similar setup with Twilio API for SMS notifications.

---

## 🧪 Testing

### Run in Paper Trading Mode

Default mode uses Alpaca Paper Trading (virtual money):

```bash
APCA_PAPER=true
```

### Manual Testing

```bash
# Test API endpoints
curl http://localhost:8000/api/portfolio

# Trigger strategy manually
curl -X POST http://localhost:8000/api/run-strategy

# Execute test trade
curl -X POST http://localhost:8000/api/manual-trade \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL", "action": "BUY", "quantity": 10}'
```

---

## 🚨 Important Notes

### ⚠️ Risk Disclaimer

This is an **experimental trading system**. Always:
- Start with **paper trading**
- Test thoroughly before using real money
- Never invest more than you can afford to lose
- Monitor the system regularly
- Have kill switches and position limits

### 🔐 Security

- **Never commit API keys** to version control
- Use environment variables for all secrets
- Enable 2FA on your Alpaca account
- Monitor for unauthorized access

### 📊 Performance

- RL models require retraining as market conditions change
- Past performance doesn't guarantee future results
- Regularly evaluate model performance
- Consider ensemble approaches

---

## 🛠️ Deployment

### Production Setup

1. **Use Process Manager**

```bash
# Install PM2
npm install -g pm2

# Start backend
pm2 start backend/main.py --name ai-portfolio

# Start frontend
cd frontend && npm run build
pm2 serve dist 3000 --name dashboard
```

2. **Setup Reverse Proxy (Nginx)**

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location /api {
        proxy_pass http://localhost:8000;
    }
    
    location / {
        proxy_pass http://localhost:3000;
    }
}
```

3. **Enable SSL (Let's Encrypt)**

```bash
sudo certbot --nginx -d yourdomain.com
```

4. **Monitor Logs**

```bash
pm2 logs ai-portfolio
```

---

## 📚 Resources

- [Alpaca API Docs](https://alpaca.markets/docs/)
- [Stable-Baselines3 Docs](https://stable-baselines3.readthedocs.io/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🎓 Next Steps

- [ ] Add more sector models
- [ ] Implement portfolio rebalancing
- [ ] Add risk management rules
- [ ] Create backtesting framework
- [ ] Implement model retraining pipeline
- [ ] Add more technical indicators
- [ ] Create mobile app
- [ ] Add social trading features

---

**Built with ❤️ using RL, FastAPI, React, and Alpaca**

*Last Updated: November 2025*
