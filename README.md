# Binance to MoneyForward Sync

Binanceの暗号資産残高を日本円換算でマネーフォワードに自動同期するツールです。

## 特徴

- **複数通貨対応**: BTC、ETH、SOL、USDTなど、Binanceで取引可能な全ての暗号資産に対応
- **自動JPY換算**: 直接JPYペアまたはUSDT経由で自動的に日本円換算
- **スケジュール実行**: Google Cloud Run Jobsで毎日自動実行
- **完全無料**: Cloud Runの無料枠内で動作（月180万vCPU秒）
- **エラーハンドリング**: リトライ機構と詳細なログ出力

## アーキテクチャ

```
┌─────────────────────────────────────────┐
│      Google Cloud Run Jobs              │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │    Docker Container               │ │
│  │  ┌─────────────┐  ┌────────────┐ │ │
│  │  │   main.py   │  │ config.yaml│ │ │
│  │  └──────┬──────┘  └────────────┘ │ │
│  │         │                         │ │
│  │    ┌────┴────┐                   │ │
│  │    │         │                   │ │
│  │    ▼         ▼                   │ │
│  │ ┌─────┐  ┌──────────┐           │ │
│  │ │Binance│ │MoneyForward│         │ │
│  │ │ API  │  │ Selenium │           │ │
│  │ └─────┘  └──────────┘           │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
         │                    │
         ▼                    ▼
    Binance API        MoneyForward Web
```

## クイックスタート

### 前提条件

- Googleアカウント
- Binance APIキー（読み取り専用権限）
- マネーフォワードアカウント
- マネーフォワードに作成済みの手動入力資産

### セットアップ手順

1. **リポジトリをクローン**

```bash
git clone https://github.com/preferred-inc/binance-moneyforward-sync.git
cd binance-moneyforward-sync
```

2. **Google Cloud プロジェクトを作成**

[Google Cloud Console](https://console.cloud.google.com/)で新しいプロジェクトを作成

3. **gcloud CLIをインストール**

```bash
# macOS
brew install --cask google-cloud-sdk

# Linux
curl https://sdk.cloud.google.com | bash

# 初期化
gcloud init
```

4. **シークレットを設定**

```bash
./setup-secrets.sh
```

5. **デプロイ**

`deploy.sh`を編集してプロジェクトIDを設定後：

```bash
./deploy.sh
```

6. **スケジュール実行を設定**

詳細は[CLOUDRUN_SETUP.md](CLOUDRUN_SETUP.md)を参照

## ファイル構成

```
binance-moneyforward-sync/
├── main.py                   # メインスクリプト
├── config.yaml               # 設定ファイル
├── requirements.txt          # Python依存関係
├── Dockerfile                # Docker設定
├── .dockerignore             # Docker除外設定
├── deploy.sh                 # デプロイスクリプト
├── setup-secrets.sh          # シークレット設定スクリプト
├── README.md                 # このファイル
├── CLOUDRUN_SETUP.md         # 詳細セットアップガイド
└── .env.example              # 環境変数サンプル
```

## 設定

### config.yaml

同期する暗号資産を設定：

```yaml
assets:
  - symbol: BTC
    account_name: "Binance BTC"
  
  - symbol: ETH
    account_name: "Binance ETH"
  
  - symbol: SOL
    account_name: "Binance SOL"
  
  - symbol: USDT
    account_name: "Binance USDT"

retry:
  max_attempts: 3
  delay_seconds: 60
```

**注意**: `account_name`はマネーフォワードで作成した口座名と完全に一致させてください。

## 使い方

### 手動実行

```bash
gcloud run jobs execute binance-moneyforward-sync \
    --region=asia-northeast1
```

### ログ確認

```bash
# 最新の実行ログを表示
gcloud logging read "resource.type=cloud_run_job" --limit=50
```

### スケジュール変更

```bash
# 実行時刻を変更（例: 毎日22:00 JST）
gcloud scheduler jobs update http binance-sync-scheduler \
    --location=asia-northeast1 \
    --schedule="0 22 * * *"
```

## 対応通貨

Binanceで取引可能な全ての暗号資産に対応しています。主な例：

| Symbol | 名称 | JPY換算方法 |
|--------|------|------------|
| BTC | Bitcoin | 直接JPYペア |
| ETH | Ethereum | 直接JPYペア |
| USDT | Tether | 直接JPYペア |
| SOL | Solana | USDT経由 |
| BNB | Binance Coin | USDT経由 |
| XRP | Ripple | USDT経由 |
| ADA | Cardano | USDT経由 |
| DOGE | Dogecoin | USDT経由 |

## コスト

### Google Cloud Run Jobs 無料枠

- 月180万vCPU秒（約500時間）
- 月360万GBメモリ秒
- 月200万リクエスト

### このツールの使用量（1日1回実行）

- 実行時間: 約5-10分
- vCPU: 1
- メモリ: 1GB
- **月間コスト: 無料枠内（$0）**

## セキュリティ

### Binance APIキー

以下の権限のみを有効にしてください：

- ✅ **Enable Reading** (読み取り)
- ❌ Enable Spot & Margin Trading (取引) - **無効**
- ❌ Enable Futures (先物) - **無効**
- ❌ Enable Withdrawals (出金) - **無効**

### シークレット管理

- Google Cloud Secret Managerで安全に管理
- コードやログにシークレットを含めない
- 定期的にAPIキーをローテーション

## トラブルシューティング

### エラー: "Account not found"

**原因**: マネーフォワードに該当する口座が存在しない

**解決策**:
1. マネーフォワードで手動入力資産を作成
2. `config.yaml`の`account_name`が口座名と完全一致しているか確認

### エラー: "Binance API error"

**原因**: APIキーが無効または権限不足

**解決策**:
1. BinanceのAPI管理画面でAPIキーが有効か確認
2. 「Enable Reading」権限が有効になっているか確認
3. シークレットが正しく設定されているか確認

### エラー: "Login failed"

**原因**: マネーフォワードへのログインに失敗

**解決策**:
1. メールアドレスとパスワードが正しいか確認
2. 2段階認証が無効になっているか確認
3. マネーフォワードのログイン画面が変更されている可能性

詳細は[CLOUDRUN_SETUP.md](CLOUDRUN_SETUP.md)のトラブルシューティングセクションを参照してください。

## 制限事項

1. **マネーフォワード2段階認証**: 有効時は動作不可
2. **DOM変更**: マネーフォワードのサイト変更時にコード修正が必要
3. **実行時間**: 1回の実行は最大30分（通常は5-10分）

## 今後の拡張案

- [ ] 他の取引所対応（Coinbase、Kraken等）
- [ ] 他の家計簿対応（Zaim、Moneytree等）
- [ ] Slack/Discord通知
- [ ] 履歴管理とグラフ化
- [ ] Web UI

## ライセンス

MIT License - 詳細は[LICENSE](LICENSE)を参照

## サポート

問題が発生した場合は、[GitHub Issues](https://github.com/preferred-inc/binance-moneyforward-sync/issues)で報告してください。

## 貢献

プルリクエストを歓迎します！大きな変更の場合は、まずIssueで議論してください。

---

**注意**: このツールは非公式であり、Binanceやマネーフォワードとは関係ありません。自己責任でご使用ください。
