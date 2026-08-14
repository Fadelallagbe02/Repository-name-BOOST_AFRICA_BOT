import os
import json
import asyncio
import argparse
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from telegram import Bot

from cross_promo import CROSS_PROMO
from visual_generator import generate_visual
from content_generator import generate_content

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

CHANNELS = {
    "bet": "@BetBoostAfrica",
    "tech": "@TechBoostAfrica24",
    "crypto": "@CryptoBoostAfrica",
}

HISTORY_FILE = "history.json"

MESSAGES = {
    "08:00": {
        "bet": [
            "⚽🔥 BET BOOST AFRICA\n\n🎯 MESSAGE DU JOUR\n\nUne bonne analyse commence par la patience.\n\n📊 Analyse\n🧠 Discipline\n💰 Gestion du capital\n🚫 Pas de décision impulsive\n\n🔥 BET BOOST AFRICA"
        ],
        "tech": [
            "💻🚀 TECH BOOST AFRICA\n\n🌍 MESSAGE DU JOUR\n\nL'Afrique ne doit pas seulement consommer la technologie.\n\nElle doit aussi la créer.\n\n🤖 IA\n📱 Applications\n⚙️ Automatisation\n🌐 Blockchain\n📊 Data\n\n🔥 Apprendre. Construire. Innover."
        ],
        "crypto": [
            "₿🔥 CRYPTO BOOST AFRICA\n\n📊 MESSAGE DU JOUR\n\nLe marché crypto récompense la discipline, pas la précipitation.\n\n📈 Pas de FOMO.\n📉 Pas de panique.\n🧠 Analyse avant décision.\n🛡️ Gestion du risque.\n\n⚠️ Aucun mouvement de marché n'est garanti.\n\n🌍 CRYPTO BOOST AFRICA"
        ],
    },

    "13:00": {
        "bet": [
            "📚⚽ BET BOOST AFRICA\n\n💡 CONSEIL DU JOUR\n\nAvant de regarder la cote, regarde d'abord le contexte du match.\n\nForme récente, absences, motivation et statistiques peuvent changer complètement une analyse.\n\n🎯 L'information avant l'impulsion."
        ],
        "tech": [
            "📚💻 TECH BOOST AFRICA\n\n💡 LE SAVIEZ-VOUS ?\n\nL'automatisation permet à une entreprise de transformer des tâches répétitives en processus exécutés automatiquement.\n\n⚙️ Moins de tâches manuelles.\n📈 Plus de productivité.\n💡 Plus de temps pour créer."
        ],
        "crypto": [
            "📚₿ CRYPTO BOOST AFRICA\n\n💡 CONCEPT DU JOUR\n\nLe Bitcoin est un actif très volatil.\n\nCela signifie que son prix peut connaître de fortes variations en peu de temps.\n\n🎯 Comprendre la volatilité est essentiel avant de prendre un risque."
        ],
    },

    "19:00": {
        "bet": [
            "🌙⚽ BET BOOST AFRICA\n\nQUESTION À LA TEAM 👇\n\nQu'est-ce qui compte le plus pour vous avant un pari ?\n\n📊 Les statistiques\n🧠 La forme des équipes\n💰 La cote\n🎯 La stratégie\n\nRépondez dans les commentaires 👇"
        ],
        "tech": [
            "🌙💻 TECH BOOST AFRICA\n\nQUESTION À LA COMMUNAUTÉ 👇\n\nQuelle technologie aura le plus grand impact en Afrique dans les prochaines années ?\n\n🤖 IA\n📱 Fintech\n🌐 Blockchain\n⚙️ Automatisation\n\nVotre avis ? 👇"
        ],
        "crypto": [
            "🌙₿ CRYPTO BOOST AFRICA\n\nQUESTION À LA COMMUNAUTÉ 👇\n\nSelon vous, quel sera le plus grand changement dans la crypto dans les prochaines années ?\n\n₿ Bitcoin\n🏦 Adoption institutionnelle\n🌐 Blockchain\n💳 Paiements numériques\n\nVotre avis 👇"
        ],
    },
}


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def get_benin_slot():
    """
    GitHub Actions travaille en UTC.
    On convertit explicitement vers l'heure du Bénin.
    """
    now_benin = datetime.now(
        timezone.utc
    ).astimezone(
        ZoneInfo("Africa/Porto-Novo")
    )

    return now_benin.strftime("%H:%M"), now_benin


async def publish(slot):
    if slot not in MESSAGES:
        print(f"❌ Créneau inconnu : {slot}")
        return

    if not TOKEN:
        print("❌ BOT_TOKEN introuvable")
        return

    bot = Bot(TOKEN)
    history = load_history()

    slot_time, now_benin = get_benin_slot()
    today = now_benin.strftime("%Y-%m-%d")

    print(f"🇧🇯 Heure Bénin : {now_benin.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Créneau demandé : {slot}")

    if today not in history:
        history[today] = []

    for category, channel in CHANNELS.items():

        key = f"{today}_{slot}_{category}"

        if key in history[today]:
            print(f"⏭️ {category.upper()} déjà publié")
            continue

        try:
            message = (
                generate_content(category, slot)
                + CROSS_PROMO[category]
            )

            visual_path = generate_visual(
                category,
                slot,
                message
            )

            print(
                f"📤 Envoi {category.upper()} "
                f"→ {channel}"
            )

            with open(visual_path, "rb") as photo:
                await bot.send_photo(
                    chat_id=channel,
                    photo=photo,
                    caption=message
                )

            history[today].append(key)
            save_history(history)

            print(
                f"✅ {category.upper()} → "
                f"{slot} → PUBLIÉ"
            )

            await asyncio.sleep(3)

        except Exception as e:
            print(
                f"❌ {category.upper()} → "
                f"{type(e).__name__}: {e}"
            )

    await bot.shutdown()


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--once",
        action="store_true",
        help="Publie une seule fois puis quitte"
    )
    parser.add_argument(
        "--slot",
        choices=["08:00", "13:00", "19:00"],
        help="Créneau explicite"
    )

    args = parser.parse_args()

    print("=" * 50)
    print("🤖 BOOST AFRICA MANAGER")
    print("=" * 50)

    if args.slot:
        slot = args.slot
    else:
        slot, now_benin = get_benin_slot()

    print(f"🇧🇯 Heure Bénin : {get_benin_slot()[1].strftime('%H:%M:%S')}")
    print(f"🎯 Slot : {slot}")

    if args.once:
        print("⚡ MODE ONCE")
        await publish(slot)
        print("🏁 Publication terminée")
        return

    print("🔄 MODE CONTINU")

    last_slot = None

    while True:
        current_slot, _ = get_benin_slot()

        if current_slot in MESSAGES and last_slot != current_slot:
            print(f"\n🚀 Publication {current_slot}")
            await publish(current_slot)
            last_slot = current_slot

        await asyncio.sleep(20)


if __name__ == "__main__":
    asyncio.run(main())
