from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from Data import db_session
from Data.trenirovki import Trenirovki
from Data.users import Users
from text_msg import *
from controlUser import ControlUser
from datetime import date

import traceback
import json
import yaml


# with open('tg_bot//cfg.yml') as fh:
with open('cfg.yml') as fh:
    read_data = yaml.load(fh, Loader=yaml.FullLoader)

updater = Updater(read_data["tg_key"], use_context=True)
bot = Bot(read_data["tg_key"])
dp = updater.dispatcher
db_session.global_init('db/botfit.sqlite')
user_class = {}


def start(update, context):
    print('OKEY!111')
    session = db_session.create_session()
    try:
        user = session.query(Users).filter(Users.tg_id == update.message.from_user.id).first()
        if not user:
            new_user = ControlUser(update.message.from_user.id)
            user_class[update.message.from_user.id] = new_user
            new_user = Users(tg_id=update.message.from_user.id, first_name=update.message.from_user.first_name)
            session.add(new_user)
            session.commit()
            keyboard_start = InlineKeyboardMarkup(
                [[InlineKeyboardButton('Создать тренировку', callback_data='new_fit')]])
            update.message.reply_text(add_new_user.format(name=update.message.from_user.first_name),
                                      reply_markup=keyboard_start)
        else:
            user_start = user_class[update.message.from_user.id]
            user_start.reboot()
            treni = session.query(Trenirovki).filter(Trenirovki.user_id == user.id).first()
            if not treni:
                keyboard_start = InlineKeyboardMarkup(
                    [[InlineKeyboardButton('Создать тренировку', callback_data='new_fit')]])
                update.message.reply_text(add_new_user.format(name=update.message.from_user.first_name),
                                          reply_markup=keyboard_start)
            else:
                keyboard_start = InlineKeyboardMarkup(
                    [[InlineKeyboardButton('Показать тренировку', callback_data='get_fit')],
                     [InlineKeyboardButton('Начать тренировку', callback_data='start_fit')],
                     [InlineKeyboardButton('Удалить тренировку', callback_data='delete_fit')],
                     [InlineKeyboardButton('Показать статистику', callback_data='get_statistic')]])
                update.message.reply_text(main_menu, reply_markup=keyboard_start)
    except Exception as e:
        print(traceback.format_exc())
    finally:
        session.close()


def msg(update, context):
    session = db_session.create_session()
    try:
        user = user_class[update.message.from_user.id]
        if user.get_button_new_fit():
            user_text = update.message.text.split('\n')
            days = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']
            treni = {}
            res = {}
            day = ''
            for i in user_text:
                if i.lower() in days:
                    treni[i.lower()] = []
                    day = i.lower()
                elif i != ' ':
                    res[f'{day}_{i}'] = {}
                    treni[day].append(i)
            json_treni = json.dumps(treni)
            json_res = json.dumps(res)
            user = session.query(Users).filter(Users.tg_id == update.message.from_user.id).first()
            new_treni = Trenirovki(user_id=user.id, description=json_treni, result=json_res)
            session.add(new_treni)
            session.commit()
            update.message.reply_text(add_new_fit_success)
        elif user.get_number_fit() != -1:
            user_text = update.message.text
            userr = session.query(Users).filter(Users.tg_id == update.message.from_user.id).first()
            treni = session.query(Trenirovki).filter(Trenirovki.user_id == userr.id).first()
            desc_json = json.loads(treni.description)
            res_json = json.loads(treni.result)
            res_json[f'{user.get_day()}_{desc_json[user.get_day()][user.get_number_fit()]}'][
                str(date.today())] = user_text
            json_res = json.dumps(res_json)
            treni.result = json_res
            session.commit()
            if len(desc_json[user.get_day()]) > user.get_number_fit() + 1:
                update.message.reply_text(
                    template_exersice.format(desc_json[user.get_day()][user.get_number_fit() + 1]))
                user.set_number_fit(user.get_number_fit() + 1)
            else:
                update.message.reply_text(end_fit)
                user.set_number_fit(-1)
                user.set_day('')
        else:
            update.message.reply_text(fail)
    except Exception as e:
        print(traceback.format_exc())
    finally:
        session.close()


