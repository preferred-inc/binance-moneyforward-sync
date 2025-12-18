# Google Cloud Run セットアップガイド

このドキュメントでは、Google Cloud Run Jobsを使用してBinance to MoneyForward Syncをデプロイする手順を説明します。

## 目次

1. [前提条件](#前提条件)
2. [Google Cloud プロジェクトの準備](#google-cloud-プロジェクトの準備)
3. [gcloud CLIのインストール](#gcloud-cliのインストール)
4. [シークレットの設定](#シークレットの設定)
5. [デプロイ](#デプロイ)
6. [スケジュール実行の設定](#スケジュール実行の設定)
7. [手動実行とテスト](#手動実行とテスト)
8. [トラブルシューティング](#トラブルシューティング)

## 前提条件

- Googleアカウント
- クレジットカード（無料枠内でも登録必要）
- Binance APIキーとシークレット
- マネーフォワードのログイン情報
- マネーフォワードに作成済みの口座（Binance BTC、ETH、SOL、USDT）

## Google Cloud プロジェクトの準備

### ステップ1: Google Cloud Consoleにアクセス

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. Googleアカウントでログイン

### ステップ2: 新しいプロジェクトを作成

1. 画面上部のプロジェクト選択ドロップダウンをクリック
2. 「新しいプロジェクト」をクリック
3. プロジェクト名を入力（例: "binance-sync"）
4. 「作成」をクリック

### ステップ3: プロジェクトIDを確認

作成後、プロジェクトIDをメモしてください（例: `binance-sync-123456`）

### ステップ4: 請求先アカウントを設定

1. 左メニューから「お支払い」を選択
2. クレジットカード情報を登録
3. **注意**: 無料枠内であれば課金されません

## gcloud CLIのインストール

### macOS

```bash
# Homebrewを使用
brew install --cask google-cloud-sdk

# 初期化
gcloud init
```

### Linux

```bash
# スクリプトでインストール
curl https://sdk.cloud.google.com | bash

# シェルを再起動
exec -l $SHELL

# 初期化
gcloud init
```

### Windows

1. [Google Cloud SDK インストーラー](https://cloud.google.com/sdk/docs/install)をダウンロード
2. インストーラーを実行
3. PowerShellまたはコマンドプロンプトで `gcloud init` を実行

### 初期化手順

```bash
# ログイン
gcloud auth login

# プロジェクトを設定
gcloud config set project YOUR_PROJECT_ID

# デフォルトリージョンを設定（東京）
gcloud config set run/region asia-northeast1
```

## シークレットの設定

### 方法1: スクリプトを使用（推奨）

```bash
# リポジトリのルートディレクトリで実行
./setup-secrets.sh
```

プロンプトに従って以下を入力：
- BINANCE_API_KEY
- BINANCE_API_SECRET
- MONEYFORWARD_USER（メールアドレス）
- MONEYFORWARD_PASSWORD

### 方法2: 手動で設定

```bash
# Secret Manager APIを有効化
gcloud services enable secretmanager.googleapis.com

# 各シークレットを作成
echo -n "YOUR_BINANCE_API_KEY" | gcloud secrets create BINANCE_API_KEY --data-file=-
echo -n "YOUR_BINANCE_API_SECRET" | gcloud secrets create BINANCE_API_SECRET --data-file=-
echo -n "YOUR_EMAIL@example.com" | gcloud secrets create MONEYFORWARD_USER --data-file=-
echo -n "YOUR_PASSWORD" | gcloud secrets create MONEYFORWARD_PASSWORD --data-file=-
```

### シークレットの確認

```bash
# 作成されたシークレットを確認
gcloud secrets list
```

## デプロイ

### ステップ1: deploy.shを編集

`deploy.sh`ファイルを開いて、プロジェクトIDを設定：

```bash
PROJECT_ID="your-gcp-project-id"  # ← ここを変更
```

### ステップ2: デプロイスクリプトを実行

```bash
./deploy.sh
```

このスクリプトは以下を自動実行します：
1. 必要なAPIの有効化
2. Dockerイメージのビルド
3. Container Registryへのプッシュ
4. Cloud Run Jobの作成/更新

### デプロイ時間

初回デプロイは5-10分程度かかります。

## スケジュール実行の設定

### ステップ1: サービスアカウントを作成

```bash
# サービスアカウントを作成
gcloud iam service-accounts create binance-sync-scheduler \
    --display-name="Binance Sync Scheduler"

# プロジェクトIDを取得
PROJECT_ID=$(gcloud config get-value project)

# サービスアカウントのメールアドレス
SA_EMAIL="binance-sync-scheduler@${PROJECT_ID}.iam.gserviceaccount.com"

# Cloud Run Invoker権限を付与
gcloud run jobs add-iam-policy-binding binance-moneyforward-sync \
    --region=asia-northeast1 \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/run.invoker"
```

### ステップ2: Cloud Schedulerジョブを作成

```bash
# プロジェクトIDを取得
PROJECT_ID=$(gcloud config get-value project)
SA_EMAIL="binance-sync-scheduler@${PROJECT_ID}.iam.gserviceaccount.com"

# スケジューラーを作成（毎日23:00 JST）
gcloud scheduler jobs create http binance-sync-scheduler \
    --location=asia-northeast1 \
    --schedule="0 23 * * *" \
    --time-zone="Asia/Tokyo" \
    --uri="https://asia-northeast1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/binance-moneyforward-sync:run" \
    --http-method=POST \
    --oauth-service-account-email="${SA_EMAIL}"
```

### スケジュールの変更

```bash
# スケジュールを更新（例: 毎日22:00に変更）
gcloud scheduler jobs update http binance-sync-scheduler \
    --location=asia-northeast1 \
    --schedule="0 22 * * *"
```

### スケジュールの確認

```bash
# スケジューラージョブを確認
gcloud scheduler jobs list --location=asia-northeast1
```

## 手動実行とテスト

### Cloud Run Jobを手動実行

```bash
gcloud run jobs execute binance-moneyforward-sync \
    --region=asia-northeast1
```

### 実行ログを確認

```bash
# 最新の実行を確認
gcloud run jobs executions list \
    --job=binance-moneyforward-sync \
    --region=asia-northeast1 \
    --limit=1

# 実行IDを取得してログを表示
EXECUTION_ID=$(gcloud run jobs executions list \
    --job=binance-moneyforward-sync \
    --region=asia-northeast1 \
    --limit=1 \
    --format="value(name)")

gcloud logging read "resource.labels.job_name=binance-moneyforward-sync AND resource.labels.execution_name=${EXECUTION_ID}" \
    --limit=100 \
    --format=json
```

### Cloud Consoleでログを確認

1. [Cloud Console](https://console.cloud.google.com/)にアクセス
2. 左メニューから「Cloud Run」→「Jobs」を選択
3. `binance-moneyforward-sync`をクリック
4. 「ログ」タブを選択

## トラブルシューティング

### エラー: "Permission denied"

**原因**: 権限が不足している

**解決策**:
```bash
# プロジェクトのオーナー権限を確認
gcloud projects get-iam-policy $(gcloud config get-value project)

# 必要に応じてオーナー権限を付与
gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
    --member="user:YOUR_EMAIL@gmail.com" \
    --role="roles/owner"
```

### エラー: "API not enabled"

**原因**: 必要なAPIが有効化されていない

**解決策**:
```bash
# 必要なAPIを有効化
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### エラー: "Secret not found"

**原因**: シークレットが作成されていない

**解決策**:
```bash
# シークレットを確認
gcloud secrets list

# 不足しているシークレットを作成
./setup-secrets.sh
```

### エラー: "Container failed to start"

**原因**: Dockerイメージのビルドまたは実行エラー

**解決策**:
```bash
# ローカルでDockerイメージをテスト
docker build -t test-image .
docker run --rm \
    -e BINANCE_API_KEY="YOUR_KEY" \
    -e BINANCE_API_SECRET="YOUR_SECRET" \
    -e MONEYFORWARD_USER="YOUR_EMAIL" \
    -e MONEYFORWARD_PASSWORD="YOUR_PASSWORD" \
    test-image

# ログを確認
gcloud logging read "resource.type=cloud_run_job" --limit=50
```

### スケジューラーが実行されない

**原因**: サービスアカウントの権限不足

**解決策**:
```bash
# サービスアカウントの権限を確認
gcloud run jobs get-iam-policy binance-moneyforward-sync \
    --region=asia-northeast1

# Invoker権限を再付与
PROJECT_ID=$(gcloud config get-value project)
SA_EMAIL="binance-sync-scheduler@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud run jobs add-iam-policy-binding binance-moneyforward-sync \
    --region=asia-northeast1 \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/run.invoker"
```

## コスト管理

### 無料枠の確認

Cloud Run Jobsの無料枠：
- 月180万vCPU秒
- 月360万GBメモリ秒
- 月200万リクエスト

このツールの使用量（1日1回実行）：
- 実行時間: 約5-10分
- vCPU: 1
- メモリ: 1GB
- 月間使用量: 約300-600 vCPU秒（無料枠の0.03%）

### コストの監視

```bash
# 請求情報を確認
gcloud billing accounts list

# 予算アラートを設定（推奨）
# Cloud Console → お支払い → 予算とアラート
```

## セキュリティのベストプラクティス

### 1. シークレットの管理

- ✅ Secret Managerを使用
- ✅ シークレットを直接コードに含めない
- ✅ 定期的にAPIキーをローテーション

### 2. 権限の最小化

```bash
# サービスアカウントに最小限の権限のみ付与
gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/run.invoker"
```

### 3. ログの監視

定期的にログを確認して異常な動作を検出：

```bash
# エラーログのみ表示
gcloud logging read "resource.type=cloud_run_job AND severity>=ERROR" \
    --limit=50
```

## 次のステップ

1. ✅ デプロイ完了
2. ✅ 手動実行でテスト
3. ✅ スケジュール実行を設定
4. ✅ マネーフォワードで残高を確認
5. 📊 定期的にログを確認

## サポート

問題が発生した場合は、以下の情報を含めてGitHub Issueを作成してください：

1. エラーメッセージの全文
2. 実行ログ（機密情報は削除）
3. 使用しているgcloud CLIのバージョン
4. 実行環境（OS、バージョン）

おめでとうございます！セットアップが完了しました 🎉
