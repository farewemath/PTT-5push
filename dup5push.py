# -*- coding: utf-8 -*-
import sys
from PTTLibrary import PTT
import json
import numpy as np
import pandas as pd
from collections import Counter

print('Import end.')


#Initial Global Param
PTTBot = PTT.Library(kickOtherLogin=False)

relogin = 0
pushLB = 0
pushUB = 100
Board  = 'Test'
startId= 0
endId  = 0
keywords = ['key']
mode   = 'Default'

nameDict = {}

Month={'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}

#Read Setting
def readSettings():
    Errflag = False

    setting = []
    st = pd.read_json('./settings.json', orient='records', encoding='utf-8')
    setting.append(st["ID"].values[0])
    setting.append(st["Password"].values[0])

    global relogin, pushLB, pushUB, Board, startId, endId, keywords, mode
    
    try:
        relogin= int(st["relogin"].values[0])
        pushLB = int(st["pushLB"].values[0])
        pushUB = int(st["pushUB"].values[0])
        Board  = st["Board"].values[0]
        startId= int(st["startId"].values[0])
        endId  = int(st["endId"].values[0])
        keywords = st["keywords"].values[0]
        mode   = st["mode"].values[0]
    except ValueError:
        Errflag = True
        print('Error in reading settings: ')
        print('    relogin, pushLB, pushUB, startId, endId should be integers.')
    
    if pushLB < -100:
        pushLB = -100
    if pushUB > 100:
        pushUB = 100
    if pushLB > pushUB:
        Errflag = True
        print('Error in reading settings: ')
        print('    pushLB should not be greater then pushUB.')
    if relogin < 0:
        Errflag = True
        print('Error in reading settings: ')
        print('    relogin should be nonnegative integer.')
    if startId <= 0 or endId <= 0:
        Errflag = True
        print('Error in reading settings: ')
        print('    startId, endId should be positive integers.')
    if startId > endId:
        Errflag = True
        print('Error in reading settings: ')
        print('    startId should not be greater then endId.')
    if mode != 'PUSH_COUNTING' and mode != 'PUSH_SEARCH_BY_KEYWORD' \
                               and mode != 'PUSH_SORT_BY_AUTHOR':
        Errflag = True
        print('Error in reading settings: ')
        print('    invalid mode.')
    if mode == 'PUSH_SEARCH_BY_KEYWORD' and len(keywords) == 0:
        Errflag = True
        print('Error in reading settings: ')
        print('    no keywords.')	
    if Errflag:
       sys.exit()
       
    return setting    

def PTTlogin(ID, password):
    global PTTBot
    ErrCode = PTTBot.login(ID, password)
    if ErrCode != PTT.ErrorCode.Success:
        PTTBot.Log('Login Failed.')
        sys.exit()
    return


#PushCounting
def PushCounting(ErrCode, Post, i, fo):
    if ErrCode != PTT.ErrorCode.Success:
        print('id', i, 'deleted')
        return
        
    global startId
    pushCount  = 0
    booCount   = 0
    arrowCount = 0

    for push in Post.getPushList():
        if push.getType() == PTT.PushType.Push:
            pushCount  += 1
        elif push.getType() == PTT.PushType.Boo:
            booCount   += 1
        elif push.getType() == PTT.PushType.Arrow:
            arrowCount += 1    

    print('Test', i)
    mystr = 'id ' + str(i) + ': push ' + str(pushCount)  \
                           + ', boo ' + str(booCount)    \
                           + ', arrow ' + str(arrowCount)
    if __debug__ :
        print(mystr)
        
    fo.write(mystr + '\n')
    startId += 1
    
    return
    
 
def myCharLen(c):
    if '\u2e80' <= c and c <= '\uffff':  #chinese
        return 2
    if '\u2010' <= c and c <= '\u202f':  #...
        return 2
    if '\u00a0' <= c and c <= '\u00ff':  #latin
        return 2
    if '\u2100' <= c and c <= '\u27ff':  #math + symbol
        return 2
    return 1

def myStrLen(s):
    count = 0
    for c in s:
        count += myCharLen(c)
    return count

def pushMiniString(push):
    temp = ''
    if push.getType() == PTT.PushType.Push:
        temp += '推 '
    elif push.getType() == PTT.PushType.Boo:
        temp += '噓 '
    elif push.getType() == PTT.PushType.Arrow:
        temp += '→ '
    temp += push.getAuthor() + ': '
    return temp;
    
def pushString(push):
    temp = pushMiniString(push)
    content = push.getContent()
    count = 5
    num = 0
    
    try:
        content.encode(encoding = 'cp950')
    except:
        content = '■■ Error: 本行有無法轉換字符 ■■'
    
    temp += content
    count += len(push.getAuthor())    
    count += myStrLen(content)

    if 67 >= count:
        num = 67 - count
    temp += ' ' * num
    temp += push.getTime()
    return temp
    
def postPID(Post):
    global Board
    return '#' + Post.getID() + ' (' + Board + ')'
    


def updateOutfile(lines, fopost):
    if lines == []:
        return
    fopost.write('\n')
    for line in lines:
        try:
            fopost.write(line + '\n')
        except:
            print('Error in updating output: encode error?')
    return
    
def getNameDict(lines):
    global nameDict
    for line in lines:
        if line:
            if line[0] == '#':
                continue
            else:
                aut = line.split(':')[0][2:]
                if aut in nameDict:
                    nameDict[aut] += 1
                else:
                    nameDict[aut] = 1
    return
    
#PushKeyword
def PushKeyword(ErrCode, Post, i, fopost):
    global startId
    if ErrCode != PTT.ErrorCode.Success:
        print('id', i, 'deleted')
        startId += 1
        return
    
    if __debug__:
        print('Do', i, '... ', end = '')
    
    tempLines = []
    isAnyPushMatch = False
    global keywords
    
    for push in Post.getPushList():
        for k in keywords:
            if push.getContent().find(k) >= 0:  # found
                if not isAnyPushMatch:
                    tempLines.append(postPID(Post))
                    isAnyPushMatch = True
                tempLines.append(pushString(push))
                break

    # separate PTT part and update part
    # in order to prevent suddenly PTT offline
    updateOutfile(tempLines, fopost)
    startId += 1
    
    if __debug__:
        print('done.')

    return
    

#PushKeywordSortByAuthor
def PushKeywordSortByAuthor(fopost, foauthor):
    global nameDict
    hline = '=============================================================================='
    
    lines = [line.rstrip() for line in fopost if line.rstrip()]
    getNameDict(lines)

    if __debug__:    
        for n in nameDict:
            if nameDict[n] >= 5:
                print('* ', end = '')
                print(n, nameDict[n])
            #else:
            #    print('  ', end = '')
            #print(n, nameDict[n])
    
    for n in nameDict:
        if nameDict[n] < 5:
            continue;
        
        foauthor.write('\n' + hline + '\n')
        foauthor.write('\n' + n + '\n')
        
        PID = ''
        isThisPIDhasAnyPushMatch = False
        
        for line in lines:
            if line:
                if line[0] == '#':
                    PID = line
                    isThisPIDhasAnyPushMatch = False
                if n == line[2:2+len(n)]:  # matched
                    if not isThisPIDhasAnyPushMatch:
                       foauthor.write('\n' + PID + '\n')
                       isThisPIDhasAnyPushMatch = True
                    foauthor.write(line + '\n')
    return            

    
    
#Main
def main():
    global PTTBot
    global relogin
    global Board
    global startId
    global endId
    global keywords
    global mode
    global nameDict

    PushCountingSuccess = False
    PushKeywordSuccess = False
    reloginFlag = False
    ctrlCFlag = False

    setting = readSettings()

    #Show Params
    print(' ')
    print('Relogin times:', relogin, 'left.')
    print('Target Board:', Board)
    print('Push over', pushLB, 'and under', pushUB, 'will be analysis.')
    print('Analysis posts from', startId, 'to', endId)
    print('Keywords:', end = ' ')
    for s in keywords:
        print(s, end = ' ')
    print('')
    print('')
    
    if mode == 'PUSH_COUNTING':
        open('./output_push_counting.txt', 'w').close()
    if mode == 'PUSH_SEARCH_BY_KEYWORD':
        open('./output_push_keyword_post.txt', 'w').close()
    if mode == 'PUSH_SORT_BY_AUTHOR':
        relogin = -1    # jump the login part
    
    #Analyse
    while relogin >= 0:
        try:
            #Login
            PTTlogin(str(setting[0]),str(setting[1]))
            
            if mode == 'PUSH_COUNTING':
                fo = open('./output_push_counting.txt', 'a')
                for i in range(startId, endId+1):
                    ErrCode, Post = PTTBot.getPost(Board = Board, PostIndex = i)
                    PushCounting(ErrCode, Post, i, fo)
                PushCountingSuccess = True
                break
        
            if mode == 'PUSH_SEARCH_BY_KEYWORD':
                if __debug__:
                    print('PushKeyword start.')

                fopost   = open('./output_push_keyword_post.txt', 'a')
                for i in range(startId, endId+1):
                    ErrCode, Post = PTTBot.getPost(Board = Board, PostIndex = i)
                    PushKeyword(ErrCode, Post, i, fopost)
            
                if __debug__:
                    print('PushKeyword success.')
                fopost.close()
                PushKeywordSuccess = True
                break
        

        except KeyboardInterrupt:
            relogin = -1
            ctrlCFlag = True
        
        #Relogin
        except:            
            if relogin >= 0:
                print(relogin, 'Relogin times remain...')
                relogin -= 1
                if relogin >= 0:
                    reloginFlag = True
                else:
                    print('PushKeyword fails.  Running till', startId)
            continue
        
        finally:
            #Logout
            PTTBot.logout()
            if ctrlCFlag == True:
                sys.exit()
            if reloginFlag == True:
                reloginFlag = False
                PTTBot = PTT.Library(kickOtherLogin=False)
            if mode == 'PUSH_COUNTING':
                fo.close()
            if mode == 'PUSH_SEARCH_BY_KEYWORD':
                fopost.close()
        
        
            
        
    #LaterAnalyse
    try:
        if (mode == 'PUSH_SEARCH_BY_KEYWORD' and PushKeywordSuccess) \
                                             or mode == 'PUSH_SORT_BY_AUTHOR':
            if __debug__:
                print('SortbyAuthor start.')

            fopost   = open('./output_push_keyword_post.txt', 'r')
            foauthor = open('./output_push_keyword_author.txt', 'w')
            
            PushKeywordSortByAuthor(fopost, foauthor)

            if __debug__:
                print('SortbyAuthor success.')
            fopost.close()
            foauthor.close()
            
    finally:
        if (mode == 'PUSH_SEARCH_BY_KEYWORD' and PushKeywordSuccess) \
                                             or mode == 'PUSH_SORT_BY_AUTHOR':
            fopost.close()
            foauthor.close()


#Run
main()
