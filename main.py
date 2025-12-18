#!/usr/bin/env python3
"""
Binance to MoneyForward Sync
Binanceの暗号資産残高を日本円換算でマネーフォワードに同期
"""

import os
import sys
import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import yaml

try:
    from binance.client import Client as BinanceClient
    from binance.exceptions import BinanceAPIException
except ImportError:
    print("Error: python-binance is not installed. Run: pip install python-binance")
    sys.exit(1)

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError:
    print("Error: selenium is not installed. Run: pip install selenium")
    sys.exit(1)


# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class AssetConfig:
    """資産設定"""
    symbol: str
    account_name: str


@dataclass
class Config:
    """アプリケーション設定"""
    assets: List[AssetConfig]
    retry_max_attempts: int = 3
    retry_delay_seconds: int = 60
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'Config':
        """YAMLファイルから設定を読み込む"""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        assets = [
            AssetConfig(symbol=a['symbol'], account_name=a['account_name'])
            for a in data.get('assets', [])
        ]
        
        retry_config = data.get('retry', {})
        
        return cls(
            assets=assets,
            retry_max_attempts=retry_config.get('max_attempts', 3),
            retry_delay_seconds=retry_config.get('delay_seconds', 60)
        )


class BinanceService:
    """Binance API操作"""
    
    def __init__(self, api_key: str, api_secret: str):
        self.client = BinanceClient(api_key, api_secret)
        logger.info("Binance client initialized")
    
    def get_asset_balance_jpy(self, symbol: str) -> Optional[float]:
        """
        指定した資産の残高を日本円換算で取得
        
        Args:
            symbol: 資産シンボル（例: BTC, ETH）
        
        Returns:
            日本円換算の残高、エラー時はNone
        """
        try:
            # 資産残高を取得
            balance = self.client.get_asset_balance(asset=symbol)
            if not balance:
                logger.warning(f"Asset {symbol} not found")
                return None
            
            free_amount = float(balance['free'])
            locked_amount = float(balance['locked'])
            total_amount = free_amount + locked_amount
            
            if total_amount == 0:
                logger.info(f"{symbol} balance is zero")
                return 0.0
            
            logger.info(f"{symbol} balance: {total_amount} (free: {free_amount}, locked: {locked_amount})")
            
            # JPYペアの価格を取得
            jpy_pair = f"{symbol}JPY"
            try:
                ticker = self.client.get_symbol_ticker(symbol=jpy_pair)
                jpy_price = float(ticker['price'])
            except BinanceAPIException:
                # 直接のJPYペアがない場合、USDTを経由
                logger.info(f"{jpy_pair} pair not found, trying via USDT")
                usdt_pair = f"{symbol}USDT"
                usdt_jpy_pair = "USDTJPY"
                
                usdt_ticker = self.client.get_symbol_ticker(symbol=usdt_pair)
                usdt_price = float(usdt_ticker['price'])
                
                jpy_ticker = self.client.get_symbol_ticker(symbol=usdt_jpy_pair)
                jpy_per_usdt = float(jpy_ticker['price'])
                
                jpy_price = usdt_price * jpy_per_usdt
            
            total_jpy = total_amount * jpy_price
            logger.info(f"{symbol} total value: ¥{total_jpy:,.2f} (price: ¥{jpy_price:,.2f})")
            
            return total_jpy
            
        except BinanceAPIException as e:
            logger.error(f"Binance API error for {symbol}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting {symbol} balance: {e}")
            return None


