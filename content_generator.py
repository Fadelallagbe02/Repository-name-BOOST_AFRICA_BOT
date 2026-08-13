import random

CONTENT_TEMPLATES = {
    "bet": [
        {
            "title": "⚽ ANALYSE DU JOUR",
            "body": "La forme récente des équipes, les absences et la dynamique collective peuvent fortement influencer un match.",
            "cta": "🎯 Analysez le contexte avant de regarder uniquement la cote."
        },
        {
            "title": "⚽ CONSEIL FOOT",
            "body": "Une équipe favorite n'est jamais automatiquement une équipe gagnante. Le contexte du match reste essentiel.",
            "cta": "🧠 La discipline avant l'impulsion."
        },
        {
            "title": "📊 FOOT & DONNÉES",
            "body": "Les statistiques deviennent vraiment utiles lorsqu'elles sont comparées au contexte réel d'une rencontre.",
            "cta": "📈 Regardez les données. Comprenez le contexte."
        }
    ],

    "tech": [
        {
            "title": "🤖 IA & AFRIQUE",
            "body": "L'intelligence artificielle peut permettre aux entreprises africaines d'automatiser certaines tâches et d'améliorer leur productivité.",
            "cta": "🚀 L'avenir appartient à ceux qui construisent."
        },
        {
            "title": "💻 TECHNOLOGIE",
            "body": "Une bonne automatisation peut transformer une tâche répétitive en processus exécuté automatiquement.",
            "cta": "⚙️ Moins de tâches manuelles. Plus de création."
        },
        {
            "title": "🌍 INNOVATION AFRICAINE",
            "body": "Les entrepreneurs africains disposent aujourd'hui d'outils capables de créer des produits numériques avec beaucoup moins de ressources qu'avant.",
            "cta": "🔥 Construire devient plus accessible."
        }
    ],

    "crypto": [
        {
            "title": "₿ CRYPTO DU JOUR",
            "body": "Le marché crypto reste volatil. Une variation rapide du prix peut créer des opportunités, mais aussi augmenter fortement le risque.",
            "cta": "🛡️ Comprendre le risque avant de chercher le rendement."
        },
        {
            "title": "📊 MARCHÉ CRYPTO",
            "body": "Le prix seul ne raconte pas toute l'histoire. Le volume, la liquidité et le contexte général du marché peuvent également compter.",
            "cta": "🧠 Analyse avant décision."
        },
        {
            "title": "₿ ÉDUCATION CRYPTO",
            "body": "La volatilité mesure l'ampleur des variations d'un actif. Plus elle est élevée, plus le potentiel de mouvement est important.",
            "cta": "📚 Comprendre avant d'investir."
        }
    ]
}


def generate_content(category, slot):
    templates = CONTENT_TEMPLATES.get(
        category,
        CONTENT_TEMPLATES["tech"]
    )

    content = random.choice(templates)

    message = (
        f"{content['title']}\n\n"
        f"{content['body']}\n\n"
        f"{content['cta']}\n\n"
        f"🌍 BOOST AFRICA"
    )

    return message
