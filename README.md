# Interactive Research Library (paper-lab)

Interactive Lab 向けの静的サイト。**`papers/*/lab.yaml` と markdown / json 成果物がソース・オブ・トゥルース。** `site/` 以下の生成 HTML はビューであり、手編集しないでください。

**人間向けライブラリ（GitHub Pages）の UI とラボ本文は日本語です。** 機械識別子（`id`、トピック slug、検証 enum 値、ファイル名・コード識別子）はフィルタ安定性のため英語のままにし、表示ラベルは日本語にしています。

これは「時間をかける価値のあるラボ」のライブラリであり、論文の投げ込みではありません。信頼できる理解までの時間を最適化します。

Python 環境は **[uv](https://docs.astral.sh/uv/)** を使います（生の `pip` / `venv` ではありません）。

## Install and build / インストールとビルド

このディレクトリから（Python 3.10+）:

```bash
uv sync --extra dev
uv run paper-lab build
# equivalent:
uv run python -m paper_lab.build
```

出力は `site/index.html` と、ラボごとの `site/papers/` です。ブラウザで `site/index.html` を開いてください（オフライン可。フィルタはクライアント側 JS、ネットワーク不要）。

Useful flags / 便利なフラグ:

```bash
uv run paper-lab build --root . --out site
uv run paper-lab build --papers papers --out /tmp/library-site
```

コミット済みの `site/` が含まれているので、Python なしでもデモできます。ラボを変えたらビルドを再実行してください。

Tests / テスト:

```bash
uv run pytest
```

GitHub Pages: `.github/workflows/pages.yml` が `uv` でインストールし、`paper-lab build` を実行して `site/` をデプロイします。

## How to add a paper lab / ラボの追加方法

1. `papers/<paper-id>/` を作成（URL 安全な slug。フィクスチャなら先頭 `_` 可）。
2. 下記スキーマで `lab.yaml` を追加。セクション本文はインライン、または同ディレクトリのファイル名（`mapping.md`、`overview.md` など）。
3. 実行したものがあれば `results.json`、論文 ↔ コード ↔ 公式リポ対応は `mapping.md`。
4. 小さな実実験が正しい媒体であるときだけコード（`baseline.py` / `proposed.py` / `run.py`）を同梱。科学を捏造しない。
5. `uv run paper-lab build` を実行し、`site/index.html` で新ページを確認。

低価値な論文にラボを**付けない**でください。レジストリ条目は別の場所にあって構いません。フル Interactive Lab は、関連性 × 新規性 × 重要性 × 根拠 × 情報利得が高く、かつ期待される理解の利得が実装・計算コストを上回る場合のみです。微小なベンチ差分、アーキテクチャだけの新規性、薄い根拠の宣伝、既知の増分拡張にはラボを付けません。

## `lab.yaml` schema

Required / 必須:

| Field | Notes |
| --- | --- |
| `id` | URL-safe slug; becomes `site/papers/<id>.html` |
| `title` | Human title（人間向け。日本語可） |
| `authors` | List of strings (or `{name: ...}`) |
| `year` | Int or string |
| `topics` | List of topic slugs（英語 slug のまま） |
| `urls` | `paper`, `arxiv`, `official_code`, `pdf` (string or `null`) |
| `verdict` | Short library verdict（表示用。日本語可） |
| `verification` | `mechanism`, `performance`, `scaling`, `production_applicability` each `CONFIRMED` \| `PARTIAL` \| `NOT OBSERVED` \| `NOT TESTED`（値は英語。UI は日本語ラベル） |
| `related_threads` | List of thread ids |
| `status` | `draft` \| `published` |

Optional: `summary`（索引カード）、`example: true`、`sections`（または `content`）で標準キー → markdown または相対ファイル名、構造化 `core_idea.author_claim` / `core_idea.research_bot_interpretation`。

標準ページ見出し（順）: 概要、問題設定、核心（著者の主張 vs Research Bot の解釈）、なぜ効きそうか（推論ラベル付き）、根拠、実行可能な理解、結果、検証できたこと、検証していないこと、実装、原論文・公式コード対応。

`mapping.md` と `results.json` は、論文ディレクトリにあれば自動で読み込まれます。

## Example lab / 例のラボ

`papers/_example_demo/` は**架空のフォーマットデモ**です。論文ではありません。数値は創作です。引用しないでください。

## Layout

```
paper-lab/
├── README.md
├── pyproject.toml
├── uv.lock
├── papers/_example_demo/   # lab.yaml + artifacts
├── paper_lab/              # generator
├── site/                   # generated output
├── tests/
└── .github/workflows/pages.yml
```
