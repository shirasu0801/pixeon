# フロントエンド

React + TypeScript + Viteを使用した画像認識アプリのフロントエンドです。

## セットアップ

1. 依存関係をインストール
```bash
npm install
```

2. 環境変数を設定（オプション）
`.env`ファイルを作成して以下を設定:
```
VITE_API_BASE_URL=http://localhost:8000
```

## 実行

```bash
npm run dev
```

アプリケーションは http://localhost:5173 で起動します。

## ビルド

```bash
npm run build
```

## 機能

- ユーザー登録・ログイン
- 画像アップロード
- 物体検出（YOLOv8）
- 解析履歴の表示・削除
