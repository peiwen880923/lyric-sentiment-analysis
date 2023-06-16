import requests
from selenium import webdriver
import time
from snownlp import SnowNLP
import jieba.analyse
from opencc import OpenCC

def web_crawler():
    #KKBOX華語新歌日榜網址
    url="https://kma.kkbox.com/charts/daily/newrelease?terr=tw&lang=tc#"
    count=[2,3,4,5,6]
    options = webdriver.ChromeOptions()
    driver=webdriver.Chrome(chrome_options=options,executable_path="chromedriver")
    driver.get(url)
    time.sleep(3)
    content=[]
    lyrics=[]
    #抓取前5名的歌曲資訊
    for i in range(len(count)):
        time.sleep(2)
        #抓取歌曲名稱及歌手名稱
        song=driver.find_element("xpath",'/html/body/div[3]/div/div[2]/ul/li['+str(count[i])+']/a/div/div[1]/span[1]/span[1]').text
        singer=driver.find_element("xpath",'/html/body/div[3]/div/div[2]/ul/li['+str(count[i])+']/a/div/div[1]/span[1]/span[2]').text
        #點擊歌曲名稱進入歌曲資訊頁面並抓取歌詞
        driver.find_element("xpath",'/html/body/div[3]/div/div[2]/ul/li['+str(count[i])+']/a/div/div[1]/span[1]/span[1]').click()
        lyric=driver.find_element("xpath",'/html/body/main/div[2]/div[1]').text.replace('\n','')
        time.sleep(2)
        #回到排行榜頁面
        driver.get(url)
        #到Youtube搜尋該歌曲的YT網址
        yt_url="https://www.youtube.com/results?search_query="+song+"+"+singer
        driver1=webdriver.Chrome(chrome_options=options,executable_path="chromedriver")
        driver1.get(yt_url)
        time.sleep(2)
        yt=driver1.find_element("xpath",'//*[@id="video-title"]').get_attribute("href")
        #將歌曲名稱、歌手名稱、YT網址及歌詞存入content中
        content.append([song,singer,yt])
        lyrics.append(lyric)
    print(content)
    driver.close()
    driver1.close()
    return content,lyrics

def sentiment_analysis(lyrics):
    cc = OpenCC('t2s')
    jieba.set_dictionary('dict.txt.big')
    jieba.load_userdict('userdict.txt')
    with open('stops.txt', 'r', encoding='utf8') as f: 
        stops = f.read().split('\n') 
    avg=[]
    for i in range(len(lyrics)):
        text=lyrics[i]
        total=0
        count=0
        for sent in text.split("\n"): 
            sent_words=[t for t in jieba.cut(sent) if t not in stops and t.split() and len(t)>1]
        for i in sent_words:
            new_i=cc.convert(i)
            s=SnowNLP(new_i)
            total+=s.sentiments
            count+=1
        average=total/count
        avg.append(average)
    return avg

# LINE Notify 權杖
token = 'nVrffNorEJJVJgkXHiP8UGQn3YRf1BFTLlyEhjrS6l6'

content,lyrics=web_crawler()
avg=sentiment_analysis(lyrics)
for i in range(0,len(content)):
    content[i].append(avg[i])

# 要發送的訊息
message = '\n今日華語新歌日榜前5名:\n\n'
for i in range(len(content)):
    message1='第'+str(i+1)+'名:'+str(content[i][0])+'\n歌手:'+str(content[i][1])+'\nYT網址:'+str(content[i][2])+'\n情緒數值:'+str(content[i][3])+'\n\n'
    message+=message1
message+="<註>情緒數值愈接近1，歌曲愈正面；數值愈接近0，歌曲愈負面"
print(message)

# HTTP 標頭參數與資料
headers = { "Authorization": "Bearer " + token }
data = { 'message': message }

# 以 requests 發送 POST 請求
requests.post("https://notify-api.line.me/api/notify",
    headers = headers, data = data)