from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class JaneBlogRubric:
    key: str
    label: str
    source_fit: str
    primary_themes: tuple[str, ...]
    platform_lanes: tuple[str, ...]
    audience_function: str
    serial_role: str
    search_rule: str
    story_prompts: tuple[str, ...] = ()


JANE_BLOG_RUBRICS: dict[str, JaneBlogRubric] = {
    "bali_life": JaneBlogRubric(
        key="bali_life",
        label="#bali life",
        source_fit="про новые места на острове, отели, рестораны, выставки арт, мероприятия, новости Бали в контексте",
        primary_themes=("bali_travel",),
        platform_lanes=("instagram_lifestyle",),
        audience_function="дать ощущение живого Бали через конкретный инфоповод, место или событие",
        serial_role="серия про остров: что появилось, куда сходить, что это говорит о жизни на Бали",
        search_rule="искать источники с местами, событиями, отелями, ресторанами, арт/новостями Бали, которые можно превратить в сериальный инфоповод",
        story_prompts=(
            "день цен на Бали",
            "день со мной в важном месте",
            "room tour или обзор места",
            "Убуд 5 лет назад и сейчас",
            "подборка мест",
        ),
    ),
    "lifestyle": JaneBlogRubric(
        key="lifestyle",
        label="lifestyle",
        source_fit="мой личный опыт балийской жизни",
        primary_themes=("founder_journey",),
        platform_lanes=("instagram_lifestyle",),
        audience_function="создать узнавание и близость через реальный личный опыт, а не идеальную картинку",
        serial_role="серия про личную балийскую жизнь: что сейчас на повестке дня и какой инсайт из этого родился",
        search_rule="искать личные сцены, ритуалы, повседневные решения, честные наблюдения и поводы для рефлексии о жизни на Бали",
        story_prompts=(
            "какой период прохожу сейчас",
            "моё утро и почему такой набор ритуалов",
            "мой рабочий день",
            "чувство прямо сейчас и причина",
            "последнее осознание о жизни",
        ),
    ),
    "real_estate": JaneBlogRubric(
        key="real_estate",
        label="#недвижка",
        source_fit="обзор недвижимости, земли и новости рынка недвижимости Бали",
        primary_themes=("expert_pain_bali", "land_and_legal", "market_reports", "boutique_hotels", "marketing_cases"),
        platform_lanes=("instagram_professional", "linkedin_b2b"),
        audience_function="дать экспертную пользу через опыт, риски, проверку, рынок и понятный вывод для решения",
        serial_role="серия про недвижку: один объект/сигнал/ошибка -> один практический вывод",
        search_rule="искать источники про землю, виллы, девелопмент, рынок, legal, operator logic, цены, спрос, сделки и ошибки",
        story_prompts=(
            "обзор на проект недвижимости",
            "обзор дома",
            "день цен на Бали",
            "главные неудачи месяца",
            "подставьте над собой эксперимент",
        ),
    ),
    "relationships": JaneBlogRubric(
        key="relationships",
        label="#отношения",
        source_fit="про отношения с мужем и бизнес-партнёром, с семьёй, с ребёнком в роли матери",
        primary_themes=("founder_journey",),
        platform_lanes=("instagram_lifestyle",),
        audience_function="показать реальность любви, семьи, партнёрства и материнства внутри амбициозной жизни",
        serial_role="серия про отношения: одна бытовая сцена -> одна честная мысль о семье, бизнесе или материнстве",
        search_rule="искать источники с семейными сценами, партнёрством, ролью матери, детскими решениями, честной бытовой реальностью",
        story_prompts=(
            "откровенные вопросы",
            "слухи обо мне. правда ли что я",
            "мы встретились за чашкой кофе. что бы вы спросили?",
            "прошлая я и нынешняя я",
            "уроки сложного периода",
        ),
    ),
    "founder_notes": JaneBlogRubric(
        key="founder_notes",
        label="#заметки фаундера",
        source_fit="про ведение бизнеса, лайфхаки, психология и как заработать миллион $ и не сойти с ума",
        primary_themes=("founder_journey", "marketing_cases"),
        platform_lanes=("instagram_lifestyle", "instagram_professional", "linkedin_b2b"),
        audience_function="дать энергию и пользу через честную предпринимательскую рефлексию, победы, неудачи и решения",
        serial_role="серия заметок фаундера: что сейчас в бизнесе болит/двигается -> какой вывод можно забрать",
        search_rule="искать founder lessons, бизнес-решения, психологию, деньги, управление, ошибки, рост, миллионный масштаб без глянца",
        story_prompts=(
            "главные неудачи месяца",
            "какие ближайшие цели",
            "главная задача недели",
            "личная цель + отчёты",
            "книга, которую читаю",
        ),
    ),
    "experience": JaneBlogRubric(
        key="experience",
        label="#experience",
        source_fit="про необычные арт и велнес experiences в мировой практике на стыке hospitality, business, art",
        primary_themes=("global_trends", "wellness_architecture", "boutique_hotels"),
        platform_lanes=("instagram_lifestyle", "instagram_professional", "linkedin_b2b"),
        audience_function="перевести мировой art/wellness/hospitality опыт в идею для продукта, бизнеса или жизни",
        serial_role="серия про experience: необычный мировой пример -> что из него можно забрать для Бали/AILLA/гостеприимства",
        search_rule="искать арт, wellness, hospitality, design, architecture, boutique hotel and business experiences with transferable insight",
        story_prompts=(
            "подборка",
            "цитата, которая откликается, и мысли на неё",
            "обзор места",
            "фото до / после + рефлексия",
            "выбрать рубрику в формате сериала",
        ),
    ),
}


