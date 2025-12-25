import os
import io
from io import BytesIO
import time
import logging
import requests
import threading
import twstock
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from imgurpython import ImgurClient
import re
import random
from flask import Flask, request, abort, render_template
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
import yfinance as yf

app = Flask(__name__, template_folder='templates')
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# 必須放上自己的Channel Access Token
line_bot_api = LineBotApi('9yR4ewDjV8MMC1s8DCcZbCHhwYzFvoVWR8OM3XIckQaV7JSzLvIDc581psOLe+b/J7Iu7qCIrJDPFypvefXy+D4udYFHl9OSYoSXFIEkJmKpjhHPBk3UQP5Kqk37isFkfytaPpgoWh3o0mQwrS5wvQdB04t89/1O/w1cDnyilFU=')
# 必須放上自己的Channel Secret
handler = WebhookHandler('046d3499ea137d0ac4192b9224c91899')

line_bot_api.push_message('U2245cda9373cd500a6fe9e8053729eac', TextSendMessage(text='請開始你的表演'))

#一哥起床
@app.route("/")
def index():
    return render_template("./index.html")

@app.route("/wake_up")
def wake_up():
    return "Hey!Wake Up!!"

def wake_up_render():
    while 1==1:
        url = 'https://linebot-openai-1.onrender.com' + '/wake_up'
        res = requests.get(url)
        if res.status_code==200:
            print('喚醒成功')
        else:
            print('喚醒失敗')
        time.sleep(10*60)

threading.Thread(target=wake_up_render).start()

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

 
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

