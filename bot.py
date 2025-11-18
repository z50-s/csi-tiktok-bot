 import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json, time, re
import telebot
from telebot import types

# 🔑 التوكن من متغيرات البيئة
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8335103523:AAGznpAaYMMgBkMoN_x16T_xUyIE1wCpNAA')

bot = telebot.TeleBot(BOT_TOKEN)

print("""
╔══════════════════════════════════════════╗
║           🤖 CSI Social Info Bot        ║
║             Coded By: CSI-Kr.j          ║
║         Telegram: @CSI_Kr_j             ║
║    For Educational Purposes Only        ║
╚══════════════════════════════════════════╝
🚀 البوت يعمل على السيرفر بنجاح!
""")

class CSITikTokInfo:
    def __init__(self, username: str):
        self.username = self.clean_username(username)
        self.json_data = None
        self.session = requests.Session()
    
    def get_country_name(self, region_code):
        """تحويل رمز المنطقة إلى اسم الدولة - CSI-Kr.j"""
        countries = {
            "US": "🇺🇸 الولايات المتحدة", "SA": "🇸🇦 السعودية", "AE": "🇦🇪 الإمارات",
            "EG": "🇪🇬 مصر", "KW": "🇰🇼 الكويت", "QA": "🇶🇦 قطر", "BH": "🇧🇭 البحرين",
            "OM": "🇴🇲 عمان", "JO": "🇯🇴 الأردن", "LB": "🇱🇧 لبنان", "IQ": "🇮🇶 العراق",
            "SY": "🇸🇾 سوريا", "YE": "🇾🇪 اليمن", "TR": "🇹🇷 تركيا", "FR": "🇫🇷 فرنسا",
            "DE": "🇩🇪 ألمانيا", "GB": "🇬🇧 بريطانيا", "RU": "🇷🇺 روسيا", "CN": "🇨🇳 الصين",
            "JP": "🇯🇵 اليابان", "KR": "🇰🇷 كوريا", "IN": "🇮🇳 الهند", "BR": "🇧🇷 البرازيل",
            "IT": "🇮🇹 إيطاليا", "ES": "🇪🇸 إسبانيا", "CA": "🇨🇦 كندا", "AU": "🇦🇺 أستراليا"
        }
        return countries.get(region_code, region_code if region_code != "غير معروف" else "غير معروف")
    
    def detect_country_from_language(self, language):
        """تخمين الدولة من اللغة - CSI-Kr.j"""
        lang_to_country = {
            "ar": "🇸🇦 السعودية", "en": "🇺🇸 الولايات المتحدة", "fr": "🇫🇷 فرنسا",
            "de": "🇩🇪 ألمانيا", "es": "🇪🇸 إسبانيا", "pt": "🇧🇷 البرازيل",
            "ru": "🇷🇺 روسيا", "ja": "🇯🇵 اليابان", "ko": "🇰🇷 كوريا",
            "tr": "🇹🇷 تركيا", "it": "🇮🇹 إيطاليا", "zh": "🇨🇳 الصين",
            "hi": "🇮🇳 الهند"
        }
        return lang_to_country.get(language, "غير معروف")
    
    def get_country_info(self, user_data):
        """استخراج معلومات الدولة مع توضيح مصدرها - CSI-Kr.j"""
        user = user_data.get("user", {})
        
        # 1. المحاولة الأولى: معلومات دقيقة من تيك توك
        exact_region = user.get('region') or user.get('location') or user.get('country')
        if exact_region and exact_region != "غير معروف":
            country_name = self.get_country_name(exact_region)
            return country_name, exact_region, "معلومات دقيقة من تيك توك"
        
        # 2. المحاولة الثانية: تخمين من اللغة
        language = user.get('language')
        if language and language != "غير معروف":
            guessed_country = self.detect_country_from_language(language)
            if guessed_country != "غير معروف":
                return guessed_country, language, "تخمين من لغة الحساب"
        
        return "غير معروف", "غير معروف", "لم يتم تحديد الدولة"
        
    def clean_username(self, username):
        cleaned = re.sub(r'[^a-zA-Z0-9_.]', '', username)
        return cleaned.strip()
    
    def safe_get(self, data, keys, default="غير معروف"):
        try:
            for key in keys:
                if isinstance(data, dict) and key in data:
                    data = data[key]
                else:
                    return default
            return data
        except:
            return default

    def send_request(self):
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        
        try:
            url = f"https://www.tiktok.com/@{self.username}"
            response = self.session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 404:
                raise Exception(f"الحساب @{self.username} غير موجود")
            elif response.status_code != 200:
                raise Exception(f"خطأ في الاتصال (كود: {response.status_code})")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            script_tag = soup.find('script', {'id': '__UNIVERSAL_DATA_FOR_REHYDRATION__'})
            
            if not script_tag:
                raise Exception("لم يتم العثور على بيانات الحساب")
            
            data = json.loads(script_tag.text)
            self.json_data = self.safe_get(data, ["__DEFAULT_SCOPE__", "webapp.user-detail", "userInfo"])
            
            if self.json_data == "غير معروف":
                raise Exception("فشل في استخراج البيانات")
            
            return True
            
        except Exception as e:
            raise Exception(f"خطأ في جلب البيانات: {str(e)}")

    def get_basic_info(self):
        if not self.json_data:
            return None
            
        user = self.safe_get(self.json_data, ["user"], {})
        stats = self.safe_get(self.json_data, ["stats"], {})
        
        # معلومات الدولة
        country, code, source = self.get_country_info(self.json_data)
        
        def format_number(num):
            try:
                return f"{int(num):,}"
            except:
                return str(num)
        
        info = {
            'user_id': self.safe_get(user, ["id"]),
            'nickname': self.safe_get(user, ["nickname"]),
            'verified': 'نعم' if self.safe_get(user, ["verified"]) in [True, "true"] else 'لا',
            'private': 'نعم' if self.safe_get(user, ["privateAccount"]) in [True, "true"] else 'لا',
            'followers': format_number(self.safe_get(stats, ["followerCount"])),
            'following': format_number(self.safe_get(stats, ["followingCount"])),
            'likes': format_number(self.safe_get(stats, ["heart"])),
            'videos': format_number(self.safe_get(stats, ["videoCount"])),
            'language': self.safe_get(user, ["language"]),
            'country': country,
            'country_source': source,
            'region_code': code
        }
        
        return info

    def get_creation_date(self, user_id):
        try:
            binary = "{0:b}".format(int(user_id))
            if len(binary) >= 31:
                bits = binary[:31]
                timestamp = int(bits, 2)
                return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            return "غير معروف"
        except:
            return "غير معروف"

    def format_info_for_telegram(self, info):
        creation_date = self.get_creation_date(info['user_id'])
        
        message = f"""📊 معلومات حساب تيك توك: @{self.username}

👤 الاسم: {info['nickname']}
🆔 UserID: {info['user_id']}
🌍 الدولة: {info['country']}
📊 مصدر المعلومة: {info['country_source']}
🏷️ الرمز/المصدر: {info['region_code']}
🗣️ اللغة: {info['language']}
✅ موثق: {info['verified']}
🔒 خاص: {info['private']}
👥 المتابعين: {info['followers']}
🫂 يتبع: {info['following']}
❤️ الإعجابات: {info['likes']}
🎬 عدد الفيديوهات: {info['videos']}
📅 تاريخ الإنشاء: {creation_date}

🛠️ Coded By: CSI-Kr.j | Telegram: @CSI_Kr_j
⚖️ For Educational Purposes Only
"""
        
        # إضافة تحذير حول دقة معلومات الدولة
        if "تخمين" in info['country_source']:
            message += "\n⚠️ ملاحظة: معلومات الدولة بناءً على تحليل المحتوى وقد لا تكون دقيقة"
        elif "دقيقة" في info['country_source']:
            message += "\n✅ ملاحظة: معلومات الدولة دقيقة ومستقاة من تيك توك مباشرة"
        
        return message

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
🎉 أهلاً بك في بوت تيك توك المعلومات!

