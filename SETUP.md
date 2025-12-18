# セットアップガイド

このドキュメントでは、Binance to MoneyForward Syncの初期セットアップ手順を詳しく説明します。

## 目次

1. [前提条件の確認](#前提条件の確認)
2. [Binance APIキーの取得](#binance-apiキーの取得)
3. [マネーフォワードの準備](#マネーフォワードの準備)
4. [GitHub Secretsの設定](#github-secretsの設定)
5. [設定ファイルのカスタマイズ](#設定ファイルのカスタマイズ)
6. [初回実行とテスト](#初回実行とテスト)
7. [トラブルシューティング](#トラブルシューティング)

## 前提条件の確認

以下のアカウントとアクセス権限が必要です：

- [ ] GitHubアカウント（このリポジトリへのアクセス権）
- [ ] Binanceアカウント
- [ ] マネーフォワードアカウント
- [ ] 基本的なGitの知識

## Binance APIキーの取得

### ステップ1: Binanceにログイン

1. [Binance](https://www.binance.com/)にアクセス
2. アカウントにログイン

### ステップ2: API管理画面を開く

1. 右上のアカウントアイコンをクリック
2. 「API Management」を選択

### ステップ3: 新しいAPIキーを作成

1. 「Create API」ボタンをクリック
2. ラベルを入力（例: "MoneyForward Sync"）
3. 2段階認証を完了

### ステップ4: 権限を設定

**重要**: セキュリティのため、以下の権限のみを有効にしてください：

- ✅ **Enable Reading** (読み取り)
- ❌ Enable Spot & Margin Trading (取引) - **無効にする**
- ❌ Enable Futures (先物) - **無効にする**
- ❌ Enable Withdrawals (出金) - **無効にする**

### ステップ5: APIキーとシークレットを保存

1. API Keyをコピーして安全な場所に保存
2. Secret Keyをコピーして安全な場所に保存
3. **注意**: Secret Keyは一度しか表示されません

## マネーフォワードの準備

### ステップ1: 手動入力資産を作成

1. [マネーフォワード](https://moneyforward.com/)にログイン
2. 「資産」タブをクリック
3. 「口座」→「金融機関を追加」をクリック
4. 「その他」→「手動で資産を管理」を選択

### ステップ2: 各暗号資産用の口座を作成

同期したい各暗号資産について、以下の手順を繰り返します：

1. 「財産」カテゴリを選択
2. 口座名を入力（例: "Binance BTC"）
3. 初期残高は「0」円で設定
4. 「登録」をクリック

**推奨される口座名**:
- `Binance BTC` - Bitcoin用
- `Binance ETH` - Ethereum用
- `Binance USDT` - Tether用
- `Binance BNB` - Binance Coin用

### ステップ3: 2段階認証の確認

**重要**: マネーフォワードで2段階認証を有効にしている場合、このツールは動作しません。2段階認証を無効にするか、別の方法を検討してください。

## GitHub Secretsの設定

### ステップ1: リポジトリのSettings画面を開く

1. このリポジトリのページに移動
2. 「Settings」タブをクリック
3. 左サイドバーの「Secrets and variables」→「Actions」をクリック

### ステップ2: シークレットを追加

「New repository secret」ボタンをクリックして、以下の4つのシークレットを追加します：

#### 1. BINANCE_API_KEY

- Name: `BINANCE_API_KEY`
- Secret: Binanceで取得したAPI Key
- 「Add secret」をクリック

#### 2. BINANCE_API_SECRET

- Name: `BINANCE_API_SECRET`
- Secret: Binanceで取得したSecret Key
- 「Add secret」をクリック

#### 3. MONEYFORWARD_USER

- Name: `MONEYFORWARD_USER`
- Secret: マネーフォワードのメールアドレス
- 「Add secret」をクリック

#### 4. MONEYFORWARD_PASSWORD

- Name: `MONEYFORWARD_PASSWORD`
- Secret: マネーフォワードのパスワード
- 「Add secret」をクリック

### ステップ3: シークレットの確認

設定後、以下の4つのシークレットが表示されていることを確認してください：

- BINANCE_API_KEY
- BINANCE_API_SECRET
- MONEYFORWARD_USER
- MONEYFORWARD_PASSWORD

## 設定ファイルのカスタマイズ

### ステップ1: config.yamlを編集

リポジトリの`config.yaml`ファイルを開いて編集します。

### ステップ2: 同期する資産を設定

マネーフォワードで作成した口座に合わせて設定します：

```yaml
assets:
  - symbol: BTC
    account_name: "Binance BTC"
  
  - symbol: ETH
    account_name: "Binance ETH"
  
  - symbol: USDT
    account_name: "Binance USDT"
```

**注意**: `account_name`はマネーフォワードで作成した口座名と完全に一致させてください。

### ステップ3: 対応している暗号資産

Binanceで取引可能な全ての暗号資産に対応しています。主な例：

| Symbol | 名称 |
|--------|------|
| BTC | Bitcoin |
| ETH | Ethereum |
| USDT | Tether |
| BNB | Binance Coin |
| XRP | Ripple |
| ADA | Cardano |
| DOGE | Dogecoin |
| SOL | Solana |
| DOT | Polkadot |
| MATIC | Polygon |

### ステップ4: リトライ設定（オプション）

必要に応じてリトライ設定を調整できます：

```yaml
retry:
  max_attempts: 3      # 失敗時の最大試行回数
  delay_seconds: 60    # リトライ間隔（秒）
```

### ステップ5: 変更をコミット

```bash
git add config.yaml
git commit -m "Update config for my assets"
git push origin main
```

## 初回実行とテスト

### ステップ1: GitHub Actionsを有効化

1. リポジトリの「Actions」タブをクリック
2. ワークフローが無効になっている場合、「I understand my workflows, go ahead and enable them」をクリック

### ステップ2: 手動実行でテスト

1. 「Actions」タブで「Binance to MoneyForward Sync」ワークフローを選択
2. 「Run workflow」ボタンをクリック
3. 「Run workflow」を再度クリックして実行開始

### ステップ3: 実行ログを確認

1. 実行中のワークフローをクリック
2. 「sync」ジョブをクリック
3. 各ステップのログを確認

**成功の確認ポイント**:
- ✅ "Binance client initialized"
- ✅ "BTC balance: X.XXXX"
- ✅ "Successfully updated Binance BTC"
- ✅ "All syncs completed successfully"

### ステップ4: マネーフォワードで確認

1. マネーフォワードにログイン
2. 「資産」タブで各口座の残高が更新されていることを確認

## トラブルシューティング

### エラー: "Required environment variables are not set"

**原因**: GitHub Secretsが正しく設定されていない

**解決策**:
1. Settings → Secrets and variables → Actions を確認
2. 4つのシークレットが全て設定されているか確認
3. シークレット名のスペルミスがないか確認

### エラー: "Binance API error"

**原因**: APIキーが無効、または権限が不足

**解決策**:
1. BinanceのAPI管理画面でAPIキーが有効か確認
2. 「Enable Reading」権限が有効になっているか確認
3. IPアドレス制限を設定している場合は解除
4. GitHub Secretsに正しいキーが設定されているか確認

### エラー: "Login timeout" / "Login error"

**原因**: マネーフォワードへのログインに失敗

**解決策**:
1. メールアドレスとパスワードが正しいか確認
2. 2段階認証が有効になっている場合は無効化
3. マネーフォワードのログイン画面が変更されている可能性
   - この場合、`main.py`の修正が必要

### エラー: "Account 'Binance BTC' not found"

**原因**: マネーフォワードに該当する口座が存在しない

**解決策**:
1. マネーフォワードで手動入力資産を作成
2. `config.yaml`の`account_name`が口座名と完全に一致しているか確認
3. 大文字小文字、スペースも含めて完全一致が必要

### ワークフローが実行されない

**原因**: スケジュールが正しく設定されていない、またはリポジトリが非アクティブ

**解決策**:
1. `.github/workflows/sync.yml`が正しくコミットされているか確認
2. リポジトリがアーカイブされていないか確認
3. 60日間活動がないとスケジュール実行が無効化される
   - 手動実行で再度有効化される

### GitHub Actions実行時間制限

**無料プランの制限**:
- パブリックリポジトリ: 無制限
- プライベートリポジトリ: 月2,000分

**対策**:
- パブリックリポジトリとして運用（推奨）
- または有料プランにアップグレード

## セキュリティのチェックリスト

セットアップ完了後、以下を確認してください：

- [ ] Binance APIキーは読み取り専用権限のみ
- [ ] GitHub Secretsに機密情報が正しく保存されている
- [ ] `.env`ファイルは`.gitignore`に含まれている（ローカル実行時）
- [ ] リポジトリのアクセス権限が適切に設定されている
- [ ] 定期的にログを確認する計画がある

## サポート

問題が解決しない場合は、以下の情報を含めてGitHub Issueを作成してください：

1. エラーメッセージの全文
2. GitHub Actionsのログ（機密情報は削除）
3. 実行環境（パブリック/プライベートリポジトリ）
4. 試した解決策

## 次のステップ

セットアップが完了したら：

1. 毎日の自動実行を待つ（デフォルト: JST 23:00）
2. 定期的にログを確認
3. 必要に応じて`config.yaml`を更新
4. マネーフォワードで資産推移を確認

おめでとうございます！セットアップが完了しました 🎉