keyword_responses = {"你是誰": "我是煒仔啦",
                    "ㄟ": "ㄟ",
                    "駕照": "😆",
                    "bar": "粑",
                    "有喔": "有喔",
                    "豪巴": "豪巴",
                    "小炮": "小炮",
                    "賀。": "賀。",
                    "不懂": "不董",
                    "我懂": "我董",
                    "獵豹": "癡漢",
                    "哈": "哈哈哈",
                    "認同":"認同+1",
                    "小沈": "1500",
                    "小英": "1450",
                    "謝國樑": "200",
                    "啊啊": "ah-ah",
                    "小歐": "小歐滾",
                    "唐董": "唐董滾",
                    "海膽": "臭臭的",
                    "好玩的": "乙烯",
                    "博文": "powen",
                    "氧的弟弟": "硫",
                    "博文家": "失火了",
                    "幹擾": "interfere",
                    "啊~": "好舒服啊",
                    "整人嗎": "整人嗎",
                    "沒有": "沒有 通過",
                    "很玄": "這就很玄囉",
                    "可憐": "你好可憐喔",
                    "煒仔": "我是佑哥啦",
                    "佑哥": "sheehan",
                    "車號": "9796-MP",                    
                    "ok": "好來我們開始",
                    "備胎": "你有備胎嗎",
                    "明聖的專長": "政治學",
                    "在這裡": "是一條斷層",
                    '吸星大法': "吸星大法",
                    "怕厚厚": "pa-hoy-hoy",
                    "打給我": "0965386966",
                    "冰島貓男": "冰島貓男",
                    "鳴人小哥": "鳴人小哥",
                    "西螺便當": "西螺便當",
                    "翹課": "歡迎翹課來聽",
                    "升級完成": "強勢回歸",
                    "博文人呢": "還在金瓜石",
                    "岩石與礦物": "心理陰影",
                    "大象跳舞": "會導致地震",
                    "地質垂": "可以踢足球嗎",                    
                    "巴士郭先生": "巴士郭先生",
                    "我做不到": "我就是做不到",                    
                    "哇靠": "哇靠!你還真會掰啊",
                    "五年級小男生": "0937092027",
                    "一哥": "邏輯思考 x 有一說一",
                    "牙醫": "中山醫牙科他X的超級爛 別去",
                    "北車": "台北車站台鐵售票人票爆幹爛!",
                    "最後一搏": "cc 剛才去買雨鞋，潦落去了！",
                    "仇": "不要以為我們台灣人都是客客氣氣的",
                    "速速": "速速交來，不然七星劍要劈過去了",
                    "生日快樂": "Yo~Yo~ 老大生日大快樂啊！！",
                    "騙子": "一群詐騙份子，你們遲早會滅亡在東南亞!",
                    "八位小朋友": "https://www.youtube.com/watch?v=azT-0sE4UfI", 
                    "不拍就不拍啊":"https://www.dcard.tw/f/utaipei/p/260286905" ,
                    "印度神曲": "https://youtu.be/eM8Mjuq4MwQ?si=kYgSMqRdYNGNvgaE",
                    "搶頭香": "cc 搶頭香，教報告了。先繳初稿忙完國科會計畫再來繳正式版。",                  
                    "肌肉型態": "文甫你好，關於分組的事情中午我已經用信箱email給你，可能需要麻煩你看一下。",
                    "讀書會": "今天有讀書會喔! \n 地點:S104 \n 時間:17:00-19:00 \n 系學會成員一樣有專屬小點心!",
                    "恐龍咖啡廳": "正杰，坤憶 你們在今日11：00-11：20 可到臺博古生館的恐龍餐廳找老師喝杯飲料，逾時失效~",
                    "恕我拒絕": "怒我拒絕，因評估發想，第二組使用方法與我方（第五組）不同，做出的影片內容應不會有高度重複性",
                    "火星": "火星-45°c對我們來說太easy了，我們一進去火星，只要一人發動兩台摩托車就可以把溫度升上來了，所以移民火星還不錯",
                    "名單": "1林幼鎂、2林憶蓁、3王云柔、4沈煒耀、5何續恩、6莊博文、7徐楷茹、8葉宥陞、9陳皓恩、10謝語姍、11周家甫、12林昀誼、13周子堯",
                    "青鳥": "我認為現今臺灣早已跟世界脫軌,某些人只知道美國以及視中國,但也不 看清楚現在局勢,早已反轉了,我們既沒有自己的武器供應鏈也沒強大的後勤 也沒有足夠的物資,要如何與未來的超級大國爭,「弱國無外交」就是現今臺灣 面臨的問題,要如何解決臺灣問題已經不太可能了,只能苟者才能維持自己的 地位,期待青鳥不要再丟臉了。",
                    "爆車": "收到，那市立大學這邊我就結算11位囉！\n車子應該會滿載。\n還是很多人報名  我把人數撐到極限  12 人  上次舊生11位  讓出1位  補上2位  真的爆車了  林明聖  陳泓愷  王進欽  黃至韻  林立  林貫益  葉宥陞  黃翊萱（一位）陳品聿  陳佩伶  以上為舊生保障名額  賴芓涵  林幼鎂  以上為新生遞補  真的極限了",
                    "做出口碑了": "明聖  教授 早安 \n 不敢相信！ \n 5/26 大漢溪的活動已經滿車！ \n 您這邊幫我定奪需要幾位助教跟車 \n 我好辦理遞補 \n 42座位大車 \n 目前已經報名逾50位了 \n 我會辦理遞補 \n 感謝教授 \n 我們做出口碑了！ \n  \n 教授早安  \n 這樣好不好 \n 除了明聖教授+陳泓愷助教 \n 教育局幫貴校再保留2名助教參與協助行政工作? \n (總共4位) \n 畢竟這次好不容易招滿 \n 我們不適合辦理太多學生遞補",

                    "超派": StickerSendMessage(package_id="789", sticker_id="10885"),
                    "黃色小鴨": ImageSendMessage(original_content_url="https://i.imgur.com/td883jO.jpeg", preview_image_url="https://i.imgur.com/td883jO.jpeg"),
                    "行事曆": ImageSendMessage(original_content_url="https://i.meee.com.tw/z1xRcQG.jpg", preview_image_url="https://i.meee.com.tw/z1xRcQG.jpg"),
                    "雲豹": ImageSendMessage(original_content_url="https://i.imgur.com/vy670dJ.jpg", preview_image_url="https://i.imgur.com/vy670dJ.jpg"),
                    "天意": ImageSendMessage(original_content_url="https://s.yimg.com/ny/api/res/1.2/VAx4xb76m28_GmqE9cuhaw--/YXBwaWQ9aGlnaGxhbmRlcjt3PTk2MDtoPTU0MDtjZj13ZWJw/https://media.zenfs.com/ko/news_ttv_com_tw_433/f273a5380639108f8af906a33a9d4fcd", preview_image_url="https://s.yimg.com/ny/api/res/1.2/VAx4xb76m28_GmqE9cuhaw--/YXBwaWQ9aGlnaGxhbmRlcjt3PTk2MDtoPTU0MDtjZj13ZWJw/https://media.zenfs.com/ko/news_ttv_com_tw_433/f273a5380639108f8af906a33a9d4fcd"),
                    "侯侯": ImageSendMessage(original_content_url="https://cc.tvbs.com.tw/img/upload/2023/12/26/20231226181119-db1a2fd9.jpg", preview_image_url="https://cc.tvbs.com.tw/img/upload/2023/12/26/20231226181119-db1a2fd9.jpg"),
                    "垃圾": ImageSendMessage(original_content_url="https://image.taisounds.com/newsimages/img/2023/0629/20230629125144.jpg", preview_image_url="https://image.taisounds.com/newsimages/img/2023/0629/20230629125144.jpg"),
                    "領域展開": ImageSendMessage(original_content_url="https://i.imgur.com/SLlr25K.jpg", preview_image_url="https://i.imgur.com/SLlr25K.jpg"),
                    "天母校區": ImageSendMessage(original_content_url="https://i.imgur.com/8eYOH6K.jpg", preview_image_url="https://i.imgur.com/8eYOH6K.jpg"),
                    "黨徽": ImageSendMessage(original_content_url="https://i.imgur.com/1ay9q9f.jpg", preview_image_url="https://i.imgur.com/1ay9q9f.jpg"),
                    "科學館": ImageSendMessage(original_content_url="https://i.imgur.com/NHZ3Clo.jpg", preview_image_url="https://i.imgur.com/NHZ3Clo.jpg"),
                    "收回": ImageSendMessage(original_content_url="https://i.imgur.com/khAtzmm.jpg", preview_image_url="https://i.imgur.com/khAtzmm.jpg"),
                    "勤樸樓B1": ImageSendMessage(original_content_url="https://i.imgur.com/CsefOc1.jpg", preview_image_url="https://i.imgur.com/CsefOc1.jpg"),
                    "勤樸樓": ImageSendMessage(original_content_url="https://i.imgur.com/0RVIOGZ.png", preview_image_url="https://i.imgur.com/0RVIOGZ.png"),
                    "對": ImageSendMessage(original_content_url="https://memeprod.sgp1.digitaloceanspaces.com/user-wtf/1583774054073.jpg", preview_image_url="https://memeprod.sgp1.digitaloceanspaces.com/user-wtf/1583774054073.jpg"),
                    "都會粉鳥鄰": ImageSendMessage(original_content_url="https://i.imgur.com/J591zvL.jpg", preview_image_url="https://i.imgur.com/J591zvL.jpg"),
                    "蛤": ImageSendMessage(original_content_url="https://i.imgur.com/4WCAdso.png", preview_image_url="https://i.imgur.com/4WCAdso.png"),
                    "阿猴鮮乳": ImageSendMessage(original_content_url="https://imgcdn.cna.com.tw/www/WebPhotos/800/20240327/1004x768_wmkn_0_C20240327000158.jpg", preview_image_url="https://imgcdn.cna.com.tw/www/WebPhotos/800/20240327/1004x768_wmkn_0_C20240327000158.jpg"),
                    "有啊": ImageSendMessage(original_content_url="https://i.imgur.com/hXlc2oR.jpeg", preview_image_url="https://i.imgur.com/hXlc2oR.jpeg"),
                    "實驗室": ImageSendMessage(original_content_url="https://i.imgur.com/6evqzM0.jpeg", preview_image_url="https://i.imgur.com/6evqzM0.jpeg"),
                    "尤加利葉": ImageSendMessage(original_content_url="https://i.imgur.com/inOep1X.jpeg", preview_image_url="https://i.imgur.com/inOep1X.jpeg"),
                    "小碗": ImageSendMessage(original_content_url="https://lh3.googleusercontent.com/gps-cs-s/AC9h4nqM1icOnJAdwAMAVvMk2moDr_6RLlj386JW8fvrhnIUGguLHK4-X2zIquOoqryuLMNu9Xk9jSNBZW0j63D--qodQv_jKD4O4RLuRUJufTyJM4Qrdrwol6iEYBuXkq7zBi_bu1_P=s1360-w1360-h1020-rw", preview_image_url="https://lh3.googleusercontent.com/gps-cs-s/AC9h4nqM1icOnJAdwAMAVvMk2moDr_6RLlj386JW8fvrhnIUGguLHK4-X2zIquOoqryuLMNu9Xk9jSNBZW0j63D--qodQv_jKD4O4RLuRUJufTyJM4Qrdrwol6iEYBuXkq7zBi_bu1_P=s1360-w1360-h1020-rw"),
                    "不要呼攏老師": ImageSendMessage(original_content_url="https://i.meee.com.tw/kNnvGkW.jpg", preview_image_url="https://i.meee.com.tw/kNnvGkW.jpg"),
                    "太少": ImageSendMessage(original_content_url="https://i.meee.com.tw/wj53YXo.jpg", preview_image_url="https://i.meee.com.tw/wj53YXo.jpg"),
                    "坐在那邊": ImageSendMessage(original_content_url="https://i.meee.com.tw/e7S92tV.jpg", preview_image_url="https://i.meee.com.tw/e7S92tV.jpg"),
                    "實驗衣": ImageSendMessage(original_content_url="https://i.meee.com.tw/O213hvU.jpg", preview_image_url="https://i.meee.com.tw/O213hvU.jpg"),
                    "作弊阿伯": ImageSendMessage(original_content_url="https://i.meee.com.tw/PffEtwK.jpg", preview_image_url="https://i.meee.com.tw/PffEtwK.jpg"),
                    "還在等": ImageSendMessage(original_content_url="https://i.meee.com.tw/YJBqmrD.jpg", preview_image_url="https://i.meee.com.tw/YJBqmrD.jpg"),
                    "迷你鬆餅": ImageSendMessage(original_content_url="https://i.meee.com.tw/eC8ieny.jpg", preview_image_url="https://i.meee.com.tw/eC8ieny.jpg"),
                    "小吼": ImageSendMessage(original_content_url="https://i.meee.com.tw/0DsQ3ru.jpg", preview_image_url="https://i.meee.com.tw/0DsQ3ru.jpg"),
                    "藍色自動傘": ImageSendMessage(original_content_url="https://i.meee.com.tw/6KiGUdi.jpg", preview_image_url="https://i.meee.com.tw/6KiGUdi.jpg"),
                    "大洪": ImageSendMessage(original_content_url="https://i.meee.com.tw/HpFRxkJ.jpg", preview_image_url="https://i.meee.com.tw/HpFRxkJ.jpg"),
                    }

