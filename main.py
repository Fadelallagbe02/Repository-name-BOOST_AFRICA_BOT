import os
import json
from datetime import datetime

from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from telegram.request import HTTPXRequest


load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

DATA_FILE = "members.json"


# ============================================================
# CANAUX
# ============================================================

CHANNELS = {

    "bet": {
        "username": "@BetBoostAfrica",
        "url": "https://t.me/BetBoostAfrica",
        "title": "⚽ BET BOOST AFRICA",
        "description": (
            "📊 Sport, analyses et contenus football."
        ),
    },

    "tech": {
        "username": "@TechBoostAfrica24",
        "url": "https://t.me/TechBoostAfrica24",
        "title": "💻 TECH BOOST AFRICA",
        "description": (
            "🤖 IA, technologie, innovation et business digital."
        ),
    },

    "crypto": {
        "username": "@CryptoBoostAfrica",
        "url": "https://t.me/CryptoBoostAfrica",
        "title": "₿ CRYPTO BOOST AFRICA",
        "description": (
            "🌐 Crypto, blockchain et éducation."
        ),
    },
}


# ============================================================
# CAMPAGNES
# ============================================================

CAMPAIGNS = {

    "telegram": "Telegram",

    "facebook": "Facebook",

    "instagram": "Instagram",

    "tiktok": "TikTok",

    "whatsapp": "WhatsApp",

    "youtube": "YouTube",

    "direct": "Direct",
}


# ============================================================
# BASE DE DONNÉES
# ============================================================

def load_data():

    if not os.path.exists(DATA_FILE):
        return {}

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception:

        return {}


def save_data(data):

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


def ensure_user(data, user):

    user_id = str(user.id)

    if user_id not in data:

        data[user_id] = {

            "id": user.id,

            "username": user.username,

            "first_name": user.first_name,

            "campaign": "direct",

            "created_at":
                datetime.now().isoformat(),

            "choices": [],

            "confirmed": [],

            "clicks": []

        }

    # Compatibilité avec anciennes données
    data[user_id].setdefault(
        "choices",
        []
    )

    data[user_id].setdefault(
        "confirmed",
        []
    )

    data[user_id].setdefault(
        "clicks",
        []
    )

    data[user_id].setdefault(
        "campaign",
        "direct"
    )

    return user_id


# ============================================================
# /START
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    user = update.effective_user

    data = load_data()

    user_id = ensure_user(
        data,
        user
    )


    # --------------------------------------------------------
    # Récupération de la campagne
    # --------------------------------------------------------

    campaign = "direct"

    if context.args:

        received = context.args[0].lower()

        if received in CAMPAIGNS:

            campaign = received


    # --------------------------------------------------------
    # Première source d'acquisition
    # --------------------------------------------------------

    current_campaign = data[user_id].get(
        "campaign",
        "direct"
    )

    if current_campaign == "direct" and campaign != "direct":

        data[user_id]["campaign"] = campaign


    # Enregistre chaque visite/campagne
    data[user_id]["clicks"].append({

        "campaign": campaign,

        "date":
            datetime.now().isoformat()

    })


    save_data(data)


    # --------------------------------------------------------
    # MENU PRINCIPAL
    # --------------------------------------------------------

    keyboard = [

        [
            InlineKeyboardButton(
                "⚽ BET BOOST AFRICA",
                callback_data="choose_bet"
            )
        ],

        [
            InlineKeyboardButton(
                "💻 TECH BOOST AFRICA",
                callback_data="choose_tech"
            )
        ],

        [
            InlineKeyboardButton(
                "₿ CRYPTO BOOST AFRICA",
                callback_data="choose_crypto"
            )
        ],

    ]


    source_name = CAMPAIGNS.get(
        campaign,
        "Direct"
    )


    await update.message.reply_text(

        "🚀 BIENVENUE SUR BOOST AFRICA !\n\n"

        "Choisis la communauté qui t'intéresse 👇\n\n"

        "⚽ BET BOOST AFRICA\n"
        "📊 Sport & analyses\n\n"

        "💻 TECH BOOST AFRICA\n"
        "🤖 IA • Technologie • Innovation\n\n"

        "₿ CRYPTO BOOST AFRICA\n"
        "🌐 Crypto • Blockchain\n\n"

        f"📣 Source : {source_name}\n\n"

        "👇 FAIS TON CHOIX :",

        reply_markup=
            InlineKeyboardMarkup(
                keyboard
            )
    )


# ============================================================
# CHOIX D'UN CANAL
# ============================================================

