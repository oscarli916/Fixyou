from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters
from telegram.ext.conversationhandler import ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from google_sheet.google_sheet import GoogleSheet

import logging
from typing import List

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s]: %(message)s',)

END = ConversationHandler.END

BACK_TO_MENU = "back to menu"

EYEBROW = "eyebrow"
MAKEUP = "makeup"
IMAGE = "image"
APPOITMENT = "appoitment"
INQUIRY = "inquiry"

EYEBROW_DETERMINE = "eyebrow determine"

CONCEALER = "concealer"

MATCHING = "matching"

EYEBROW_CLASS = "eyebrow class"
MAKEUP_CLASS = "makeup class"
IMAGE_CLASS = "image class"

WAX_BOOK = "wax_book"
REMOVAL_BOOK = "removal_book"
FACIAL_BOOK = "facial_book"

SELECTION, REGISTER, REGISTER2, EYEBROW_SELECTION, MAKEUP_SELECTION, IMAGE_SELECTION, INQUIRY_SELECTION, APPOITMENT_SELECTION = range(8)

class TelegramBot:

    def __init__(self):
        # self.bot = Bot('1812782819:AAGmYMyDitcBhsTLtgCKJ_fH0vYHzeZtVgA')
        self.updater = Updater(token='1812782819:AAGmYMyDitcBhsTLtgCKJ_fH0vYHzeZtVgA', 
                               use_context=True,
                               workers=32)
        self.dispatcher = self.updater.dispatcher
        self.sheet = GoogleSheet("Fixyou")

    def run(self) -> None:
        """
        Add handler and start listening
        """
        # handlers = []
        handlers = self.get_Handlers()
        for handler in handlers:
            self.dispatcher.add_handler(handler)
        main_Handler = self.main_Handler()
        self.dispatcher.add_handler(main_Handler)

        # self.updater.start_polling(timeout=9999, clean=True)
        self.updater.start_polling()
        self.updater.idle()

    def get_Handlers(self):
        """
        Return Command Handler
        """
        return [CommandHandler("start", self.start)]

    def main_Handler(self) -> ConversationHandler:
        """
        Return Conversation Handler
        """
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("menu", self.menu),
                          CommandHandler("register", self.register)],
            states={
                SELECTION: 
                    [CallbackQueryHandler(self.eyebrow, pattern=f"^{EYEBROW}$"),
                     CallbackQueryHandler(self.makeup, pattern=f"^{MAKEUP}$"),
                     CallbackQueryHandler(self.image, pattern=f"^{IMAGE}$"),
                     CallbackQueryHandler(self.appoitment, pattern=f"^{APPOITMENT}$"),
                     CallbackQueryHandler(self.inquiry, pattern=f"^{INQUIRY}$"),],
                
                REGISTER:
                    [MessageHandler(Filters.text, self.input_phone_number)],

                REGISTER2:
                    [MessageHandler(Filters.text, self.register_user)],

                EYEBROW_SELECTION:
                    [CallbackQueryHandler(self.eyebrow_determine, pattern=f"^{EYEBROW_DETERMINE}$"),
                     CallbackQueryHandler(self.appoitment, pattern=f"^{APPOITMENT}$"),
                     CallbackQueryHandler(self.inquiry, pattern=f"^{INQUIRY}$"),
                     CallbackQueryHandler(self.menu, pattern=f"^{BACK_TO_MENU}$"),],

                MAKEUP_SELECTION:
                    [CallbackQueryHandler(self.concelaer, pattern=f"^{CONCEALER}$"),
                     CallbackQueryHandler(self.appoitment, pattern=f"^{APPOITMENT}$"),
                     CallbackQueryHandler(self.inquiry, pattern=f"^{INQUIRY}$"),
                     CallbackQueryHandler(self.menu, pattern=f"^{BACK_TO_MENU}$"),],

                IMAGE_SELECTION:
                    [CallbackQueryHandler(self.matching, pattern=f"^{MATCHING}$"),
                     CallbackQueryHandler(self.appoitment, pattern=f"^{APPOITMENT}$"),
                     CallbackQueryHandler(self.inquiry, pattern=f"^{INQUIRY}$"),
                     CallbackQueryHandler(self.menu, pattern=f"^{BACK_TO_MENU}$"),],

                INQUIRY_SELECTION:
                    [CallbackQueryHandler(self.eyebrow_class, pattern=f"^{EYEBROW_CLASS}$"),
                     CallbackQueryHandler(self.makeup_class, pattern=f"^{MAKEUP_CLASS}$"),
                     CallbackQueryHandler(self.image_class, pattern=f"^{IMAGE_CLASS}$"),],

                APPOITMENT_SELECTION:
                    [CallbackQueryHandler(self.wax_book, pattern=f"^{WAX_BOOK}$"),
                     CallbackQueryHandler(self.removal_book, pattern=f"^{REMOVAL_BOOK}$"),
                     CallbackQueryHandler(self.facial_book, pattern=f"^{FACIAL_BOOK}$"),]
            },
            fallbacks=[CommandHandler("restart", self.restart)],
            # per_message=True,
            run_async=True
        )

        return conv_handler

    def menu(self, update: Update, context: CallbackContext):
        """
        Telegram Bot menu command
        """
        ## Check User registered or not
        user_id = update.effective_user.id
        user_list = self.get_all_tg_bot_id()
        if not str(user_id) in user_list:
            ## User not registered
            text = "此帳號沒有注冊, 請按 /register 進行注冊"
            update.message.reply_text(text=text)
            self.log_to_console(user_info=update.effective_user, msg="User not yet registered.")
            return END

        # Button
        keyboard = [
                    [InlineKeyboardButton(text="修眉入門介紹", callback_data=str(EYEBROW))],
                    [InlineKeyboardButton(text="化妝新手簡介", callback_data=str(MAKEUP))],
                    [InlineKeyboardButton(text="形象小教學", callback_data=str(IMAGE))],
                    [InlineKeyboardButton(text="美容服務", callback_data=str(APPOITMENT))],
                    [InlineKeyboardButton(text="課程查詢", callback_data=str(INQUIRY))],
                ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        text = "請選擇:" 
        # try:
        #     update.message.reply_text(text=text, reply_markup=reply_markup)
        # except:
        #     update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)

        if context.user_data.get("start_over"):
            update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
        else:
            update.message.reply_text(text=text, reply_markup=reply_markup)
        context.user_data["start_over"] = False

        return SELECTION

# =========================================
# Start
# =========================================
    def start(self, update: Update, context: CallbackContext):
        text = "請按 /menu 開始"
        update.message.reply_text(text=text)
        return END
        
# =========================================
# Register
# =========================================
    def register(self, update: Update, context: CallbackContext):
        """
        Register User.
        If user id not in google sheet. Ask user input email
        """
        user_id = update.effective_user.id
        user_list = self.get_all_tg_bot_id()
        if str(user_id) in user_list:
            ## User registered
            text = "此帳號已注冊 請按 /menu 開始"
            update.message.reply_text(text=text)
            self.log_to_console(user_info=update.effective_user, 
                                msg="Account has been registered (ID already in googlesheet).")
            return END
        else:
            text = "請輸入電郵地址:"
            update.message.reply_text(text=text)
            return REGISTER
    
    def input_phone_number(self, update: Update, context: CallbackContext):
        """
        Save email input
        Ask user input phone number
        """
        ### Save email
        msg = update.message.text
        context.user_data['email'] = str(msg).lower()
        ### Phone number
        text = "請輸入電話號碼: (例如:852 12345678)"
        update.message.reply_text(text=text)
        return REGISTER2

    def register_user(self, update: Update, context: CallbackContext):
        """
        Save Phone number
        Check if input has been used
        If not yet used then register user
        """
        ### Save Phone number
        msg = update.message.text
        context.user_data['phone'] = str(msg).lower()

        ### Check if input has been used
        user_data = context.user_data
        email = user_data['email']
        phone_num = user_data['phone']
        user_id = update.effective_user.id
        if self.check_input_exist(email=email, phone_num=phone_num):
            ## Input has been used
            text = f"此帳號已被使用, 請檢查輸入是否正確"
            update.message.reply_text(text=text)
            self.log_to_console(user_info=update.effective_user, 
                                msg="Account has been used (Input already exist in googlesheet).")
            return END  
        else:
            ## Input not yet used. Register
            self.register_user_to_sheet(email=email, phone_num=phone_num, id=user_id)
            text = "成功註冊 請按 /menu 開始"
            update.message.reply_text(text=text)
            self.log_to_console(user_info=update.effective_user, 
                                msg="Successful registered.")

        context.user_data.clear()
        return END

# =========================================
# Restart
# =========================================
    def restart(self, update: Update, context: CallbackContext) -> END:
        """
        Clear all user data(input) and stop conversation
        """
        update.message.reply_text("已重新開始, 請按:\n/menu")
        context.user_data.clear()
        self.log_to_console(user_info=update.effective_user, msg="RESTART")
        return END

# =========================================
# Eyebrow
# =========================================
    def eyebrow(self, update: Update, context: CallbackContext) -> EYEBROW_SELECTION:
        """
        Telegram Bot 修眉入門介紹 Button
        """
        ### Get Chat ID
        chat_id = update.effective_chat.id
        ### Title
        update.callback_query.edit_message_text(text="眉形分類:")
        ### Image
        path = r"C:\Users\Option00\Share\Programing\fix_you_make_up\telegram_bot\images\A_eyebrow.jpg"
        with open(path, "rb") as f:
            context.bot.send_photo(chat_id, f)
        ### Content
        content = '以上就係眉形一共可以分為 8 個種類，而眉的大小粗幼都可以影響到以上的眉形出現微小的變化，我們先分類幾種眉形種類方便令大家識別。\n\n' '以上古裝的演員就是 "柳葉眉" ，因為眉頭比較细，只有小拇指一半粗细，以及帶出古風，顯成熟優雅女人味，而要留意的地方就是如果使用失當，就會直接顯老，故近代都比較小人使用。\n\n' '以上現代眼大的人都會比較喜歡 "劍眉"，眉形方面眉頭略窄，眉山為最高峰，下綫畫平，令人感覺容易接近有善意，所以會是大家容易喜歡的眉型種類。\n\n' '而我地就確定到自己的眉形之前，其實面形及眼形辨認都非常緊要。'
        context.bot.send_message(chat_id, content)
        ### Keyboard
        keyboard = [
                    [InlineKeyboardButton(text="修眉的判斷", callback_data=str(EYEBROW_DETERMINE))],
                ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id, text="下一篇:", reply_markup=reply_markup)

        return EYEBROW_SELECTION

    def eyebrow_determine(self, update: Update, context: CallbackContext) -> EYEBROW_SELECTION:
        """
        Telegram Bot 修眉的判斷 Button
        """
        ### Get Chat ID
        chat_id = update.effective_chat.id
        ### Title
        update.callback_query.edit_message_text(text="修眉的判斷:")
        ### Image
        path = r"C:\Users\Option00\Share\Programing\fix_you_make_up\telegram_bot\images\B_eyebrow.jpg"
        with open(path, "rb") as f:
            context.bot.send_photo(chat_id, f)
        ### Content
        content='以上左上角的面形就是 "Oval" 鵝蛋臉，鵝蛋臉是一個適合任何眉型的屈機面形，例如鵝蛋臉配合 "低彎眉" 會比較帶女人味，又或者平直略帶弧度的眉型即 "流星眉" 或英眉，也可帶有聰明及知性的感覺。\n\n' '以上左下角的面形就是 "Square" 方形臉，方形臉帶給人的感覺容易有 "霸氣" 外洩的問題，眉形上如果菱角比較明顯例如 "工字眉" 都會令 "霸氣" 更甚，面相看起來更凶惡，所以比較合適的眉形例如 "粗流星眉"，會較為適合。'
        context.bot.send_message(chat_id, content)
        ### Keyboard
        keyboard = [
                     [InlineKeyboardButton(text="美容服務", callback_data=str(APPOITMENT))],
                     [InlineKeyboardButton(text="課程查詢", callback_data=str(INQUIRY))],
                     [InlineKeyboardButton(text="返回首頁資訊站", callback_data=str(BACK_TO_MENU))],
                ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id, text="請選擇:", reply_markup=reply_markup)
        ### Start over
        context.user_data["start_over"] = True

        return EYEBROW_SELECTION

# =========================================
# Makeup
# =========================================
    def makeup(self, update: Update, context: CallbackContext) -> MAKEUP_SELECTION:
        """
        Telegram Bot 化妝新手簡介 Button
        """
        ### Get Chat ID
        chat_id = update.effective_chat.id
        ### Title
        update.callback_query.edit_message_text(text="膚淺配合:")
        ### Content
        content = "Content"
        context.bot.send_message(chat_id, content)
        ### Image
        path = r"C:\Users\Option00\Pictures\yip fb\WhatsApp Image 2021-03-24 at 3.05.26 PM.jpeg"
        with open(path, "rb") as f:
            context.bot.send_photo(chat_id, f)
        ### Keyboard
        keyboard = [
                    [InlineKeyboardButton(text="遮瑕方法", callback_data=str(CONCEALER))],
                ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id, text="下一篇:", reply_markup=reply_markup)

        return MAKEUP_SELECTION

    def concelaer(self, update: Update, context: CallbackContext) -> MAKEUP_SELECTION:
        """
        Telegram Bot 遮瑕方法 Button
        """
        ### Get Chat ID
        chat_id = update.effective_chat.id
        ### Title
        update.callback_query.edit_message_text(text="遮瑕方法:")
        ### Content
        content = "Content"
        context.bot.send_message(chat_id, content)
        ### Image
        path = r"C:\Users\Option00\Pictures\yip fb\WhatsApp Image 2021-03-24 at 3.05.27 PM.jpeg"
        with open(path, "rb") as f:
            context.bot.send_photo(chat_id, f)
        ### Keyboard
        keyboard = [
                     [InlineKeyboardButton(text="美容服務", callback_data=str(APPOITMENT))],
                     [InlineKeyboardButton(text="課程查詢", callback_data=str(INQUIRY))],
                     [InlineKeyboardButton(text="返回首頁資訊站", callback_data=str(BACK_TO_MENU))],
                ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id, text="請選擇:", reply_markup=reply_markup)
        ### Start over
        context.user_data["start_over"] = True

        return MAKEUP_SELECTION

# =========================================
# Image
# =========================================
    def image(self, update: Update, context: CallbackContext) -> IMAGE_SELECTION:
        """
        Telegram Bot 形象小教學 Button
        """
        ### Get Chat ID
        chat_id = update.effective_chat.id
        ### Title
        update.callback_query.edit_message_text(text="顏色學:")
        ### Content
        content = "Content"
        context.bot.send_message(chat_id, content)
        ### Image
        path = r"C:\Users\Option00\Pictures\yip fb\WhatsApp Image 2021-03-24 at 3.05.26 PM.jpeg"
        with open(path, "rb") as f:
            context.bot.send_photo(chat_id, f)
        ### Keyboard
        keyboard = [
                    [InlineKeyboardButton(text="配搭風格", callback_data=str(MATCHING))],
                ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id, text="下一篇:", reply_markup=reply_markup)

        return IMAGE_SELECTION

    def matching(self, update: Update, context: CallbackContext) -> IMAGE_SELECTION:
        """
        Telegram Bot 配搭風格 Button
        """
        ### Get Chat ID
        chat_id = update.effective_chat.id
        ### Title
        update.callback_query.edit_message_text(text="配搭風格:")
        ### Content
        content = "Content"
        context.bot.send_message(chat_id, content)
        ### Image
        path = r"C:\Users\Option00\Pictures\yip fb\WhatsApp Image 2021-03-24 at 3.05.27 PM.jpeg"
        with open(path, "rb") as f:
            context.bot.send_photo(chat_id, f)
        ### Keyboard
        keyboard = [
                     [InlineKeyboardButton(text="美容服務", callback_data=str(APPOITMENT))],
                     [InlineKeyboardButton(text="課程查詢", callback_data=str(INQUIRY))],
                     [InlineKeyboardButton(text="返回首頁資訊站", callback_data=str(BACK_TO_MENU))],
                ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id, text="請選擇:", reply_markup=reply_markup)
        ### Start over
        context.user_data["start_over"] = True

        return IMAGE_SELECTION

# =========================================
# Appoitment
# =========================================
    def appoitment(self, update: Update, context: CallbackContext) -> APPOITMENT_SELECTION:
        """
        Telegram Bot 美容服務 Button
        """
        keyboard = [
                    [InlineKeyboardButton(text="蜜蠟修眉 預約", callback_data=str(WAX_BOOK))],
                    [InlineKeyboardButton(text="Body Wax(身體脫毛) 預約", callback_data=str(REMOVAL_BOOK))],
                    [InlineKeyboardButton(text="Facial(臉部皮膚護理) 預約", callback_data=str(FACIAL_BOOK))],
                ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        text = "請選擇:" 
        update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)

        return APPOITMENT_SELECTION
    
    def wax_book(self, update: Update, context: CallbackContext) -> END:
        """
        Telegram Bot 蜜蠟修眉 預約 Button
        """
        text = "https://wa.me/85291224282?text=蜜蠟修眉$250"
        update.callback_query.edit_message_text(text=text)
        self.log_to_console(user_info=update.effective_user, msg="蜜蠟修眉 預約")
        return END

    def removal_book(self, update: Update, context: CallbackContext) -> END:
        """
        Telegram Bot Body Wax(身體脫毛) 預約 Button
        """
        text = "https://wa.me/85291224282?text=蜜蠟修眉$250"
        update.callback_query.edit_message_text(text=text)
        self.log_to_console(user_info=update.effective_user, msg="Body Wax(身體脫毛) 預約")
        return END

    def facial_book(self, update: Update, context: CallbackContext) -> END:
        """
        Telegram Bot Facial(臉部皮膚護理) 預約 Button
        """
        text = "https://wa.me/85291224282?text=蜜蠟修眉$250"
        update.callback_query.edit_message_text(text=text)
        self.log_to_console(user_info=update.effective_user, msg="Facial(臉部皮膚護理) 預約")
        return END

# =========================================
# Inquiry
# =========================================
    def inquiry(self, update: Update, context: CallbackContext) -> INQUIRY_SELECTION:
        """
        Telegram Bot 課程查詢 Button
        """
        keyboard = [
                    [InlineKeyboardButton(text="眉妝班查詢及預約", callback_data=str(EYEBROW_CLASS))],
                    [InlineKeyboardButton(text="化妝班查詢及預約", callback_data=str(MAKEUP_CLASS))],
                    [InlineKeyboardButton(text="形象班查詢及預約", callback_data=str(IMAGE_CLASS))],
                ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        text = "請選擇:" 
        update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)

        return INQUIRY_SELECTION

    def eyebrow_class(self, update: Update, context: CallbackContext) -> END:
        """
        Telegram Bot 眉妝班查詢及預約 Button
        """
        text = "https://wa.me/85261220025?text=我想查詢修眉課程"
        update.callback_query.edit_message_text(text=text)
        self.log_to_console(user_info=update.effective_user, msg="眉妝班查詢及預約")
        return END

    def makeup_class(self, update: Update, context: CallbackContext) -> END:
        
        """
        Telegram Bot 化妝班查詢及預約 Button
        """
        text = "https://wa.me/85261220025?text=我想查詢修眉課程"
        update.callback_query.edit_message_text(text=text)
        self.log_to_console(user_info=update.effective_user, msg="化妝班查詢及預約")
        return END

    def image_class(self, update: Update, context: CallbackContext) -> END:
        """
        Telegram Bot 形象班查詢及預約 Button
        """
        text = "https://wa.me/85261220025?text=我想查詢修眉課程"
        update.callback_query.edit_message_text(text=text)
        self.log_to_console(user_info=update.effective_user, msg="形象班查詢及預約")
        return END

# =========================================
# Helper Function
# =========================================
    def get_all_tg_bot_id(self) -> List[str]:
        """
        Return List of tg user id
        """
        user_list_df = self.sheet.get_df_by_range_names(["tg_bot_id"])
        user_list = user_list_df['tg_bot_id'].to_list()
        user_list.pop(0)
        return user_list

    def get_all_email(self) -> List[str]:
        """
        Return List of email
        """
        email_list_df = self.sheet.get_df_by_range_names(["email"])
        email_list = email_list_df["email"].to_list()
        email_list.pop(0)
        return email_list
    
    def get_all_phone_number(self) -> List[str]:
        """
        Return List of phone number
        """
        phone_list_df = self.sheet.get_df_by_range_names(["phone_num"])
        phone_list = phone_list_df["phone_num"].to_list()
        phone_list.pop(0)
        return phone_list

    def check_input_exist(self, email: str, phone_num: str) -> bool:
        """
        Return True if input is already exists

        Args:
            email: User input's email
            phone_num: User input's phone number
        """
        email_list = self.get_all_email()
        phone_list = self.get_all_phone_number()
        if email in email_list or phone_num in phone_list:
            return True
        return False

    def get_sheet_last_row(self) -> int:
        """
        Return row number of the last row of the sheet (Use Email column)
        """
        email_list = self.get_all_email()
        return len(email_list) + 2
     
    def register_user_to_sheet(self, email: str, phone_num: str, id:int) -> None:
        """
        Register user input to google sheet

        Args:
            email: User input's email
            phone_num: User input's phone number
            id: tg id
        """
        row = self.get_sheet_last_row()
        ## Update Email column
        self.sheet.update_by_col_name(row, "Email", email)
        ## Update Phone column
        self.sheet.update_by_col_name(row, "Phone", phone_num)
        ## Update tg bot id column
        self.sheet.update_by_col_name(row, "tg bot id", id)
        
    def log_to_console(self, user_info, msg="") -> None:
        logging.info(f"{user_info}: {msg}")