go_list = ["警察根本不在乎你去不去","不來最好啊","就不要去啊",
           "還是去啊","你去不去確實會被拘啊","你不要去就不要報案啊",
           "警察根本不在乎你要不要去","就不去阿","不爽就不要去阿",
           "不然案件都不要弄了啊","最好要去","根本沒人在乎你要不要去",
           "不去就不去啊","不爽去就不要去啊","不去就不去啊！",
           "可以不去","為何要去","威脅你去","檢察官傳喚你你就得去",
           "你可以不去","不介意的話可以去","還是會叫你去的",
           "因為警察的威脅態度就不想去了嗎?","不去做會被拘？",
           "會去啊！","等老子有空就會去了","建議你還是去一趟",
           "無故不到的話就會拘提囉","你不去就發公文傳你","不要去啊",
           "可以無視","你愛來不來","不去做筆錄根本不會被拘提","去了就是共犯"

            ]
image_list = ['https://i.imgur.com/Bt6PYE0.jpeg', 'https://i.imgur.com/7ynCsE3.jpeg', 
              'https://i.imgur.com/c0foSQj.jpeg', 'https://i.imgur.com/BLYnTMq.jpeg', 
              'https://i.imgur.com/9Ykkrxc.jpeg', 'https://i.imgur.com/sdPGFB7.jpeg', 
              'https://i.imgur.com/T8UGXaW.jpeg', 'https://i.imgur.com/cTFGT5k.jpeg', 
              'https://i.imgur.com/pcZvIHJ.jpeg', 'https://i.imgur.com/TGAmg76.jpeg', 
              'https://i.imgur.com/dyDOrMc.jpeg', 'https://i.imgur.com/hZ925NZ.jpeg', 
              'https://i.imgur.com/KrkOC6o.jpeg', 'https://i.imgur.com/u6iQD32.jpeg', 
              'https://i.imgur.com/PrW4tYv.jpeg', 'https://i.imgur.com/BtYm7XQ.jpeg', 
              'https://i.imgur.com/RCyEkC0.jpeg', 'https://i.imgur.com/Rs2sib2.jpg', 
              'https://i.imgur.com/fVRomwL.jpg', 'https://i.imgur.com/XA3xJUM.jpg', 
              'https://i.imgur.com/WtW4tXe.jpg', 'https://i.imgur.com/waQGu1o.jpg', 
              'https://i.imgur.com/Dy1jKRY.jpg', 'https://i.imgur.com/x6c80PN.jpg', 
              'https://i.imgur.com/VMbUfMT.jpg', 'https://i.imgur.com/SWa74YC.jpg', 
              'https://i.imgur.com/H8znubO.jpg', 'https://i.imgur.com/mYI3oEb.jpg', 
              'https://i.imgur.com/bKVIimf.jpg', 'https://i.imgur.com/9uNlJDV.jpg', 
              'https://i.imgur.com/Xnjko1g.jpg', 'https://i.imgur.com/tf9D64m.jpg', 
              'https://i.imgur.com/V3xlXUz.jpg', 'https://i.imgur.com/yGP3g3x.jpg', 
              'https://i.imgur.com/4EQLRbc.jpg', 'https://i.imgur.com/t2rQkFN.jpg', 
              'https://i.imgur.com/nqyb2DR.jpg', 'https://i.imgur.com/4BxfNw5.jpg', 
              'https://i.imgur.com/a623wqJ.jpg', 'https://i.imgur.com/gjxZ35v.jpg', 
              'https://i.imgur.com/04ZdolO.jpg', 'https://i.imgur.com/QkkCMXG.jpg', 
              'https://i.imgur.com/IsfQ2zE.jpg', 'https://i.imgur.com/ZbSgNye.jpg', 
              'https://i.imgur.com/broJHa4.jpg', 'https://i.imgur.com/Bq9wZH8.jpg', 
              'https://i.imgur.com/kKBvxpu.jpg', 'https://i.meee.com.tw/mirpzH8.gif', 
              'https://i.meee.com.tw/ypRbjzd.gif', 'http://i.imgur.com/0noCJQx.jpg', 
              'https://i.imgur.com/yAsOePs.jpg', 'http://i.imgur.com/FHIPVQj.jpg', 
              'https://i.imgur.com/2LE4iBg.jpg', 'https://i.imgur.com/RY6RFDE.jpg', 
              'https://i.imgur.com/Y0Uwq2Z.jpg', 'https://i.imgur.com/6Y00ho0.jpg', 
              'https://i.imgur.com/qP6Upvr.jpg', 'https://i.imgur.com/DRnG5MY.jpg', 
              'https://i.imgur.com/MaNqDAM.jpg', 'https://i.imgur.com/dqPpa7R.jpg', 
              'https://i.imgur.com/qoeNHjg.jpg', 'https://i.imgur.com/IIqJ2Ys.jpg', 
              'https://i.meee.com.tw/P0PZ6gy.gif', 'https://i.meee.com.tw/BUdbzY5.gif', 
              'https://i.meee.com.tw/IDr863V.gif', 'https://i.meee.com.tw/S5P0Osl.gif',
              'https://imgur.com/z1Oeta8.jpg', 'https://imgur.com/YdK8sWG.jpg', 
              'https://imgur.com/RYJ40Ws.jpg', 'https://i.imgur.com/JJJqfGh.jpg', 
              'https://i.imgur.com/Vq6V5uw.jpg', 'https://i.imgur.com/9Gm2Lum.jpg', 
              'https://i.imgur.com/NP7smTX.jpg', 'https://i.imgur.com/hhWsDwx.jpg', 
              'https://i.imgur.com/MGZxm2c.jpg', 'https://i.imgur.com/Kn5gT6H.jpg', 
              'https://i.imgur.com/VhMOsf1.jpg', 'https://i.imgur.com/PBGFHtB.jpg', 
              'https://i.imgur.com/dWrOY2r.jpg', 'https://i.meee.com.tw/ayiRKl2.gif', 
              'https://i.meee.com.tw/azaDSgF.gif', 'https://i.meee.com.tw/hhQXiSF.gif', 
              'https://i.imgur.com/96oEPLz.jpg', 'https://i.imgur.com/JnyG2yx.jpg', 
              'https://i.imgur.com/LyqFK18.jpg', 'https://i.imgur.com/IOqbshu.jpg', 
              'https://i.imgur.com/VEi91HZ.jpg', 'https://i.imgur.com/KV9j1iM.jpg', 
              'https://i.imgur.com/VQD9dIe.jpg', 'https://i.imgur.com/xk7EtQr.jpg', 
              'https://i.imgur.com/f4y4pAH.jpg', 'https://i.imgur.com/2cv0lwt.jpg', 
              'https://i.imgur.com/hgpumwT.jpg', 'https://i.imgur.com/wshZr9G.jpg', 
              'https://i.imgur.com/msN9wvx.jpg', 'https://i.imgur.com/BE6V2lc.jpg', 
              'https://i.imgur.com/000FxCe.jpg', 'https://i.imgur.com/0O4XrC9.jpg', 
              'https://i.imgur.com/dZMFnyu.jpg', 'https://i.imgur.com/29WviyT.jpg', 
              'https://i.imgur.com/SA5bDCk.jpg', 'https://i.imgur.com/f15Ny7E.jpg', 
              'https://i.imgur.com/MeAvN83.jpg', 'https://i.imgur.com/c11UTEX.jpg', 
              'https://i.imgur.com/IYzbbul.jpg', 'https://i.imgur.com/aMNcBUJ.jpg', 
              'https://i.imgur.com/szwGi3A.jpg', 'https://i.imgur.com/zqr26Xj.jpg', 
              'https://i.imgur.com/Ac3gO5A.jpg', 'https://i.imgur.com/rXMLFrr.jpg', 
              'https://i.imgur.com/njZ9AQs.jpg', 'https://i.imgur.com/XLfQXwp.jpg', 
              'https://i.imgur.com/ExflRIM.jpg', 'https://i.imgur.com/S7l3XpY.jpg', 
              'https://i.imgur.com/ihyFDFg.jpg', 'https://i.imgur.com/ThHUogR.jpg', 
              'https://i.imgur.com/UB91Yhe.jpg', 'https://i.imgur.com/S3ToJ5B.jpg',
              'https://i.imgur.com/WsdyOOf.jpg', 'https://i.imgur.com/GkFlYYk.jpg',
              'https://i.imgur.com/rsmW5dc.jpg', 'https://i.imgur.com/kkm5KG4.jpg', 
              'https://i.imgur.com/mZIjFA9.gif', 'https://i.imgur.com/ul72jeV.gif', 
              'https://i.imgur.com/VgrM0TM.gif', 'https://i.imgur.com/xyGPi6f.jpg', 
              'https://i.imgur.com/PUv0iIW.jpg', 'https://i.imgur.com/t5jm7a4.gif', 
              'https://i.imgur.com/WpD756c.gif', 'https://i.imgur.com/HCGVn8x.gif', 
              'https://i.imgur.com/v9Cgos7.gif', 'https://i.imgur.com/PfSqErJ.jpg', 
              'https://i.meee.com.tw/LO4UinC.jpg', 'https://i.imgur.com/naSSISi.jpg', 
              'https://i.imgur.com/YLE9NOF.jpg', 'https://i.imgur.com/qV6Ojzu.jpg', 
              'https://i.imgur.com/PRNkwLz.jpg', 'https://i.imgur.com/imEnEpy.jpg', 
              'https://i.imgur.com/hebFqtp.jpg', 'https://i.imgur.com/Qh4QYXd.jpg', 
              'https://i.imgur.com/Z2k3MPN.jpg', 'https://i.imgur.com/sbZWlSn.jpg', 
              'https://i.imgur.com/mtoDi5u.jpg', 'https://i.imgur.com/UrW1eZx.jpg', 
              'https://i.imgur.com/CEPp9aj.jpg', 'https://i.imgur.com/yZxjoaO.jpg', 
              'https://i.imgur.com/g9o2JDu.jpg', 'https://i.imgur.com/G9m67Cq.jpg', 
              'https://i.imgur.com/omgnKO1.jpg', 'https://i.imgur.com/jJbrten.jpg', 
              'https://i.imgur.com/kc0ABc1.jpg', 'https://i.imgur.com/wzmbSAN.jpg', 
              'https://i.imgur.com/WQlLWQ1.jpg', 'https://i.imgur.com/qAD2YTB.jpg', 
              'https://i.imgur.com/bLh9sRY.jpg', 'https://i.imgur.com/AauSV7V.jpg', 
              'https://i.imgur.com/j589je1.jpg', 'https://pbs.twimg.com/media/F3ffJfebIAA2ixF?format=jpg&name=900x900',
              'https://i.imgur.com/WkCQqCC.jpg', 'https://pbs.twimg.com/media/GHagSEpagAAXa1h?format=jpg&name=900x900',
              'https://pbs.twimg.com/media/GAFwvcIaEAA4qiF?format=jpg&name=large', 'https://pbs.twimg.com/media/GHenwznaUAA4agJ?format=jpg&name=medium',
              'https://i.imgur.com/34Ul8SK.jpg', 'https://i.imgur.com/dS4J24E.jpg', 
              'https://i.imgur.com/YD36RJ3.jpg', 'https://i.imgur.com/rBLHGL3.jpg', 
              'https://i.imgur.com/rfxQdPm.jpg', 'https://i.imgur.com/P4mJX81.jpg',
              'https://i.imgur.com/dQNQQVp.jpg', 'https://i.imgur.com/zpsARa9.jpg', 
              'https://i.imgur.com/rRcg8nv.jpg', 'https://i.imgur.com/jkPtMyc.jpg', 
              'https://i.imgur.com/4g44O7m.jpg', 'https://i.imgur.com/AhITdYN.jpg', 
              'https://i.imgur.com/trmLUgY.jpg', 'https://i.imgur.com/m0qIZpz.jpg', 
              'https://i.imgur.com/yfavx2v.jpg', 'https://i.imgur.com/TbWefKA.jpg', 
              'https://i.imgur.com/kl0BZLt.jpg', 'https://i.imgur.com/5utO0D1.jpg', 
              'https://i.imgur.com/VkW9axn.jpg', 'https://i.imgur.com/SZDSseH.jpg', 
              'https://i.imgur.com/M4q22RV.jpg', 'https://i.imgur.com/wGmpDVE.jpg', 
              'https://i.imgur.com/ec8gW5o.jpg', 'https://i.imgur.com/20PKLzL.jpg', 
              'https://i.imgur.com/H2NB0hq.jpg', 'https://i.imgur.com/04xLAFu.jpg', 
              'https://i.imgur.com/efNS0ir.jpg', 'https://i.imgur.com/awPma84.jpg',
              'https://i.imgur.com/qfH5w6c.jpg', 'https://i.imgur.com/hUNoDQB.jpg', 
              'https://i.imgur.com/beGe9tU.jpg', 'https://i.imgur.com/awPma84.jpg',
              'https://i.imgur.com/dnR76pN.jpg', 'https://i.imgur.com/0aG7she.jpg', 
              'https://i.imgur.com/empukyF.jpg', 'https://i.imgur.com/2bHyV8z.jpg', 
              'https://i.imgur.com/MhOjO0o.jpg', 'https://i.imgur.com/85QHHFG.jpg', 
              'https://i.imgur.com/WeGq0Ix.jpg', 'https://i.imgur.com/ZN4FKra.jpg', 
              'https://i.imgur.com/4u4NkFj.jpg', 'https://i.imgur.com/UcogiNv.jpg', 
              'https://i.imgur.com/29PSj4J.jpg', 'https://i.imgur.com/J3Ic1yq.jpg', 
              'https://i.imgur.com/YfiMjBD.jpg', 'https://i.imgur.com/qUCk6al.jpg', 
              'https://i.imgur.com/gMEkLLa.jpg', 'https://i.imgur.com/hmyIsck.jpg', 
              'https://i.imgur.com/IR4F6DC.jpg', 'https://i.imgur.com/5itSd85.jpg', 
              'https://i.imgur.com/FkwrVDd.jpg', 'https://i.imgur.com/cPin9Ec.jpg', 
              'https://i.imgur.com/98kvU6d.jpg', 'https://i.imgur.com/nCqHXvi.jpg',
              'http://i.imgur.com/UVGAWF1.jpg', 'http://i.imgur.com/LIUkUKG.jpg', 
              'http://i.imgur.com/bYJmiet.jpg', 'http://i.imgur.com/YTi0OkC.jpg', 
              'http://i.imgur.com/chFlcJt.jpg', 'http://i.imgur.com/Iya6vqH.jpg', 
              'http://i.imgur.com/9x4xU9j.jpg', 'http://i.imgur.com/6qReuax.jpg', 
              'http://i.imgur.com/Kw5EXyi.jpg', 'http://i.imgur.com/0eUWBdg.jpg', 
              'http://i.imgur.com/4qoW7fx.jpg', 'http://i.imgur.com/zatmStI.jpg', 
              'http://i.imgur.com/rek2f09.jpg', 'https://i.imgur.com/xMWjIq1.jpg',
              'https://i.imgur.com/hHLSzhC.jpg', 'https://i.imgur.com/8akbfEw.jpg', 
              'https://i.imgur.com/tGCRUms.jpg', 'https://i.imgur.com/O163ih5.jpg', 
              'https://i.imgur.com/wTFsIJt.jpg', 'https://i.imgur.com/MiDrAYI.jpg', 
              'https://i.imgur.com/OolY4LT.jpg', 'https://i.imgur.com/Dz1KpDD.jpg',
              'https://i.imgur.com/tvgxjKa.jpg', 'https://i.imgur.com/EBK1CtE.jpg', 
              'https://i.imgur.com/c3xDxwR.jpg', 'https://i.imgur.com/3rD3pQB.jpg', 
              'https://i.imgur.com/XF4b0Xd.jpg', 'https://i.imgur.com/7ZjamvH.jpg', 
              'https://i.imgur.com/VTPdxkJ.jpg', 'https://i.imgur.com/YDF4v0K.jpg', 
              'https://i.imgur.com/zTtNXKz.jpg', 'https://i.imgur.com/Rag74Kg.jpg', 
              'https://i.imgur.com/ugflsmp.jpg', 'https://i.imgur.com/hICwsEm.jpg', 
              'https://i.imgur.com/9eDstiV.jpg', 'https://i.imgur.com/U6AU0lf.jpg', 
              'https://i.imgur.com/9gfWhVU.jpg', 'https://i.imgur.com/daTfcBh.jpg', 
              'https://i.imgur.com/EYAjAiZ.jpg', 'https://i.imgur.com/WwU2ZKd.jpg', 
              'https://i.imgur.com/tC1Zwub.jpg', 'https://i.imgur.com/5jEWVam.jpg', 
              'https://i.imgur.com/rlZTVKe.jpg', 'https://i.imgur.com/TxlZLga.jpg', 
              'https://i.imgur.com/WY1AIzp.jpg', 'https://i.imgur.com/c3JgjSe.jpg', 
              'https://i.imgur.com/ENsY9cS.jpg', 'https://i.imgur.com/RCMolNL.jpg', 
              'https://i.imgur.com/uLDC0hX.jpg', 'https://i.imgur.com/yDsns2f.jpg', 
              'https://i.imgur.com/clWsnaZ.jpg', 'https://i.imgur.com/tJM8L2Z.jpg', 
              'https://i.imgur.com/arAA4kS.jpg', 'https://i.imgur.com/zjrS6Hh.jpg', 
              'https://i.imgur.com/2T6GCn7.jpg', 'https://i.imgur.com/JRmZxdF.jpg', 
              'https://i.imgur.com/RmFVtYU.jpg', 'https://i.imgur.com/iaUXE6j.jpg', 
              'https://i.imgur.com/ljnGciM.jpg', 'http://i.imgur.com/bIz9jSP.jpg', 
              'http://i.imgur.com/04nOqbR.jpg', 'http://i.imgur.com/ekejiR0.jpg', 
              'http://i.imgur.com/X4WOJ6O.jpg', 'http://i.imgur.com/mV7PxUS.jpg', 
              'http://i.imgur.com/0WKY4bc.jpg', 'http://i.imgur.com/RkKDifG.jpg', 
              'http://i.imgur.com/0KtmjJ5.jpg', 'http://i.imgur.com/zRDF38z.jpg', 
              'http://i.imgur.com/zgm2Q5X.jpg', 'https://i.imgur.com/bMmGmzj.jpg', 
              'https://i.imgur.com/vxbneNN.jpg', 'https://i.imgur.com/Q7O4xHE.jpg', 
              'https://i.imgur.com/aGbhDuJ.jpg', 'https://i.imgur.com/1dOqpku.jpg', 
              'https://i.imgur.com/NOzWytm.jpg', 'https://i.imgur.com/FNymdiV.jpg', 
              'https://i.imgur.com/ZIzGMEv.jpg', 'https://i.imgur.com/EE2VAAA.jpg',
              "https://i.imgur.com/ImBNjjN.jpeg", "https://i.imgur.com/hZUGN6a.jpeg",
              'https://i.imgur.com/yx3vj49.jpg', 'https://i.imgur.com/gZh8u6J.jpg', 
              'https://i.imgur.com/YTmf5z9.jpg', 'https://i.imgur.com/TALNFOZ.jpg', 
              'https://i.imgur.com/Cyspx5O.jpg', 'https://i.imgur.com/lysMufD.jpg', 
              'https://i.imgur.com/lLNSump.jpg', 'https://i.imgur.com/NJ2M3lZ.jpg',
              'https://i.imgur.com/FSeELb2.jpg', 'https://i.imgur.com/i6vNZkG.jpg', 
              'https://i.imgur.com/tWAd59E.jpg', 'https://i.imgur.com/pIroMZf.jpg', 
              'https://i.imgur.com/LSaowAo.jpg', 'https://i.imgur.com/GFMhc1Z.jpg', 
              'https://i.imgur.com/Uqya73o.jpg', 'https://i.imgur.com/HsCUJAV.jpg',
              'https://i.imgur.com/DYJ42d3.jpg', 'https://i.imgur.com/iUIb560.jpg', 
              'https://i.imgur.com/hkgLh6A.jpg', 'https://i.imgur.com/sK4SsKV.jpg', 
              'https://i.imgur.com/JRvXRaz.jpg', 'https://i.imgur.com/xijEwmy.jpg', 
              'https://i.imgur.com/paFrGiA.jpg', 'https://i.imgur.com/ZG0yMJt.jpg', 
              'https://i.imgur.com/WSoBFh9.jpg', 'http://i.imgur.com/GFBeLju.jpg', 
              'https://i.imgur.com/odIg9Ez.jpeg', 'https://i.imgur.com/4XddcrH.jpeg', 
              'https://i.imgur.com/IiKSl2j.jpeg', 'https://i.imgur.com/WhGTNA5.jpeg', 
              'https://i.imgur.com/RcL6AAI.jpeg', 'https://i.imgur.com/JwuOCRR.jpeg', 
              'https://i.imgur.com/uYEk0fX.jpeg', 'https://i.imgur.com/zrt9VzG.jpeg', 
              'https://i.imgur.com/CzN9mZ8.jpeg', 'https://i.imgur.com/jCX7g5n.jpeg', 
              'https://i.imgur.com/LwK6Xu2.jpeg', 'https://i.imgur.com/XCT9OMD.jpeg', 
              "https://i.imgur.com/o0b07ou.jpeg", 'https://files.catbox.moe/7zjmze.jpg', 
              'https://files.catbox.moe/8hq9vz.jpg', 'https://files.catbox.moe/d46vrl.jpg', 
              'https://files.catbox.moe/6xy066.jpeg', 'https://files.catbox.moe/wjfjd9.jpg', 
              'https://files.catbox.moe/cyrpg6.jpg', 'https://files.catbox.moe/veuzr8.jpg', 
              'https://files.catbox.moe/sw4xmk.jpg', 'https://files.catbox.moe/rpb0hg.jpg', 
              'https://files.catbox.moe/86ki3o.jpg', 'https://files.catbox.moe/0uellg.jpg', 
              'https://files.catbox.moe/alaiwh.jpg', 'https://files.catbox.moe/tb1wai.jpg', 
              'https://files.catbox.moe/5uuhrm.jpg', 'https://files.catbox.moe/9m8rib.jpg', 
              'https://files.catbox.moe/pbdchs.jpg', 'https://files.catbox.moe/hadfto.jpg', 
              'https://files.catbox.moe/h01p3w.jpg', 'https://files.catbox.moe/9usv9j.jpg', 
              'https://files.catbox.moe/zdxqam.jpg', 'https://files.catbox.moe/80wzyc.jpg', 
              'https://files.catbox.moe/dpmt4i.png', 'https://files.catbox.moe/mgvpiq.jpeg', 
              'https://i.imgur.com/lrzYND8.gif', 'https://i.imgur.com/EOPSC40.gif', 
              'https://i.imgur.com/5eC9EwH.jpeg', 'https://i.imgur.com/T8h5rth.jpeg', 
              'https://i.imgur.com/6jORwgo.jpeg', 'https://i.imgur.com/eNkAOlh.jpeg', 
              'https://i.imgur.com/ORd0zAK.jpeg', 'https://i.imgur.com/TlXH6Eg.jpeg', 
              'https://i.imgur.com/t3QROwT.jpeg', 'https://i.imgur.com/1TRz8ev.jpeg', 
              'https://i.imgur.com/EXKjdYT.jpeg', 'https://i.imgur.com/PhsySux.jpeg', 
              'https://i.imgur.com/waeAGWD.jpeg', 'https://i.imgur.com/DLbR02D.jpeg', 
              'https://i.imgur.com/4c7pi9B.jpeg', 'https://i.imgur.com/8LxrdzT.jpeg', 
              'https://i.imgur.com/Bsce9bI.jpeg', 'https://i.imgur.com/41vzGJJ.jpeg', 
              'https://i.imgur.com/fPBmoMM.jpeg', 'https://i.imgur.com/Yd63DS6.jpeg', 
              'https://i.imgur.com/hLJQ76Z.jpeg', 'https://i.imgur.com/XwWNMw1.jpeg', 
              'https://i.imgur.com/8Sk1K5W.jpeg', 'https://i.imgur.com/CHZWRgU.jpeg', 
              'https://i.imgur.com/kIboV81.jpeg', 'https://i.imgur.com/eLQxSoM.jpeg', 
              'https://i.imgur.com/QUBZx2E.jpeg', 'https://i.imgur.com/fn8S9xL.jpeg', 
              'http://i.imgur.com/YUi4AEy.jpg', 'https://i.imgur.com/0J7Xz8y.jpeg', 
              'https://i.imgur.com/ICDqDQW.jpeg', 'https://i.imgur.com/KnJbVGt.jpeg', 
              'https://i.imgur.com/LCuG9UY.jpeg', 'https://i.imgur.com/LLn63HN.jpeg', 
              'https://i.imgur.com/NNyA3Im.jpeg', 'https://i.imgur.com/qWGjauP.jpeg', 
              'https://i.imgur.com/odriJEX.jpeg', 'https://i.imgur.com/msDYY0t.jpeg', 
              'https://i.imgur.com/o3n3BM8.jpeg', 'https://i.imgur.com/M1QKeiR.jpeg', 
              'https://i.imgur.com/onH28k9.jpeg', 'https://i.imgur.com/Nmq5Sib.jpeg', 
              'https://i.imgur.com/gJAJDNK.jpeg', 'https://i.imgur.com/BrMy9gQ.jpeg', 
              'https://i.imgur.com/7nP7Bsu.jpeg', 'https://i.imgur.com/oO1Ef4Q.jpeg', 
              'https://i.imgur.com/mUkePgK.jpeg', 'https://i.imgur.com/GomLXCr.jpeg', 
              'https://i.imgur.com/DCoznkX.jpeg', 'https://i.imgur.com/NopdIVg.jpeg',
              'https://i.imgur.com/763rfoU.jpeg', 'https://i.imgur.com/n51wobU.jpeg', 
              'https://i.imgur.com/OPAoXNi.jpeg', 'https://i.imgur.com/zJIJgtV.jpeg', 
              'https://i.imgur.com/d2HSOef.jpeg', "http://i.imgur.com/n88oEOn.jpg",
              
              ]

