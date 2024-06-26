# このレポジトリの説明
## ファイル構成
1～4の.pyファイルがあるが、実際に毎日実行するのは4だけ。
1～3は、実行するための前処理用のファイル。
|ファイル|1_url_collector.py|2_open_url.py|3_first_check.py|4_scraping_rate.py|5_check_robots_txt.py|
|:--:|:--|:--|:--|:--|:--|
|機能|seleniumパッケージを使って、グーグルで銀行名と預金金利を検索し、最初の検索結果のURLを自動的に収集する|URLのリストから、10個ずつブラウザで自動的に開く（CSSセレクターを効率的に集めるため）|URLとCSSセレクタのリストから、スクレイピングがうまくいくかを試す|本番用ファイル|対象サイトがクローリング許可サイトか確認する|
|入出力ファイル|banks_list.csvから銀行名を読み取って、banks_output.csvに銀行名とURLの一覧を出力する|banks_output.csvからURLを読み取って開く（それを使って手動でCSSセレクターを収集し、banks_list_ok.csvを作成する）|banks_list_ok.csvからURLとCSSセレクタのリストを読み取り、スクレイピングを実施し、その結果をfirst_check_result2.csvに出力する|first_check_result.csvを読み取って、結果をyokin_rate.xlsxに付記する（ファイルがなければ作成する）|対象金融機関のウェブサイトのrobots.txtを確認し、クローリングを許可しているかどうかを自動で確認する|

# 補足的な説明
## タスクスケジューラへのタスク登録方法（ここでは、4.scraping_rate.pyをタスク登録することを想定しています）
- タスクスケジューラを開く:
    - Windowsキー + Sを押して「タスクスケジューラ」と入力し、タスクスケジューラを開きます。

- 「タスクの作成」を選択:
    - 右側の「基本タスクの作成」をクリックします。
    - 「タスクの作成」ウィザードが開きます。

- タスクの名前と説明を入力:
    - タスクの名前を入力し、必要なら説明を入力します（例: Daily Python Script）。
    - 「次へ」をクリックします。

- トリガーの設定:
    - 「毎日」を選択し、「次へ」をクリックします。
    - スクリプトの実行開始日時と時間を設定します（例: 明日の朝6時に設定）。
    - 「次へ」をクリックします。

- 操作の設定:
    - 「プログラムの開始」を選択し、「次へ」をクリックします。

- プログラム/スクリプトの設定:
    - 「プログラム/スクリプト」に以下のようにWinPythonの実行ファイルのフルパスを入力します。（例．C:\Users\ryasu\WinPython-3.12.x\python-3.12.x.amd64\python.exe）
    - 「引数の追加 (オプション)」にスクリプトのフルパスを入力します。（例:C:\Users\ryasu\Documents\GitHub\web_scraping\4_scraping_rate.py）

- 完了:
    - 「次へ」をクリックして、「完了」をクリックします。

## パスの通し方（タスクスケジューラが動くようにするためには、当然ながらpythonのパスを通しておかないといけないので、その方法）
- WinPythonのインストールディレクトリを開く:
    - WinPythonのインストールパスを確認します。例えば、C:\Users\ryasu\WinPython-3.12.xのようになっているかもしれません。
    - Pythonの実行ファイルがあるフォルダ（通常はpython-3.12.x.amd64など）を探します。

- Python実行ファイルのパスをコピー:
    - 例: C:\Users\ryasu\WinPython-3.12.x\python-3.12.x.amd64

- Windowsのシステム設定を開く:
    - Windowsキー + Sを押して「環境変数」と入力し、「システム環境変数の編集」をクリックします。

- 環境変数ダイアログを開く:
    - 「システムのプロパティ」ウィンドウが開いたら、「環境変数」をクリックします。

- Path変数を編集:
    - 「システム環境変数」の一覧から「Path」を選択し、「編集」をクリックします。

- 新しいパスを追加:
    - 「新規」ボタンをクリックし、Python実行ファイルのパスを追加します。（例: C:\Users\ryasu\WinPython-3.12.x\python-3.12.x.amd64）

- 変更を保存:
    - 「OK」をクリックして変更を保存し、すべてのダイアログを閉じます。
