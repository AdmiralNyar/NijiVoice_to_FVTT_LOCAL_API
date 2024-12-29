# NijiVoice_to_FVTT_LOCAL_API
にじボイス[^1]APIとFoundryVTTのmodule [Bouyomichan Connector](https://github.com/AdmiralNyar/Bouyomichan-Connector)とやり取りをするためのデスクトップアプリです<br>
当アプリは非公式なものであり、このアプリを使用した時のエラー等の問い合わせについてはこのGithubリポジトリにお願いします。<br>

Windows10[^2]で実行可能です(11は未検証)
<br>
<br>
<br>


# インストールの仕方と使い方
1. 右側リリース内の最新のリリースから、`hontai.zip`ファイルをダウンロードして解凍してください
 <br>
 <br>

2. `NijiVoice_to_Foundry.exe`というアプリケーションを実行してください
<br>
<br>

3. 実行すると下のようなコマンドラインとアプリケーションウィンドウが表示されます

![コマンドラインとアプリケーションウィンドウ](https://github.com/user-attachments/assets/c9498da8-bae1-49c3-90b6-edca8c658c97)

<br>
<br>

4. にじボイス APIのアクセスキーを➊に入力します
<br>
<br>

5. にじボイス APIのアクセスキーは、まずにじボイスAPIにログインします
![にじボイスAPIのログイン](https://github.com/user-attachments/assets/f2b1a2f3-7868-41ff-adf2-d7ffe2c32e87)
<br>
<br>

6.次にAPIキーをクリックし、眼のマークをクリックすれば確認できます
![にじボイスAPIのアクセスキーの場所](https://github.com/user-attachments/assets/906a15bb-ff77-473c-8f3c-345415fedce3)
<br>
<br>

7.起動するポート番号を➋に入力し、指定します（特別の理由が無ければ2000のままで問題ないです）
<br>
<br>

8.Foundry VTTのアドレスを➌に入力します
<br>
<br>

9.自分のPCでFoundry Virtual Tabletop.exe（Foundry VTTデスクトップアプリ）を起動している場合にはローカル（家の中）のアドレスを使用してください
![ローカルFoundry](https://github.com/user-attachments/assets/df43eb87-10a5-4a94-91a4-17553c2dbf03)
<br>
<br>

10.Forgeを使用している場合には、Game URLのアドレスを使用してください
![ForgeFoundry](https://github.com/user-attachments/assets/80dec1a7-7dda-4cd0-9f07-6c9413abb389)
<br>
<br>

11. 生成した音声ファイルをPC上に自動保存する場合には「音声ファイルをダウンロードする」にチェックをつけて、フォルダを指定してください
<br>
<br>

12. 「サーバーを立ち上げる」ボタンを押すとアプリケーションウィンドウが閉じてコマンドラインが下のようになります。黄色線の文字をCTRL+Cキーでコピーしてください。
<br>
<br>
![サーバー起動](https://github.com/user-attachments/assets/2bd21e2e-ae00-4b32-8c38-9c1de6801c4a)


<br>
<br>

13. CTRL+Cでコピーした内容（デフォルトでは、http://localhost:2000） をBouyomichan ConnectorのMODを有効化したワールドの「コンフィグ設定」⇒「Bouyomichan Connector」⇒「NijiVoice to FoundryアプリケーションのAPIサーバーアドレス」に張り付けて「変更内容を保存」してください
![URLを入力する](https://github.com/user-attachments/assets/3f00c453-3efe-4dc0-a39c-baaa5862d2e6)
<br>
<br>

14.「NijiVoice to FoundryアプリケーションのAPIサーバーアドレス」の欄が表示されておらず、「にじボイスとの連携機能」に✓が入っていなければ、✓を入れて「変更を保存」し、リロードしてください
<br>
<br>

15.Bouyomichan Connectorの設定については、[Bouyomichan Connectorの説明](https://github.com/AdmiralNyar/Bouyomichan-Connector)を参照してください（残クレジットの通知やにじボイスの資料の作製等について）
<br>
<br>

16.サーバーのコンソールウィンドウはコンソールウィンドウをマウスで選択中にキーボードのCTRL+Cを2回押すことで閉じることができます
<br>
<br>

# 出力音声について
このNijiVoice_to_Foundry自体が、にじボイスAPIにより生成された音声ファイルURLデータを受け取った時に、その音声を自動再生しています。<br>
音量（最大）を調整する場合やミキサーを使用する場合には、タスクバー上のWindowsのマークを右クリック＞「設定」＞「システム」＞「サウンド」＞「アプリの音量とデバイスの設定」から設定を変更できます。
![アプリの音量とデバイスの設定](https://github.com/user-attachments/assets/116905e2-efaf-48de-aa8b-928f216f325e)
<br>
<br>

# EXEファイルについて
現在、Windowsでは外部認証を受けていないアプリケーションについて一律に保護表示をするようになっています。外部認証には年額6万円ほどかかるため、このアプリは認証をしていません。<br>
この画面が表示された場合、「詳細情報」をクリックすると「実行」ボタンが表示されるようになるので、実行してください。
![SmartScreen](https://github.com/user-attachments/assets/c3d1693f-2dda-436b-bbf9-38388c299714)
![SmartScreen実行](https://github.com/user-attachments/assets/28faa0a8-f459-467d-9abd-1532032c04fd)

実行形式ファイルの中身が心配な人は、Python 3.10.4(32bit)にてPyInstaller(5.0.1)で`pyinstaller NijiVoice_to_Foundry.spec`を実行してください（NijiVoice_to_Foundry.pyファイル内でimportしているパッケージをインストールください）

[^1]:にじボイスは株式会社Algomaticが運営するサービスです。
[^2]:Windows10, Edgeは、MicrosoftCorporationの米国及びその他の国における商標または登録商標です。