ho_list = ['https://i.meee.com.tw/j4L7fv7.jpg', 'https://i.meee.com.tw/PKXkloH.jpg',
           'https://i.meee.com.tw/kL7BLBN.jpg', 'https://i.meee.com.tw/pe8pjQK.jpg',
           'https://i.meee.com.tw/I3lidV2.jpg', 'https://i.meee.com.tw/0b00aPn.jpg',
           'https://i.meee.com.tw/AHRQWZ5.jpg', 'https://i.meee.com.tw/2NFFKPB.jpg',
           'https://i.meee.com.tw/8GRoLAk.jpg', 'https://i.meee.com.tw/RFUGt1y.jpg',
           'https://i.meee.com.tw/Wf7b7TA.jpg', 'https://i.meee.com.tw/4gbhngn.jpg',
           'https://i.imgur.com/vy670dJ.jpg'
        ]

forestfire_list = ['https://i.meee.com.tw/KI1m9bW.jpg', 'https://i.meee.com.tw/WIimNLH.jpg',
                   'https://i.meee.com.tw/IkGpi8d.jpg', 'https://i.meee.com.tw/42wjoU7.jpg',
        ]
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    return driver

# def jable():
    driver = get_driver()
    driver.get("https://jable.tv/")
    WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "title"))
    )
    driver.execute_script("window.scrollTo(0,document.bodyscrollHeight);")
    time.sleep(1)
    titles = driver.find_elements(By.CLASS_NAME, "title")
    i = 1
    latest_videos = []
    popular_videos = []
    watching_now_videos = []
    for title in titles:
        if "-" in title.text:
            if i <= 6:
                latest_videos.append(title.text)
                i += 1
            elif i <= 17:
                popular_videos.append(title.text)
                i += 1
            else:
                watching_now_videos.append(title.text)
    driver.quit()
    jable_title = "最新影片:\n" + "\n".join(latest_videos) + "\n\n" + \
          "熱門影片:\n" + "\n".join(popular_videos) + "\n\n" + \
          "他們在看:\n" + "\n".join(watching_now_videos)
    return jable_title

