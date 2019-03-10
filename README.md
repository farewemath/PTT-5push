# PTT-5push

檢查是否有 5 推相同的情況

實際上只是把 5 推以上符合關鍵字的情況列表，請自行檢查是否相似

==

需求模組:
--
PTTLibrary,json,numpy,pandas

執行方式:
-
調整完參數之後直接 python 執行

dup5push.py 和 settings.json 需要在同一目錄底下

結果會存進 output_push_keyword_post.txt 
和 output_push_keyword_author.txt 當中


參數設定: 
--
在**settings.json**中

ID: PTT帳號

Password: PTT密碼

relogin: 斷線後至多重連幾次

pushLB: 分析不低於多少則推的文

pushUB: 分析不高於多少則推的文 (不得小於pushLB)

Board:分析哪個版

startId: 要分析的起始文章編號

endId: 要分析的結束文章編號

keywords: ["字串一", "字串二", ...]

mode: 請使用 PUSH_SEARCH_BY_KEYWORD
      另一個是 PUSH_COUNTING 為計算推文數，當初編寫時作為測試用途
      