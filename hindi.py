import telebot
import time

# Constants
bot_token = '7452696572:AAECBrmGAwH72hPN1F51d3Y8R0lii-S2N0c'
developer_id = 7329859398
developer_username = '@IndiPhoenix'

# Initialize bot
bot = telebot.TeleBot(bot_token)

# Data storage
user_messages = {}
user_stats = {}
authorized_groups = set()
blocked_users = set()
counted_message_types = {'text'}
spam_limit = 10

# Helper functions
def count_user_message(user, chat_id):
    if user not in user_stats:
        user_stats[user] = {'level': 1, 'xp': 0}
    user_stats[user]['xp'] += 1
    if user_stats[user]['xp'] >= 10:
        level_up(user, chat_id)

def level_up(user, chat_id):
    user_stats[user]['level'] += 1
    user_stats[user]['xp'] = 0
    bot.send_message(chat_id, f"🎉 Congrats @{user}! You've leveled up to Level {user_stats[user]['level']}!")

# Commands
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "Welcome to the chat ranking bot! 🎉 Use /help to see available commands.")

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "📜 Available Commands:\n"
        "/start - Bot chaalu karne ke liye.\n"
        "/help - Saare commands ki help ke liye.\n"
        "/setspamlimit <number> - Jyada naitanki waalon ko sudhaarne ke liye (Admin ki power)\n"
        "/blockuser <username> - Leaderboard se user ko block karne ke liye (Admin ki power)\n"
        "/unblockuser <username> - Leader board se user ko unblock karne ke liye (Admin ki power)\n"
        "/rank - Tumhaari aukaat\n"
        "/leaderboard - Sabse nikamme log\n"
        "/stats - Tumhaari izzat kholne ke liye\n"
        "/achievements - Saare kaale kaarnaame janne ke liye\n"
        "/suggest <message> - Phoenix ko apna gyaan do iske liye\n"
        "/authorizegroup <group_id> - Free ka maal use karne waalon se bachaane ke liye (Owner ki taaqat)\n"
    )
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['setspamlimit'])
def set_spam_limit(message):
    if message.from_user.id == developer_id:
        try:
            global spam_limit
            spam_limit = int(message.text.split()[1])
            bot.reply_to(message, f"Spam limit set to {spam_limit}.")
        except (IndexError, ValueError):
            bot.reply_to(message, "Please provide a valid number.")

@bot.message_handler(commands=['blockuser'])
def block_user(message):
    if message.from_user.id == developer_id:
        try:
            blocked_user = message.text.split()[1]
            blocked_users.add(blocked_user)
            bot.reply_to(message, f"User @{blocked_user} has been blocked from the leaderboard.")
        except IndexError:
            bot.reply_to(message, "username to dedo na bhai.")

@bot.message_handler(commands=['unblockuser'])
def unblock_user(message):
    if message.from_user.id == developer_id:
        try:
            unblocked_user = message.text.split()[1]
            blocked_users.discard(unblocked_user)
            bot.reply_to(message, f"User @{unblocked_user} has been unblocked from the leaderboard.")
        except IndexError:
            bot.reply_to(message, "Please provide a username to unblock.")

@bot.message_handler(commands=['setmessagetypes'])
def set_message_types(message):
    if message.from_user.id == developer_id:
        global counted_message_types
        types = set(message.text.split()[1:])
        counted_message_types = types
        bot.reply_to(message, f"Message types to be counted: {', '.join(counted_message_types)}.")

@bot.message_handler(commands=['authorizegroup'])
def authorize_group(message):
    if message.from_user.id == developer_id:
        try:
            group_id = int(message.text.split()[1])
            authorized_groups.add(group_id)
            bot.reply_to(message, f"Group {group_id} has been authorized.")
        except (IndexError, ValueError):
            bot.reply_to(message, "Please provide a valid group ID.")

@bot.message_handler(commands=['rank'])
def show_rank(message):
    user = message.from_user.username
    rank_info = user_stats.get(user, {'level': 0, 'xp': 0})
    bot.reply_to(message, f"📊 Your rank: Level {rank_info['level']} with {rank_info['xp']} XP.")

@bot.message_handler(commands=['leaderboard'])
def show_leaderboard(message):
    sorted_users = sorted(user_stats.items(), key=lambda x: x[1]['xp'], reverse=True)
    leaderboard = "\n".join([f"{i+1}. @{user} - Level {stats['level']} ({stats['xp']} XP)" for i, (user, stats) in enumerate(sorted_users)])
    bot.reply_to(message, f"🏆 Leaderboard:\n{leaderboard}")

@bot.message_handler(commands=['stats'])
def show_stats(message):
    user = message.from_user.username
    stats = user_stats.get(user, {'level': 0, 'xp': 0})
    bot.reply_to(message, f"📈 Your statistics:\nLevel: {stats['level']}\nXP: {stats['xp']}")

@bot.message_handler(commands=['achievements'])
def show_achievements(message):
    # Placeholder for achievements functionality
    bot.reply_to(message, "🏅 Achievements feature is coming soon!")

@bot.message_handler(commands=['dailychallenge'])
def daily_challenge(message):
    # Placeholder for daily challenge functionality
    bot.reply_to(message, "🎯 Daily challenge feature is coming soon!")

@bot.message_handler(commands=['weeklychallenge'])
def weekly_challenge(message):
    # Placeholder for weekly challenge functionality
    bot.reply_to(message, "🎯 Weekly challenge feature is coming soon!")

@bot.message_handler(commands=['suggest'])
def handle_suggestion(message):
    suggestion = ' '.join(message.text.split()[1:])
    bot.send_message(developer_id, f"💡 New suggestion from @{message.from_user.username}:\n{suggestion}")
    bot.reply_to(message, "📨 Thank you for your suggestion!")

# Message handling and spam detection
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user = message.from_user.username

    if chat_id not in authorized_groups:
        bot.send_message(chat_id, f"🚫 This group is not authorized to use this bot. Please contact the developer: {developer_username}")
        return

    if user in blocked_users:
        return

    if message.content_type in counted_message_types:
        if user not in user_messages:
            user_messages[user] = []
        user_messages[user].append(time.time())
        user_messages[user] = [t for t in user_messages[user] if time.time() - t < 60]

        if len(user_messages[user]) > spam_limit:
            bot.reply_to(message, "🚫 You are sending messages too quickly. Please slow down.")
            return

        count_user_message(user, chat_id)

# Start polling
if __name__ == '__main__':
    bot.polling(none_stop=True)
