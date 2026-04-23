# import os
# from dotenv import load_dotenv
# from openai import OpenAI
# from chatbot.prompt import PROMPTS

# load_dotenv()

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# if client.api_key is None:
#     raise ValueError("OPENAI_API_KEY отсутствует")


# def generate_text(input_data: dict) -> str:

#     # validation
#     required = ["age_group", "theme", "output_type"]
#     for k in required:
#         if k not in input_data:
#             raise ValueError(f"Отсутствует поле {k}")
    

#     template = PROMPTS.get(input_data["output_type"], PROMPTS["brief_plan"])
#     prompt = template.format(
#         age_group=input_data["age_group"],
#         theme=input_data["theme"],
#         teacher_notes=input_data.get("teacher_notes", "")
#     )

#     max_tokens = int(input_data.get("max_tokens", 800))
#     temp = float(input_data.get("temperature", 0.7))

#     try:
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": (
#                     "Ты — AI-помощник воспитателя. "
#                     "Отвечай кратко/структурировано. "
#                     "Не предлагай опасных действий. "
#                 )},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=max_tokens,
#             temperature=temp
#         )
#     except Exception as e:
#         raise RuntimeError("Не удалось получить ответ от модели") from e
    
#     try:
#         text = response.choices[0].message.content
#     except Exception as e:
#         raise RuntimeError("Неверная структура ответа модели") from e

#     return text




# import os
# from dotenv import load_dotenv
# from openai import OpenAI
# from chatbot.prompt import PROMPTS

# load_dotenv()

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# if client.api_key is None:
#     raise ValueError("OPENAI_API_KEY отсутствует")


# def generate_text(input_data: dict) -> str:

#     # validation
#     required = ["age_group", "theme", "output_type"]
#     for k in required:
#         if k not in input_data:
#             raise ValueError(f"Отсутствует поле {k}")

#     template = PROMPTS.get(input_data["output_type"], PROMPTS["brief_plan"])

#     # 🔥 NEW LOGIC (special needs)
#     has_special = input_data.get("has_special_needs", False)
#     special_notes = input_data.get("special_notes", "").strip()

#     extra_context = ""

#     if has_special:
#         if special_notes:
#             extra_context = f"""
# Important:
# Some children in the group may have additional learning or developmental needs.
# Details: {special_notes}

# Adapt the activities:
# - Avoid physically or cognitively overwhelming tasks
# - Provide alternative options
# - Emphasize safety and inclusivity
# """
#         else:
#             extra_context = """
# Important:
# Some children may require additional support.

# Adapt the plan to be:
# - inclusive
# - flexible
# - safe for different ability levels
# """

#     # основной prompt (старый не ломаем)
#     prompt = template.format(
#         age_group=input_data["age_group"],
#         theme=input_data["theme"],
#         teacher_notes=input_data.get("teacher_notes", "")
#     )

#     # аккуратно добавляем контекст
#     if extra_context:
#         prompt = prompt.strip() + "\n\n" + extra_context.strip()

#     max_tokens = int(input_data.get("max_tokens", 800))
#     temp = float(input_data.get("temperature", 0.7))

#     try:
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": (
#                         "Ты — AI-помощник воспитателя. "
#                         "Отвечай кратко и структурированно. "
#                         "Учитывай безопасность детей и разные уровни развития. "
#                         "Если в группе есть дети с дополнительными потребностями — адаптируй задания."
#                     )
#                 },
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=max_tokens,
#             temperature=temp
#         )
#     except Exception as e:
#         raise RuntimeError("Не удалось получить ответ от модели") from e

#     try:
#         text = response.choices[0].message.content
#     except Exception as e:
#         raise RuntimeError("Неверная структура ответа модели") from e

#     return text



import os
from dotenv import load_dotenv
from openai import OpenAI
from chatbot.prompt import PROMPTS

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

if client.api_key is None:
    raise ValueError("OPENAI_API_KEY отсутствует")


def generate_text(input_data: dict) -> str:

    required = ["age_group", "theme", "output_type"]
    for k in required:
        if k not in input_data:
            raise ValueError(f"Отсутствует поле {k}")

    template = PROMPTS.get(input_data["output_type"], PROMPTS["brief_plan"])

    has_special = input_data.get("has_special_needs", False)
    special_notes = input_data.get("special_notes", "").strip()

    extra_context = ""

    if has_special:
        if special_notes:
            extra_context = f"""
Important:
Some children in the group may have additional learning or developmental needs.

Adapt the plan in an inclusive way without labeling individual children.
Use this context for adaptation only:
{special_notes}

Guidelines:
- avoid overwhelming tasks
- provide multiple difficulty levels
- use step-by-step instructions
- ensure inclusive participation
"""
        else:
            extra_context = """
Important:
Some children in the group may require additional support.

Adapt the plan in an inclusive and flexible way:
- provide simplified instructions
- allow different levels of participation
- ensure accessibility for all children
"""

    prompt = template.format(
        age_group=input_data["age_group"],
        theme=input_data["theme"],
        teacher_notes=input_data.get("teacher_notes", "")
    )

    if extra_context:
        prompt = prompt.strip() + "\n\n" + extra_context.strip()

    max_tokens = int(input_data.get("max_tokens", 800))
    temp = float(input_data.get("temperature", 0.7))

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant for kindergarten teachers. "
                        "Always respond in a structured, safe, and professional way. "
                        "Ensure inclusivity for children with different developmental needs without explicitly labeling or stigmatizing them."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temp
        )
    except Exception as e:
        raise RuntimeError("Не удалось получить ответ от модели") from e

    try:
        text = response.choices[0].message.content
    except Exception as e:
        raise RuntimeError("Неверная структура ответа модели") from e

    return text