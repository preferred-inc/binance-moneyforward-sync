# Binance to MoneyForward Sync

Binanceの暗号資産残高を日本円換算でマネーフォワードに自動同期するツールです。GitHub Actionsで完全無料で動作し、複数の暗号資産に対応しています。

## 特徴

このツールは以下の特徴を持っています：

- **完全無料**: GitHub Actionsで動作するため、追加コストなし
- **複数通貨対応**: 設定ファイルで指定した複数の暗号資産を一括処理
- **日本円換算**: Binance APIを使用してリアルタイムのJPYレートで換算
- **自動同期**: 毎日指定時刻に自動実行（デフォルト: JST 23:00）
- **エラーハンドリング**: 包括的なエラー処理とリトライ機構
- **詳細なログ**: 実行状況を詳細に記録

## アーキテクチャ

このシステムはGitHub上で以下のコンポーネントを使用して構築されています：

| コンポーネント | 説明 |
|--------------|------|
| **GitHub Actions** | スケジュール実行環境（完全無料） |
| **GitHub Secrets** | 認証情報の安全な管理 |
| **Python 3.11** | メインロジックの実装言語 |
| **Selenium** | マネーフォワードの自動操作 |
| **python-binance** | Binance API クライアント |

## 前提条件

以下のアカウントとAPIキーが必要です：

- GitHubアカウント
- Binance API Key/Secret
- マネーフォワードアカウント

## セットアップ

### 1. リポジトリのフォークまたはクローン

このリポジトリをフォークするか、新しいリポジトリを作成してファイルをコピーします。

```bash
# 新規リポジトリを作成する場合
git clone https://github.com/preferred-inc/binance-moneyforward-sync.git
cd binance-moneyforward-sync
```

### 2. GitHub Secretsの設定

リポジトリの Settings → Secrets and variables → Actions で以下のシークレットを追加します：

| シークレット名 | 説明 | 例 |
|--------------|------|-----|
| `BINANCE_API_KEY` | Binance APIキー | `abc123...` |
| `BINANCE_API_SECRET` | Binance APIシークレット | `xyz789...` |
| `MONEYFORWARD_USER` | マネーフォワードのメールアドレス | `user@example.com` |
| `MONEYFORWARD_PASSWORD` | マネーフォワードのパスワード | `your_password` |

#### Binance APIキーの取得方法

