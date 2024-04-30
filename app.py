import os
import io
from io import BytesIO
import time
import logging
import requests
import threading
import twstock
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
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *


app = Flask(__name__)
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# 必須放上自己的Channel Access Token
line_bot_api = LineBotApi('9yR4ewDjV8MMC1s8DCcZbCHhwYzFvoVWR8OM3XIckQaV7JSzLvIDc581psOLe+b/J7Iu7qCIrJDPFypvefXy+D4udYFHl9OSYoSXFIEkJmKpjhHPBk3UQP5Kqk37isFkfytaPpgoWh3o0mQwrS5wvQdB04t89/1O/w1cDnyilFU=')
# 必須放上自己的Channel Secret
handler = WebhookHandler('046d3499ea137d0ac4192b9224c91899')

# line_bot_api.push_message('U2245cda9373cd500a6fe9e8053729eac', TextSendMessage(text='請開始你的表演'))

#一哥起床
@app.route("/render_wake_up")
def render_wake_up():
    return "Hey!Wake Up!!"

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
                    "有": "有喔",
                    "豪巴": "豪巴",
                    "小炮": "小炮",
                    "哈": "哈哈哈",
                    "小歐": "小歐滾",
                    "唐董": "唐董滾",
                    "氧的弟弟": "硫",
                    "沒有":"沒有 通過",
                    "很玄": "這就很玄囉",
                    "可憐": "你好可憐喔",
                    "煒仔": "我是佑哥啦",
                    "佑哥": "領域展開",
                    "車號": "9796-MP",
                    "備胎": "你有備胎嗎",
                    "冰島貓男": "冰島貓男",
                    "鳴人小哥": "鳴人小哥",
                    "翹課": "歡迎翹課來聽",
                    "升級完成": "強勢回歸",
                    "岩石與礦物": "心理陰影",
                    "我做不到": "我就是做不到",
                    "一哥": "邏輯思考 x 有一說一",
                    "哇靠": "哇靠!你還真會掰啊",
                    "仇": "不要以為我們台灣人都是客客氣氣的",
                    "生日快樂": "Yo~Yo~ 老大生日大快樂啊！！",
                    "騙子": "一群詐騙份子，你們遲早會滅亡在東南亞!",
                    "讀書會": "今天有讀書會喔! \n 地點:S104 \n 時間:17:00-19:00 \n 系學會成員一樣有專屬小點心!",                  
                    "人氣王": "timeout=0.1;\ncount=0\ncurrent=location.href;\nif(timeout>0)\nsetTimeout('reload()',1000*timeout);\nelse\nlocation.replace(current);\nfunction reload(){\nsetTimeout('reload()',1000*timeout);\ncount++;\nconsole.log('每（'+timeout+'）秒自動刷新,刷新次數：'+count);\nfr4me='<frameset cols=\'*\'>\n<frame src=\''+current+'\'/>';\nfr4me+='</frameset>';\nwith(document){write(fr4me);void(close())};\n}",
                    "恐龍咖啡廳":"正杰，坤憶 你們在今日11：00-11：20 可到臺博古生館的恐龍餐廳找老師喝杯飲料，逾時失效~",
                    "名單": "1姚如庭、2黃正杰、3林幼鎂、4林憶蓁、5王云柔、6沈煒耀、7何續恩、8莊博文、9林坤億、10徐楷茹、11葉宥陞、12何寬祐、13陳皓恩、14蔣承祐、15張宥朋、16謝語姍、17周家甫、18林昀誼、19周子堯、20黃加榕",
                    "爆車": "收到，那市立大學這邊我就結算11位囉！\n車子應該會滿載。\n還是很多人報名  我把人數撐到極限  12 人  上次舊生11位  讓出1位  補上2位  真的爆車了  林明聖  陳泓愷  王進欽  黃至韻  林立  林貫益  葉宥陞  黃翊萱（一位）陳品聿  陳佩伶  以上為舊生保障名額  賴芓涵  林幼鎂  以上為新生遞補  真的極限了",
                    
                    "超派": StickerSendMessage(package_id="789", sticker_id="10885"),
                    "黃色小鴨": ImageSendMessage(original_content_url="https://i.imgur.com/td883jO.jpeg", preview_image_url="https://i.imgur.com/td883jO.jpeg"),
                    "行事曆": ImageSendMessage(original_content_url="https://i.imgur.com/loYEcr3.jpg", preview_image_url="https://i.imgur.com/loYEcr3.jpg"),
                    "吼": ImageSendMessage(original_content_url="https://i.imgur.com/vy670dJ.jpg", preview_image_url="https://i.imgur.com/vy670dJ.jpg"),
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
                    }

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
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36", "Cookie": "over18=1"}
    response_ptt = requests.get(url, headers=headers)
    if response_ptt.status_code == 200:
        soup = BeautifulSoup(response_ptt.text, "html.parser")
        article = soup.find_all("div", class_="r-ent")
        response_ptt = ""
        for a in article:
            title = a.find("div", class_="title")
            if title and title.a:
                title = title.a.text.strip()  # Strip whitespace
            else:
                title = "找不到"

            popular = a.find("div", class_="nrec")
            if popular and popular.span:
                popular = popular.span.text.strip()  # Strip whitespace
            else:
                popular = "無"

            date = a.find("div", class_="date")
            if date:
                date = date.text.strip()  # Strip whitespace
            else:
                date = "無"

            response_ptt += f"{title} \n 人氣: {popular} \n 日期:{date}\n"

        return response_ptt
    else:
        return "無法取得 PTT 文章"


