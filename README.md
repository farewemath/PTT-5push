# PTT-5push

檢查是否有 5 推相同的情況

實際上只是把 5 推以上符合關鍵字的情況列表，請自行檢查是否相似

==

需求模組:
--
PTTLibrary, json, numpy, pandas


執行方式:
-
於 settings.json 調完參數，之後直接 python dup5push.py 執行

或是 python -O dup5push.py 省略 debug 文字

dup5push.py 和 settings.json 需要在同一目錄底下

結果會存進 output_push_keyword_post.txt 
和 output_push_keyword_author.txt 當中


參數設定: 
--
在**settings.json**中

ID: PTT帳號

Password: PTT密碼

relogin: 斷線後至多重連幾次

pushLB: 分析不低於多少則推的文 (不重要)

pushUB: 分析不高於多少則推的文 (不得小於pushLB) (不重要)

Board:分析哪個版

startId: 要分析的起始文章編號

endId: 要分析的結束文章編號

keywords: ["字串一", "字串二", ...]

mode: 請使用 PUSH_SEARCH_BY_KEYWORD
      另一個是 PUSH_COUNTING 為計算推文數，當初編寫時作為測試用途
      

其他: 
--      

本程式修改自 Daniel34569/PTTCrawler

本程式效能取決於 PTTLibrary 連線良好程度，偶爾會自動斷線

如果自動重新登入會循環鬼打牆的話，請按 Ctrl + Break 強制停止程式

