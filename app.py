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
image_list = ["https://imgur.com/2l9Yqh3", 
              "https://imgur.com/TSyfpYs", 
              ]

def dcard():
    path = "C:/Users/alan6/Downloads/edgedriver_win64/msedgedriver.exe"
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
        
        response += f"標題: {title} 人氣: {popular} 日期:{date}\n"
    
    return response

#訊息傳遞區塊
##### 基本上程式編輯都在這個function #####
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    if re.match("你是誰", message):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="我是煒仔啦"))
    elif re.match("超派", message):
        sticker_message = StickerSendMessage(package_id="789", sticker_id="10885")
        line_bot_api.reply_message(event.reply_token, sticker_message)
    elif re.match("ptt (.*)", message):
        index = re.match("ptt (.*)", message).group(1)
        response = ptt(index)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))
    elif re.match("dcard", message):
        response = dcard()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))
    elif re.match("小歐", message):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="小歐滾"))
    elif re.match("唐董", message):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="唐董滾"))
    elif re.match("抽", message):
        image_message = ImageSendMessage(original_content_url=random.choice(image_list))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=image_message))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="哈哈哈"))


#主程式
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