🤖 البوت الرسمي من CSI-Kr.j

📋 الأوامر المتاحة:
/start - عرض هذه الرسالة
/info [username] - جلب معلومات حساب تيك توك
/help - المساعدة

🔍 مثال على الاستخدام:
/info charlidamelio
أو
/info khaby.lame

🛠️ المطور: CSI-Kr.j
📞 للتواصل: @CSI_Kr_j
"""
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['info'])
def get_info(message):
    try:
        command_parts = message.text.split()
        if len(command_parts) < 2:
            bot.reply_to(message, "❌ الاستخدام الصحيح:\n/info username\n\nمثال:\n/info charlidamelio")
            return
        
        username = command_parts[1]
        wait_msg = bot.reply_to(message, "⏳ جاري البحث عن المعلومات...")
        
        tikbot = CSITikTokInfo(username)
        tikbot.send_request()
        info = tikbot.get_basic_info()
        
        if info:
            message_text = tikbot.format_info_for_telegram(info)
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=wait_msg.message_id,
                text=message_text
            )
        else:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=wait_msg.message_id,
                text="❌ لم أتمكن من العثور على معلومات لهذا الحساب"
            )
    
    except Exception as e:
        error_msg = f"❌ حدث خطأ:\n{str(e)}"
        try:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=wait_msg.message_id,
                text=error_msg
            )
        except:
            bot.reply_to(message, error_msg)

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
🆘 مساعدة بوت تيك توك المعلومات

📋 الأوامر:
/start - بدء استخدام البوت
/info [username] - جلب معلومات حساب
/help - المساعدة

🔍 أمثلة:
/info charlidamelio
/info khaby.lame

🛠️ المطور: CSI-Kr.j
📞 الدعم: @CSI_Kr_j
"""
    bot.reply_to(message, help_text)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if not message.text.startswith('/'):
        bot.reply_to(message, "🤖 أرسل /start لبدء استخدام البوت\nأو /help للمساعدة")

if __name__ == "__main__":
    print("🚀 بدأ تشغيل بوت تيليجرام على السيرفر...")
    print(f"🔗 البوت متاح على: t.me/CSI_krj_Sociallnfo_Bot")
    bot.infinity_polling()
