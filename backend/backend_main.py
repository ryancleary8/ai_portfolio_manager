"""
AI Portfolio Manager - Main Backend Server
FastAPI + APScheduler + RL Trading Loop + Alpaca Integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import os
import json
import logging
from typing import Dict, List, Optional
import pytz

# Import custom modules (to be created)
from utils.data_fetch import fetch_market_data, get_historical_data
from utils.indicators import calculate_indicators
from utils.trader import AlpacaTrader, prepare_observation
from utils.logger import TradeLogger, PerformanceTracker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="AI Portfolio Manager API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
MODELS = {}
SCALERS = {}
MODEL_GROUPS = {
    "tech": ["AAPL", "MSFT", "NVDA", "GOOGL", "TSLA"],
    "energy": ["XOM", "CVX", "JPM", "BAC"]
}
ALL_TICKERS = ["AAPL", "MSFT", "NVDA", "GOOGL", "TSLA", "XOM", "CVX", "JPM", "BAC"]

# Initialize components
trader = AlpacaTrader()
trade_logger = TradeLogger()
performance_tracker = PerformanceTracker()
scheduler = BackgroundScheduler(timezone=pytz.timezone('America/New_York'))


def load_models():
    """Load RL models from disk or Hugging Face"""
    try:
        from stable_baselines3 import PPO
        import joblib
        
        # Load tech model
        if os.path.exists("models/tech_model.zip"):
            MODELS["tech"] = PPO.load("models/tech_model.zip")
            logger.info("✅ Loaded tech_model.zip")
        
        # Load energy model
        if os.path.exists("models/energy_model.zip"):
            MODELS["energy"] = PPO.load("models/energy_model.zip")
            logger.info("✅ Loaded energy_model.zip")
        
        # Load scalers
        if os.path.exists("models/scaler.pkl"):
            SCALERS["tech"] = joblib.load("models/scaler.pkl")
            SCALERS["energy"] = joblib.load("models/scaler.pkl")
            logger.info("✅ Loaded scaler.pkl")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error loading models: {e}")
        return False


def run_daily_strategy():
    """
    Main daily trading loop - runs at 6:45 AM EST
    1. Fetch latest market data
    2. Calculate indicators
    3. Run RL model predictions
    4. Execute trades via Alpaca
    5. Log results and send report
    """
    logger.info("🚀 Starting daily strategy execution...")
    
    try:
        # 1. Fetch market data
        logger.info("📊 Fetching market data...")
        market_data = fetch_market_data(ALL_TICKERS, days=60)
        
        if not market_data:
            logger.error("❌ Failed to fetch market data")
            return
        
        # 2. Process each model group
        daily_signals = []
        
        for model_name, tickers in MODEL_GROUPS.items():
            if model_name not in MODELS:
                logger.warning(f"⚠️ Model {model_name} not loaded, skipping...")
                continue
            
            model = MODELS[model_name]
            scaler = SCALERS.get(model_name)
            
            logger.info(f"🧠 Running {model_name} model predictions...")
            
            for ticker in tickers:
                try:
                    # Get ticker data
                    ticker_data = market_data.get(ticker)
                    if ticker_data is None or len(ticker_data) < 30:
                        logger.warning(f"⚠️ Insufficient data for {ticker}")
                        continue
                    
                    # Calculate technical indicators
                    obs_data = calculate_indicators(ticker_data)
                    
                    # Prepare observation for model
                    obs = prepare_observation(obs_data, scaler)
                    
                    # Get model prediction
                    action, _ = model.predict(obs, deterministic=True)
                    
                    # Decode action
                    # action[0] = 0: HOLD, 1: BUY, 2: SELL
                    # action[1] = position size (0-1)
                    action_type = ["HOLD", "BUY", "SELL"][int(action[0])]
                    position_size = float(action[1])
                    
                    signal = {
                        "timestamp": datetime.now().isoformat(),
                        "ticker": ticker,
                        "model": model_name,
                        "action": action_type,
                        "position_size": position_size,
                        "confidence": abs(position_size)  # Higher size = higher confidence
                    }
                    
                    daily_signals.append(signal)
                    logger.info(f"📈 {ticker}: {action_type} (size: {position_size:.2f})")
                    
                    # 3. Execute trade
                    if action_type != "HOLD":
                        trade_result = trader.execute_trade(
                            ticker, 
                            action_type, 
                            position_size
                        )
                        
                        if trade_result:
                            trade_logger.log_trade(trade_result)
                            logger.info(f"✅ Trade executed: {trade_result}")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing {ticker}: {e}")
                    continue
        
        # 4. Update performance metrics
        portfolio_value = trader.get_portfolio_value()
        performance_tracker.update(portfolio_value, daily_signals)
        
        # 5. Generate and send daily report
        report = generate_daily_report(daily_signals)
        send_daily_notification(report)
        
        logger.info("✅ Daily strategy execution completed!")
        
    except Exception as e:
        logger.error(f"❌ Error in daily strategy: {e}")
        raise


def generate_daily_report(signals: List[Dict]) -> Dict:
    """Generate daily summary report"""
    portfolio = trader.get_portfolio_summary()
    trades = trade_logger.get_today_trades()
    performance = performance_tracker.get_metrics()
    
    report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "portfolio": portfolio,
        "signals_generated": len(signals),
        "trades_executed": len(trades),
        "signals": signals,
        "trades": trades,
        "performance": performance
    }
    
    # Save to file
    os.makedirs("data", exist_ok=True)
    with open(f"data/daily_report_{datetime.now().strftime('%Y%m%d')}.json", "w") as f:
        json.dump(report, f, indent=2)
    
    return report


def send_daily_notification(report: Dict):
    """Send email/SMS notification with daily summary"""
    try:
        # TODO: Implement SendGrid or SMTP email
        summary = f"""
        🤖 AI Portfolio Manager - Daily Report
        Date: {report['date']}
        
        📊 Portfolio:
        - Total Equity: ${report['portfolio'].get('equity', 0):,.2f}
        - Day P&L: ${report['portfolio'].get('day_pnl', 0):,.2f}
        - Total P&L: ${report['portfolio'].get('total_pnl', 0):,.2f}
        
        📈 Trading:
        - Signals Generated: {report['signals_generated']}
        - Trades Executed: {report['trades_executed']}
        
        📉 Performance:
        - Sharpe Ratio: {report['performance'].get('sharpe_ratio', 0):.2f}
        - Max Drawdown: {report['performance'].get('max_drawdown', 0):.2f}%
        """
        
        logger.info(f"📧 Daily report summary:\n{summary}")
        
    except Exception as e:
        logger.error(f"❌ Error sending notification: {e}")


# ==================== API ENDPOINTS ====================

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    logger.info("🚀 Starting AI Portfolio Manager...")
    
    # Load models
    if not load_models():
        logger.warning("⚠️ Models not loaded - running in demo mode")
    
    # Initialize trader
    trader.connect()
    
    # Schedule daily job at 6:45 AM EST (Mon-Fri)
    scheduler.add_job(
        run_daily_strategy,
        trigger=CronTrigger(
            day_of_week='mon-fri',
            hour=6,
            minute=45,
            timezone=pytz.timezone('America/New_York')
        ),
        id='daily_strategy',
        name='Daily RL Strategy Execution',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("✅ Scheduler started - Daily job at 6:45 AM EST")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    scheduler.shutdown()
    logger.info("👋 Shutting down AI Portfolio Manager")


@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "online",
        "service": "AI Portfolio Manager",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/portfolio")
async def get_portfolio():
    """Get current portfolio status"""
    try:
        portfolio = trader.get_portfolio_summary()
        return portfolio
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/positions")
async def get_positions():
    """Get all open positions"""
    try:
        positions = trader.get_positions()
        return {"positions": positions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trades")
async def get_trades(limit: int = 50):
    """Get recent trades"""
    try:
        trades = trade_logger.get_recent_trades(limit)
        return {"trades": trades}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/signals")
async def get_signals(model: Optional[str] = None):
    """Get latest AI signals"""
    try:
        # Load latest signals from file
        today = datetime.now().strftime("%Y%m%d")
        signal_file = f"data/daily_report_{today}.json"
        
        if os.path.exists(signal_file):
            with open(signal_file, 'r') as f:
                report = json.load(f)
                signals = report.get('signals', [])
                
                if model:
                    signals = [s for s in signals if s['model'] == model]
                
                return {"signals": signals}
        
        return {"signals": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/performance")
async def get_performance():
    """Get performance metrics"""
    try:
        metrics = performance_tracker.get_metrics()
        equity_curve = performance_tracker.get_equity_curve()
        
        return {
            "metrics": metrics,
            "equity_curve": equity_curve
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/manual-trade")
async def manual_trade(ticker: str, action: str, quantity: int):
    """Execute manual trade (override AI)"""
    try:
        if action not in ["BUY", "SELL"]:
            raise HTTPException(status_code=400, detail="Action must be BUY or SELL")
        
        result = trader.execute_manual_trade(ticker, action, quantity)
        trade_logger.log_trade(result)
        
        return {"success": True, "trade": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/run-strategy")
async def trigger_strategy():
    """Manually trigger strategy execution"""
    try:
        run_daily_strategy()
        return {"success": True, "message": "Strategy executed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/models")
async def get_models():
    """Get loaded models info"""
    return {
        "loaded_models": list(MODELS.keys()),
        "model_groups": MODEL_GROUPS,
        "tickers": ALL_TICKERS
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
