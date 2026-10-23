import random


def run_external_checks(business_id: str) -> dict:

    # Мок внешних проверок. Возвращает словарь с результатами
    # В реальной жизни здесь были бы запросы в БКИ, ЕГРЮЛ и ФНС

    # Для демонстрации: 80% шанс, что проверки пройдены
    is_passed = random.random() > 0.2

    return {
        "bki": {"status": "PASSED" if is_passed else "FAILED",
                "reason": "Кредитная история чистая" if is_passed else "Есть просрочки"},
        "egrul": {"status": "PASSED", "reason": "Компания существует"},
        "fns": {"status": "PASSED", "reason": "Нарушений не найдено"},
        "is_all_passed": is_passed
    }