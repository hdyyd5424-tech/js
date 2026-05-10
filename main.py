import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random
import os
from dotenv import load_dotenv
from vk_api import VkUpload



load_dotenv()
new_token = os.getenv('BOT_TOKEN')
old_token = 'vk1.a.mXrRpgPJA-bwuyIov4iafRQyZrKkO9ksxMrvzQu1i9qPcCkyMG0rBVLK2UY1dhhPi7nid7LvNH1rkHJ7viio23TqWlv2uv7BuFcdMRNGr4xnaIvDk5K2yB6z4-y1NvOlpWi8HlMDwnZd-2D5Ve6fEdtWrERaYU7CACAGpI43II6zJq3iSdU9zNn48WO18uMOfJ8IONFFDRUVbKsrVJD2Fg'
vk_session = vk_api.VkApi(token = new_token)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)
adm_id = 17692663
upload = VkUpload(vk_session)

def get_photo_attachment(photo_path):
    try:
        photo = upload.photo_messages(photos=photo_path)[0]
        return f"photo{photo['owner_id']}_{photo['id']}"
    except Exception as e:
        print(f"Ошибка загрузки фото: {e}")
        return None

def send_msg(id, text, keyboard = None):
    post = {
        "user_id":id,
        "message":text,
        "random_id":random.randint(0, 100000)
    }
    if keyboard != None:
        post['keyboard'] = keyboard.get_keyboard()
    else:
        post = post
    vk_session.method("messages.send", post)
users = {}
states = {}
questions = {"name":"Как Вас зовут?",
    "age":"Ваш возраст?",
    "height":"Ваш рост?", 
    "weight_now":"Ваш вес сейчас?", 
    "weight_wish":"Желаемый вес?",
    "target":"Ваша цель",
    "breakfast":"Что вы едите на завтрак?",
    "luch":"В какое время вы обычно обедаете?",
    "dinner":"В какое время вы ужинайте?",
    "wake_up":"Во сколько вы встаете утром?",
    "bed":"Во сколько ложитесь спать?",
    "candy":"Любите сладкое?",
    "bakery":"Любите выпечку?",
    "salt":"Любите соленое?",
    "alk":"Присутствует ли в вашей жизни алкоголь и как часто?",
    "disease":"Есть ли хронические заболевания? Если да, то какие", 
    "headaches":"Бывают ли у вас головные боли?", 
    "water":"Пьете ли вы чистую воду? Если да, то сколько?", 
    "stomach":"Есть ли проблемы с желудочно-кишечным трактом?",  
    "mail":"напишите вашу электронную почту", 
    "conn":"Удобный способ связи?",
    "number":"Укажите свой номер телефона для связи",  
    "vk":"ваш вк"}
steps = list(questions.keys())
dats = {}

