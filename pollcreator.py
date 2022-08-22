import telebot
from telebot import types

TOKEN = "YOURTOKEN"
poll_dict = {}
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['help'])
def help(message):
    bot.reply_to(message, "Use /new_poll for creating a new poll.")


@bot.message_handler(commands=['new_poll'])
def new_poll(message):
    messageArray = message.text.split()
    if len(messageArray) > 1:
        bot.reply_to(message, "Too many args.")
    else:
        msg = bot.reply_to(message, "Great. now send me the poll's title :")
        bot.register_next_step_handler(msg, process_poll_title)


def process_poll_title(message):
    if len(message.text) > 300:
        msg = bot.reply_to(message, "The maximum number of charachters in the polls title is 300. yours is : " +
                           str(len(message.text)) + ". try again")
        bot.register_next_step_handler(msg, process_poll_title)
    else:
        poll_dict["title"] = message.text
        msg = bot.reply_to(
            message, "Great. now send me your options in one message. seperate them with \"$\" e. g. : option 1 $ option 2 :")
        bot.register_next_step_handler(msg, process_poll_options)


def process_poll_options(message):
    optionsArray = []
    optionsArray = message.text.split("$")
    optionsArray = list(filter(None, optionsArray))
    invalidOption = False
    invalidLength = 0
    if len(optionsArray) <= 1:
        msg = bot.reply_to(
            message, "the number of options must be greater than 1. try again")
        bot.register_next_step_handler(msg, process_poll_options)
    else:
        for i in optionsArray:
            if len(i) > 100:
                invalidOption = True
                invalidLength = len(i)
        if invalidOption == True:
            msg = bot.reply_to(
                message, "the lengh of an option can be as large as 100 charachters. yours is : " + str(invalidLength) + " try again.")
            bot.register_next_step_handler(msg, process_poll_options)
        else:
            poll_dict["options"] = optionsArray
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('Quiz', 'Regular')
            msg = bot.reply_to(
                message, "Great. now choose between quiz and Regular", reply_markup=markup)
            bot.register_next_step_handler(msg, process_poll_type)


def process_poll_type(message):
    text = message.text
    if text == "Quiz":
        poll_dict["type"] = "quiz"
        optionArray = poll_dict["options"]
        optionsList = []
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for i in optionArray:
            optionsList.append("[" + str(optionArray.index(i)) + "] " + i)
            markup.add(str(optionArray.index(i)))
        msg = bot.reply_to(message, "The list of your options are : \n" + "\n".join(
            optionsList) + "\n choose the correct option :", reply_markup=markup)
        bot.register_next_step_handler(msg, process_poll_correct_option)
    elif text == "Regular":
        poll_dict["type"] = "regular"
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Allow', 'Disallow')
        msg = bot.reply_to(
            message, "Great. now choose between allowing multiple options and not allowing it :", reply_markup=markup)
        bot.register_next_step_handler(msg, process_poll_multiple_options)
    else:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Quiz', 'Regular')
        msg = bot.reply_to(
            message, "Invalid type. try again", reply_markup=markup)
        bot.register_next_step_handler(msg, process_poll_type)


def process_poll_multiple_options(message):
    if message.text == "Allow":
        poll_dict["multi-option"] = True
        bot.send_poll(message.from_user.id,
                      poll_dict["title"], poll_dict["options"], True, poll_dict["type"], poll_dict["multi-option"])
    elif message.text == "Disallow":
        poll_dict["multi-option"] = False
        bot.send_poll(message.from_user.id,
                      poll_dict["title"], poll_dict["options"], True, poll_dict["type"], poll_dict["multi-option"])
    else:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Allow', 'Disallow')
        msg = bot.reply_to(
            message, "Invalid response. try again", reply_markup=markup)
        bot.register_next_step_handler(msg, process_poll_multiple_options)


def process_poll_correct_option(message):
    optionArray = poll_dict["options"]
    try:
        optionArray[int(message.text)]
        pass
    except Exception as e:
        msg = bot.reply_to(message, "invalid option. try again")
        bot.register_next_step_handler(msg, process_poll_correct_option)
    poll_dict["correct-option"] = int(message.text)
    msg = bot.reply_to(
        message, "Great. now send the explanation for the correct option :")
    bot.register_next_step_handler(msg, process_poll_correct_explanation)


def process_poll_correct_explanation(message):
    if len(message.text) > 200:
        msg = bot.reply_to(message, "the lengh of the explanation can be as large as 200 charachters. yours is : " +
                           str(len(message.text)) + " try again.")
        bot.register_next_step_handler(msg, process_poll_correct_explanation)
    else:
        poll_dict["explanation"] = message.text
        bot.reply_to(message, "Your poll is ready :")
        bot.send_poll(message.from_user.id, poll_dict["title"], poll_dict["options"], True,
                      poll_dict["type"], False, poll_dict["correct-option"], poll_dict["explanation"])


def main():
    bot.polling()  # looking for message


if __name__ == '__main__':
    main()