THEME_TO_RUBRIC: dict[str, str] = {
    "bali_travel": "bali_life",
    "founder_journey": "lifestyle",
    "expert_pain_bali": "real_estate",
    "land_and_legal": "real_estate",
    "market_reports": "real_estate",
    "global_trends": "experience",
    "wellness_architecture": "experience",
    "boutique_hotels": "experience",
    "marketing_cases": "founder_notes",
}


JANE_AUDIENCE_FUNCTION_RULES: tuple[str, ...] = (
    "люди ждут от блогера мотивация и энергия",
    "люди ждут реальность жизни: победы и неудачи без глянцевой упаковки",
    "люди ждут рефлексия / инсайт, который можно примерить на себя",
    "люди ждут польза в форме опыта / эксперта в живой форме",
)


JANE_STORY_STRUCTURE_RULES: tuple[str, ...] = (
    "выходить в блог с тем, что у Jane на повестке дня",
    "размышления и инсайты важнее абстрактных советов",
    "1 мысль / 1 эмоция / 1 сюжет",
    "структура: якорь / интрига -> история / контекст -> умозаключение",
    "каждый Instagram post is an info occasion",
    "выбирать рубрику в формате сериала, чтобы пост был частью узнаваемой линии",
)


JANE_STORIES_PROMPTS: tuple[str, ...] = (
    "интерактивное: было / не было",
    "что бы ты сделала если...",
    "откровенные вопросы",
    "мы встретились за чашкой кофе. что бы вы спросили?",
    "слухи обо мне. правда ли что я...",
    "день цен на Бали",
    "день со мной — важный день, предупредить заранее",
    "фото до / после + рефлексия",
    "главные неудачи месяца",
    "какие ближайшие цели",
    "какой период прохожу сейчас",
    "главная задача недели",
    "моё утро и почему такой набор ритуалов",
    "мой рабочий день, как устроен и почему так",
    "подставьте над собой эксперимент",
    "личная цель + отчёты",
    "мемы",
    "room tour или обзор места, где я живу",
    "книга, которую читаю",
    "подборка",
    "обзор на проект недвижимости / обзор дома",
    "сравнить себя с прошлым в месте, где был раньше",
    "прошлая я и нынешняя я",
    "Убуд 5 лет назад и сейчас",
    "обзор своих покупок",
    "идеи для сюрпризов на ДР / идеи для свиданий",
    "жизненные фишечки: простые рецепты, волосы, уборка",
    "уроки сложного периода — как сложности делают тебя сильнее",
    "чувство прямо сейчас и причина",
    "последнее осознание о жизни",
    "цитата, которая откликается, и мысли на неё",
    "рассказать про окружение",
    "выбрать рубрику в формате сериала",
)


JANE_ANALYST_REVIEW_LOOP_RULES: tuple[str, ...] = (
    "Analyst reviews Writer output before human review.",
    "Check rubric fit, target audience fit, narrow topic, source-backed info occasion, and platform lane.",
    "Check 1 мысль / 1 эмоция / 1 сюжет and anchor/intrigue -> story/context -> conclusion.",
    "Check that the text gives at least one of: motivation and energy, real life wins/failures, reflection, useful lived expertise.",
    "If the check fails, send rewrite instructions back to Writer.",
    "Use maximum 3 review passes.",
    "If the text passes earlier, return immediately.",
    "If it still fails, return after the third pass with remaining issues visible.",
)


def resolve_jane_blog_rubric(content_theme: str, source_text: str = "") -> JaneBlogRubric:
    normalized_theme = content_theme.strip().lower().replace(" ", "_")
    text = f"{normalized_theme} {source_text}".lower()

    if _contains_any(text, ("муж", "husband", "партн", "partner", "семь", "family", "реб", "child", "мать", "mother", "материн")):
        return JANE_BLOG_RUBRICS["relationships"]
    if _contains_any(text, ("миллион", "million", "$", "фаундер", "founder notes", "психолог", "не сойти", "burnout", "business hack")):
        return JANE_BLOG_RUBRICS["founder_notes"]
    if normalized_theme in {"bali_travel", "global_trends", "wellness_architecture", "boutique_hotels"}:
        return JANE_BLOG_RUBRICS[THEME_TO_RUBRIC[normalized_theme]]
    if _contains_any(text, ("зем", "недвиж", "real estate", "property", "villa", "legal", "law", "market report", "рынок", "сделк")):
        return JANE_BLOG_RUBRICS["real_estate"]
    if _contains_any(text, ("новые места", "restaurant", "ресторан", "выстав", "event", "мероприят", "новости бали", "bali travel", "отел")):
        return JANE_BLOG_RUBRICS["bali_life"]
    if _contains_any(text, ("wellness", "art", "experience", "hospitality", "architecture", "spa", "dezeen", "wallpaper")):
        return JANE_BLOG_RUBRICS["experience"]

    return JANE_BLOG_RUBRICS.get(THEME_TO_RUBRIC.get(normalized_theme, "lifestyle"), JANE_BLOG_RUBRICS["lifestyle"])


def format_rubric_labels() -> str:
    return ", ".join(rubric.label for rubric in JANE_BLOG_RUBRICS.values())


def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    return any(marker in text for marker in markers)
