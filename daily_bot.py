import os
import requests
from telegram import Bot
import asyncio
import hmac
import base64
import time
import urllib.parse
from hashlib import sha256

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
CITY_NAME = os.getenv('CITY_NAME')
CLOUDFLARE_API_KEY = os.getenv('CLOUDFLARE_API_KEY')

ICON_MAP = {
    '01d': '☀️',
    '02d': '⛅️',
    '03d': '☁️',
    '04d': '☁️',
    '09d': '🌧',
    '10d': '🌦',
    '11d': '🌩',
    '13d': '❄️',
    '50d': '🌫',
}

def get_weather_icon(icon_id):
    return ICON_MAP.get(icon_id)

def generate_weather_img(weather):
    message = "/text2img"
    # utc 0 时区
    timestamp = time.time()
    timestamp = str(int(time.time()))
    digest = hmac.new(CLOUDFLARE_API_KEY.encode('utf8'), "{}{}".format(message, timestamp).encode('utf8'), sha256)
    token = urllib.parse.quote_plus(base64.b64encode(digest.digest()))
    url = f'https://ai.catlulu.net/text2img?prompt={weather}&verify={timestamp}-{token}'
    response = requests.get(url)
    return response.content

def get_weather():
    url = f'http://api.openweathermap.org/data/2.5/weather?q={CITY_NAME}&appid={WEATHER_API_KEY}&units=metric'
    response = requests.get(url)
    weather_data = response.json()

    if response.status_code == 200:
        weather_description = weather_data['weather'][0]['description']
        temperature = weather_data['main']['temp']
        icon_id = weather_data['weather'][0]['icon']
        weather_report = f"Weather in {CITY_NAME}: {get_weather_icon(icon_id)} {weather_description}, Temperature: {temperature}°C"
        weather_img = generate_weather_img(weather_description)
    else:
        weather_report = "Unable to fetch weather data at the moment."
    
    return {'text': weather_report, 'img': weather_img}

def get_exchange_rate():
    url = f'https://fin.paas.cmbchina.com/fininfo/api/calculator/getFxRealRate?bsflag=buy&chflag=XH&currency=39'
    response = requests.get(url)
    exchange_data = response.json()

    if response.status_code == 200:
        exchange_report = f"今日招行加币🇨🇦汇率：{exchange_data['body']['rate']}🇨🇳"
    else:
        exchange_report = '获取汇率失败'

    return exchange_report

async def send_message(message):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    response = await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    print(response)

async def send_photo(photo, caption):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    response = await bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=photo, caption=caption)

async def main():
    weather = get_weather()
    exchange_rate = get_exchange_rate()
    if weather['img']:
        await send_photo(weather['img'], f"{weather['text']}\n{exchange_rate}")
    else:
        message = f"{weather}\n{exchange_rate}"
        await send_message(message)

if __name__ == '__main__':
    asyncio.run(main())