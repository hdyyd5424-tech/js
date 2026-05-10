import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api import VkUpload
import random
import os
from dotenv import load_dotenv
base_path = os.path.dirname(os.path.abspath(__file__))
photo_path = os.path.join(base_path, "my_photo.jpg")
load_dotenv()
new_token = os.getenv('BOT_TOKEN')

vk_session = vk_api.VkApi(token=new_token)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)
adm_id = 17692663
upload = VkUpload(vk_session)

def get_photo_attachment(photo_path):
    try:
        # Важно: файл должен быть в той же папке или по полному пути
        photo = upload.photo_messages(photos=photo_path)[0]
        return f"photo{photo['owner_id']}_{photo['id']}"
    except Exception as e:
        print(f"Ошибка загрузки фото: {e}")
        return None

def send_msg(id, text, keyboard=None, attachment=None):
    post = {
        "user_id": id,
        "message": text,
        "random_id": random.randint(0, 100000)
    }
    if keyboard:
        post['keyboard'] = keyboard.get_keyboard()
    if attachment:
        post['attachment'] = attachment
    vk_session.method("messages.send", post)

questions = {
    "name":"Как Вас зовут?", "age":"Ваш возраст?", "height":"Ваш рост?", 
    "weight_now":"Ваш вес сейчас?", "weight_wish":"Желаемый вес?",
    "target":"Ваша цель", "breakfast":"Что вы едите на завтрак?",
    "luch":"В какое время вы обычно обедаете?", "dinner":"В какое время вы ужинайте?",
    "wake_up":"Во сколько вы встаете утром?", "bed":"Во сколько ложитесь спать?",
    "candy":"Любите сладкое?", "bakery":"Любите выпечку?", "salt":"Любите соленое?",
    "alk":"Присутствует ли в вашей жизни алкоголь и как часто?",
    "disease":"Есть ли хронические заболевания? Если да, то какие", 
    "headaches":"Бывают ли у вас головные боли?", 
    "water":"Пьете ли вы чистую воду? Если да, то сколько?", 
    "stomach":"Есть ли проблемы с желудочно-кишечным трактом?",  
    "mail":"напишите вашу электронную почту", 
    "conn":"Удобный способ связи?",
    "number":"Укажите свой номер телефона для связи",  
    "vk":"ваш вк"
}
steps = list(questions.keys())
users_data = {} # Данные анкеты
states = {}     # Текущее состояние пользователя

