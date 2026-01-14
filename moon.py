import argparse
from datetime import datetime, date, timezone

import ephem

SYNODIC_MONTH = 29.53058867 #средняя длина лунного месяца (дни)

def parse_date(s: str) -> date:
    #ожидаем формат DD-MM-YYYY
    return datetime.strptime(s, "%d-%m-%Y").date()

def phase_name(age_days: float) -> str:
    # Условные границы по "возрасту" Луны
    # 0    — новолуние
    # ~7.4 — первая четверть
    # ~14.8— полнолуние
    # ~22.1— последняя четверть
    if age_days < 1.0 or age_days > SYNODIC_MONTH - 1.0:
        return "Новолуние 🌑"
    if age_days < 7.4:
        return "Растущий серп 🌒"
    if age_days < 8.4:
        return "Первая четверть 🌓"
    if age_days < 14.8:
        return "Растущая (перед полнолунием) 🌔"
    if age_days < 15.8:
        return "Полнолуние 🌕"
    if age_days < 22.1:
        return "Убывающая (после полнолуния) 🌖"
    if age_days < 23.1:
        return "Последняя четверть 🌗"
    return "Убывающий серп 🌘"

def moon_info(for_date: date) -> dict:
    dt = datetime(for_date.year, for_date.month, for_date.day, 12, 0, 0, tzinfo=timezone.utc)

    #освещённость в проценнтах
    moon = ephem.Moon(dt)
    illumination = float(moon.phase) #0...100

    prev_new = ephem.previous_new_moon(dt)
    next_new = ephem.next_new_moon(dt)
    next_full = ephem.next_full_moon(dt)

    age_days = (ephem.Date(dt) - prev_new)

    return{
        "date": for_date.strftime("%d-%m-%Y"),
        "phase": phase_name(age_days),
        "age_days": float(age_days),
        "illumination": illumination,
        "prev_new": str(prev_new),
        "next_new": str(next_new),
        "next_full": str(next_full),
    }

def main ():
    parser = argparse.ArgumentParser(description="Лунный помощник: фаза Луны по дате")
    parser.add_argument("date", nargs="?", help="Дата в формате DD-MM-YYYY (если не указано — сегодня)")
    args = parser.parse_args()

    d = date.today() if args.date is None else parse_date(args.date)
    info = moon_info(d)

    print(f"Дата: {info['date']}")
    print(f"Фаза: {info['phase']}")
    print(f"Возраст луны: {info['age_days']:.1f} дней")
    print(f"Освещённость: {info['illumination']:.1f}%")
    print()
    print(f"Предыдущее новолуние: {info['prev_new']}")
    print(f"Следующее новолуние: {info['next_new']}")
    print(f"Следующее полнолуние: {info['next_full']}")

if __name__ == "__main__":
    main()
