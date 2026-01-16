from datetime import datetime, date, timezone
from flask import Flask, request, render_template_string
import ephem

app = Flask(__name__)
@app.after_request
def add_csp(resp):
    # Разрешаем встраивание только на veneficamagic.ru
    resp.headers["Content-Security-Policy"] = "frame-ancestors https://veneficamagic.ru"
    return resp


SYNODIC_MONTH = 29.53058867


def parse_date(s: str) -> date:
    # формат DD-MM-YYYY
    return datetime.strptime(s, "%d-%m-%Y").date()


def phase_name(age_days: float) -> str:
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


def format_ephem_date(d) -> str:
    dt = ephem.Date(d).datetime()  # UTC
    return dt.strftime("%d/%m/%Y")


def moon_info(for_date: date) -> dict:
    dt = datetime(for_date.year, for_date.month, for_date.day, 12, 0, 0, tzinfo=timezone.utc)

    moon = ephem.Moon(dt)
    illumination = float(moon.phase)

    prev_new = ephem.previous_new_moon(dt)
    next_new = ephem.next_new_moon(dt)
    next_full = ephem.next_full_moon(dt)

    age_days = (ephem.Date(dt) - prev_new)

    return {
        "date": for_date.strftime("%d/%m/%Y"),
        "phase": phase_name(age_days),
        "age_days": float(age_days),
        "illumination": illumination,
        "prev_new": format_ephem_date(prev_new),
        "next_new": format_ephem_date(next_new),
        "next_full": format_ephem_date(next_full),
    }


HTML = """
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Лунный помощник</title>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; margin: 24px; }
    .card { max-width: 560px; padding: 16px; border: 1px solid #ddd; border-radius: 14px; }
    input, button { font-size: 16px; padding: 10px 12px; }
    button { cursor: pointer; }
    .row { display: flex; gap: 8px; flex-wrap: wrap; margin: 12px 0; }
    .muted { color: #666; }
    h1 { margin: 0 0 12px; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Лунный помощник 🌙</h1>
    <div class="muted">Введи дату в формате <b>дд-мм-ГГГГ</b> или оставь пустым (тогда будет сегодняшнее число).</div>

    <form method="get" class="row">
      <input name="date" placeholder="например 14-01-2026" value="{{qdate}}">
      <button type="submit">Показать</button>
      <a href="/" style="align-self:center;">Сегодня</a>
    </form>

    {% if info %}
      <hr>
      <div><b>Дата:</b> {{info.date}}</div>
      <div><b>Фаза:</b> {{info.phase}}</div>
      <div><b>Возраст Луны:</b> {{'%.1f'|format(info.age_days)}} дней</div>
      <div><b>Освещённость:</b> {{'%.1f'|format(info.illumination)}}%</div>
      <hr>
      <div><b>Предыдущее новолуние:</b> {{info.prev_new}}</div>
      <div><b>Следующее новолуние:</b> {{info.next_new}}</div>
      <div><b>Следующее полнолуние:</b> {{info.next_full}}</div>
    {% endif %}
  </div>
</body>
</html>
"""


@app.route("/")
def index():
    q = request.args.get("date", "").strip()
    if q:
        try:
            d = parse_date(q)
            info = moon_info(d)
        except ValueError:
            info = None
            q = ""
    else:
        info = moon_info(date.today())
    return render_template_string(HTML, info=info, qdate=q)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
