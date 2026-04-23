# PROMPTS = {
#     "brief_plan": """Ты — опытный воспитатель детского сада.
# Составь краткий план занятия для детей {age_group} по теме '{theme}'.
# Дополнительно: {teacher_notes}

# Требования:
# - Структура: цель, материалы, шаги занятия, рекомендации по безопасности.
# - Язык и задания должны соответствовать возрасту.
# - Ответ в виде списка с подзаголовками.
# """,

#     "detailed": """Ты — опытный воспитатель детского сада.
# Составь подробный конспект занятия для детей {age_group} по теме '{theme}'.
# Дополнительно: {teacher_notes}

# Требования:
# - Включи: цели образовательные и развивающие, материалы, пошаговое описание, варианты для разных уровней, рекомендации по безопасности.
# - Каждое действие подписано номерами шагов.
# - Лексика и задания соответствуют возрасту.
# - Ответ должен быть читаемым, структурированным, без лишнего текста.
# """,

#     "outdoor_games": """Составь список безопасных уличных игр для детей {age_group} по теме '{theme}'.
# Дополнительно: {teacher_notes}

# Требования:
# - Указать название игры и короткое описание.
# - Время игры и материалы.
# - Рекомендации по безопасности.
# - Лексика соответствует возрасту.
# """,

#     "indoor_games": """Составь список безопасных игр в помещении для детей {age_group} по теме '{theme}'.
# Дополнительно: {teacher_notes}

# Требования:
# - Указать название игры и короткое описание.
# - Время игры и материалы.
# - Рекомендации по безопасности.
# - Лексика соответствует возрасту.
# """,

#     "morning_event_text": """Составь текст для утренника для детей {age_group} по теме '{theme}'.
# Дополнительно: {teacher_notes}

# Требования:
# - Структурируй текст в виде сцен, действий и реплик.
# - Лексика и задания соответствуют возрасту.
# - Ответ должен быть готов к использованию в мероприятии.
# """,

#     "mini_scenario": """Составь мини-сценарий для детей {age_group} по теме '{theme}'.
# Дополнительно: {teacher_notes}

# Требования:
# - Укажи роли, реплики и последовательность действий.
# - Сделай сценарий простым и безопасным для детей.
# - Лексика соответствует возрасту.
# """
# }


PROMPTS = {
    "brief_plan": """You are an experienced kindergarten teacher.
Create a short lesson plan for children {age_group} on the topic '{theme}'.
Additional notes: {teacher_notes}

Requirements:
- Structure: goal, materials, lesson steps, safety recommendations.
- Language and tasks must be appropriate for the age.
- Answer in a list format with subheadings.
""",

    "detailed": """You are an experienced kindergarten teacher.
Create a detailed lesson outline for children {age_group} on the topic '{theme}'.
Additional notes: {teacher_notes}

Requirements:
- Include: educational and developmental goals, materials, step-by-step description, variations for different skill levels, safety recommendations.
- Each action should be numbered.
- Vocabulary and tasks must be age-appropriate.
- The response should be readable, well-structured, and without unnecessary text.
""",

    "outdoor_games": """Create a list of safe outdoor games for children {age_group} on the topic '{theme}'.
Additional notes: {teacher_notes}

Requirements:
- Provide the name of the game and a short description.
- Include game duration and required materials.
- Safety recommendations.
- Vocabulary must be appropriate for the age group.
""",

    "indoor_games": """Create a list of safe indoor games for children {age_group} on the topic '{theme}'.
Additional notes: {teacher_notes}

Requirements:
- Provide the name of the game and a short description.
- Include game duration and required materials.
- Safety recommendations.
- Vocabulary must be appropriate for the age group.
""",

    "morning_event_text": """Create a script for a kindergarten morning event for children {age_group} on the topic '{theme}'.
Additional notes: {teacher_notes}

Requirements:
- Structure the text in scenes, actions, and dialogues.
- Vocabulary and tasks must be appropriate for the age group.
- The response should be ready to use in an event.
""",

    "mini_scenario": """Create a mini-scenario for children {age_group} on the topic '{theme}'.
Additional notes: {teacher_notes}

Requirements:
- Specify roles, dialogues, and sequence of actions.
- Make the scenario simple and safe for children.
- Vocabulary must be appropriate for the age group.
"""
}