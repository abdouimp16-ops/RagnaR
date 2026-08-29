import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
TELEGRAM_ADMIN_ID = os.getenv("TELEGRAM_ADMIN_ID", "")

# Account
ACCOUNT_BALANCE = float(os.getenv("ACCOUNT_BALANCE", 1000))
BASE_RISK_PCT = float(os.getenv("BASE_RISK_PCT", 0.5))

# Safety
PAPER_MODE = os.getenv("PAPER_MODE", "true").lower() == "true"
LIVE_TRADING = os.getenv("LIVE_TRADING", "false").lower() == "true"

# Operations
SIGNAL_HOUR_UTC = int(os.getenv("SIGNAL_HOUR_UTC", 8))

# Notion
NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
NOTION_TRADES_DB = os.getenv("NOTION_TRADES_DB", "")
NOTION_WEEKLY_DB = os.getenv("NOTION_WEEKLY_DB", "")

# Exchange
EXCHANGE = "binance"
QUOTE = "USDT"
TIMEFRAME = "4h"

# Data
CANDLES = 800
LOOKAHEAD = 60
EMBARGO_PCT = 0.01

# Model thresholds
MIN_PROB = 0.55
MIN_CONVICTION = 0.60
MIN_EXPECTANCY_R = 0.30
MAX_PSI = 0.25
PBO_LIMIT = 0.35
DEFLATED_SHARPE_LIMIT = 0.95
AUC_MIN = 0.53

# Risk
MAX_RISK_PCT = 2.2
VOL_TARGET_DAILY = 1.2
KELLY_FRACTION = 0.5
WILSON_Z = 1.96

# Regimes
N_REGIMES = 4

# Sizing multipliers
MULT_CLASS = {"A+": 1.6, "A": 1.0, "B": 0.5}

# Kill switches
MAX_DRAWDOWN_R = -8
MAX_SLIPPAGE_MULT = 2.0

# Macro events
MACRO_BLOCK_HOURS_BEFORE = 3
MACRO_BLOCK_HOURS_AFTER = 2

# Paths
DATA_DIR = "data"
REGISTRY_DIR = os.path.join(DATA_DIR, "registry")
DB_PATH = os.path.join(DATA_DIR, "apex.db")
SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "BNB/USDT",
    "XRP/USDT",
    "ADA/USDT",
    "AVAX/USDT",
    "LINK/USDT",
    "DOGE/USDT",
    "TON/USDT",
    "DOT/USDT",
    "NEAR/USDT",
    "ARB/USDT",
    "OP/USDT",
    "INJ/USDT",
    "SUI/USDT",
    "APT/USDT",
    "LTC/USDT",
    "ATOM/USDT",
    "FIL/USDT",
]
SYMBOLS = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT",
    "XRP/USDT", "ADA/USDT", "AVAX/USDT", "LINK/USDT",
    "DOGE/USDT", "TON/USDT", "DOT/USDT", "NEAR/USDT",
    "ARB/USDT", "OP/USDT", "INJ/USDT", "SUI/USDT",
    "APT/USDT", "LTC/USDT", "ATOM/USDT", "FIL/USDT",
]
