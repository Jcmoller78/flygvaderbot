import requests
import json
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Din API-nyckel för Telegram-botten
TELEGRAM_BOT_TOKEN = "DIN_TELEGRAM_BOT_TOKEN"

# Funktion för att hämta platsinformation via IP
def get_location():
    response = requests.get("https://ipinfo.io/json")
    data = response.json()
    if "loc" in data:
        lat, lon = data["loc"].split(",")
        return float(lat), float(lon)
    return None, None

# Funktion för att hämta väder från SMHI
def get_smhi_weather(lat, lon):
    url = f"https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geopoint/lat/{lat}/lon/{lon}/data.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for item in data["timeSeries"][:3]:  # Nu, 1h, 24h
            print(item)
        return data["timeSeries"][:3]  # Returnerar de tre första mätningarna
    return None

# Funktion för att hämta KP-index
def get_kp_index():
    url = "https://api.spaceweatherlive.com/kp.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["kpIndex"]["current"]  # Nuvarande KP-index
    return "Ej tillgängligt"

# Funktion för Telegram-kommandot /väder
def weather_command(update: Update, context: CallbackContext) -> None:
    lat, lon = get_location()
    if not lat or not lon:
        update.message.reply_text("Kunde inte hämta platsinformation.")
        return

    smhi_weather = get_smhi_weather(lat, lon)
    kp_index = get_kp_index()

    if smhi_weather:
        weather_text = "**Väderinformation:**\n"
        for i, entry in enumerate(smhi_weather):
            time = entry["validTime"]
            temp = next(param["values"][0] for param in entry["parameters"] if param["name"] == "t")
            wind = next(param["values"][0] for param in entry["parameters"] if param["name"] == "ws")
            humidity = next(param["values"][0] for param in entry["parameters"] if param["name"] == "r")
            precipitation = next(param["values"][0] for param in entry["parameters"] if param["name"] == "pmean")

            if i == 0:
                title = "Nu"
            elif i == 1:
                title = "Om 1 timme"
            else:
                title = "Om 24 timmar"

            weather_text += f"\n🔹 **{title}** ({time})\n"
            weather_text += f"🌡 Temperatur: {temp}°C\n"
            weather_text += f"💨 Vindhastighet: {wind} m/s\n"
            weather_text += f"💧 Luftfuktighet: {humidity}%\n"
            weather_text += f"🌧 Nederbörd: {precipitation} mm\n"

        weather_text += f"\n🌍 **Geomagnetisk aktivitet (KP-index):** {kp_index}"
    else:
        weather_text = "Kunde inte hämta väderinformation."

    update.message.reply_text(weather_text, parse_mode="Markdown")

# Skapa och starta Telegram-botten
def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("väder", weather_command))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