async def choose_channel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    user = query.from_user

    choice = query.data.replace(
        "choose_",
        ""
    )

    if choice not in CHANNELS:
        return


    data = load_data()

    user_id = ensure_user(
        data,
        user
    )


    if choice not in data[user_id]["choices"]:

        data[user_id]["choices"].append(
            choice
        )


    data[user_id]["clicks"].append({

        "action": "choose_channel",

        "channel": choice,

        "date":
            datetime.now().isoformat()

    })


    save_data(data)


    channel = CHANNELS[choice]


    keyboard = [

        [
            InlineKeyboardButton(
                "📲 REJOINDRE LE CANAL",
                url=channel["url"]
            )
        ],

        [
            InlineKeyboardButton(
                "✅ J'AI REJOINT — VÉRIFIER",
                callback_data=f"verify_{choice}"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ RETOUR",
                callback_data="back"
            )
        ]

    ]


    await query.edit_message_text(

        f"{channel['title']}\n\n"

        f"{channel['description']}\n\n"

        "👇 Étape 1 :\n"
        "Rejoins le canal avec le bouton ci-dessous.\n\n"

        "👇 Étape 2 :\n"
        "Après ton abonnement, appuie sur :\n\n"

        "✅ J'AI REJOINT — VÉRIFIER",

        reply_markup=
            InlineKeyboardMarkup(
                keyboard
            )
    )


# ============================================================
# VÉRIFICATION ABONNEMENT
# ============================================================

async def verify_channel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    user = query.from_user

    choice = query.data.replace(
        "verify_",
        ""
    )

    if choice not in CHANNELS:

        await query.answer(
            "Canal inconnu.",
            show_alert=True
        )

        return


    channel = CHANNELS[choice]


    try:

        member = await context.bot.get_chat_member(

            chat_id=channel["username"],

            user_id=user.id

        )


        status = member.status


        is_member = status in [

            "member",

            "administrator",

            "creator"

        ]


        if is_member:

            data = load_data()

            user_id = ensure_user(
                data,
                user
            )


            if choice not in data[user_id]["confirmed"]:

                data[user_id]["confirmed"].append(
                    choice
                )


            data[user_id]["clicks"].append({

                "action":
                    "subscription_confirmed",

                "channel":
                    choice,

                "date":
                    datetime.now().isoformat()

            })


            save_data(data)


            await query.answer(
                "✅ Abonnement confirmé !",
                show_alert=True
            )


            keyboard = [

                [
                    InlineKeyboardButton(
                        "⚽ BET BOOST AFRICA",
                        url=CHANNELS["bet"]["url"]
                    )
                ],

                [
                    InlineKeyboardButton(
                        "💻 TECH BOOST AFRICA",
                        url=CHANNELS["tech"]["url"]
                    )
                ],

                [
                    InlineKeyboardButton(
                        "₿ CRYPTO BOOST AFRICA",
                        url=CHANNELS["crypto"]["url"]
                    )
                ]

            ]


            await query.edit_message_text(

                "🎉 ABONNEMENT CONFIRMÉ !\n\n"

                f"{channel['title']}\n\n"

                "✅ Tu fais maintenant partie "
                "de cette communauté.\n\n"

                "🔥 Bienvenue dans BOOST AFRICA !\n\n"

                "Découvre aussi nos autres communautés 👇",

                reply_markup=
                    InlineKeyboardMarkup(
                        keyboard
                    )
            )


        else:

            await query.answer(

                "❌ Je ne vois pas encore ton abonnement. "
                "Rejoins d'abord le canal.",

                show_alert=True
            )


    except Exception as e:

        print(
            f"⚠️ Vérification {choice} : {e}"
        )

        await query.answer(

            "⚠️ Vérification temporairement impossible. "
            "Réessaie dans quelques secondes.",

            show_alert=True
        )


# ============================================================
# RETOUR MENU
# ============================================================