def ptt(index):
    url = f"https://www.ptt.cc/bbs/{index}/index.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Cookie": "over18=1"
    }
    response_ptt = requests.get(url, headers=headers)
    if response_ptt.status_code == 200:
        soup = BeautifulSoup(response_ptt.text, "html.parser")
        article = soup.find_all("div", class_="r-ent")
        result = ""
        for a in article:
            title = a.find("div", class_="title")
            if title and title.a:
                title_text = title.a.text.strip()
            else:
                title_text = "找不到"
            
            popular = a.find("div", class_="nrec")
            if popular and popular.span:
                popular_text = popular.span.text.strip()
            else:
                popular_text = "無"

            date = a.find("div", class_="date")
            if date:
                date_text = date.text.strip()
            else:
                date_text = "無"

            result += f"{title_text} \n人氣: {popular_text} \n日期: {date_text}\n\n"

        return result
    else:
        return "無法取得 PTT 文章"


# 股票趨勢圖 (yfinance + twstock 混合版)
def plot_stock_trend(code):
    # 設定圖片儲存路徑
    image_path = f"{code}_trend.png"
    
    # --- 1. 抓取即時資料 (twstock) ---
    try:
        stock_rt = twstock.realtime.get(code)
        if not stock_rt['success']:
            return TextSendMessage(text=f"無法獲取 {code} 的即時資料，請確認股號是否正確。")
        
        stock_name = stock_rt['info']['name'] # 中文名稱
        latest_price = float(stock_rt['realtime']['latest_trade_price'])
    except Exception as e:
        print(f"即時資料錯誤: {e}")
        return TextSendMessage(text="即時股價讀取失敗")

    # --- 2. 抓取歷史資料 (yfinance, 鎖定半年) ---
    try:
        yf_code = f"{code}.TW"
        df = yf.download(yf_code, period="3mo", auto_adjust=True, progress=False)
        
        # 如果上市抓不到，試試看上櫃 (.TWO)
        if df.empty:
            yf_code = f"{code}.TWO"
            df = yf.download(yf_code, period="3mo", auto_adjust=True, progress=False)
            
        if df.empty:
            return TextSendMessage(text="無法獲取歷史股價資料 (Yahoo Finance)")

        # 資料清理
        df = df.reset_index()
        # 處理 yfinance 可能的多層索引問題
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        df = df[['Date', 'Close']].copy()
        df.columns = ['date', 'close']
        df['date'] = df['date'].dt.tz_localize(None) # 移除時區
        
    except Exception as e:
        print(f"歷史資料錯誤: {e}")
        return TextSendMessage(text="歷史資料讀取發生錯誤")

    # --- 3. 合併資料 (將最新價格接到歷史資料後面) ---
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    last_hist_date = df.iloc[-1]['date']
    
    if last_hist_date < today:
        new_row = pd.DataFrame({'date': [today], 'close': [latest_price]})
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        # 如果歷史資料已包含今天，強制更新為即時價格
        df.iloc[-1, df.columns.get_loc('close')] = latest_price

    # --- 4. 繪圖 (Matplotlib) ---
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 畫走勢線
        ax.plot(df['date'], df['close'], label='Close Price', color='#1f77b4', linewidth=2)
        
        # 標示最新價格紅點
        last_date = df.iloc[-1]['date']
        last_val = df.iloc[-1]['close']
        ax.scatter(last_date, last_val, color='red', s=60, zorder=5)
        
        # 標示價格文字
        ax.annotate(f'{last_val}', 
                     xy=(last_date, last_val), 
                     xytext=(5, 5), 
                     textcoords='offset points',
                     fontsize=12, color='red', fontweight='bold')

        # 設定標題 (使用英文以避免 Render 伺服器中文亂碼)
        ax.set_title(f'{code} Stock Trend (6 Months)', fontsize=16)
        ax.set_xlabel('Date')
        ax.set_ylabel('Price (TWD)')
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend()
        
        # 旋轉日期標籤
        fig.autofmt_xdate()

        # 存檔
        plt.savefig(image_path, format='png')
        plt.close(fig) # ★★★ 關鍵：釋放記憶體 ★★★

        # --- 5. 上傳到 Imgur ---
        # 建議改用 os.environ.get('IMGUR_CLIENT_ID')
        client_id = 'c0fad094e155b1e' 
        client_secret = '861df13b5b7bf435cc4c27369ee11029ed543f7f'
        client = ImgurClient(client_id, client_secret)
        
        image = client.upload_from_path(image_path, anon=True)
        os.remove(image_path) # 刪除本地暫存檔
        
        url = image['link']
        
        # 回傳圖片訊息與文字簡述
        return [
            TextSendMessage(text=f"{stock_name} ({code}) \n最新價格: {latest_price}"),
            ImageSendMessage(original_content_url=url, preview_image_url=url)
        ]

    except Exception as e:
        print(f"繪圖或上傳錯誤: {e}")
        return TextSendMessage(text="圖片生成失敗")