class MoneyForwardService:
    """マネーフォワード操作"""
    
    def __init__(self, email: str, password: str, profile_path: Optional[str] = None):
        self.email = email
        self.password = password
        self.profile_path = profile_path
        self.driver = None
        logger.info("MoneyForward service initialized")
    
    def _setup_driver(self):
        """Chromeドライバーのセットアップ"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        if self.profile_path:
            options.add_argument(f'--user-data-dir={self.profile_path}')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)
        logger.info("Chrome driver setup completed")
    
    def _login(self):
        """マネーフォワードにログイン"""
        try:
            logger.info("Attempting to login to MoneyForward")
            self.driver.get("https://moneyforward.com/sign_in")
            
            # メールアドレス入力
            email_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "sign_in_session_service_email"))
            )
            email_input.send_keys(self.email)
            
            # パスワード入力
            password_input = self.driver.find_element(By.ID, "sign_in_session_service_password")
            password_input.send_keys(self.password)
            
            # ログインボタンをクリック
            login_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
            login_button.click()
            
            # ログイン完了を待機
            time.sleep(5)
            logger.info("Login successful")
            
        except TimeoutException:
            logger.error("Login timeout")
            raise
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise
    
    def update_account(self, account_name: str, amount: float) -> bool:
        """
        マネーフォワードの口座残高を更新
        
        Args:
            account_name: 口座名
            amount: 残高（日本円）
        
        Returns:
            成功時True、失敗時False
        """
        try:
            if not self.driver:
                self._setup_driver()
                self._login()
            
            logger.info(f"Updating account '{account_name}' to ¥{amount:,.2f}")
            
            # 資産画面に移動
            self.driver.get("https://moneyforward.com/accounts")
            time.sleep(3)
            
            # 口座を検索して更新
            # 注: 実際のDOM構造に応じて要素の特定方法を調整する必要があります
            accounts = self.driver.find_elements(By.CSS_SELECTOR, ".account-item")
            
            for account in accounts:
                try:
                    name_element = account.find_element(By.CSS_SELECTOR, ".account-name")
                    if account_name in name_element.text:
                        # 編集ボタンをクリック
                        edit_button = account.find_element(By.CSS_SELECTOR, ".edit-button")
                        edit_button.click()
                        time.sleep(2)
                        
                        # 残高を入力
                        balance_input = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.ID, "account_balance"))
                        )
                        balance_input.clear()
                        balance_input.send_keys(str(int(amount)))
                        
                        # 保存
                        save_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
                        save_button.click()
                        time.sleep(2)
                        
                        logger.info(f"Successfully updated {account_name}")
                        return True
                        
                except NoSuchElementException:
                    continue
            
            logger.warning(f"Account '{account_name}' not found")
            return False
            
        except Exception as e:
            logger.error(f"Error updating account {account_name}: {e}")
            return False
    
    def close(self):
        """ドライバーを閉じる"""
        if self.driver:
            self.driver.quit()
            logger.info("Chrome driver closed")


class SyncService:
    """同期サービス"""
    
    def __init__(self, config: Config, binance: BinanceService, moneyforward: MoneyForwardService):
        self.config = config
        self.binance = binance
        self.moneyforward = moneyforward
    
    def sync_asset(self, asset: AssetConfig) -> bool:
        """単一の資産を同期"""
        logger.info(f"Syncing {asset.symbol}...")
        
        for attempt in range(1, self.config.retry_max_attempts + 1):
            try:
                # Binanceから残高を取得
                balance_jpy = self.binance.get_asset_balance_jpy(asset.symbol)
                
                if balance_jpy is None:
                    logger.error(f"Failed to get balance for {asset.symbol}")
                    if attempt < self.config.retry_max_attempts:
                        logger.info(f"Retrying in {self.config.retry_delay_seconds} seconds... (attempt {attempt}/{self.config.retry_max_attempts})")
                        time.sleep(self.config.retry_delay_seconds)
                        continue
                    return False
                
                # マネーフォワードに更新
                success = self.moneyforward.update_account(asset.account_name, balance_jpy)
                
                if success:
                    logger.info(f"Successfully synced {asset.symbol}")
                    return True
                else:
                    if attempt < self.config.retry_max_attempts:
                        logger.info(f"Retrying in {self.config.retry_delay_seconds} seconds... (attempt {attempt}/{self.config.retry_max_attempts})")
                        time.sleep(self.config.retry_delay_seconds)
                        continue
                    return False
                    
            except Exception as e:
                logger.error(f"Error syncing {asset.symbol}: {e}")
                if attempt < self.config.retry_max_attempts:
                    logger.info(f"Retrying in {self.config.retry_delay_seconds} seconds... (attempt {attempt}/{self.config.retry_max_attempts})")
                    time.sleep(self.config.retry_delay_seconds)
                    continue
                return False
        
        return False
    
    def sync_all(self) -> Dict[str, bool]:
        """全ての資産を同期"""
        logger.info("Starting sync for all assets")
        results = {}
        
        for asset in self.config.assets:
            results[asset.symbol] = self.sync_asset(asset)
        
        # 結果サマリー
        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)
        logger.info(f"Sync completed: {success_count}/{total_count} successful")
        
        return results


def main():
    """メイン処理"""
    logger.info("=== Binance to MoneyForward Sync Started ===")
    
    # 環境変数から認証情報を取得
    binance_api_key = os.getenv('BINANCE_API_KEY')
    binance_api_secret = os.getenv('BINANCE_API_SECRET')
    mf_email = os.getenv('MONEYFORWARD_USER')
    mf_password = os.getenv('MONEYFORWARD_PASSWORD')
    chrome_profile_path = os.getenv('CHROME_PROFILE_PATH')
    
    if not all([binance_api_key, binance_api_secret, mf_email, mf_password]):
        logger.error("Required environment variables are not set")
        logger.error("Required: BINANCE_API_KEY, BINANCE_API_SECRET, MONEYFORWARD_USER, MONEYFORWARD_PASSWORD")
        sys.exit(1)
    
    # 設定ファイルを読み込み
    config_path = os.getenv('CONFIG_PATH', 'config.yaml')
    try:
        config = Config.from_yaml(config_path)
        logger.info(f"Loaded config from {config_path}")
        logger.info(f"Assets to sync: {', '.join(a.symbol for a in config.assets)}")
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        sys.exit(1)
    
    # サービスを初期化
    binance = BinanceService(binance_api_key, binance_api_secret)
    moneyforward = MoneyForwardService(mf_email, mf_password, chrome_profile_path)
    sync_service = SyncService(config, binance, moneyforward)
    
    try:
        # 同期実行
        results = sync_service.sync_all()
        
        # 結果を出力
        logger.info("=== Sync Results ===")
        for symbol, success in results.items():
            status = "✓ SUCCESS" if success else "✗ FAILED"
            logger.info(f"{symbol}: {status}")
        
        # 失敗があれば終了コード1
        if not all(results.values()):
            logger.warning("Some assets failed to sync")
            sys.exit(1)
        
        logger.info("=== All syncs completed successfully ===")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    
    finally:
        moneyforward.close()


if __name__ == '__main__':
    main()