while True:
    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                msg = event.text.lower().strip()
                user_id = event.user_id

                # 1. Если пользователь новый — начинаем анкету
                if user_id not in users_data:
                    users_data[user_id] = {"step": 0, "answers": {}}
                    send_msg(user_id, "Заполните анкету и я с вами свяжусь в ближайшее время")
                    send_msg(user_id, questions[steps[0]])
                    continue

                # 2. ОБРАБОТКА СОСТОЯНИЙ (после анкеты)
                user_state = states.get(user_id)

                # Этап: Выбор услуги (цифра 1-5)
                if user_state == "waiting_choice":
                    if msg in ['1', '2', '3', '4', '5']:
                        users_data[user_id]['selected_service'] = msg
                        kb = VkKeyboard(one_time=True)
                        kb.add_button("ДА", VkKeyboardColor.POSITIVE)
                        send_msg(user_id, "Даю согласие на обработку персональных данных", kb)
                        states[user_id] = "waiting_agreement"
                    else:
                        send_msg(user_id, "Пожалуйста, введите цифру от 1 до 5.")
                    continue

                # Этап: Согласие (ДА) -> Финал с ФОТО
                if user_state == "waiting_agreement":
                    if msg == "да":
                        kb = VkKeyboard(one_time=False)
                        kb.add_openlink_button(label='Перейти в сообщество', link='https://vk.com/club148920320')
                        photo_filename = "my_photo.jpg"
                        if os.path.exists(photo_filename):
                            photo = get_photo_attachment(photo_filename)
                        else:
                            print(f"Файл {photo_filename} не найден в директории {os.getcwd()}")
                            photo = None
                        final_text = "Отлично, я свяжусь с вами в ближайшее время, а также рекомендую подписаться на мою группу и получать полезные фишки."
                        
                        send_msg(user_id, final_text, kb, attachment=photo)

                        # Отчет админу
                        ans = users_data[user_id]['answers']
                        report = f"НОВАЯ ЗАЯВКА!\nУслуга: {users_data[user_id]['selected_service']}\n\n"
                        report += "".join([f"{questions[k]}: {ans.get(k, '—')}\n" for k in steps])
                        report += f"\nПрофиль: https://vk.com/id{user_id}"
                        send_msg(adm_id, report)

                        # Очистка данных
                        del users_data[user_id]
                        if user_id in states: del states[user_id]
                    else:
                        send_msg(user_id, "Для продолжения нужно нажать 'ДА'")
                    continue

                # 3. ПРОЦЕСС АНКЕТЫ
                current_step_idx = users_data[user_id]["step"]
                if current_step_idx < len(steps):
                    # Записываем ответ на текущий вопрос
                    current_field = steps[current_step_idx]
                    users_data[user_id]["answers"][current_field] = event.text
                    
                    # Переходим к следующему
                    users_data[user_id]["step"] += 1
                    next_step_idx = users_data[user_id]["step"]

                    # Если еще есть вопросы
                    if next_step_idx < len(steps):
                        kb = None
                        # Проверка на спец. клавиатуры для конкретных шагов
                        if next_step_idx == 5:
                            kb = VkKeyboard(one_time=True)
                            kb.add_button("Снижение веса", VkKeyboardColor.PRIMARY)

                            kb.add_button("Набор массы", VkKeyboardColor.PRIMARY)

                            kb.add_line()

                            kb.add_button("Разобраться в питании", VkKeyboardColor.PRIMARY)

                            kb.add_button("Улучшить самочувствие", VkKeyboardColor.PRIMARY)

                            kb.add_line()

                            kb.add_button("Качество тела", VkKeyboardColor.PRIMARY)

                            kb.add_button("Наладить работу ЖКТ", VkKeyboardColor.PRIMARY)

                            kb.add_line()

                            kb.add_button("Наладить сон", VkKeyboardColor.PRIMARY)

                            kb.add_button("Повысить энергию", VkKeyboardColor.PRIMARY)

                            send_msg(id, questions[steps[dats[id]["step"]]], keyboard)

                        elif next_step_idx == 20:
                            kb = VkKeyboard(one_time=True)
                            kb.add_button("Telegram", VkKeyboardColor.PRIMARY)

                            kb.add_button("Vk", VkKeyboardColor.PRIMARY)

                            kb.add_line()

                            kb.add_button("Max", VkKeyboardColor.PRIMARY)

                            kb.add_button("ZOOM", VkKeyboardColor.PRIMARY)

                            send_msg(id, questions[steps[dats[id]["step"]]], keyboard)

                        elif next_step_idx == 7:
                            kb = VkKeyboard(one_time=True)
                            kb.add_button("12ч", VkKeyboardColor.PRIMARY)

                            kb.add_button("13ч", VkKeyboardColor.PRIMARY)

                            kb.add_button("14ч", VkKeyboardColor.PRIMARY)

                            kb.add_button("15ч", VkKeyboardColor.PRIMARY)

                            kb.add_line()

                            kb.add_button("нет обеда совсем", VkKeyboardColor.PRIMARY)

                            kb.add_button("только небольшие перекусы", VkKeyboardColor.PRIMARY)

                            send_msg(id, questions[steps[dats[id]["step"]]], keyboard)

                        elif next_step_idx == 17:
                            kb = VkKeyboard(one_time=True)
                            kb.add_button("нет", VkKeyboardColor.PRIMARY)

                            kb.add_button("До 0,5 литров", VkKeyboardColor.PRIMARY)

                            kb.add_button("От 0,5 до 1 литра", VkKeyboardColor.PRIMARY)

                            kb.add_line()

                            kb.add_button("От 1 до 2 литров", VkKeyboardColor.PRIMARY)

                            kb.add_button("Более 2 литров", VkKeyboardColor.PRIMARY)

                            kb.add_button("Пью в основном чай / кофе / газировки", VkKeyboardColor.PRIMARY)

                            send_msg(id, questions[steps[dats[id]["step"]]], keyboard)

                        elif next_step_idx == 18:
                            kb = VkKeyboard(one_time=True)
                            kb.add_button("Вздутие живота", VkKeyboardColor.PRIMARY)

                            kb.add_button("Диарея", VkKeyboardColor.PRIMARY)

                            kb.add_button("Запоры", VkKeyboardColor.PRIMARY)

                            kb.add_line()

                            kb.add_button("Изжога", VkKeyboardColor.PRIMARY)

                            kb.add_button("Нет", VkKeyboardColor.PRIMARY)

                            kb.add_button("Реакция на определенные продукты", VkKeyboardColor.PRIMARY)

                            #keyboard.add_button("Другое", VkKeyboardColor.PRIMARY)

                    send_msg(user_id, questions[steps[next_step_idx]], kb)
                    
                    # Если вопросы закончились
                else:
                    send_msg(user_id, "Благодарю за ответы!")
                    choices = ("Чем я могу быть вам полезна?\n(введите цифру)\n"
                               "1. Скорректировать вес\n2. Консультация по рациону\n"
                               "3. Приобрести продукт\n4. Марафон стройности\n5. Доход")
                    send_msg(user_id, choices)
                    states[user_id] = "waiting_choice"

    except Exception as e:
        print(f"Критическая ошибка: {e}")