#天氣
def weather(address):
    # ★★★ 彩蛋：佑哥區 ★★★
    if address == "佑哥區":
        return ImageSendMessage(
            original_content_url="https://i.meee.com.tw/6GEFRdH.jpg", 
            preview_image_url="https://i.meee.com.tw/6GEFRdH.jpg"
        )

    # 建議將 API Key 放到環境變數，這裡先照你的習慣寫入
    # CWA_API_KEY = os.environ.get('CWA_API_KEY', '你的API_KEY')
    code = 'CWA-3EFEACCD-9F99-4C6F-88DB-1DE133DD4CAE' 
    
    # 1. 獲取當前天氣觀測數據 (溫度、濕度、風速)
    current_weather_urls = [
        f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0001-001?Authorization={code}',
        f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001?Authorization={code}'
    ]
    
    current_weather_data = {} 
    
    for url in current_weather_urls:
        try:
            # 設定 timeout 防止卡死
            req = requests.get(url, timeout=5)
            if req.status_code != 200: continue
            data = req.json()
            
            if 'records' not in data or 'Station' not in data['records']: continue

            for station in data['records']['Station']:
                if 'GeoInfo' not in station: continue
                
                town = station['GeoInfo']['TownName']
                if not town: continue
                
                # 建立資料索引，解決同名鄉鎮問題通常需要配合縣市，但這裡先維持簡單邏輯
                current_weather_data[town] = {
                    'weather': station['WeatherElement'].get('Weather', 'N/A'),
                    'temp': station['WeatherElement'].get('AirTemperature', 'N/A'),
                    'humid': station['WeatherElement'].get('RelativeHumidity', 'N/A'),
                    'WindSpeed': station['WeatherElement'].get('WindSpeed', 'N/A')
                }
        except Exception as e:
            print(f"觀測資料讀取錯誤: {e}")
            continue

    # 2. 獲取降雨機率 (全台鄉鎮預報 F-D0047-093)
    # 呼叫一次 API 即可取得全台灣資料
    forecast_url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-093?Authorization={code}&elementName=PoP12h"
    
    precipitation_map = {} # { "鄉鎮名": "降雨機率" }

    try:
        req = requests.get(forecast_url, timeout=10)
        if req.status_code == 200:
            data = req.json()
            if 'records' in data and 'locations' in data['records']:
                counties = data['records']['locations'][0]['location']
                # 雙層迴圈解析：縣市 -> 鄉鎮
                for county in counties:
                    townships = county.get('location', [])
                    for town in townships:
                        town_name = town['locationName']
                        pop_value = "N/A"
                        weather_elements = town.get('weatherElement', [])
                        for element in weather_elements:
                            if element['elementName'] == 'PoP12h':
                                if element['time']:
                                    # 取第一筆預報 (最近的未來)
                                    pop_value = element['time'][0]['elementValue'][0]['value']
                                break
                        precipitation_map[town_name] = pop_value
    except Exception as e:
        print(f"預報資料讀取錯誤: {e}")

    # 3. 匹配與回傳結果
    target_data = None
    found_name = ""
    
    # 搜尋邏輯：先找觀測資料
    if address in current_weather_data:
        target_data = current_weather_data[address]
        found_name = address
    else:
        # 模糊搜尋 (例如輸入"蘆洲" -> 找到"蘆洲區")
        for name, data in current_weather_data.items():
            if address in name:
                target_data = data
                found_name = name
                break
    
    if target_data:
        weather_desc = target_data['weather']
        temp = target_data['temp']
        humid = target_data['humid']
        wind = target_data['WindSpeed']
        
        # 嘗試取得降雨機率
        rain_prob = precipitation_map.get(found_name, "N/A")
        if rain_prob == "N/A":
             rain_prob = precipitation_map.get(address, "N/A")

        return f'「{found_name}」目前天氣「{weather_desc}」，氣溫 {temp}°C，濕度 {humid}%，風速 {wind}m/s，降雨機率 {rain_prob}%'
    else:
        return f"找不到「{address}」的氣象資料，請確認輸入完整的鄉鎮市區名稱（例如：煒仔區）。"