1. [Binance](https://www.binance.com/)にログイン
2. アカウント → API管理
3. 新しいAPIキーを作成
4. **重要**: 「読み取り専用」権限のみを有効化（セキュリティのため）

### 3. 対象通貨の設定

`config.yaml`を編集して、同期したい暗号資産を設定します：

```yaml
assets:
  - symbol: BTC
    account_name: "Binance BTC"
  
  - symbol: ETH
    account_name: "Binance ETH"
  
  - symbol: USDT
    account_name: "Binance USDT"

retry:
  max_attempts: 3
  delay_seconds: 60
```

**注意**: `account_name`はマネーフォワードに登録されている口座名と一致させてください。

### 4. マネーフォワードでの準備

マネーフォワードに以下の手動入力資産を作成します：

1. マネーフォワードにログイン
2. 「資産」→「口座」→「金融機関を追加」
3. 「その他」→「手動で資産を管理」を選択
4. 各暗号資産用の口座を作成（例: "Binance BTC", "Binance ETH"）

### 5. リポジトリにプッシュ

変更をコミットしてGitHubにプッシュします：

```bash
git add .
git commit -m "Initial setup"
git push origin main
```

### 6. GitHub Actionsの有効化

1. リポジトリの「Actions」タブを開く
2. ワークフローを有効化
3. 「Run workflow」ボタンで手動実行してテスト

## 使い方

### 自動実行

デフォルトでは毎日JST 23:00（UTC 14:00）に自動実行されます。

スケジュールを変更する場合は、`.github/workflows/sync.yml`のcron設定を編集します：

```yaml
schedule:
  - cron: '0 14 * * *'  # UTC時刻で指定
```

**cron形式の例**:
- `0 14 * * *`: 毎日14:00 UTC（JST 23:00）
- `0 9 * * *`: 毎日09:00 UTC（JST 18:00）
- `0 0 * * 1`: 毎週月曜日00:00 UTC

### 手動実行

GitHub ActionsのUIから手動で実行できます：

1. リポジトリの「Actions」タブを開く
2. 「Binance to MoneyForward Sync」ワークフローを選択
3. 「Run workflow」ボタンをクリック

### ローカル実行

開発やテスト時にローカルで実行する場合：

```bash
# 依存関係のインストール
pip install -r requirements.txt

# 環境変数を設定
cp .env.example .env
# .envファイルを編集して認証情報を入力

# 実行
python main.py
```

## 設定

### 対象通貨の追加

`config.yaml`に新しいエントリを追加します：

```yaml
assets:
  - symbol: BNB
    account_name: "Binance BNB"
```

対応している通貨はBinanceで取引可能な全ての暗号資産です。JPYペアが存在しない場合は、自動的にUSDT経由で換算されます。

### リトライ設定

API呼び出しやブラウザ操作が失敗した場合のリトライ動作を設定できます：

```yaml
retry:
  max_attempts: 3      # 最大試行回数
  delay_seconds: 60    # リトライ間隔（秒）
```

## トラブルシューティング

### ログの確認

GitHub Actionsの実行ログを確認します：

1. リポジトリの「Actions」タブを開く
2. 該当するワークフロー実行をクリック
3. 「sync」ジョブのログを展開

### よくある問題

**問題**: マネーフォワードへのログインに失敗する

**解決策**: 
- GitHub Secretsの`MONEYFORWARD_USER`と`MONEYFORWARD_PASSWORD`が正しいか確認
- マネーフォワードで2段階認証を有効にしている場合は無効化が必要
- マネーフォワードのログイン画面のDOM構造が変更されている可能性があり、`main.py`の修正が必要な場合があります

**問題**: Binance APIエラー

**解決策**:
- GitHub Secretsの`BINANCE_API_KEY`と`BINANCE_API_SECRET`が正しいか確認
- Binance APIキーが有効で、読み取り権限があるか確認
- APIの利用制限に達していないか確認

**問題**: 口座が見つからない

**解決策**:
- `config.yaml`の`account_name`がマネーフォワードの口座名と完全に一致しているか確認
- マネーフォワードで該当する手動入力資産が作成されているか確認

**問題**: GitHub Actionsが実行されない

**解決策**:
- リポジトリの「Actions」タブでワークフローが有効になっているか確認
- リポジトリがプライベートの場合、GitHub Actionsの実行時間制限を確認（無料プランは月2,000分まで）
- `.github/workflows/sync.yml`が正しくコミットされているか確認

## セキュリティ

このツールは機密情報を扱うため、以下のセキュリティ対策を実施しています：

- **GitHub Secrets**: 認証情報は暗号化されて保存され、ログに出力されません
- **読み取り専用API**: Binance APIは読み取り専用権限のみを使用
- **ヘッドレスブラウザ**: Seleniumはヘッドレスモードで動作し、画面は表示されません
- **最小権限**: 必要最小限の権限のみを使用

### セキュリティのベストプラクティス

1. **Binance APIキーは読み取り専用に設定**
   - 取引権限は絶対に有効にしないでください

2. **定期的なパスワード変更**
   - マネーフォワードのパスワードを定期的に変更し、GitHub Secretsも更新

3. **プライベートリポジトリの使用**
   - 可能であればプライベートリポジトリを使用してください

4. **ログの確認**
   - 定期的にGitHub Actionsのログを確認し、異常な動作がないかチェック

## 制限事項

- **GitHub Actions実行時間**: 1回の実行は最大6時間まで（通常は数分で完了）
- **プライベートリポジトリ**: 無料プランでは月2,000分まで（パブリックリポジトリは無制限）
- **マネーフォワードのDOM変更**: マネーフォワードのWebサイト構造が変更された場合、コードの修正が必要になる可能性があります

## ライセンス

MIT License

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずIssueを開いて変更内容を議論してください。

### 開発ガイドライン

1. コードスタイルはPEP 8に準拠
2. 新機能には適切なログ出力を追加
3. エラーハンドリングを適切に実装
4. READMEを更新

## サポート

問題が発生した場合は、GitHubのIssueを作成してください。以下の情報を含めると、より迅速に対応できます：

- エラーメッセージの全文
- GitHub Actionsのログ（機密情報は削除してください）
- 使用している設定（`config.yaml`の内容）
- 期待される動作と実際の動作

## 関連リンク

- [Binance API Documentation](https://binance-docs.github.io/apidocs/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [MoneyForward](https://moneyforward.com/)