while True:
    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    msg = event.text.lower()
                    id = event.user_id
                    if id in states and msg in ['1', '2', '3', '4', '5']:
                        keyboard = VkKeyboard(one_time=False)
                        keyboard.add_openlink_button(
                            text='Перейти в сообщество',
                            link='https://vk.com/club148920320',
                            payload={'button': 'link'}
                        )
                        send_msg(id, "перейдите в сообщество и в меню нажмите получать статьи для получения дальнейшей информации", keyboard)
                    if id not in users:
                        users[id] = 1
                        dats[id] = {"phase":0, "step":0, "data":{}}  # Инициализируем сразу
                        send_msg(id, "Заполните анкету и я с вами свяжусь в ближайшее время")
                        send_msg(id, questions['name'])  # Шаг 0
                        continue
                    print(dats[id]["step"])
                    if dats[id]["step"] < len(steps)-1:
                        dats[id]['data'][steps[dats[id]["step"]]] = msg
                        dats[id]["step"]+=1
                        if dats[id]["step"] in [5, 17, 18, 20, 7]:
                            keyboard = VkKeyboard(one_time=True)
                            if dats[id]["step"] == 5:
                                keyboard.add_button("Снижение веса", VkKeyboardColor.PRIMARY)
                                keyboard.add_button("Набор массы", VkKeyboardColor.PRIMARY)
                                keyboard.add_line()
                                keyboard.add_button("Разобраться в питании", VkKeyboardColor.PRIMARY)
                                keyboard.add_button("Улучшить самочувствие", VkKeyboardColor.PRIMARY)
                                keyboard.add_line()
                                keyboard.add_button("Качество тела", VkKeyboardColor.PRIMARY)
                                keyboard.add_button("Наладить работу ЖКТ", VkKeyboardColor.PRIMARY)
                                keyboard.add_line()
                                keyboard.add_button("Наладить сон", VkKeyboardColor.PRIMARY)
                                keyboard.add_button("Повысить энергию", VkKeyboardColor.PRIMARY)
                                send_msg(id, questions[steps[dats[id]["step"]]], keyboard)
                            elif dats[id]["step"] == 20:
                                keyboard.add_button("Telegram", VkKeyboardColor.PRIMARY)
                                keyboard.add_button("Vk", VkKeyboardColor.PRIMARY)
                                keyboard.add_line()
                                keyboard.add_button("Max", VkKeyboardColor.PRIMARY)
                                keyboard.add_button("ZOOM", VkKeyboardColor.PRIMARY)
                                send_msg(id, questions[steps[dats[id]["step"]]], keyboard)
                            elif dats[id]["step"] == 7:
                                keyboard.add_button("12ч", VkKeyboardColor.PRIMARY)
                                keyboard.add_button("13ч", VkKeyboardColor.PRIMARY)
                                keyboard.add_button("14ч", VkKeyboardColor.PRIMARY)
                                keyboard.add_button("15ч", VkKeyboardColor.PRIMARY)
                                keyboard.add_line()
                                keyboard.add_button("нет обеда совсем", VkKeyboardColor.PRIMARY)
                                keyboard.add_button("только небольшие перекусы", VkKeyboardColor.PRIMARY)
                                send_msg(id, questions[steps[dats[id]["step"]]], keyboard)
                            elif dats[id]["step"] == 17:
                                keyboard.add_button("нет", VkKeyboardColor.PRIMARY)
                                keyboard.add_button("До 0,5 литров", VkKeyboardColor.PRIMARY)
                                keyboard.add_button("От 0,5 до 1 литра", VkKeyboardColor.PRIMARY)
                                keyboard.add_line()
                                keyboard.add_button("От 1 до 2 литров", VkKeyboardColor.PRIMARY)
                                keyboard.add_button("Более 2 литров", VkKeyboardColor.PRIMARY)
                                keyboard.add_button("Пью в основном чай / кофе / газировки", VkKeyboardColor.PRIMARY)
                                send_msg(id, questions[steps[dats[id]["step"]]], keyboard)
                            elif dats[id]["step"] == 18:
                                keyboard.add_button("Вздутие живота", VkKeyboardColor.PRIMARY)
                                keyboard.add_button("Диарея", VkKeyboardColor.PRIMARY)
                                keyboard.add_button("Запоры", VkKeyboardColor.PRIMARY)
                                keyboard.add_line()
                                keyboard.add_button("Изжога", VkKeyboardColor.PRIMARY)
                                keyboard.add_button("Нет", VkKeyboardColor.PRIMARY)
                                keyboard.add_button("Реакция на определенные продукты", VkKeyboardColor.PRIMARY)
                                #keyboard.add_button("Другое", VkKeyboardColor.PRIMARY)
                                send_msg(id, questions[steps[dats[id]["step"]]], keyboard)
                        else:
                            send_msg(id, questions[steps[dats[id]["step"]]])
                    elif dats[id]["step"] >= len(steps)-1 and dats[id]['step'] != 999:
                        dats[id]['data'][steps[dats[id]["step"]]] = msg
                        dats[id]['step'] = 999
                        
                        send_msg(id, "Благодарю за ответы!")
                        send_msg(id, "Чем я могу быть вам полезна? \n (поставьте цифру) \n "
                                     "1. Скорректировать свой вес (набрать / снизить вес) \n "
                                     "2. Консультация по рациону питания \n "
                                     "3. Приобрести продукт - доставка во все регионы \n "
                                     "4. Хочу участвовать в марафоне стройности \n "
                                     "5. Вас интересует дополнительный доход?")
                        states[id] = "waiting_choice"

                    elif states.get(id) == "waiting_choice" and msg in ['1', '2', '3', '4', '5']:
                        dats[id]['user_selected_service'] = msg # Сохраняем выбор
                        
                        keyboard = VkKeyboard(one_time=True)
                        keyboard.add_button("ДА", VkKeyboardColor.POSITIVE)
                        
                        send_msg(id, "Даю согласие на обработку персональных данных", keyboard)
                        states[id] = "waiting_agreement"

                    elif states.get(id) == "waiting_agreement" and msg == "да":
                        # Создаем кнопку-ссылку
                        keyboard = VkKeyboard(one_time=False)
                        keyboard.add_openlink_button(
                            label='Перейти в сообщество', 
                            link='https://vk.com/club148920320'
                        )
                        
                        final_text = "Отлично, я свяжусь с вами в ближайшее время, а также рекомендую подписаться на мою группу и получать полезные фишки."
                        
                        # Путь к картинке (проверь, чтобы файл реально лежал рядом с .py)
                        photo_path = "my_photo.jpg" 
                        attachment = get_photo_attachment(photo_path)
                        
                        # Отправляем сообщение через прямой метод API (чтобы вложить фото и клавиатуру)
                        vk_session.method("messages.send", {
                            "user_id": id,
                            "message": final_text,
                            "attachment": attachment if attachment else "",
                            "random_id": random.randint(0, 100000),
                            "keyboard": keyboard.get_keyboard()
                        })

                        # Отправляем полный отчет админу
                        values = [f"{questions[k]}: {dats[id]['data'][k]}\n" for k in dats[id]['data']]
                        report = (f"НОВАЯ ЗАЯВКА!\nУслуга: {dats[id]['user_selected_service']}\n"
                                 f"Согласие: ДАНO\n\n{''.join(values)}\nПрофиль: https://vk.com/id{id}")
                        send_msg(adm_id, report)
                        
                        del states[id] # Очищаем состояние
    except Exception as e:
        print("Ошибка:", e)
