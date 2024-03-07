import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
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

############################################################################
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
service = Service('${PATH}:/opt/render/project/.render/chrome/opt/google/chrome') 
driver = webdriver.Chrome(service=service)
############################################################################

app = Flask(__name__)

# 必須放上自己的Channel Access Token
line_bot_api = LineBotApi('9yR4ewDjV8MMC1s8DCcZbCHhwYzFvoVWR8OM3XIckQaV7JSzLvIDc581psOLe+b/J7Iu7qCIrJDPFypvefXy+D4udYFHl9OSYoSXFIEkJmKpjhHPBk3UQP5Kqk37isFkfytaPpgoWh3o0mQwrS5wvQdB04t89/1O/w1cDnyilFU=')
# 必須放上自己的Channel Secret
handler = WebhookHandler('046d3499ea137d0ac4192b9224c91899')

line_bot_api.push_message('U2245cda9373cd500a6fe9e8053729eac', TextSendMessage(text='請開始你的表演'))


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
                    "超派": StickerSendMessage(package_id="789", sticker_id="10885"),
                    "小歐": "小歐滾",
                    "唐董": "唐董滾",
                    "一哥": "邏輯思考 x 有一說一",
                    "哈": "哈哈哈",
                    "煒仔": "我是佑哥啦",
                    "升級完成": "強勢回歸",
                    "仇": "不要以為我們台灣人都是客客氣氣的",
                    "吼": ImageSendMessage(original_content_url="https://i.imgur.com/vy670dJ.jpg", preview_image_url="https://i.imgur.com/vy670dJ.jpg"),
                    "天意": ImageSendMessage(original_content_url="https://s.yimg.com/ny/api/res/1.2/VAx4xb76m28_GmqE9cuhaw--/YXBwaWQ9aGlnaGxhbmRlcjt3PTk2MDtoPTU0MDtjZj13ZWJw/https://media.zenfs.com/ko/news_ttv_com_tw_433/f273a5380639108f8af906a33a9d4fcd", preview_image_url="https://s.yimg.com/ny/api/res/1.2/VAx4xb76m28_GmqE9cuhaw--/YXBwaWQ9aGlnaGxhbmRlcjt3PTk2MDtoPTU0MDtjZj13ZWJw/https://media.zenfs.com/ko/news_ttv_com_tw_433/f273a5380639108f8af906a33a9d4fcd"),
                    "侯侯": ImageSendMessage(original_content_url="https://cc.tvbs.com.tw/img/upload/2023/12/26/20231226181119-db1a2fd9.jpg", preview_image_url="https://cc.tvbs.com.tw/img/upload/2023/12/26/20231226181119-db1a2fd9.jpg"),
                    "垃圾": ImageSendMessage(original_content_url="https://image.taisounds.com/newsimages/img/2023/0629/20230629125144.jpg", preview_image_url="https://image.taisounds.com/newsimages/img/2023/0629/20230629125144.jpg"),

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
              'https://i.imgur.com/kl0BZLt.jpg'
              ]

def dcard():
    path = "${PATH}:/opt/render/project/.render/chrome/opt/google/chrome/"
    driver = webdriver.Edge()
    url = "https://www.dcard.tw/f/utaipei?tab=latest"
    driver.get(url)
    dates = []
    titles = []

    def get_title():
        title_value = driver.find_elements(By.CLASS_NAME, "atm_cs_1hcvtr6")
        for a in title_value:
            titles.append(a.text)
        return titles

    def get_date():
        time_element = driver.find_elements(By.XPATH, "//time")
        for times in time_element:
            datetime = times.get_attribute("datetime")
            date = datetime.split("T")[0]
            dates.append(date)
        return dates

    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "atm_9s_1txwivl"))
    )

    dates = get_date()
    titles = get_title()

    response = ""

    for i in range(len(dates)):
        response += f"\n{dates[i]} {titles[i]}\n"

    return response

def ptt(index):
    url = f"https://www.ptt.cc/bbs/{index}/index.html"
    headers = {"userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36", "Cookie": "over18=1"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    article = soup.find_all("div", class_ = "r-ent")
    response = ""
    for a in article:
        title = a.find("div", class_ = "title")
        if title and title.a:
            title = title.a.text
        else:
            title = "找不到"

        popular = a.find("div", class_ = "nrec")
        if popular and popular.span:
            popular = popular.span.text
        else:
            popular = "無"

        date = a.find("div", class_ = "date")
        if date:
            date = date.text
        else:
            date = "無"
        
        response += f"{title} \n 人氣: {popular} \n 日期:{date}\n"
    
    return response

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
        elif re.match("dcard", message):
            response = dcard()
        elif re.match("ptt (.*)", message):
            index = re.match("ptt (.*)", message).group(1)
            response = ptt(index)
        elif re.match("佑哥", message):
            img_url = "https://i.imgur.com/SLlr25K.jpg"
            response = ImageSendMessage(original_content_url=img_url, preview_image_url=img_url)
            line_bot_api.reply_message(event.reply_token, response)
            response = TextSendMessage(text="領域展開")
            line_bot_api.reply_message(event.reply_token, response)
    
    # 如果 response 不是 None，則表示找到了相符的回覆
    if response:
        if isinstance(response, str):
            response = TextSendMessage(text=response)
        line_bot_api.reply_message(event.reply_token, response)


#主程式
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
