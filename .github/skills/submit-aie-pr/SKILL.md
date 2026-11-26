---
name: submit-aie-pr
description: AIE2026 の課題を終了し、対象回の作業ブランチを push して、自分の fork の main へ PR を作成する。Use when asked to submit, finish, or create a pull request for an AIE2026 lecture exercise or homework.
---

# AIE2026 PR提出

## 目的

指定された第N回の課題を終了し、次を完了する。

1. 対象回の作業ブランチを作成または使用する。
2. この課題で変更したファイルだけをコミットする。
3. fork に push する。
4. 自分の fork の `main` を base とした PR を作成する。
5. 作成した PR の URL を報告する。

講座の元リポジトリへ PR を作成しない。

課題中に作成・更新したスキルやエージェント共通ルールも、このPRの課題変更として含める。
対象に含めるものは、少なくとも次を確認する。

- `AGENTS.md`（またはリポジトリの各階層にある `AGENTS.md`）
- `.github/skills/**/SKILL.md`
- 課題固有のスキルやエージェント設定
- 課題で変更した `lectures/NN/answer.md`
- 課題で変更した実装、テスト、設定、スクリプト、参考ファイル

## 対象回の特定

次の優先順位で第N回を特定する。

1. ユーザーが指定した回。
2. 現在のブランチ名（例: `lec01`）。
3. 対象の `lectures/NN/answer.md` と課題変更。

不明な場合は推測せず、ユーザーへ確認する。

対象回のブランチ名は `lecNN` とし、回番号は二桁で表す。

## 開始前の確認

次を確認する。

```bash
git --no-pager status --short
git --no-pager branch --show-current
git remote -v
```

- 作業開始前から存在する変更と、今回の課題で変更するファイルを区別する。
- `AGENTS.md`、`.github/skills/**/SKILL.md`、課題回答、課題実装について、
  作業中に更新されたか確認し、課題成果ならコミット対象に含める。
- 作業開始時点の変更一覧と、現在の変更一覧を比較し、課題中に新規追加されたファイル、
  更新されたファイルを特定する。
- 不明な変更はコミット、追加、削除しない。
- 移行前のブランチで作業している場合は、課題差分を失わないことを確認してから `lecNN` を作成する。
- 新規ブランチの作成先が存在しない場合、次を実行する。

```bash
git switch -c lecNN
```

既存ブランチがある場合は、意図しないブランチ切り替えを避けて確認する。

## 提出前の検証

対象課題を確認し、足りない項目や未記入項目を報告する。

```bash
uv run pytest -q
git --no-pager diff --stat
git --no-pager diff -- lectures/NN/answer.md
```

課題でAPIを使う場合は、キーなしテストだけで正常完了と扱わない。
テスト失敗、未実行項目、秘密情報の混入がある場合は、修正して再検証するか、
そのまま提出せずユーザーに報告する。

## コミット対象

今回の課題で変更したファイルだけを明示的に指定する。
課題中に作ったスキルやエージェント設定も、無関係な変更ではなく課題成果として
検討し、依頼者が学習の成果物として残したいものならステージする。

例:

```bash
git add \
  AGENTS.md \
  .github/skills/submit-aie-pr/SKILL.md \
  lectures/NN/answer.md \
  app/example.py \
  tests/test_example.py
git diff --cached --check
git diff --cached --stat
git diff --cached
git commit -m "第N回 演習"
```

- `git add -A` と `git add .` は使わない。
- `AGENTS.md` と `.github/skills/**/SKILL.md` を、課題の成果物として明示的に確認する。
- 新しく作った課題用スキル、プロンプト、エージェント設定がある場合は、課題差分に含めるかを判定する。
- 課題成果として不要な生成物やキャッシュは除外する。
- APIキー、環境ファイル、キャッシュ、生成物、既存の無関係な変更をコミットしない。
- コミット前にステージ済み差分を確認する。
- 複数の課題変更が混ざっている場合はコミットせず、分離方法を確認する。

コミットメッセージは課題内容に合わせて短くする。

## push

現在のリモート構成を確認し、自分の fork を正しく特定する。

```bash
git remote -v
git remote get-url origin
git status --short --branch
git push -u origin lecNN
```

`origin` が講座の元リポジトリを指している場合は、ユーザーの fork のリモートを
確認または追加する。fork のリモート名は既存の設定を優先し、勝手に既存URLを変更しない。

元リポジトリへ直接 push しようとしている場合は、実行せずに報告する。

## PR作成

GitHub CLI が利用できる場合は、以下で作成する。

```bash
gh pr create \
  --repo <fork-owner>/<fork-repository> \
  --base main \
  --head <fork-owner>:lecNN \
  --title "第N回 演習・宿題" \
  --body "AIE2026 第N回の演習・宿題を提出します。"
```

`<fork-owner>/<fork-repository>` はリモート URLから fork を特定する。
既に同じ head から main へのPRがある場合は、重複作成せず既存PRを報告する。

```bash
gh pr view lecNN --repo <fork-owner>/<fork-repository>
```

GitHub CLI がない、認証されていない、または権限不足の場合は、
push と base/head の指定を報告し、手動作成URLを提示する。

```text
https://github.com/<fork-owner>/<fork-repository>/compare/main...<fork-owner>:lecNN?expand=1
```

## 完了報告

最低限、次を報告する。

- 対象回とブランチ名
- コミットに含めたファイル
- テスト結果
- push先
- PR URL、または自動作成できなかった理由と手動作成URL
