import os
from telegram.ext import Application, CommandHandler
import requests

# Hämta din Telegram-bot-token från miljövariabler
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Skapa bot-applikationen
app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Funktion för att hämta platsinformation via ipinfo.io
def get_location():
    response = requests.get("https://ipinfo.io/json")
    data = response.json()
    
    if "loc" in data:
        lat, lon = data["loc"].split(",")
        return float(lat), float(lon)
    
    return None, None

# Kommandohanterare för /start
async def start(update, context):
    await update.message.reply_text("Hej! Jag kan ge dig flygväder. Använd /weather för att få aktuell information.")

# Kommandohanterare för /weather
async def weather(update, context):
    lat, lon = get_location()
    
    if lat is None or lon is None:
        await update.message.reply_text("Kunde inte hämta platsinformationen.")
        return

    weather_api_url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}"
    headers = {"User-Agent": "TelegramBot/1.0"}
    
    response = requests.get(weather_api_url, headers=headers)
    weather_data = response.json()

    if "properties" in weather_data:
        temp = weather_data["properties"]["timeseries"][0]["data"]["instant"]["details"]["air_temperature"]
        await update.message.reply_text(f"Temperaturen är {temp}°C på din plats.")
    else:
        await update.message.reply_text("Kunde inte hämta väderdata.")

# Lägg till kommandon i botten
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("weather", weather))

# Starta botten
if __name__ == "__main__":
    print("Botten startar...")
    app.run_polling()
