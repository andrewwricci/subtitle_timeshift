# JDrama Subtitle Timeshift
Japanese translation follows below

This is a simple tool for fixing timing on TV show subtitles, specifically for JDramas.

If you've ever downloaded subtitles from a site like jpsubbers, you probably notice 
that the subtitles include commerical breaks, which then need to be adjusted to match 
the commercial-less show that you've downloaded.

This tool allows you to, either manually or automatically, remove the commerical break 
gaps from the subtitle files.

## Dependency Install
```
pip3 install -r requirements.txt
```

## Execution Examples

Automatically adjust one file, adding new suffix "fix"\
Starting commerical break 30 seconds, all other commerical breaks 120 seconds
```
python3 main.py -o subtitle.srt -a fix -first 30 -following 120 -auto true
```
Manually adjust all srt files in current directory\
No commerical break at start, all commerical breaks > 90 seconds
```
python3 main.py -o ALL -first 0 -following 90                 
```

# ドラマ字幕タイムシフト
このツールはテレビ番組、特に日本のドラマの字幕のタイムコードを編集できるツールです。

もしjpsubbersのようなサイトから字幕をダウンロードしたことがあったら、
字幕ファイルにコマーシャルの時間が入ってることを気づいてダウンロードした番組と
一緒に使うたびに字幕ファイルを編集しないといけなかったはずです。

このツールで、自動でも手動でも、コマーシャルの時間を字幕ファイルから除けます。

## 依存関係をインストール
```
pip3 install -r requirements.txt
```

## 実行の例

自動的に一つのファイルを編集して、「fix」のサフィックスを追加します。\
番組の前のコマーシャルは30秒、他は120秒です。
```
python3 main.py -o subtitle.srt -a fix -first 30 -following 120 -auto true
```
手動で全てのディレクトリーの字幕を編集します。\
番組の前のコマーシャルはなく、全てのコマーシャルは90秒以下です。
```
python3 main.py -o ALL -first 0 -following 90                      
```