def button(update, context):
    session = db_session.create_session()
    try:
        query = update.callback_query
        variant = query.data
        if variant == 'new_fit':
            user_class[query.from_user.id].set_button_new_fit()
            bot.edit_message_text(chat_id=query.from_user.id, text=add_new_fit, reply_markup=None,
                                  message_id=query.message.message_id)
        elif variant == 'get_fit':
            user = session.query(Users).filter(Users.tg_id == query.from_user.id).first()
            treni = session.query(Trenirovki).filter(Trenirovki.user_id == user.id).first()
            if treni:
                description = ''
                for key, value in json.loads(treni.description).items():
                    description += key.title() + ':\n'
                    for j in value:
                        description += j.title() + '\n'
                    description += '\n'
                bot.edit_message_text(chat_id=query.from_user.id, text=get_fit_msg.format(trenya=description),
                                      message_id=query.message.message_id)
            else:
                bot.send_message(chat_id=query.from_user.id, text=fail)
        elif variant == 'delete_fit':
            user = session.query(Users).filter(Users.tg_id == query.from_user.id).first()
            treni = session.query(Trenirovki).filter(Trenirovki.user_id == user.id).first()
            session.delete(treni)
            session.commit()
            bot.edit_message_text(chat_id=query.from_user.id, text=delete_fit, message_id=query.message.message_id)
        elif variant == 'get_statistic':
            user = session.query(Users).filter(Users.tg_id == query.from_user.id).first()
            treni = session.query(Trenirovki).filter(Trenirovki.user_id == user.id).first()
            trenya_json = json.loads(treni.description)
            keyboard_trenya = []
            for key in trenya_json.keys():
                keyboard_trenya.append([InlineKeyboardButton(key, callback_data=f'stata;{key}')])
            keyboard_trenya = InlineKeyboardMarkup(keyboard_trenya)
            bot.edit_message_text(chat_id=query.from_user.id, text=start_fit_msg, reply_markup=keyboard_trenya,
                                  message_id=query.message.message_id)
        elif 'stata' in variant:
            user = session.query(Users).filter(Users.tg_id == query.from_user.id).first()
            treni = session.query(Trenirovki).filter(Trenirovki.user_id == user.id).first()
            json_trenya = json.loads(treni.result)
            day_trenya = variant.split(';')[1]
            res = ''
            for key, value in json_trenya.items():
                if day_trenya in key:
                    f = key.split('_')[1]
                    if f:
                        res += f + ':\n'
                        sorted_list = sorted(list(value.keys()))
                        res += '\n'.join([f'{i}: {value[i]}' for i in sorted_list[-5:]]) + '\n\n'
            if '2' not in res:
                bot.send_message(chat_id=query.from_user.id, text=not_found_res)
            else:
                bot.send_message(chat_id=query.from_user.id, text=res)
        elif variant == 'start_fit':
            user = session.query(Users).filter(Users.tg_id == query.from_user.id).first()
            treni = session.query(Trenirovki).filter(Trenirovki.user_id == user.id).first()
            json_trenya = json.loads(treni.description)
            keyboard_trenya = []
            for key in json_trenya.keys():
                keyboard_trenya.append([InlineKeyboardButton(key, callback_data=f'day;{key}')])
            keyboard_trenya = InlineKeyboardMarkup(keyboard_trenya)
            bot.edit_message_text(chat_id=query.from_user.id, text=start_fit_msg, reply_markup=keyboard_trenya,
                                  message_id=query.message.message_id)
        elif 'day' in variant:
            user = session.query(Users).filter(Users.tg_id == query.from_user.id).first()
            treni = session.query(Trenirovki).filter(Trenirovki.user_id == user.id).first()
            json_trenya = json.loads(treni.description)
            day_trenya = variant.split(';')[1]
            user_class[query.from_user.id].set_number_fit(0)
            user_class[query.from_user.id].set_day(day_trenya)
            bot.send_message(chat_id=query.from_user.id, text=template_exersice.format(json_trenya[day_trenya][0]))
        bot.answer_callback_query(callback_query_id=query.id)
    except Exception as e:
        print(traceback.format_exc())
    finally:
        session.close()


def initialize():
    session = db_session.create_session()
    users = session.query(Users).all()
    for user in users:
        new_user = ControlUser(user.tg_id)
        user_class[user.tg_id] = new_user
    session.close()


dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text, msg))
dp.add_handler(CallbackQueryHandler(button))

if __name__ == "__main__":
    initialize()
    updater.start_polling()