#地震資訊
def earthquake():
    output = []
    try:
        code = 'CWA-3EFEACCD-9F99-4C6F-88DB-1DE133DD4CAE'
        # 小區域
        url = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0016-001?Authorization={code}'
        req1 = requests.get(url)  # 爬取資料
        data1 = req1.json()       # 轉換成 json
        eq1 = data1['records']['Earthquake'][0]           # 取得第一筆地震資訊
        t1 = data1['records']['Earthquake'][0]['EarthquakeInfo']['OriginTime']
        # 顯著有感
        url2 = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001?Authorization={code}'
        req2 = requests.get(url2)  # 爬取資料
        data2 = req2.json()        # 轉換成 json
        eq2 = data2['records']['Earthquake'][0]           # 取得第一筆地震資訊
        t2 = data2['records']['Earthquake'][0]['EarthquakeInfo']['OriginTime']
        
        output = [eq1['ReportContent'], eq1['ReportImageURI']] # 先使用小區域地震
        if t2>t1:
          output = [eq2['ReportContent'], eq2['ReportImageURI']] # 如果顯著有感地震時間較近，就用顯著有感地震
    except Exception as e:
        print(e)
        output = ['沒有~','']
    return output

#校網
def scrape_utaipei_news():
    url = 'https://www.utaipei.edu.tw/'
    
    # 發送請求
    response = requests.get(url)
    html_content = response.text
    
    # 解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    text = []
    # 找到指定的div
    div_content = soup.find('div', class_='col col_01')
    if div_content:
        # 提取所有條目
        items = div_content.find_all(string=True)  # 使用string參數
        for item in items:
            clean_text = item.strip()  # 去掉多餘的空白字符
            # 過濾不要的部分
            if clean_text and not clean_text.startswith('<div class="list module md_style1">') and not clean_text.startswith('generated at') and clean_text != '更多最新消息':
                text.append(clean_text)
    
    # 將所有內容組合成一個字符串
    message = "\n".join(text)
    
    return message if message else "沒有找到指定的 div 或沒有內容"