#股票價格
def get_stock_info(code):
    stock = twstock.Stock(code)
    return stock

def get_latest_price(code):
    stock_rt = twstock.realtime.get(code)
    if stock_rt['success']:
        latest_trade_price = stock_rt['realtime']['latest_trade_price']
        name = stock_rt['info']['name']
        response_message = f"{name} 最新交易價格: {latest_trade_price}"
    else:
        response_message = "無法獲取最新交易價格。"
        
    return TextSendMessage(text=response_message)

def plot_trend(code, duration):
    stock = get_stock_info(code)
    date_ranges = {'1M': 30, '6M': 180, '1Y': 365, '2Y': 365*2, '5Y': 365*5, '10Y': 365*10}
    image_messages = []  # 存儲圖片消息的列表

    if duration not in date_ranges:  
        print("無法獲取最新交易價格。")
        return "無法獲取最新交易價格。"

    num_days = date_ranges[duration]

    # Calculate date range
    end_date = datetime.today()
    start_date = end_date - timedelta(days=num_days)

    # Get historical data for the specified date range
    data = stock.fetch_from(start_date.year, start_date.month)

    # Convert data to DataFrame format
    df = pd.DataFrame(data)

    # Plot the trend
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df['date'], df['close'], label='Close Price', color='blue')
    ax.set_title(f'Stock Price Trend - {duration}')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price (TWD)')
    plt.xticks(rotation=45)
    ax.legend()
    ax.grid(True)
    plt.tight_layout()

    # Save plot to local file
    image_path = f"{code}_{duration}.png"
    plt.savefig(image_path, format='png')

    # Upload image to Imgur
    client_id = 'c0fad094e155b1e'
    client_secret = '861df13b5b7bf435cc4c27369ee11029ed543f7f'
    client = ImgurClient(client_id, client_secret)
    image = client.upload_from_path(image_path, anon=True)  # 上傳本地文件
    url = image['link']
    image_message = ImageSendMessage(
        original_content_url=url,
        preview_image_url=url
    )
    image_messages.append(image_message)  # 將圖片消息存儲到列表中

    # Delete local image file
    os.remove(image_path)

    return image_messages  # 返回圖片消息列表




def stock_main(command):
    if command.startswith("價格"):
        code = command[2:]
        get_latest_price(code)
    else:
        parts = command.split()
        duration, code = parts
        return plot_trend(code, duration)



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
        if re.match("抽", message):
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
        elif re.match(r"價格(\d+)", message):
            code = re.match(r"價格(\d+)", message).group(1)
            response = get_latest_price(code)
        elif re.match(r"(\d+[DdMmYy])\s+(\d+)", message):
            duration_code = re.match(r"(\d+[DdMmYy])\s+(\d+)", message).groups()
            response = stock_main(" ".join(duration_code))

    # 如果 response 不是 None，則表示找到了相符的回覆
    if response:
        if isinstance(response, str):
            response = TextSendMessage(text=response)
        line_bot_api.reply_message(event.reply_token, response)


#主程式
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)