async def back(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()


    keyboard = [

        [
            InlineKeyboardButton(
                "⚽ BET BOOST AFRICA",
                callback_data="choose_bet"
            )
        ],

        [
            InlineKeyboardButton(
                "💻 TECH BOOST AFRICA",
                callback_data="choose_tech"
            )
        ],

        [
            InlineKeyboardButton(
                "₿ CRYPTO BOOST AFRICA",
                callback_data="choose_crypto"
            )
        ]

    ]


    await query.edit_message_text(

        "🚀 BOOST AFRICA\n\n"

        "Choisis ta communauté 👇",

        reply_markup=
            InlineKeyboardMarkup(
                keyboard
            )
    )


# ============================================================
# STATISTIQUES
# ============================================================

async def stats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    data = load_data()


    # --------------------------------------------------------
    # Sources
    # --------------------------------------------------------

    campaign_visitors = {

        campaign: 0

        for campaign in CAMPAIGNS

    }


    campaign_confirmed = {

        campaign: 0

        for campaign in CAMPAIGNS

    }


    # --------------------------------------------------------
    # Canaux
    # --------------------------------------------------------

    selected = {

        "bet": 0,

        "tech": 0,

        "crypto": 0

    }


    confirmed = {

        "bet": 0,

        "tech": 0,

        "crypto": 0

    }


    # --------------------------------------------------------
    # Analyse
    # --------------------------------------------------------

    for user in data.values():

        campaign = user.get(
            "campaign",
            "direct"
        )


        if campaign in campaign_visitors:

            campaign_visitors[
                campaign
            ] += 1


        for choice in user.get(
            "choices",
            []
        ):

            if choice in selected:

                selected[
                    choice
                ] += 1


        for choice in user.get(
            "confirmed",
            []
        ):

            if choice in confirmed:

                confirmed[
                    choice
                ] += 1


        # Conversion par campagne
        if campaign in campaign_confirmed:

            if user.get(
                "confirmed",
                []
            ):

                campaign_confirmed[
                    campaign
                ] += 1


    # --------------------------------------------------------
    # Rapport
    # --------------------------------------------------------

    message = (

        "📊 BOOST AFRICA — STATISTIQUES\n\n"

        f"👥 UTILISATEURS UNIQUES : "
        f"{len(data)}\n\n"

        "📣 SOURCES D'ACQUISITION\n"

        f"📱 Telegram : "
        f"{campaign_visitors['telegram']}\n"

        f"📘 Facebook : "
        f"{campaign_visitors['facebook']}\n"

        f"📸 Instagram : "
        f"{campaign_visitors['instagram']}\n"

        f"🎵 TikTok : "
        f"{campaign_visitors['tiktok']}\n"

        f"💬 WhatsApp : "
        f"{campaign_visitors['whatsapp']}\n"

        f"▶️ YouTube : "
        f"{campaign_visitors['youtube']}\n"

        f"🔗 Direct : "
        f"{campaign_visitors['direct']}\n\n"

        "👥 ABONNEMENTS CONFIRMÉS PAR SOURCE\n"

        f"📱 Telegram : "
        f"{campaign_confirmed['telegram']}\n"

        f"📘 Facebook : "
        f"{campaign_confirmed['facebook']}\n"

        f"📸 Instagram : "
        f"{campaign_confirmed['instagram']}\n"

        f"🎵 TikTok : "
        f"{campaign_confirmed['tiktok']}\n"

        f"💬 WhatsApp : "
        f"{campaign_confirmed['whatsapp']}\n"

        f"▶️ YouTube : "
        f"{campaign_confirmed['youtube']}\n\n"

        "📌 CHOIX DES CANAUX\n"

        f"⚽ Bet : "
        f"{selected['bet']}\n"

        f"💻 Tech : "
        f"{selected['tech']}\n"

        f"₿ Crypto : "
        f"{selected['crypto']}\n\n"

        "✅ ABONNEMENTS CONFIRMÉS\n"

        f"⚽ Bet : "
        f"{confirmed['bet']}\n"

        f"💻 Tech : "
        f"{confirmed['tech']}\n"

        f"₿ Crypto : "
        f"{confirmed['crypto']}\n"

    )


    await update.message.reply_text(
        message
    )


# ============================================================
# ERREURS
# ============================================================

async def error_handler(
    update,
    context
):

    print(
        "⚠️ Erreur réseau :",
        context.error
    )

    print(
        "🔄 Le bot continue..."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    if not TOKEN:

        print(
            "❌ BOT_TOKEN introuvable dans .env"
        )

        return


    request = HTTPXRequest(

        connect_timeout=30.0,

        read_timeout=30.0,

        write_timeout=30.0,

        pool_timeout=30.0

    )


    app = (

        Application

        .builder()

        .token(TOKEN)

        .request(request)

        .get_updates_request(request)

        .build()

    )


    # --------------------------------------------------------
    # Commandes
    # --------------------------------------------------------

    app.add_handler(

        CommandHandler(
            "start",
            start
        )

    )


    app.add_handler(

        CommandHandler(
            "stats",
            stats
        )

    )


    # --------------------------------------------------------
    # Boutons
    # --------------------------------------------------------

    app.add_handler(

        CallbackQueryHandler(

            choose_channel,

            pattern="^choose_"

        )

    )


    app.add_handler(

        CallbackQueryHandler(

            verify_channel,

            pattern="^verify_"

        )

    )


    app.add_handler(

        CallbackQueryHandler(

            back,

            pattern="^back$"

        )

    )


    app.add_error_handler(
        error_handler
    )


    print(
        "==================================="
    )

    print(
        "🤖 BOOST AFRICA MANAGER"
    )

    print(
        "📣 MODE ACQUISITION"
    )

    print(
        "==================================="
    )

    print(
        "📱 Telegram"
    )

    print(
        "📘 Facebook"
    )

    print(
        "📸 Instagram"
    )

    print(
        "🎵 TikTok"
    )

    print(
        "💬 WhatsApp"
    )

    print(
        "▶️ YouTube"
    )

    print(
        "==================================="
    )

    print(
        "✅ Tracking campagnes"
    )

    print(
        "✅ Vérification abonnements"
    )

    print(
        "📊 Statistiques"
    )

    print(
        "🔄 Reconnexion activée"
    )

    print(
        "⏳ En attente..."
    )


    app.run_polling(

        bootstrap_retries=-1

    )


if __name__ == "__main__":

    main()

