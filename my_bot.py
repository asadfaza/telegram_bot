import logging
import telebot
import openai

users_list = {}
with open('api.txt') as f:
    api = f.read().strip().split()

with open('users_list.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
        username, user_id = line.strip().split()
        users_list[username] = user_id

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(api[0])
openai.api_key = api[1]

# Set up a welcome message
welcome_message = "Hi! I'm a chatbot, ask your damn questions"

# Set up a message handler for the /start command
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, welcome_message)

# Set up a message handler for the /help command
@bot.message_handler(commands=['help'])
def handle_help(message):
    help_message = "Just type anything you want to chat about, and I'll try my best to respond to you."
    bot.reply_to(message, help_message)

# Set up a message handler for all other messages
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """
    Handle all messages sent to the bot.
    """
    try:
        # Send typing action to make it seem as if the bot is typing
        bot.send_chat_action(message.chat.id, 'typing')

        # Handle text messages
        if message.content_type == 'text':
            handle_text_message(message)

    except Exception as e:
        logger.error(f"Error processing message: {message.text}, error: {str(e)}")
        bot.reply_to(message, "Sorry, I couldn't understand that.")

@bot.message_handler(content_types=['photo'])
def send_gif(message):
    # Open and read the gif file
    bot.reply_to(message, 'It is not a fucking chat for sending nudes')
    with open('if_not_message.mp4', 'rb') as gif:
        bot.send_document(message.chat.id, gif)
    with open('full.mp4', 'rb') as gif:
        bot.send_document(message.chat.id, gif)

@bot.message_handler(content_types=['document', 'voice'])
def send_voice(message):
    # Open and read the gif file
    bot.reply_to(message, 'You think someone listen it')
    with open('timas_voise.ogg', 'rb') as voice:
        bot.send_document(message.chat.id, voice)

def handle_text_message(message):
    """
    Handle text messages sent to the bot.
    """
    try:
        # Check if the message mentions another user
        if '@' in message.text:
            index = message.text.index('@')
            user_name = message.text[index+1:].split()[0]
            if user_name in users_list:
                # Ask the user if they want to send a message to the specified user
                bot.reply_to(message, f"What do you want to say to this user?")
                # Register a callback function to receive the user's response
                bot.register_next_step_handler(message, lambda m: send_message_to_chat(user_name, m.text))
            else:
                # Get a response from the OpenAI API
                response_text = f"@{user_name} is not exist \n{get_bot_response(message.text)}"
                print(f'{message.chat.username}: {message.text} \nbot: {response_text}')
                write_user_info(message.chat.username, message.chat.id)
                # Send the response back to the user
                bot.reply_to(message, response_text)

        else:
            # Get a response from the OpenAI API
            response_text = get_bot_response(message.text)
            print(f'{message.chat.username}: {message.text} \nbot: {response_text}')
            write_user_info(message.chat.username, message.chat.id)
            # Send the response back to the user
            bot.reply_to(message, response_text)

    except Exception as e:
        logger.error(f"Error processing message: {message.text}, error: {str(e)}")
        bot.reply_to(message, "Sorry, I couldn't understand that.")

def get_bot_response(user_input):
    """
    Call the OpenAI API to get a response to the user's input.
    """
    prompt = f"User: {user_input}\nAI:"
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-0301",
        prompt=prompt,
        temperature=0.7,
        max_tokens=1024,
        n=1,
        stop=None,
        frequency_penalty=0,
        presence_penalty=0
    )
    # Extract the text from the API response
    response_text = response.choices[0].text.strip()
    return response_text

def send_message_to_chat(username, message_text):
    """
    Send a message to the specified chat ID with a delay between each character.
    """
    try:
        user_id = users_list[username]
        message1 = "Someone say to you: "
        bot.send_message(user_id, message1+message_text)
    except Exception as e:
        print("Error sending message to user:", str(e))

def write_user_info(username, user_id):
    with open('users_list.txt', 'r+') as f:
        # Check if user ID and username already exist in the file
        lines = f.readlines()
        for line in lines:
            if line.startswith(f"{username} {user_id}"):
                return  # User already exists, so return without adding to file

        # User doesn't exist, so add to file
        f.write(f"{username} {user_id}\n")
        users_list[username[1:]] = user_id

# Start the bot
if __name__ == '__main__':
    logger.info("Starting Telegram bot...")
    bot.polling(none_stop=True)