#系網
def Departmental_website():
    url = "https://envir.utaipei.edu.tw/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Cookie": "over18=1"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # 找到所有 <div class="mtitle"> 元素
    mtitle_divs = soup.find_all("div", class_="mtitle")

    # 初始化列表來存儲最新公告和其他公告
    new_announcements = []
    other_announcements = []

    # 處理每個 <div class="mtitle"> 元素的內容
    for i, div in enumerate(mtitle_divs):
        # 獲取 div 元素的文本內容
        text_content = div.get_text(strip=True)
        
        # 判斷是否為最新公告或其他公告
        if i < 5:
            new_announcements.append(text_content)
        else:
            other_announcements.append(text_content)

    # 構建輸出訊息
    message = "最新公告:\n"
    message += "\n".join(new_announcements)
    message += "\n\n其他公告:\n"
    message += "\n".join(other_announcements)

    return message

#訊息傳遞區塊
##### 基本上程式編輯都在這個function #####
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    response = None
    for keyword, reply in keyword_responses.items():
        if re.match(keyword, message):
            response = reply
            break
    if not response:
        if re.search("抽", message):
            img_url = random.choice(image_list)
            response = ImageSendMessage(original_content_url=img_url, preview_image_url=img_url)
        # elif re.match("jable", message):
        #     response = jable()
        elif re.match("ptt (.*)", message):
            index = re.match("ptt (.*)", message).group(1)
            response = ptt(index)
        elif re.match("星光閃耀", message):
            video_url = "https://i.imgur.com/WFs8P52.mp4"
            response = VideoSendMessage(original_content_url=video_url, preview_image_url="https://i.imgur.com/SLlr25K.jpg")
        elif re.match(r"股票(\d+)", message):
            code = re.match(r"股票(\d+)", message).group(1)
            response = plot_stock_trend(code)
        elif re.match("天氣 (.*)", message):
            index = re.match("天氣 (.*)", message).group(1)
            response = weather(index)
        elif re.match("地震報告", message):
            eq_info = earthquake()
            if eq_info[0] != '沒有~':
                response = [
                    TextSendMessage(text=eq_info[0])
                ]
                if eq_info[1]:  # 確保圖片 URL 不為空
                    response.append(ImageSendMessage(original_content_url=eq_info[1], preview_image_url=eq_info[1]))
        elif re.match("浩哥", message):
            response = scrape_utaipei_news()
        elif re.match("笑cc", message):
            response = Departmental_website()
        elif re.match("^去嗎$", message) or ("去" in message and random.randint(1, 4) == 1):
            response = random.choice(go_list)
        elif re.search("呃", message):
            response = "呃呃呃呃呃"
        elif re.match("吼", message):
            img_url = random.choice(ho_list)
            response = ImageSendMessage(original_content_url=img_url, preview_image_url=img_url)
        elif re.match("森林火災", message):
            img_url = random.choice(forestfire_list)
            response = ImageSendMessage(original_content_url=img_url, preview_image_url=img_url)
    # 如果 response 不是 None，則表示找到了相符的回覆
    if response:
        if isinstance(response, str):
            response = TextSendMessage(text=response)
        line_bot_api.reply_message(event.reply_token, response)

#主程式
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)