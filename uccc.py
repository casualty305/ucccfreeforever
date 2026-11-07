# -*- coding: utf-8 -*-
"""
UCCC - Ultimate Custom Cursor Creator  v1.1.1
Free & open. Draw your own mouse cursor (static .cur or animated .ani via ACC)
and install it with one click. Windows 10/11.  Python 3.9+ / PyQt6.
"""
import sys, os, json, math, struct, time, random, base64
from pathlib import Path
from PyQt6.QtCore import (Qt, QTimer, QPointF, QRectF, QSize, QLocale, QUrl, pyqtSignal,
                          QBuffer, QByteArray, QIODevice)
from PyQt6.QtGui import (QColor, QPainter, QPen, QBrush, QImage, QPixmap, QPainterPath,
                         QLinearGradient, QConicalGradient, QIcon, QFont, QCursor,
                         QPolygonF, QMovie, QDesktopServices, QShortcut, QKeySequence,
                         QFontMetrics, QRadialGradient)
from PyQt6.QtWidgets import (QApplication, QWidget, QFrame, QLabel, QPushButton, QToolButton,
                             QVBoxLayout, QHBoxLayout, QGridLayout, QStackedWidget, QSlider,
                             QComboBox, QCheckBox, QLineEdit, QSpinBox, QListWidget,
                             QListWidgetItem, QListView, QFileDialog, QMessageBox, QDialog,
                             QButtonGroup, QSizeGrip, QScrollArea, QSizePolicy, QInputDialog)

# ───────────────────────── paths & settings ─────────────────────────
FROZEN = getattr(sys, "frozen", False)
APP_DIR = Path(sys.executable).parent if FROZEN else Path(__file__).resolve().parent
CURSOR_DIR = Path(os.environ.get("APPDATA", str(Path.home()))) / "UCCC" / "cursors"

DEFAULTS = dict(lang="en", theme="dark", autofit=True, cur_size=32, rainbow=35,
                grid=True, smooth=True, tut_done=False, accent="",
                bar_mode="rainbow", bar_c1="#b45309", bar_c2="#fbbf24", bar_pattern="amber",
                grad_saved=False, grad_c1="#7c3aed", grad_c2="#0ea5e9", grad_pattern="smooth")
S = dict(DEFAULTS)
LANG, THEME = "en", "dark"


def _spath():
    p = APP_DIR / "uccc_settings.json"           # portable: next to the exe
    if p.exists():
        return p
    try:
        with open(p, "a"):
            pass
        return p
    except OSError:
        d = Path(os.environ.get("APPDATA", str(Path.home()))) / "UCCC"
        d.mkdir(parents=True, exist_ok=True)
        return d / "uccc_settings.json"


def load_settings():
    global LANG, THEME
    try:
        S.update(json.loads(_spath().read_text("utf-8")))
    except Exception:
        pass                                           # first launch: English by default
    LANG, THEME = S["lang"], S["theme"]


def save_settings():
    try:
        _spath().write_text(json.dumps(S, ensure_ascii=False, indent=1), "utf-8")
    except Exception:
        pass


# ───────────────────────── translations ─────────────────────────
STR = {"en": {}, "ru": {}}


def _t(k, en, ru):
    STR["en"][k], STR["ru"][k] = en, ru


def tr(k):
    return STR[LANG].get(k) or STR["en"].get(k, k)


BIND = []


def bind(setter, key):
    BIND.append(lambda: setter(tr(key)))
    setter(tr(key))


def bindf(fn):
    BIND.append(fn)
    fn()


def retranslate():
    for f in BIND:
        f()


_t("nav_draw", "Draw", "Рисование")
_t("nav_acc", "ACC · Animation", "ACC · Анимация")
_t("nav_set", "Settings", "Настройки")
_t("nav_about", "About", "О программе")
for k, en, ru in [
    ("pen", "Pen", "Карандаш"), ("eraser", "Eraser", "Ластик"), ("fill", "Fill", "Заливка"),
    ("picker", "Eyedropper", "Пипетка"), ("hotspot", "Hotspot (click point)", "Точка клика (hotspot)"),
    ("line", "Line", "Линия"), ("rect", "Rectangle", "Прямоугольник"),
    ("rrect", "Rounded rectangle", "Скруглённый прямоугольник"), ("ellipse", "Ellipse", "Эллипс"),
    ("triangle", "Triangle", "Треугольник"), ("diamond", "Diamond", "Ромб"), ("star", "Star", "Звезда"),
    ("hexagon", "Hexagon", "Шестиугольник"), ("arrow", "Arrow", "Стрелка"), ("heart", "Heart", "Сердце")]:
    _t("t_" + k, en, ru)
_t("size", "Brush size", "Размер кисти")
_t("shape_mode", "Shapes", "Фигуры")
_t("m_outline", "Outline", "Контур")
_t("m_fill", "Filled", "Заливка")
_t("m_both", "Outline + fill", "Контур + заливка")
_t("grid", "Pixel grid", "Сетка пикселей")
_t("smooth", "Smooth edges", "Сглаживание")
_t("canvas_px", "Canvas (px)", "Холст (px)")
_t("undo", "Undo (Ctrl+Z)", "Отменить (Ctrl+Z)")
_t("redo", "Redo (Ctrl+Y)", "Повторить (Ctrl+Y)")
_t("clear", "Clear", "Очистить")
_t("flip_h", "Flip horizontally", "Отразить по горизонтали")
_t("flip_v", "Flip vertically", "Отразить по вертикали")
_t("primary", "Primary colour (left button)", "Основной цвет (левая кнопка)")
_t("secondary", "Secondary colour (right button)", "Доп. цвет (правая кнопка)")
_t("opacity", "Opacity", "Непрозрачность")
_t("preview", "Preview (real size)", "Просмотр (реальный размер)")
_t("hover_test", "Hover the preview to test your cursor", "Наведите на просмотр, чтобы проверить курсор")
_t("role", "Replace this cursor:", "Заменить курсор:")
for k, en, ru in [
    ("Arrow", "Normal pointer", "Обычный указатель"), ("Hand", "Link (hand)", "Ссылка (рука)"),
    ("IBeam", "Text", "Текст"), ("Crosshair", "Precision", "Точный выбор"),
    ("Wait", "Busy", "Занят"), ("AppStarting", "Working in background", "Фоновый режим"),
    ("Help", "Help", "Справка"), ("No", "Unavailable", "Недоступно"), ("SizeAll", "Move", "Перемещение")]:
    _t("role_" + k, en, ru)
_t("apply", "▶  Apply as my cursor", "▶  Применить как мой курсор")
_t("save", "Save file…", "Сохранить файл…")
_t("restore", "Restore default cursors", "Вернуть стандартные курсоры")
_t("import", "Import image / GIF…", "Загрузить картинку / GIF…")
for k, en, ru in [
    ("Arrow", "Normal select", "Основной режим"), ("Help", "Help select", "Выбор справки"),
    ("AppStarting", "Working in background", "Фоновый режим"), ("Wait", "Busy", "Занят"),
    ("Crosshair", "Precision select", "Точный выбор"), ("IBeam", "Text select", "Выделение текста"),
    ("NWPen", "Handwriting", "Рукописный ввод"), ("No", "Unavailable", "Недоступно"),
    ("SizeNS", "Vertical resize", "Изменение размера по вертикали"),
    ("SizeWE", "Horizontal resize", "Изменение размера по горизонтали"),
    ("SizeNWSE", "Diagonal resize 1", "Изменение размера по диагонали 1"),
    ("SizeNESW", "Diagonal resize 2", "Изменение размера по диагонали 2"),
    ("SizeAll", "Move", "Перемещение"), ("UpArrow", "Alternate select", "Альтернативное выделение"),
    ("Hand", "Link select", "Выбор ссылки"), ("Pin", "Location select", "Выбор положения"),
    ("Person", "Person select", "Выбор пользователя")]:
    _t("role_" + k, en, ru)
_t("applied", "✔ Cursor applied!", "✔ Курсор применён!")
_t("saved", "✔ Saved: ", "✔ Сохранено: ")
_t("restored", "✔ Default cursors restored", "✔ Стандартные курсоры возвращены")
_t("only_win", "Applying cursors works on Windows only. The file was saved to:\n",
   "Применение курсоров работает только в Windows. Файл сохранён сюда:\n")
_t("err", "Error", "Ошибка")
_t("hot", "Hotspot", "Точка клика")
_t("acc_sub", "Create your own animated cursor frame by frame and install it on your PC.",
   "Создайте свой анимированный курсор покадрово и установите его на компьютер.")
_t("tutorial", "?  Tutorial", "?  Обучение")
_t("f_add", "New frame", "Новый кадр")
_t("f_dup", "Duplicate frame", "Дублировать кадр")
_t("f_del", "Delete frame", "Удалить кадр")
_t("f_left", "Move left", "Сдвинуть влево")
_t("f_right", "Move right", "Сдвинуть вправо")
_t("onion", "Onion skin", "Калька (прошлый кадр)")
_t("delay", "Delay, ms", "Задержка, мс")
_t("delay_all", "To all", "Всем")
_t("tut_title", "How to make an animated cursor", "Как сделать анимированный курсор")
_t("tut_next", "Next ▶", "Далее ▶")
_t("tut_back", "◀ Back", "◀ Назад")
_t("tut_skip", "Skip tutorial — I can animate", "Пропустить обучение — я умею")
_t("tut_end", "Let's draw!", "Начать рисовать!")
_t("tut_never", "Don't show again", "Больше не показывать")
_t("tut_step", "Step", "Шаг")
T = [
    ("An animation is a flipbook", "Анимация — это флипбук",
     "An animated cursor is a set of tiny pictures (frames) shown one after another very fast. "
     "Your eyes blend them into motion. You draw the frames, UCCC loops them.",
     "Анимированный курсор — это набор маленьких картинок (кадров), которые быстро сменяют друг друга. "
     "Глаз сливает их в движение. Вы рисуете кадры, а UCCC зацикливает их."),
    ("Draw the first frame", "Нарисуйте первый кадр",
     "Keep it simple: cursors are tiny, so use bold shapes — a circle, a star, an arrow. "
     "Pick a colour on the wheel and draw on the grey canvas. Use the Hotspot tool to mark the exact click point.",
     "Проще — лучше: курсор крошечный, поэтому берите крупные фигуры — круг, звезду, стрелку. "
     "Выберите цвет на колесе и рисуйте на сером холсте. Инструментом «Точка клика» отметьте место нажатия."),
    ("Copy the frame, change it a little", "Скопируйте кадр и слегка измените",
     "Press “Duplicate frame” in the Frames bar, then move or modify the drawing just a bit. "
     "Small steps = smooth motion, big steps = jumpy. Repeat for 4–8 frames.",
     "Нажмите «Дублировать кадр» в панели кадров и чуть-чуть сдвиньте или измените рисунок. "
     "Маленькие шаги — плавное движение, большие — рывки. Повторите для 4–8 кадров."),
    ("Use the onion skin", "Включите «кальку»",
     "Turn on “Onion skin” to see the previous frame as a faint ghost under your drawing. "
     "It shows exactly where the next movement should go.",
     "Включите «Калька», чтобы видеть предыдущий кадр бледной тенью под рисунком. "
     "Так видно, куда именно должно двигаться изображение."),
    ("Set the timing", "Настройте скорость",
     "Every frame has a delay in milliseconds: 100 ms = 10 frames per second. "
     "“To all” gives every frame the same delay. The Preview panel plays your animation live.",
     "У каждого кадра есть задержка в миллисекундах: 100 мс = 10 кадров в секунду. "
     "«Всем» ставит одинаковую задержку на все кадры. Панель просмотра проигрывает анимацию вживую."),
    ("Save and apply", "Сохраните и примените",
     "Choose which Windows pointer to replace and press Apply — your cursor is installed instantly. "
     "Or save a .ani file to share. You can restore the default cursors in one click anytime.",
     "Выберите, какой указатель Windows заменить, и нажмите «Применить» — курсор установится мгновенно. "
     "Или сохраните .ani-файл, чтобы поделиться. Стандартные курсоры возвращаются одним кликом."),
]
for i, (te, tr_, de, dr) in enumerate(T, 1):
    _t(f"tut_{i}_t", te, tr_)
    _t(f"tut_{i}_d", de, dr)
_t("s_title", "Settings", "Настройки")
_t("s_look", "Appearance", "Оформление")
_t("s_lang", "Language", "Язык")
_t("s_theme", "Theme", "Тема")
_t("th_dark", "Dark", "Тёмная")
_t("th_light", "Light", "Светлая")
_t("s_rainbow", "Rainbow bar speed", "Скорость радужной шторки")
_t("s_cur", "Cursor size", "Размер курсора")
_t("s_autofit", "Fit drawing to cursor size", "Подгонять рисунок под размер курсора")
_t("s_autofit_h", "Turn OFF for a giant cursor: draw on a 128 or 256 canvas and it will be saved as is.",
   "ВЫКЛЮЧИТЕ для гигантского курсора: рисуйте на холсте 128 или 256 — он сохранится как есть.")
_t("s_size", "Cursor size (px)", "Размер курсора (px)")
_t("s_tools", "Tools", "Инструменты")
_t("s_folder", "Open cursor folder", "Открыть папку курсоров")
_t("s_tut", "Show tutorial again", "Показать обучение снова")
_t("ab_title", "Ultimate Custom Cursor Creator", "Ultimate Custom Cursor Creator")
_t("ab_text",
   "<p><b>UCCC</b> is a free, open program: everyone can draw their own mouse cursor and install it with one click.</p>"
   "<p>✏️ <b>Draw</b> — static cursors: pen, shapes, fill, eyedropper, colour wheel, hotspot.<br>"
   "🎞️ <b>ACC (Animated Cursor Creator)</b> — frame-by-frame animated cursors with a frame manager, onion skin, "
   "timing, GIF import and a built-in tutorial.<br>"
   "📥 Load PNG / JPG / GIF / ICO and keep editing it.<br>"
   "📐 Drawings are fitted to the cursor size automatically (can be turned off in Settings).<br>"
   "🎨 Make it yours: interface colour, ready-made themes, a gradient theme and a custom animated title bar "
   "with patterns (including Amber).</p>"
   "<p>Portable: no installation. Settings are stored next to the program.</p>",
   "<p><b>UCCC</b> — бесплатная открытая программа: каждый может нарисовать свой курсор мыши и установить его одной кнопкой.</p>"
   "<p>✏️ <b>Рисование</b> — статичные курсоры: карандаш, фигуры, заливка, пипетка, цветовое колесо, точка клика.<br>"
   "🎞️ <b>ACC (Animated Cursor Creator)</b> — покадровые анимированные курсоры: менеджер кадров, калька, "
   "тайминг, импорт GIF и встроенное обучение.<br>"
   "📥 Загружайте PNG / JPG / GIF / ICO и редактируйте их.<br>"
   "📐 Рисунок автоматически подгоняется под размер курсора (отключается в настройках).<br>"
   "🎨 Настройте под себя: цвет интерфейса, готовые темы, градиентная тема и своя анимированная шторка "
   "с узорами (включая «Янтарь»).</p>"
   "<p>Портативная версия: установка не нужна. Настройки хранятся рядом с программой.</p>")
_t("ab_author_t", "A word from the author", "Слово автора")
_t("ab_author",
   "<p>This program was written entirely by an AI. It is completely free and open — there are no limits on how "
   "you use it. UCCC was made purely for free use and was never meant to be a paid product: the idea of a free "
   "program was shaped mostly by the very fact that the code was written by a neural network.</p>"
   "<p>I didn't build it myself, but it is available to everyone, and anyone can use it.</p>"
   "<p>If you're curious about the author anyway, find me on Discord: <b>tutrusik</b></p>",
   "<p>Эта программа полностью написана нейросетью. Она бесплатна и находится в открытом доступе — никаких "
   "ограничений на использование нет. UCCC создан исключительно для свободного использования и даже не "
   "задумывался как платный продукт: на идею бесплатной программы больше всего повлиял сам факт, что код "
   "написан нейросетью.</p>"
   "<p>Делал я её не сам, зато она доступна каждому, и пользоваться ею может кто угодно.</p>"
   "<p>Если вам всё же интересен автор — мой юзернейм в Discord: <b>tutrusik</b></p>")
for k, en, ru in [
    ("th_midnight", "Midnight", "Полночь"), ("th_forest", "Forest", "Лес"), ("th_sunset", "Sunset", "Закат"),
    ("th_sakura", "Sakura", "Сакура"), ("th_mocha", "Mocha", "Мокко"),
    ("th_gradient", "Custom gradient…", "Свой градиент…"),
    ("s_speed", "Animation speed", "Скорость анимации"),
    ("s_accent", "Interface colour", "Цвет интерфейса"),
    ("s_accent_h", "Pick a colour and press Save: buttons, sliders and highlights will follow it.",
     "Выберите цвет и нажмите «Сохранить»: кнопки, ползунки и подсветка перекрасятся."),
    ("btn_save", "Save", "Сохранить"), ("btn_reset", "Reset", "Сбросить"),
    ("btn_save_apply", "Save & apply", "Сохранить и применить"),
    ("s_bar", "Title bar", "Верхняя шторка"), ("bar_rainbow", "Rainbow", "Радуга"),
    ("bar_grad", "Custom gradient", "Свой градиент"), ("s_pattern", "Pattern", "Узор"),
    ("pt_amber", "Amber", "Янтарь"), ("pt_smooth", "Silk", "Шёлк"), ("pt_waves", "Waves", "Волны"),
    ("pt_stripes", "Stripes", "Полосы"),
    ("s_gtheme", "Gradient theme", "Градиентная тема"),
    ("s_gtheme_h", "Pick two colours, choose a pattern and press Save. Until then the theme is not applied.",
     "Выберите два цвета и узор, затем нажмите «Сохранить». Пока вы этого не сделаете, тема не применяется."),
    ("gt_need", "The gradient theme is not set up yet — pick two colours below and press Save.",
     "Градиентная тема ещё не настроена — выберите два цвета ниже и нажмите «Сохранить»."),
    ("col_a", "Colour 1", "Цвет 1"), ("col_b", "Colour 2", "Цвет 2")]:
    _t(k, en, ru)

for k, en, ru in [
    ("nav_lib", "Library", "Библиотека"),
    ("lib_title", "Cursor library", "Библиотека курсоров"),
    ("lib_hint", "Everything you save here stays available: pick a cursor and apply it in one click, even if it is no longer on the canvas.",
     "Всё, что вы сюда сохраните, остаётся доступным: выберите курсор и примените одной кнопкой, даже если его уже нет на холсте."),
    ("lib_empty", "The library is empty. Draw a cursor and press “Save to library”.",
     "Библиотека пуста. Нарисуйте курсор и нажмите «Сохранить в библиотеку»."),
    ("lib_save", "Save to library", "Сохранить в библиотеку"),
    ("lib_name_q", "Cursor name:", "Название курсора:"),
    ("lib_saved", "✔ Saved to library: ", "✔ Сохранено в библиотеку: "),
    ("lib_apply", "▶  Apply this cursor", "▶  Применить этот курсор"),
    ("lib_edit", "Open in editor", "Открыть в редакторе"),
    ("lib_rename", "Rename", "Переименовать"),
    ("lib_export", "Export file…", "Экспортировать файл…"),
    ("lib_delete", "Delete", "Удалить"),
    ("lib_folder", "Open library folder", "Открыть папку библиотеки"),
    ("lib_del_q", "Delete this cursor from the library?", "Удалить этот курсор из библиотеки?"),
    ("lib_count", "Cursors: ", "Курсоров: "),
    ("lib_type_cur", "static", "статичный"), ("lib_type_ani", "animated", "анимированный"),
    ("lib_select", "Select a cursor on the left.", "Выберите курсор слева."),
    ("rs_all", "Reset ALL settings", "Сбросить ВСЕ настройки"),
    ("rs_title", "Reset", "Сброс"),
    ("rs_all_q", "Reset all settings to defaults (theme, colours, title bar, cursor size, language)? Cursors in your library are kept.",
     "Сбросить все настройки по умолчанию (тема, цвета, шторка, размер курсора, язык)? Курсоры из библиотеки сохранятся."),
    ("apply_all", "Apply to ALL pointers", "Применить ко ВСЕМ указателям"),
    ("lib_size", "Cursor size", "Размер курсора"),
    ("lib_resize", "Change size", "Изменить размер"),
    ("lib_resized", "✔ Size changed: ", "✔ Размер изменён: "),
    ("ab_patch_t", "Patch notes · v1.1.1", "Список изменений · v1.1.1"),
    ("ab_patch",
     "<p><b>v1.1.1 — patch</b><br>"
     "<b>Fixed:</b> buttons in the side panels were squeezed and their text cut off when the window was small. "
     "They now adapt to the window size (and the panel scrolls if there is really no room).<br>"
     "<b>Added:</b> cursor library (save static and animated cursors, apply in one click, reopen for editing, "
     "change the size of a saved cursor); “Apply to ALL pointers”; pictures of the real default Windows pointers (all 17 types) in the "
     "list so it is clear what gets replaced; reset buttons for the title bar and the gradient theme; “Reset ALL settings”; "
     "English is now the default language on first launch; this list of changes.</p>"
     "<p><b>v1.1 — personalization</b><br>"
     "Interface colour, ready-made themes, gradient theme, custom animated title bar with patterns (including Amber), "
     "author's note, auto-shrinking button text, faster canvas.</p>",
     "<p><b>v1.1.1 — патч</b><br>"
     "<b>Исправлено:</b> в боковых панелях кнопки сжимались и текст на них обрезался при маленьком окне. "
     "Теперь они подстраиваются под размер окна (а если места совсем нет — панель прокручивается).<br>"
     "<b>Добавлено:</b> библиотека курсоров (сохранение статичных и анимированных курсоров, применение одной кнопкой, "
     "повторное открытие для редактирования, изменение размера сохранённого курсора); «Применить ко ВСЕМ указателям»; "
     "картинки настоящих стандартных указателей Windows (все 17 типов) в списке, чтобы было понятно, что именно заменяется; "
     "кнопки сброса для шторки и градиентной темы; «Сбросить ВСЕ настройки»; "
     "английский теперь язык по умолчанию при первом запуске; этот список изменений.</p>"
     "<p><b>v1.1 — персонализация</b><br>"
     "Цвет интерфейса, готовые темы, градиентная тема, своя анимированная шторка с узорами (включая «Янтарь»), "
     "слово автора, автоуменьшение текста кнопок, более быстрый холст.</p>")]:
    _t(k, en, ru)

# ───────────────────────── themes ─────────────────────────
THEMES = {
    "dark": dict(bg="#0a0a0e", side="#0f0f14", panel="#15151c", panel2="#1d1d26", zone="#23232c",
                 tools="#121218", text="#ececf4", sub="#8d8da0", border="#2c2c38", fborder="#2a2a36",
                 accent="#7c5cff", accent2="#22c3ee", ck1="#34343e", ck2="#3e3e49"),
    "light": dict(bg="#f4f4f9", side="#ffffff", panel="#ffffff", panel2="#ebebf3", zone="#dcdce8",
                  tools="#ffffff", text="#1b1b24", sub="#6d6d7e", border="#cdcddb", fborder="#1b1b24",
                  accent="#6c4cf0", accent2="#0ea5e9", ck1="#ffffff", ck2="#e4e4ee"),
    "midnight": dict(bg="#070b17", side="#0a1022", panel="#0f1730", panel2="#172347", zone="#1a2850",
                     tools="#0c1428", text="#e8eeff", sub="#8fa0c8", border="#26356a", fborder="#1f2d5c",
                     accent="#4f8cff", accent2="#38e0ff", ck1="#2a3560", ck2="#34417a"),
    "forest": dict(bg="#08110c", side="#0b1710", panel="#112419", panel2="#183323", zone="#1d3b2a",
                   tools="#0d1c13", text="#e6f4ea", sub="#86a893", border="#244634", fborder="#1f3d2d",
                   accent="#2fbf71", accent2="#a3e635", ck1="#2c4636", ck2="#36543f"),
    "sunset": dict(bg="#140a0c", side="#1a0d10", panel="#26141a", panel2="#331b22", zone="#3a2028",
                   tools="#1d0f13", text="#ffeee8", sub="#c89a8e", border="#4a262f", fborder="#4a262f",
                   accent="#ff6b57", accent2="#ffb347", ck1="#4a2a31", ck2="#57333b"),
    "sakura": dict(bg="#fff5f8", side="#ffffff", panel="#ffffff", panel2="#ffe6ee", zone="#f7d3df",
                   tools="#ffffff", text="#3a1f2b", sub="#8a6573", border="#efc3d1", fborder="#3a1f2b",
                   accent="#e8508a", accent2="#ff8fb1", ck1="#ffffff", ck2="#fbe1ea"),
    "mocha": dict(bg="#17120e", side="#1d1712", panel="#261e17", panel2="#31271e", zone="#3a2f25",
                  tools="#1b1510", text="#f1e6d8", sub="#a8967f", border="#43362a", fborder="#43362a",
                  accent="#c98b4a", accent2="#e9c46a", ck1="#3d3227", ck2="#483c30"),
}
THEME_KEYS = ["dark", "light", "midnight", "forest", "sunset", "sakura", "mocha", "gradient"]
PAL = {}


def shift_color(c, dh=0, dl=0.0):
    c = QColor(c)
    h, s, l, _ = c.getHslF()
    h = 0.0 if h < 0 else h
    return QColor.fromHslF((h + dh / 360.0) % 1.0, s, min(1.0, max(0.0, l + dl)))


def is_gradient():
    return S.get("theme") == "gradient" and bool(S.get("grad_saved"))


def refresh_palette():
    global PAL
    if is_gradient():
        acc = QColor(S["grad_c2"])
        h, s, l, _ = acc.getHslF()
        acc = QColor.fromHslF(max(h, 0), max(s, .55), min(max(l, .6), .8))
        PAL = dict(bg="#15121c", pop="#1e1a2a", side="#66000000", panel="#8c0b0b12", panel2="#26ffffff",
                   zone="#59000000", tools="#73000000", text="#ffffff", sub="#cfcfdc", border="#40ffffff",
                   fborder="#40ffffff", accent=acc.name(), accent2=shift_color(acc, 40).name(),
                   ck1="#3a3a44", ck2="#454550")
    else:
        PAL = dict(THEMES.get(S.get("theme"), THEMES["dark"]))
        PAL["pop"] = PAL["panel"]
    if S.get("accent"):
        a = QColor(S["accent"])
        PAL["accent"], PAL["accent2"] = a.name(), shift_color(a, 40, .08).name()


def P(k):
    return PAL[k]


def qcol(v):
    """#AARRGGBB -> rgba(...) for stylesheets."""
    if isinstance(v, str) and len(v) == 9 and v[0] == "#":
        return "rgba(%d,%d,%d,%d%%)" % (int(v[3:5], 16), int(v[5:7], 16), int(v[7:9], 16), round(int(v[1:3], 16) / 2.55))
    return v


QSS = """
QWidget{color:@text;font-family:"Segoe UI","Inter",Arial;font-size:13px}
QDialog,QMessageBox{background:@pop}
QFrame#sidebar{background:@side;border-bottom-left-radius:12px;border-right:1px solid @border}
QFrame#zone{background:@zone;border-radius:12px}
QFrame#tools{background:@tools;border:1px solid @border;border-radius:12px}
QFrame#card{background:@panel;border:1px solid @border;border-radius:12px}
QFrame#hdr{background:@panel;border:1px solid @border;border-radius:12px}
QLabel{background:transparent}
QLabel#h1{font-size:20px;font-weight:700}
QLabel#h2{font-size:15px;font-weight:700;color:@accent}
QLabel#sub{color:@sub;font-size:12px}
QPushButton{background:@panel2;border:1px solid @border;border-radius:8px;padding:7px 12px}
QPushButton:hover{border-color:@accent}
QPushButton:pressed{background:@border}
QPushButton#nav{text-align:left;padding:11px 14px;border:none;background:transparent;font-size:14px;border-radius:10px}
QPushButton#nav:hover{background:@panel2}
QPushButton#nav:checked{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 @accent,stop:1 @accent2);color:white;font-weight:700}
QPushButton#primary{border:none;color:white;font-weight:700;font-size:14px;padding:9px 12px;
  background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 @accent,stop:1 @accent2)}
QPushButton#primary:hover{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 @accent2,stop:1 @accent)}
QPushButton#wbtn,QPushButton#wclose{background:transparent;border:none;border-radius:0;color:white;font-size:15px;padding:0}
QPushButton#wbtn:hover{background:rgba(255,255,255,70)}
QPushButton#wclose{border-top-right-radius:12px}
QPushButton#wclose:hover{background:#e81123}
QToolButton{background:@panel2;border:1px solid @border;border-radius:8px;padding:2px}
QToolButton:hover{border-color:@accent}
QToolButton:checked{background:@accent;border-color:@accent2;color:white}
QComboBox,QLineEdit,QSpinBox{background:@panel2;border:1px solid @border;border-radius:8px;padding:5px 8px}
QComboBox:hover,QLineEdit:focus,QSpinBox:focus{border-color:@accent}
QComboBox QAbstractItemView{background:@pop;color:@text;selection-background-color:@accent;border:1px solid @border}
QSlider::groove:horizontal{height:6px;background:@border;border-radius:3px}
QSlider::sub-page:horizontal{background:@accent;border-radius:3px}
QSlider::handle:horizontal{background:@accent2;width:14px;margin:-5px 0;border-radius:7px}
QCheckBox{spacing:7px}
QListWidget#strip{background:transparent;border:none;outline:none}
QListWidget#strip::item{border:2px solid transparent;border-radius:8px;color:@sub}
QListWidget#strip::item:selected{border-color:@accent;background:@panel2;color:@text}
QScrollArea{background:transparent;border:none}
QScrollBar:horizontal{height:10px;background:transparent}
QScrollBar::handle:horizontal{background:@border;border-radius:5px;min-width:30px}
QScrollBar:vertical{width:10px;background:transparent}
QScrollBar::handle:vertical{background:@border;border-radius:5px;min-height:30px}
QScrollBar::add-line,QScrollBar::sub-line{width:0;height:0}
QToolTip{background:@pop;color:@text;border:1px solid @border;padding:4px}
"""


def make_qss():
    q = QSS
    for k in sorted(PAL, key=len, reverse=True):
        q = q.replace("@" + k, qcol(PAL[k]))
    return q


# ───────────────────────── animated patterns ─────────────────────────
def mix(a, b, m):
    return QColor(int(a.red() + (b.red() - a.red()) * m), int(a.green() + (b.green() - a.green()) * m),
                  int(a.blue() + (b.blue() - a.blue()) * m))


def with_alpha(c, a):
    c = QColor(c)
    c.setAlpha(int(max(0, min(255, a))))
    return c


def pattern_t():
    """Animation clock in cycles. Driven by real time, so it always moves."""
    return time.monotonic() / max(1.0, 420.0 / max(5, int(S["rainbow"])))


def wave_stops(g, c1, c2, t, cycles=1.0, n=18):
    for k in range(n + 1):
        s = k / n
        g.setColorAt(s, mix(c1, c2, (1 + math.cos(2 * math.pi * (s * cycles - t))) / 2))


def checker_brush(c1, c2, cell=10):
    pm = QPixmap(cell * 2, cell * 2)
    pm.fill(c1)
    q = QPainter(pm)
    q.fillRect(cell, 0, cell, cell, c2)
    q.fillRect(0, cell, cell, cell, c2)
    q.end()
    return QBrush(pm)


_rr = random.Random(7)
BUBBLES = [(_rr.random(), _rr.random(), _rr.random(), .4 + _rr.random()) for _ in range(22)]


def _waves(p, w, h, c1, c2, t):
    for i in range(3):
        path = QPainterPath()
        path.moveTo(0, h)
        x = 0.0
        while x <= w + 8:
            y = h * (.55 + .12 * i) + h * .16 * math.sin(2 * math.pi * (x / max(w, 1) * (1.3 + .5 * i) + t * (1 + .6 * i) + i / 3))
            path.lineTo(x, y)
            x += 8
        path.lineTo(w, h)
        path.closeSubpath()
        p.fillPath(path, with_alpha(mix(c2, QColor("#ffffff"), .35) if i % 2 == 0 else c1, 70))


def _stripes(p, w, h, c1, c2, t):
    sw = 14.0 if h < 100 else 30.0
    step, slant = sw * 2, h * .6
    x = -step - slant + (t * step * 4) % step
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(255, 255, 255, 38))
    while x < w + step:
        p.drawPolygon(QPolygonF([QPointF(x + slant, 0), QPointF(x + slant + sw, 0), QPointF(x + sw, h), QPointF(x, h)]))
        x += step


def _amber(p, w, h, c1, c2, t):
    """Slowly flowing resin: glowing pockets, dark veins, drifting bubbles, a moving glint."""
    hi, lo = mix(c2, QColor("#ffffff"), .5), mix(c1, QColor("#000000"), .45)
    full = QRectF(0, 0, w, h)
    for i, (fx, fy, fr, sp) in enumerate(((.18, .5, 1.0, 1.0), (.55, .45, 1.3, -.7), (.88, .55, .9, 1.3))):
        cx = w * (fx + .10 * math.sin(2 * math.pi * (t * .5 * sp + i / 3)))
        cy = h * (fy + .28 * math.cos(2 * math.pi * (t * .4 * sp + i / 5)))
        rx, ry = w * .2 * fr + 40, max(h * .8 * fr, 12)
        p.save()
        p.translate(cx, cy)
        p.scale(1, ry / rx)
        rg = QRadialGradient(0, 0, rx)
        rg.setColorAt(0, with_alpha(hi, 150))
        rg.setColorAt(.55, with_alpha(c2, 60))
        rg.setColorAt(1, with_alpha(c2, 0))
        p.fillRect(QRectF(-rx, -rx, 2 * rx, 2 * rx), QBrush(rg))
        p.restore()
    for j in range(3):
        path = QPainterPath()
        x, first = 0.0, True
        while x <= w + 10:
            y = h * (.22 + .28 * j) + h * .13 * math.sin(2 * math.pi * (x / max(w, 1) * (1.1 + .35 * j) + t * (.35 + .15 * j) + j * .3))
            path.moveTo(x, y) if first else path.lineTo(x, y)
            first = False
            x += 10
        p.setPen(QPen(with_alpha(lo, 80), max(1.2, h * .014)))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)
    p.setPen(Qt.PenStyle.NoPen)
    k = 1.0 if h < 100 else 1.7
    for fx, fy, fr, sp in BUBBLES:
        x, y, rad = w * fx, h * ((fy - t * sp * .35) % 1.0), (1.0 + fr * 2.2) * k
        a = 70 + 60 * math.sin(2 * math.pi * (t * sp + fx))
        p.setBrush(with_alpha(hi, a))
        p.drawEllipse(QPointF(x, y), rad, rad)
        p.setBrush(QColor(255, 255, 255, int(min(255, a + 40))))
        p.drawEllipse(QPointF(x - rad * .3, y - rad * .3), rad * .35, rad * .35)
    pos = ((t * .6) % 1.6 - .3) * w
    g = QLinearGradient(pos - w * .1, 0, pos + w * .1, h * .4)
    g.setColorAt(0, QColor(255, 255, 255, 0))
    g.setColorAt(.5, QColor(255, 248, 220, 85))
    g.setColorAt(1, QColor(255, 255, 255, 0))
    p.fillRect(full, QBrush(g))
    d = QLinearGradient(0, 0, 0, h)
    d.setColorAt(0, QColor(0, 0, 0, 60))
    d.setColorAt(.35, QColor(0, 0, 0, 0))
    d.setColorAt(.8, QColor(0, 0, 0, 0))
    d.setColorAt(1, QColor(0, 0, 0, 90))
    p.fillRect(full, QBrush(d))


def paint_pattern(p, r, pat, c1, c2, t):
    """Paint an animated pattern into rect r (caller sets the clip)."""
    p.save()
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.translate(r.x(), r.y())
    w, h = r.width(), r.height()
    full = QRectF(0, 0, w, h)
    if pat == "rainbow":
        g = QLinearGradient(0, 0, w, 0)
        for k in range(13):
            g.setColorAt(k / 12, QColor.fromHslF((k / 12 - t) % 1.0, .85, .56))
        p.fillRect(full, QBrush(g))
    else:
        g = QLinearGradient(0, 0, w, h * .5)
        wave_stops(g, c1, c2, t * (.5 if pat == "amber" else 1.0), .7 if pat == "waves" else 1.0)
        p.fillRect(full, QBrush(g))
        if pat == "waves":
            _waves(p, w, h, c1, c2, t)
        elif pat == "stripes":
            _stripes(p, w, h, c1, c2, t)
        elif pat == "amber":
            _amber(p, w, h, c1, c2, t)
    p.restore()


# ───────────────────────── auto-shrinking text widgets ─────────────────────────
def fit_px(text, width, base, bold, minpx=8):
    f = QFont("Segoe UI")
    f.setBold(bold)
    px = base
    while px > minpx:
        f.setPixelSize(px)
        if QFontMetrics(f).horizontalAdvance(text) <= width:
            break
        px -= 1
    return px


class _Fit:
    def set_h(self, h):
        """Fixed button height that follows the window size; the font follows the height."""
        if h != self._h:
            self._h, self._px = h, 0
            self.setFixedHeight(h)
            self._fit()

    def _fit(self):
        w = self.width()
        if w < 30 or not self.text():
            return
        px = fit_px(self.text(), w - self._pad, self._base, self._bold)
        if self._h:
            px = min(px, max(8, self._h - 11))
        if px != self._px:
            self._px = px
            self.setStyleSheet(f"font-size:{px}px;" + ("padding-top:0px;padding-bottom:0px;" if self._h else ""))


class FitButton(_Fit, QPushButton):
    """Button whose font shrinks so the text always fits."""

    def __init__(self, base=13, pad=28, bold=False, flex=True):
        QPushButton.__init__(self)
        self._base, self._pad, self._bold, self._px, self._h = base, pad, bold, 0, 0
        if flex:
            self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)

    def setText(self, t):
        QPushButton.setText(self, t)
        self._fit()

    def resizeEvent(self, e):
        QPushButton.resizeEvent(self, e)
        self._fit()


class FitCheck(_Fit, QCheckBox):
    def __init__(self, base=13, flex=True):
        QCheckBox.__init__(self)
        self._base, self._pad, self._bold, self._px, self._h = base, 36, False, 0, 0
        if flex:
            self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)

    def setText(self, t):
        QCheckBox.setText(self, t)
        self._fit()

    def resizeEvent(self, e):
        QCheckBox.resizeEvent(self, e)
        self._fit()


def FB(key, name="", base=13, bold=False, flex=True, pad=28):
    b = FitButton(base, pad, bold, flex)
    if name:
        b.setObjectName(name)
    bind(b.setText, key)
    return b


# ───────────────────────── cursor file formats ─────────────────────────
def dib_from_image(img):
    """32-bit BGRA DIB (bottom-up) + empty AND mask, as stored inside .cur files."""
    img = img.convertToFormat(QImage.Format.Format_ARGB32)
    w, h = img.width(), img.height()
    ptr = img.constBits()
    ptr.setsize(img.sizeInBytes())
    raw, bpl = bytes(ptr), img.bytesPerLine()
    rows = [raw[y * bpl:y * bpl + w * 4] for y in range(h)]
    pix = b"".join(reversed(rows))
    hdr = struct.pack("<IiiHHIIiiII", 40, w, h * 2, 1, 32, 0, len(pix), 0, 0, 0, 0)
    mask = b"\0" * (((w + 31) // 32) * 4 * h)
    return hdr + pix + mask


def cur_bytes(dib, w, h, hx, hy):
    entry = struct.pack("<BBBBHHII", w % 256, h % 256, 0, 0, hx, hy, len(dib), 22)
    return struct.pack("<HHH", 0, 2, 1) + entry + dib


def _chunk(tag, data):
    return tag + struct.pack("<I", len(data)) + data + (b"\0" if len(data) % 2 else b"")


def ani_bytes(curs, delays_ms):
    n = len(curs)
    jif = [max(1, round(d * 60 / 1000)) for d in delays_ms]          # 1 jiffy = 1/60 s
    anih = struct.pack("<9I", 36, n, n, 0, 0, 0, 1, jif[0], 1)        # AF_ICON
    rate = struct.pack("<%dI" % n, *jif)
    frames = b"fram" + b"".join(_chunk(b"icon", c) for c in curs)
    body = b"ACON" + _chunk(b"anih", anih) + _chunk(b"rate", rate) + _chunk(b"LIST", frames)
    return b"RIFF" + struct.pack("<I", len(body)) + body


ROLES = ["Arrow", "Help", "AppStarting", "Wait", "Crosshair", "IBeam", "NWPen", "No", "SizeNS", "SizeWE",
         "SizeNWSE", "SizeNESW", "SizeAll", "UpArrow", "Hand", "Pin", "Person"]
ALL_REG_ROLES = list(ROLES)


def win_apply(path, role):
    import winreg, ctypes
    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, r"Control Panel\Cursors", 0,
                            winreg.KEY_ALL_ACCESS) as k:
        for r in ([role] if isinstance(role, str) else role):
            winreg.SetValueEx(k, r, 0, winreg.REG_EXPAND_SZ, str(path))
    ctypes.windll.user32.SystemParametersInfoW(0x0057, 0, None, 0)    # SPI_SETCURSORS


def win_restore():
    import winreg, ctypes
    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, r"Control Panel\Cursors", 0,
                            winreg.KEY_ALL_ACCESS) as k:
        for r in ALL_REG_ROLES:
            winreg.SetValueEx(k, r, 0, winreg.REG_EXPAND_SZ, "")
    ctypes.windll.user32.SystemParametersInfoW(0x0057, 0, None, 0)


# ───────────────────────── cursor library & installing ─────────────────────────
def install_cursor(data, ext, role):
    """Write cursor bytes into the cursor folder and register them in Windows. Returns (installed, path)."""
    CURSOR_DIR.mkdir(parents=True, exist_ok=True)
    for old in CURSOR_DIR.glob(f"uccc_{role}_*"):
        try:
            old.unlink()
        except OSError:
            pass
    path = CURSOR_DIR / f"uccc_{role}_{int(time.time())}{ext}"
    path.write_bytes(data)
    if os.name != "nt":
        return False, path
    win_apply(path, ALL_REG_ROLES if role == "ALL" else role)
    return True, path


_LIB = None


def lib_dir():
    """Portable library folder next to the program (falls back to %APPDATA% if not writable)."""
    global _LIB
    if _LIB:
        return _LIB
    for base in (APP_DIR / "uccc_library", Path(os.environ.get("APPDATA", str(Path.home()))) / "UCCC" / "library"):
        try:
            base.mkdir(parents=True, exist_ok=True)
            t = base / ".w"
            t.write_text("1")
            t.unlink()
            _LIB = base
            return base
        except OSError:
            continue
    raise OSError("No writable folder for the library")


def img_to_b64(img):
    ba = QByteArray()
    buf = QBuffer(ba)
    buf.open(QIODevice.OpenModeFlag.WriteOnly)
    img.save(buf, "PNG")
    buf.close()
    return base64.b64encode(bytes(ba.data())).decode("ascii")


def img_from_b64(s):
    im = QImage()
    im.loadFromData(base64.b64decode(s), "PNG")
    return im


def lib_list():
    d, out = lib_dir(), []
    for f in d.glob("*.json"):
        try:
            m = json.loads(f.read_text("utf-8"))
            if (d / (m["id"] + m["ext"])).exists():
                out.append(m)
        except Exception:
            pass
    out.sort(key=lambda m: m.get("created", ""), reverse=True)
    return out


def lib_add(name, data, ext, size, hot, chot, delays, frames, n, thumb):
    d = lib_dir()
    cid = time.strftime("%Y%m%d-%H%M%S") + "-%04d" % random.randint(0, 9999)
    (d / (cid + ext)).write_bytes(data)
    (d / (cid + ".proj")).write_text(json.dumps({"frames": [img_to_b64(f) for f in frames]}), "utf-8")
    thumb = small_thumb(thumb)
    meta = dict(id=cid, name=name, ext=ext, size=size, hot=list(hot), chot=list(chot), count=len(frames),
                delays=list(delays), n=n, created=time.strftime("%Y-%m-%d %H:%M:%S"), thumb=img_to_b64(thumb))
    lib_save_meta(meta)
    return meta


def lib_save_meta(m):
    (lib_dir() / (m["id"] + ".json")).write_text(json.dumps(m, ensure_ascii=False), "utf-8")


def lib_delete(m):
    for ext in (m["ext"], ".proj", ".json"):
        try:
            (lib_dir() / (m["id"] + ext)).unlink()
        except OSError:
            pass


def lib_frames(m):
    proj = json.loads((lib_dir() / (m["id"] + ".proj")).read_text("utf-8"))
    return [img_from_b64(s) for s in proj["frames"]]


def thumb_pixmap(img, side=72):
    pm = QPixmap(side, side)
    p = QPainter(pm)
    p.fillRect(pm.rect(), checker_brush(QColor(P("ck1")), QColor(P("ck2")), 8))
    mode = Qt.TransformationMode.FastTransformation if max(img.width(), img.height()) * 2 <= side \
        else Qt.TransformationMode.SmoothTransformation
    s = img.scaled(side - 8, side - 8, Qt.AspectRatioMode.KeepAspectRatio, mode)
    p.drawImage((side - s.width()) // 2, (side - s.height()) // 2, s)
    p.end()
    return pm


def small_thumb(img):
    if max(img.width(), img.height()) > 96:
        return img.scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    return img


def render_cursor(frames, delays, n, chot, size):
    """Re-render project frames (drawn on an n x n canvas) into a cursor file of the given size."""
    mode = Qt.TransformationMode.FastTransformation if (size > n and size % n == 0) \
        else Qt.TransformationMode.SmoothTransformation
    imgs = []
    for f in frames:
        f = f.convertToFormat(QImage.Format.Format_ARGB32)
        if f.width() != size:
            f = f.scaled(size, size, Qt.AspectRatioMode.IgnoreAspectRatio, mode)
        imgs.append(f)
    k = size / n
    hot = (min(size - 1, int((chot[0] + .5) * k)), min(size - 1, int((chot[1] + .5) * k)))
    curs = [cur_bytes(dib_from_image(i), size, size, *hot) for i in imgs]
    if len(curs) > 1:
        return ani_bytes(curs, list(delays)), ".ani", imgs, hot
    return curs[0], ".cur", imgs, hot


def adapt_column(sa, pv, btns, other=175):
    """Fit a side column to the window: button height (and preview size) follow the free space."""
    avail = sa.viewport().height()
    pvh = 112 if avail >= 600 else 84
    pv.setFixedHeight(pvh)
    bh = int((avail - pvh - other) / max(1, len(btns)))
    bh = max(24, min(38, bh))
    for b in btns:
        b.set_h(bh)


def _arc(cx, cy, r, a0, a1, n=6):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def hand_points():
    """Outline of the classic 'pointing hand' pointer on a 28x28 grid."""
    pts = [(10.0, 14.5), (10.0, 4.6)]
    pts += _arc(12.2, 4.6, 2.2, 180, 360)              # index fingertip
    pts += [(14.4, 10.2)]
    pts += _arc(16.1, 10.6, 1.7, 215, 360, 4)[1:]      # middle finger
    pts += [(17.8, 11.6)]
    pts += _arc(19.5, 11.9, 1.7, 200, 360, 4)[1:]      # ring finger
    pts += [(21.2, 12.8)]
    pts += _arc(22.9, 13.2, 1.7, 200, 360, 4)[1:]      # little finger
    pts += [(24.6, 19.0), (23.0, 23.0), (22.2, 25.6), (11.6, 25.6), (10.6, 23.6), (7.0, 19.0)]
    pts += _arc(6.2, 16.6, 1.5, 70, 250, 5)[1:]        # thumb
    pts += [(8.2, 15.0), (10.0, 17.4)]
    return pts


def role_icon_drawn(role, s=28):
    """Small picture of the default Windows pointer that this role replaces."""
    pm = QPixmap(s, s)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    blk, wht = QColor("#111111"), QColor("#ffffff")
    solid, rnd = Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap

    def poly(pts):
        pa = QPainterPath()
        pa.addPolygon(QPolygonF([QPointF(*q) for q in pts]))
        pa.closeSubpath()
        return pa

    def shape(path, fill=wht):
        p.setPen(QPen(blk, 1.6, solid, rnd, Qt.PenJoinStyle.RoundJoin))
        p.setBrush(fill)
        p.drawPath(path)

    def lines(segs, w=1.8):
        for col, wd in ((blk, w + 2.6), (wht, w)):
            p.setPen(QPen(col, wd, solid, rnd))
            for a, b in segs:
                p.drawLine(QPointF(*a), QPointF(*b))

    arrow = [(6, 3), (6, 22), (11, 17.5), (14.5, 25), (17.5, 23.5), (14, 16.5), (20.5, 16.5)]
    if role == "Arrow":
        shape(poly(arrow))
    elif role == "Help":
        p.save()
        p.translate(1, 1)
        p.scale(.78, .78)
        shape(poly(arrow))
        p.restore()
        f = QFont("Segoe UI")
        f.setPixelSize(14)
        f.setBold(True)
        p.setFont(f)
        p.setPen(blk)
        p.drawText(QRectF(14, 9, 14, 17), Qt.AlignmentFlag.AlignCenter, "?")
    elif role == "AppStarting":
        p.save()
        p.translate(1, 0)
        p.scale(.85, .85)
        shape(poly(arrow))
        p.restore()
        c = QPainterPath()
        c.addEllipse(QPointF(21.5, 21.5), 4.2, 4.2)
        shape(c)
    elif role == "Hand":
        shape(poly(hand_points()))
    elif role == "IBeam":
        lines([((14, 5), (14, 23)), ((10.5, 5), (17.5, 5)), ((10.5, 23), (17.5, 23))])
    elif role == "Crosshair":
        lines([((14, 3), (14, 11)), ((14, 17), (14, 25)), ((3, 14), (11, 14)), ((17, 14), (25, 14))])
    elif role == "Wait":
        shape(poly([(8, 4), (20, 4), (14, 13.5)]))
        shape(poly([(14, 14.5), (8, 24), (20, 24)]))
        lines([((7, 4), (21, 4)), ((7, 24), (21, 24))])
    elif role == "No":
        p.setPen(QPen(blk, 3, solid, rnd))
        p.setBrush(wht)
        p.drawEllipse(QPointF(14, 14), 8.5, 8.5)
        p.drawLine(QPointF(8, 20), QPointF(20, 8))
    elif role == "SizeAll":
        lines([((14, 5), (14, 23)), ((5, 14), (23, 14))])
        for tri in ([(14, 2), (10.5, 7), (17.5, 7)], [(14, 26), (10.5, 21), (17.5, 21)],
                    [(2, 14), (7, 10.5), (7, 17.5)], [(26, 14), (21, 10.5), (21, 17.5)]):
            shape(poly(tri))
    elif role in ("SizeNS", "SizeWE", "SizeNWSE", "SizeNESW"):
        p.translate(14, 14)
        p.rotate({"SizeNS": 90, "SizeWE": 0, "SizeNWSE": 45, "SizeNESW": -45}[role])
        lines([((-9, 0), (9, 0))])
        for tri in ([(-12, 0), (-7, -3.5), (-7, 3.5)], [(12, 0), (7, -3.5), (7, 3.5)]):
            shape(poly(tri))
    elif role == "UpArrow":
        shape(poly([(14, 3), (21, 12), (16.5, 12), (16.5, 25), (11.5, 25), (11.5, 12), (7, 12)]))
    else:                                              # NWPen, Pin, Person: plain arrow as a fallback
        shape(poly(arrow))
    p.end()
    return pm


# Real Windows pointers: files of the default scheme + built-in system cursors (OEM ids).
CURSOR_FILES = dict(Arrow="aero_arrow.cur", Help="aero_helpsel.cur", AppStarting="aero_working.ani",
                    Wait="aero_busy.ani", NWPen="aero_pen.cur", No="aero_unavail.cur", SizeNS="aero_ns.cur",
                    SizeWE="aero_ew.cur", SizeNWSE="aero_nwse.cur", SizeNESW="aero_nesw.cur",
                    SizeAll="aero_move.cur", UpArrow="aero_up.cur", Hand="aero_link.cur",
                    Pin="aero_pin.cur", Person="aero_person.cur")
OEM_IDS = dict(Arrow=32512, IBeam=32513, Wait=32514, Crosshair=32515, UpArrow=32516, NWPen=32631,
               SizeNWSE=32642, SizeNESW=32643, SizeWE=32644, SizeNS=32645, SizeAll=32646, No=32648,
               Hand=32649, AppStarting=32650, Help=32651, Pin=32671, Person=32672)
_SYS_CACHE = {}


def bgra_from_black_white(blk, wht):
    """Recover straight-alpha BGRA from the same cursor drawn on a black and on a white background."""
    n = len(blk)
    out = bytearray(n)
    for i in range(0, n, 4):
        bb, bg, br = blk[i], blk[i + 1], blk[i + 2]
        a = 255 - ((wht[i] - bb) + (wht[i + 1] - bg) + (wht[i + 2] - br)) // 3
        a = max(0, min(255, a))
        if a:
            out[i], out[i + 1], out[i + 2] = min(255, bb * 255 // a), min(255, bg * 255 // a), min(255, br * 255 // a)
        out[i + 3] = a
    return bytes(out)


def _win_cursor(role, size):
    import ctypes
    c = ctypes
    u32, g32 = c.windll.user32, c.windll.gdi32
    V = c.c_void_p
    u32.LoadImageW.argtypes, u32.LoadImageW.restype = [V, V, c.c_uint, c.c_int, c.c_int, c.c_uint], V
    u32.DrawIconEx.argtypes = [V, c.c_int, c.c_int, V, c.c_int, c.c_int, c.c_uint, V, c.c_uint]
    u32.GetDC.argtypes, u32.GetDC.restype = [V], V
    u32.ReleaseDC.argtypes = [V, V]
    u32.DestroyCursor.argtypes = [V]
    g32.CreateCompatibleDC.argtypes, g32.CreateCompatibleDC.restype = [V], V
    g32.CreateDIBSection.argtypes = [V, V, c.c_uint, c.POINTER(V), V, c.c_uint]
    g32.CreateDIBSection.restype = V
    g32.SelectObject.argtypes, g32.SelectObject.restype = [V, V], V
    g32.DeleteObject.argtypes = [V]
    g32.DeleteDC.argtypes = [V]

    class BIH(c.Structure):
        _fields_ = [("biSize", c.c_uint32), ("biWidth", c.c_int32), ("biHeight", c.c_int32),
                    ("biPlanes", c.c_uint16), ("biBitCount", c.c_uint16), ("biCompression", c.c_uint32),
                    ("biSizeImage", c.c_uint32), ("biXPelsPerMeter", c.c_int32), ("biYPelsPerMeter", c.c_int32),
                    ("biClrUsed", c.c_uint32), ("biClrImportant", c.c_uint32)]

    fn = CURSOR_FILES.get(role)
    path = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "Cursors" / fn if fn else None
    own = bool(path and path.exists())
    if own:
        h = u32.LoadImageW(None, str(path), 2, size, size, 0x10)       # IMAGE_CURSOR, LR_LOADFROMFILE
    else:
        h = u32.LoadImageW(None, OEM_IDS[role], 2, size, size, 0x8000)  # built-in cursor, LR_SHARED
    if not h:
        return None
    bmi = BIH(c.sizeof(BIH), size, -size, 1, 32, 0, 0, 0, 0, 0, 0)
    sdc = u32.GetDC(None)
    dc = g32.CreateCompatibleDC(sdc)
    bits = V()
    bmp = g32.CreateDIBSection(dc, c.byref(bmi), 0, c.byref(bits), None, 0)
    old = g32.SelectObject(dc, bmp)
    n, shots = size * size * 4, []
    for fill in (0x00, 0xFF):
        c.memset(bits, fill, n)
        u32.DrawIconEx(dc, 0, 0, h, size, size, 0, None, 3)           # DI_NORMAL
        shots.append(c.string_at(bits, n))
    g32.SelectObject(dc, old)
    g32.DeleteObject(bmp)
    g32.DeleteDC(dc)
    u32.ReleaseDC(None, sdc)
    if own:
        u32.DestroyCursor(h)
    data = bgra_from_black_white(*shots)
    return QImage(data, size, size, size * 4, QImage.Format.Format_ARGB32).copy()


def system_cursor_image(role, size=32):
    if os.name != "nt":
        return None
    if role not in _SYS_CACHE:
        try:
            _SYS_CACHE[role] = _win_cursor(role, size)
        except Exception:
            _SYS_CACHE[role] = None
    return _SYS_CACHE[role]


def role_icon(role, s=28):
    """Picture of the real Windows pointer this role replaces (hand-drawn fallback if unavailable)."""
    img = system_cursor_image(role)
    if img is not None and not img.isNull():
        return QPixmap.fromImage(img.scaled(s, s, Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation))
    return role_icon_drawn(role, s)


# ───────────────────────── geometry & icons ─────────────────────────
SHAPES = ["rect", "rrect", "ellipse", "triangle", "diamond", "star", "hexagon", "arrow", "heart"]
TOOLS = ["pen", "eraser", "fill", "picker", "hotspot", "line"] + SHAPES


def shape_path(kind, r):
    def pt(fx, fy):
        return QPointF(r.x() + fx * r.width(), r.y() + fy * r.height())
    p = QPainterPath()
    if kind == "rect":
        p.addRect(r)
    elif kind == "rrect":
        p.addRoundedRect(r, r.width() * .22, r.height() * .22)
    elif kind == "ellipse":
        p.addEllipse(r)
    elif kind in ("triangle", "diamond", "arrow"):
        pts = {"triangle": [(.5, 0), (1, 1), (0, 1)],
               "diamond": [(.5, 0), (1, .5), (.5, 1), (0, .5)],
               "arrow": [(0, .35), (.55, .35), (.55, .08), (1, .5), (.55, .92), (.55, .65), (0, .65)]}[kind]
        p.addPolygon(QPolygonF([pt(*q) for q in pts]))
        p.closeSubpath()
    elif kind == "hexagon":
        p.addPolygon(QPolygonF([pt(.25, 0), pt(.75, 0), pt(1, .5), pt(.75, 1), pt(.25, 1), pt(0, .5)]))
        p.closeSubpath()
    elif kind == "star":
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            rr = .5 if i % 2 == 0 else .21
            pts.append(pt(.5 + rr * math.cos(a), .5 + rr * math.sin(a)))
        p.addPolygon(QPolygonF(pts))
        p.closeSubpath()
    elif kind == "heart":
        p.moveTo(pt(.5, .93))
        p.cubicTo(pt(-.12, .5), pt(.08, -.02), pt(.5, .26))
        p.cubicTo(pt(.92, -.02), pt(1.12, .5), pt(.5, .93))
    return p


def tool_icon(tid, col):
    pm = QPixmap(28, 28)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    c = QColor(col)
    p.setPen(QPen(c, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    p.setBrush(Qt.BrushStyle.NoBrush)
    if tid in SHAPES:
        p.drawPath(shape_path(tid, QRectF(5, 5, 18, 18)))
    elif tid == "line":
        p.drawLine(5, 23, 23, 5)
    elif tid == "pen":
        p.setPen(QPen(c, 5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap))
        p.drawLine(10, 18, 21, 7)
        p.setPen(QPen(c, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawLine(5, 23, 9, 19)
    elif tid == "eraser":
        p.translate(14, 14)
        p.rotate(-35)
        p.drawRoundedRect(QRectF(-10, -5, 20, 10), 2, 2)
        p.drawLine(-2, -5, -2, 5)
    elif tid == "fill":
        p.drawPolygon(QPolygonF([QPointF(13, 4), QPointF(22, 13), QPointF(13, 22), QPointF(4, 13)]))
        p.setBrush(c)
        p.drawEllipse(QPointF(23, 22), 2.5, 2.5)
    elif tid == "picker":
        p.drawLine(5, 23, 15, 13)
        p.drawEllipse(QPointF(19, 9), 4.5, 4.5)
    elif tid == "hotspot":
        p.drawEllipse(QPointF(14, 14), 6, 6)
        p.drawLine(14, 3, 14, 25)
        p.drawLine(3, 14, 25, 14)
    p.end()
    return pm


def arrow_path():
    pts = [(14, 12), (14, 50), (24, 41), (31, 56), (38, 53), (31, 38), (44, 38)]
    path = QPainterPath()
    path.addPolygon(QPolygonF([QPointF(*q) for q in pts]))
    path.closeSubpath()
    return path


def logo_grad(x0, x1):
    g = QLinearGradient(x0, 0, x1, 0)
    g.setColorAt(0, QColor("#a78bfa"))
    g.setColorAt(.5, QColor("#22d3ee"))
    g.setColorAt(1, QColor("#34d399"))
    return g


def app_icon():
    pm = QPixmap(256, 256)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.scale(4, 4)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#14141a"))
    p.drawRoundedRect(0, 0, 64, 64, 14, 14)
    p.translate(11, 4)
    p.scale(.88, .88)
    p.setBrush(QBrush(logo_grad(10, 46)))
    p.drawPath(arrow_path())
    p.end()
    return QIcon(pm)


# ───────────────────────── custom widgets ─────────────────────────
class Logo(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(84)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        g = logo_grad(0, self.width())
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(g))
        p.drawPath(arrow_path())
        f = QFont("Segoe UI", 21)
        f.setWeight(QFont.Weight.ExtraBold)
        p.setFont(f)
        p.setPen(QPen(QBrush(g), 1))
        p.drawText(QRectF(54, 6, self.width() - 56, 40), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, "UCCC")
        f2 = QFont("Segoe UI", 8)
        p.setFont(f2)
        p.setPen(QColor(P("sub")))
        p.drawText(QRectF(56, 42, self.width() - 58, 34), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
                   "Ultimate Custom\nCursor Creator")


class TitleBar(QWidget):
    """Animated title bar (rainbow or custom gradient pattern) running under the window buttons."""
    TITLE = "UCCC   ·   Ultimate Custom Cursor Creator   ·   v1.1.1"

    def __init__(self, win):
        super().__init__()
        self.win = win
        self.setFixedHeight(34)
        h = QHBoxLayout(self)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)
        h.addStretch()
        for txt, name, fn in (("—", "wbtn", win.showMinimized), ("☐", "wbtn", self.toggle), ("✕", "wclose", win.close)):
            b = QPushButton(txt)
            b.setObjectName(name)
            b.setFixedSize(48, 34)
            b.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            b.clicked.connect(fn)
            h.addWidget(b)
        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self.tick)
        self.timer.start(33)

    def toggle(self):
        self.win.showNormal() if self.win.isMaximized() else self.win.showMaximized()

    def tick(self):
        self.repaint()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, w, h + 20), 12, 12)
        p.setClipRect(0, 0, w, h)
        p.setClipPath(path, Qt.ClipOperation.IntersectClip)
        if S.get("bar_mode") == "gradient":
            paint_pattern(p, QRectF(0, 0, w, h), S["bar_pattern"], QColor(S["bar_c1"]), QColor(S["bar_c2"]), pattern_t())
        else:
            paint_pattern(p, QRectF(0, 0, w, h), "rainbow", QColor(), QColor(), pattern_t())
        p.setClipping(False)
        f = QFont("Segoe UI")
        f.setPixelSize(13)
        f.setBold(True)
        p.setFont(f)
        flags = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
        r = QRectF(14, 0, max(10, w - 170), h)
        p.setPen(QColor(0, 0, 0, 150))
        p.drawText(r.translated(0, 1), flags, self.TITLE)
        p.setPen(QColor("white"))
        p.drawText(r, flags, self.TITLE)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton and self.window().windowHandle():
            self.window().windowHandle().startSystemMove()

    def mouseDoubleClickEvent(self, e):
        self.toggle()


class ColorWheel(QWidget):
    changed = pyqtSignal(QColor)
    R, W, C = 84, 16, 88

    def __init__(self):
        super().__init__()
        self.setFixedSize(176, 176)
        self.h = self.s = self.v = 0.0
        self.mode = None
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def color(self):
        return QColor.fromHsvF(self.h, self.s, self.v)

    def setColor(self, c):
        h, s, v, _ = c.getHsvF()
        if h >= 0:
            self.h = h
        self.s, self.v = s, v
        self.update()

    def sq(self):
        return QRectF(self.C - 46, self.C - 46, 92, 92)

    def _marker(self, p, m):
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(QColor("white"), 2))
        p.drawEllipse(m, 6, 6)
        p.setPen(QPen(QColor("black"), 1))
        p.drawEllipse(m, 7.5, 7.5)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = QPointF(self.C, self.C)
        g = QConicalGradient(c, 0)
        for i in range(7):
            g.setColorAt(i / 6, QColor.fromHsvF((i % 6) / 6, 1, 1))
        rm = self.R - self.W / 2
        p.setPen(QPen(QBrush(g), self.W))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(c, rm, rm)
        a = self.h * 2 * math.pi
        self._marker(p, QPointF(self.C + rm * math.cos(a), self.C - rm * math.sin(a)))
        sq = self.sq()
        p.setPen(Qt.PenStyle.NoPen)
        p.fillRect(sq, QColor.fromHsvF(self.h, 1, 1))
        g1 = QLinearGradient(sq.left(), 0, sq.right(), 0)
        g1.setColorAt(0, QColor(255, 255, 255, 255))
        g1.setColorAt(1, QColor(255, 255, 255, 0))
        p.fillRect(sq, QBrush(g1))
        g2 = QLinearGradient(0, sq.top(), 0, sq.bottom())
        g2.setColorAt(0, QColor(0, 0, 0, 0))
        g2.setColorAt(1, QColor(0, 0, 0, 255))
        p.fillRect(sq, QBrush(g2))
        self._marker(p, QPointF(sq.left() + self.s * sq.width(), sq.top() + (1 - self.v) * sq.height()))

    def _pos(self, pt):
        if self.mode == "ring":
            self.h = (math.atan2(-(pt.y() - self.C), pt.x() - self.C) / (2 * math.pi)) % 1.0
        else:
            sq = self.sq()
            self.s = min(1.0, max(0.0, (pt.x() - sq.left()) / sq.width()))
            self.v = 1 - min(1.0, max(0.0, (pt.y() - sq.top()) / sq.height()))
        self.update()
        self.changed.emit(self.color())

    def mousePressEvent(self, e):
        pt = e.position()
        self.mode = "ring" if math.hypot(pt.x() - self.C, pt.y() - self.C) > 66 else "sq"
        self._pos(pt)

    def mouseMoveEvent(self, e):
        if self.mode and e.buttons() & Qt.MouseButton.LeftButton:
            self._pos(e.position())

    def mouseReleaseEvent(self, e):
        self.mode = None


class Swatch(QPushButton):
    def __init__(self, c):
        super().__init__()
        self.setCheckable(True)
        self.setFixedSize(42, 30)
        self.c = QColor(c)

    def set_color(self, c):
        self.c = QColor(c)
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        r = QRectF(3, 3, self.width() - 6, self.height() - 6)
        p.fillRect(r, QColor(P("ck1")))
        p.fillRect(QRectF(r.x(), r.y(), r.width() / 2, r.height() / 2), QColor(P("ck2")))
        p.fillRect(QRectF(r.x() + r.width() / 2, r.y() + r.height() / 2, r.width() / 2, r.height() / 2), QColor(P("ck2")))
        p.fillRect(r, self.c)
        p.setPen(QPen(QColor(P("accent") if self.isChecked() else P("border")), 3 if self.isChecked() else 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(r, 4, 4)


class PreviewBox(QWidget):
    """Shows the cursor at its real size (animated if it has frames) and acts as a test zone."""

    def __init__(self):
        super().__init__()
        self.setFixedSize(176, 112)
        self.pix, self.delays, self.i = [], [], 0
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.step)

    def set_frames(self, imgs, delays, hot):
        self.timer.stop()
        self.pix = [QPixmap.fromImage(i) for i in imgs]
        self.delays, self.i = delays, 0
        if self.pix:
            pm = self.pix[0]
            hx, hy = hot
            if max(pm.width(), pm.height()) > 128:
                k = 128 / max(pm.width(), pm.height())
                pm = pm.scaled(int(pm.width() * k), int(pm.height() * k), Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
                hx, hy = int(hx * k), int(hy * k)
            self.setCursor(QCursor(pm, hx, hy))
            if len(self.pix) > 1:
                self.timer.start(max(20, delays[0]))
        self.update()

    def step(self):
        self.i = (self.i + 1) % len(self.pix)
        self.timer.start(max(20, self.delays[self.i]))
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        r = QRectF(0, 0, self.width(), self.height())
        path = QPainterPath()
        path.addRoundedRect(r.adjusted(1, 1, -1, -1), 10, 10)
        p.setClipPath(path)
        p.fillRect(self.rect(), checker_brush(QColor(P("ck1")), QColor(P("ck2")), 8))
        if self.pix:
            pm = self.pix[self.i]
            lim = max(40, min(self.width(), self.height()) - 12)
            if max(pm.width(), pm.height()) > lim:
                pm = pm.scaled(lim, lim, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            p.drawPixmap((self.width() - pm.width()) // 2, (self.height() - pm.height()) // 2, pm)
        p.setClipping(False)
        p.setPen(QPen(QColor(P("border")), 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)


class AnimDemo(QWidget):
    """Tiny looping bouncing-ball demo used in the tutorial."""

    def __init__(self):
        super().__init__()
        self.setFixedHeight(130)
        self.k = 0
        t = QTimer(self)
        t.timeout.connect(self.tick)
        t.start(450)

    def tick(self):
        self.k = (self.k + 1) % 5
        self.update()

    def ball(self, p, r, k):
        u = k / 4
        hg = 4 * u * (1 - u)
        cx, cy, rad = r.x() + r.width() * (.15 + .7 * u), r.y() + r.height() * (.82 - .6 * hg), r.width() * .1
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#ff2d92"))
        p.drawEllipse(QPointF(cx, cy), rad, rad)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        tile, gap = 70, 10
        total = 5 * tile + 4 * gap + 120
        x0, y0 = (self.width() - total) / 2, (self.height() - tile) / 2
        for k in range(5):
            r = QRectF(x0 + k * (tile + gap), y0, tile, tile)
            on = k == self.k
            p.setPen(QPen(QColor(P("accent") if on else P("border")), 3 if on else 1))
            p.setBrush(QColor(P("panel2")))
            p.drawRoundedRect(r, 8, 8)
            self.ball(p, r, k)
        big = QRectF(x0 + 5 * (tile + gap) + 20, y0 - 15, 100, 100)
        p.setPen(QPen(QColor(P("accent2")), 2))
        p.setBrush(QColor(P("panel2")))
        p.drawRoundedRect(big, 10, 10)
        self.ball(p, big, self.k)


# ───────────────────────── drawing canvas ─────────────────────────
class Canvas(QWidget):
    modified = pyqtSignal()
    framesChanged = pyqtSignal()
    curChanged = pyqtSignal()
    colorPicked = pyqtSignal(QColor, bool)
    colorUsed = pyqtSignal(QColor)
    posChanged = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        self.setMinimumSize(200, 150)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.n = 64
        self.frames = [self.blank()]
        self.delays = [100]
        self.cur = 0
        self.hot = (0, 0)
        self.tool, self.size, self.mode = "pen", 3, "outline"
        self.c1, self.c2 = QColor("#000000"), QColor("#ffffff")
        self.grid, self.smooth, self.onion = S["grid"], S["smooth"], False
        self.undo_s, self.redo_s = [], []
        self.drawing, self.temp, self.base = False, None, None
        self.btn, self.start, self.last = None, (0, 0), (0, 0)

    # ---- state ----
    def blank(self, n=None):
        n = n or self.n
        im = QImage(n, n, QImage.Format.Format_ARGB32_Premultiplied)
        im.fill(Qt.GlobalColor.transparent)
        return im

    def snap(self):
        return ([f.copy() for f in self.frames], list(self.delays), self.cur, self.hot, self.n)

    def restore(self, s):
        self.frames, self.delays = [f.copy() for f in s[0]], list(s[1])
        self.cur, self.hot, self.n = s[2], s[3], s[4]
        self._changed(True)

    def push(self):
        self.undo_s.append(self.snap())
        del self.undo_s[:-30]
        self.redo_s.clear()

    def undo(self):
        if self.undo_s:
            self.redo_s.append(self.snap())
            self.restore(self.undo_s.pop())

    def redo(self):
        if self.redo_s:
            self.undo_s.append(self.snap())
            self.restore(self.redo_s.pop())

    def _changed(self, structure=False):
        self.update()
        if structure:
            self.framesChanged.emit()
        self.modified.emit()

    # ---- frame management ----
    def add_frame(self):
        self.push()
        self.frames.insert(self.cur + 1, self.blank())
        self.delays.insert(self.cur + 1, self.delays[self.cur])
        self.cur += 1
        self._changed(True)

    def dup_frame(self):
        self.push()
        self.frames.insert(self.cur + 1, self.frames[self.cur].copy())
        self.delays.insert(self.cur + 1, self.delays[self.cur])
        self.cur += 1
        self._changed(True)

    def del_frame(self):
        if len(self.frames) > 1:
            self.push()
            del self.frames[self.cur], self.delays[self.cur]
            self.cur = min(self.cur, len(self.frames) - 1)
            self._changed(True)

    def move_frame(self, d):
        j = self.cur + d
        if 0 <= j < len(self.frames):
            self.push()
            for L in (self.frames, self.delays):
                L[self.cur], L[j] = L[j], L[self.cur]
            self.cur = j
            self._changed(True)

    def set_cur(self, i):
        if 0 <= i < len(self.frames) and i != self.cur:
            self.cur = i
            self.update()
            self.curChanged.emit()

    # ---- whole-image operations ----
    def clear(self):
        self.push()
        self.frames[self.cur].fill(Qt.GlobalColor.transparent)
        self._changed()

    def flip(self, h, v):
        self.push()
        self.frames[self.cur] = self.frames[self.cur].mirrored(h, v)
        self._changed()

    def set_size(self, n):
        if n == self.n:
            return
        self.push()
        k = n / self.n
        self.frames = [f.scaled(n, n, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
                       .convertToFormat(QImage.Format.Format_ARGB32_Premultiplied) for f in self.frames]
        self.hot = (min(n - 1, int(self.hot[0] * k)), min(n - 1, int(self.hot[1] * k)))
        self.n = n
        self._changed(True)

    def fit(self, img):
        out = self.blank()
        mode = Qt.TransformationMode.FastTransformation if max(img.width(), img.height()) <= self.n \
            else Qt.TransformationMode.SmoothTransformation
        s = img.scaled(self.n, self.n, Qt.AspectRatioMode.KeepAspectRatio, mode)
        p = QPainter(out)
        p.drawImage((self.n - s.width()) // 2, (self.n - s.height()) // 2, s)
        p.end()
        return out

    def set_image(self, img):
        self.push()
        self.frames[self.cur] = self.fit(img)
        self._changed()

    def set_frames(self, imgs, delays):
        self.push()
        self.frames = [self.fit(i) for i in imgs]
        self.delays = list(delays)
        self.cur = 0
        self._changed(True)

    def export(self, size, all_frames):
        if size and size > self.n:
            size = None
        side = size or self.n
        idx = range(len(self.frames)) if all_frames else [self.cur]
        outs = []
        for i in idx:
            f = self.frames[i]
            if side != self.n:
                f = f.scaled(side, side, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
            outs.append(f.convertToFormat(QImage.Format.Format_ARGB32))
        k = side / self.n
        hot = (min(side - 1, int((self.hot[0] + .5) * k)), min(side - 1, int((self.hot[1] + .5) * k)))
        return outs, [self.delays[i] for i in idx], hot

    # ---- geometry ----
    def geo(self):
        s = min(self.width(), self.height()) - 16
        sc = max(s / self.n, 0.01)
        side = sc * self.n
        return (self.width() - side) / 2, (self.height() - side) / 2, sc

    def ipos(self, e):
        ox, oy, sc = self.geo()
        p = e.position()
        return int(math.floor((p.x() - ox) / sc)), int(math.floor((p.y() - oy) / sc))

    # ---- painting ----
    def paintEvent(self, e):
        p = QPainter(self)
        ox, oy, sc = self.geo()
        side = sc * self.n
        r = QRectF(ox, oy, side, side)
        p.setClipRect(r)
        key = (P("ck1"), P("ck2"))
        if getattr(self, "_ckkey", None) != key:
            self._ckkey, self._ckb = key, checker_brush(QColor(key[0]), QColor(key[1]))
        p.setBrushOrigin(QPointF(ox, oy))
        p.fillRect(r, self._ckb)
        if self.onion and self.cur > 0:
            p.setOpacity(.35)
            p.drawImage(r, self.frames[self.cur - 1])
            p.setOpacity(1)
        p.drawImage(r, self.temp if self.temp is not None else self.frames[self.cur])
        if self.grid and sc >= 7:
            p.setPen(QPen(QColor(128, 128, 128, 70), 1))
            for i in range(1, self.n):
                d = i * sc
                p.drawLine(QPointF(ox + d, oy), QPointF(ox + d, oy + side))
                p.drawLine(QPointF(ox, oy + d), QPointF(ox + side, oy + d))
        hx, hy = self.hot
        cx, cy = ox + (hx + .5) * sc, oy + (hy + .5) * sc
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rr = max(4.0, sc * .5)
        p.setPen(QPen(QColor("#ff2d55"), 2))
        p.drawEllipse(QPointF(cx, cy), rr, rr)
        p.drawLine(QPointF(cx - rr - 3, cy), QPointF(cx + rr + 3, cy))
        p.drawLine(QPointF(cx, cy - rr - 3), QPointF(cx, cy + rr + 3))
        p.setClipping(False)
        p.setPen(QPen(QColor(P("border")), 2))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRect(r)

    # ---- drawing primitives ----
    def _painter(self, img):
        p = QPainter(img)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, self.smooth)
        return p

    def _pen(self, col):
        return QPen(col, max(1, self.size), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)

    def stroke(self, a, b, col, first=False):
        p = self._painter(self.frames[self.cur])
        if self.tool == "eraser":
            p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        p.setPen(self._pen(col))
        pa, pb = QPointF(a[0] + .5, a[1] + .5), QPointF(b[0] + .5, b[1] + .5)
        p.drawPoint(pa) if first else p.drawLine(pa, pb)
        p.end()

    def draw_shape(self, img, a, b, btn):
        left = btn == Qt.MouseButton.LeftButton
        ca, cb = (self.c1, self.c2) if left else (self.c2, self.c1)
        p = self._painter(img)
        s = max(1, self.size)
        if self.tool == "line":
            p.setPen(self._pen(ca))
            p.drawLine(QPointF(a[0] + .5, a[1] + .5), QPointF(b[0] + .5, b[1] + .5))
            p.end()
            return
        x0, x1 = sorted((a[0], b[0]))
        y0, y1 = sorted((a[1], b[1]))
        r = QRectF(x0, y0, x1 - x0 + 1, y1 - y0 + 1)
        if self.mode == "fill":
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(ca))
        else:
            if r.width() > s and r.height() > s:
                r = r.adjusted(s / 2, s / 2, -s / 2, -s / 2)
            p.setPen(self._pen(ca))
            p.setBrush(QBrush(cb) if self.mode == "both" else Qt.BrushStyle.NoBrush)
        p.drawPath(shape_path(self.tool, r))
        p.end()

    def flood(self, x, y, col):
        n = self.n
        if not (0 <= x < n and 0 <= y < n):
            return
        w = self.frames[self.cur].convertToFormat(QImage.Format.Format_ARGB32)
        t = w.pixel(x, y)
        fill = col.rgba()

        def close(v):
            if (v >> 24) == 0 and (t >> 24) == 0:
                return True
            return (abs(((v >> 24) & 255) - ((t >> 24) & 255)) + abs(((v >> 16) & 255) - ((t >> 16) & 255)) +
                    abs(((v >> 8) & 255) - ((t >> 8) & 255)) + abs((v & 255) - (t & 255))) <= 40

        seen, st = bytearray(n * n), [(x, y)]
        while st:
            cx, cy = st.pop()
            if cx < 0 or cy < 0 or cx >= n or cy >= n:
                continue
            i = cy * n + cx
            if seen[i]:
                continue
            seen[i] = 1
            if not close(w.pixel(cx, cy)):
                continue
            w.setPixel(cx, cy, fill)
            st += [(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)]
        self.frames[self.cur] = w.convertToFormat(QImage.Format.Format_ARGB32_Premultiplied)

    # ---- mouse ----
    def mousePressEvent(self, e):
        b = e.button()
        if b not in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
            return
        x, y = self.ipos(e)
        t = self.tool
        col = self.c1 if b == Qt.MouseButton.LeftButton else self.c2
        if t == "picker":
            if 0 <= x < self.n and 0 <= y < self.n:
                self.colorPicked.emit(QColor(self.frames[self.cur].pixelColor(x, y)), b == Qt.MouseButton.RightButton)
            return
        if t == "hotspot":
            self.push()
            self.hot = (min(self.n - 1, max(0, x)), min(self.n - 1, max(0, y)))
            self._changed()
            return
        self.push()
        self.btn, self.start, self.last, self.drawing = b, (x, y), (x, y), True
        if t == "fill":
            self.flood(x, y, col)
            self.drawing = False
            self.colorUsed.emit(col)
            self._changed()
            return
        if t in ("pen", "eraser"):
            self.stroke((x, y), (x, y), col, True)
        else:
            self.base = self.frames[self.cur].copy()
            self.temp = self.base.copy()
            self.draw_shape(self.temp, self.start, (x, y), b)
        self.update()

    def mouseMoveEvent(self, e):
        x, y = self.ipos(e)
        self.posChanged.emit(x, y)
        if not self.drawing:
            return
        if self.tool in ("pen", "eraser"):
            col = self.c1 if self.btn == Qt.MouseButton.LeftButton else self.c2
            self.stroke(self.last, (x, y), col)
            self.last = (x, y)
        else:
            self.temp = self.base.copy()
            self.draw_shape(self.temp, self.start, (x, y), self.btn)
        self.update()

    def mouseReleaseEvent(self, e):
        if not self.drawing or e.button() != self.btn:
            return
        self.drawing = False
        if self.temp is not None:
            self.frames[self.cur], self.temp, self.base = self.temp, None, None
        if self.tool != "eraser":
            self.colorUsed.emit(self.c1 if self.btn == Qt.MouseButton.LeftButton else self.c2)
        self._changed()


# ───────────────────────── tutorial ─────────────────────────
class TutorialDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle(tr("tut_title"))
        self.setModal(True)
        self.setMinimumWidth(780)
        self.i, self.finished_ok = 0, False
        v = QVBoxLayout(self)
        v.setContentsMargins(24, 18, 24, 16)
        v.setSpacing(10)
        t = QLabel(tr("tut_title"))
        t.setObjectName("h1")
        v.addWidget(t)
        v.addWidget(AnimDemo())
        self.step = QLabel()
        self.step.setObjectName("sub")
        self.head = QLabel()
        self.head.setObjectName("h2")
        self.body = QLabel()
        self.body.setWordWrap(True)
        self.body.setMinimumHeight(84)
        self.body.setAlignment(Qt.AlignmentFlag.AlignTop)
        for w in (self.step, self.head, self.body):
            v.addWidget(w)
        row = QHBoxLayout()
        self.skip = QPushButton(tr("tut_skip"))
        self.skip.clicked.connect(self.on_skip)
        self.never = QCheckBox(tr("tut_never"))
        self.back = QPushButton(tr("tut_back"))
        self.back.clicked.connect(lambda: self.go(-1))
        self.next = QPushButton()
        self.next.setObjectName("primary")
        self.next.clicked.connect(lambda: self.go(1))
        row.addWidget(self.skip)
        row.addStretch()
        row.addWidget(self.never)
        row.addWidget(self.back)
        row.addWidget(self.next)
        v.addLayout(row)
        self.refresh()

    def refresh(self):
        n = len(T)
        self.step.setText(f"{tr('tut_step')} {self.i + 1} / {n}")
        self.head.setText(tr(f"tut_{self.i + 1}_t"))
        self.body.setText(tr(f"tut_{self.i + 1}_d"))
        self.back.setEnabled(self.i > 0)
        self.next.setText(tr("tut_end") if self.i == n - 1 else tr("tut_next"))

    def go(self, d):
        if self.i + d >= len(T):
            self.finished_ok = True
            self.accept()
            return
        self.i = max(0, self.i + d)
        self.refresh()

    def on_skip(self):
        self.finished_ok = True
        self.reject()

    def done(self, r):
        if self.finished_ok or self.never.isChecked():
            S["tut_done"] = True
            save_settings()
        super().done(r)


# ───────────────────────── studio page (Draw / ACC) ─────────────────────────
class Studio(QWidget):
    librarySaved = pyqtSignal()

    def __init__(self, animated):
        super().__init__()
        self.animated = animated
        self.c = Canvas()
        self.cols = [QColor("#000000"), QColor("#ffffff")]
        self.slot, self._sync, self._tut = 0, False, False
        self.recent = ["#000000", "#ffffff", "#ff3b30", "#ff9500", "#ffcc00", "#34c759",
                       "#00c7be", "#007aff", "#af52de", "#ff2d92", "#8e8e93", "#a2845e"]
        self.setAcceptDrops(True)
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 10, 14, 12)
        root.setSpacing(8)
        if animated:
            root.addWidget(self._header())
        mid = QHBoxLayout()
        mid.setSpacing(10)
        zone = QFrame()
        zone.setObjectName("zone")
        zl = QVBoxLayout(zone)
        zl.setContentsMargins(10, 10, 10, 10)
        zl.addWidget(self.c)
        mid.addWidget(zone, 1)
        mid.addWidget(self._side())
        root.addLayout(mid, 1)
        if animated:
            root.addWidget(self._strip())
        root.addWidget(self._tools())

        self.pv_timer = QTimer(self)
        self.pv_timer.setSingleShot(True)
        self.pv_timer.timeout.connect(self.refresh_preview)
        self.c.modified.connect(self.on_modified)
        self.c.framesChanged.connect(self.sync_all)
        self.c.curChanged.connect(self.sync_cur)
        self.c.colorPicked.connect(lambda col, sec: self.set_color(col, 1 if sec else 0))
        self.c.colorUsed.connect(self.add_recent)
        self.c.posChanged.connect(lambda x, y: self.pos.setText(f"x {x}  y {y}"))
        QShortcut(QKeySequence("Ctrl+Z"), self, activated=self.c.undo)
        QShortcut(QKeySequence("Ctrl+Y"), self, activated=self.c.redo)
        self.set_tool("pen")
        self.set_color(self.cols[0], 0)
        self.set_color(self.cols[1], 1)
        self.refresh_icons()
        self.sync_all()
        self.refresh_preview()

    # ---------- construction ----------
    def _header(self):
        f = QFrame()
        f.setObjectName("hdr")
        h = QHBoxLayout(f)
        h.setContentsMargins(16, 6, 12, 6)
        big = QLabel('<span style="font-size:34px;font-weight:900;letter-spacing:3px">'
                     '<span style="color:#ff2d92">A</span><span style="color:#22c3ee">C</span>'
                     '<span style="color:#ffcc00">C</span></span>')
        h.addWidget(big)
        v = QVBoxLayout()
        v.setSpacing(0)
        dec = QLabel('<span style="font-size:15px;font-weight:600"><b style="color:#ff2d92">A</b>nimated '
                     '<b style="color:#22c3ee">C</b>ursor <b style="color:#ffcc00">C</b>reator</span>')
        sub = QLabel()
        sub.setObjectName("sub")
        bind(sub.setText, "acc_sub")
        v.addWidget(dec)
        v.addWidget(sub)
        h.addSpacing(10)
        h.addLayout(v)
        h.addStretch()
        b = FB("tutorial", flex=False)
        b.clicked.connect(self.open_tutorial)
        h.addWidget(b)
        return f

    def _side(self):
        inner = QWidget()
        l = QVBoxLayout(inner)
        l.setContentsMargins(0, 0, 6, 0)
        l.setSpacing(6)
        t = QLabel()
        t.setObjectName("sub")
        bind(t.setText, "preview")
        l.addWidget(t)
        self.pv = PreviewBox()
        bind(self.pv.setToolTip, "hover_test")
        l.addWidget(self.pv, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.pos = QLabel("x 0  y 0")
        self.pos.setObjectName("sub")
        self.hot_l = QLabel()
        self.hot_l.setObjectName("sub")
        self.hot_l.setWordWrap(True)
        l.addWidget(self.pos)
        l.addWidget(self.hot_l)
        rl = QLabel()
        bind(rl.setText, "role")
        self.role = QComboBox()
        self.role.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.role.setMinimumContentsLength(8)
        self.role.setIconSize(QSize(28, 28))
        for r in ROLES:
            self.role.addItem(QIcon(role_icon(r)), "", r)
        bindf(lambda: [self.role.setItemText(i, tr("role_" + r)) for i, r in enumerate(ROLES)])
        l.addWidget(rl)
        l.addWidget(self.role)
        self.side_btns = []
        for key, fn, name in (("apply", self.do_apply, "primary"), ("apply_all", self.do_apply_all, ""),
                              ("save", self.do_save, ""),
                              ("lib_save", self.save_to_library, ""), ("import", self.do_import, ""),
                              ("restore", self.do_restore, "")):
            b = FB(key, name, 14 if name else 13, bool(name), pad=30)
            b.clicked.connect(fn)
            l.addWidget(b)
            self.side_btns.append(b)
        self.msg = QLabel()
        self.msg.setObjectName("sub")
        self.msg.setWordWrap(True)
        l.addWidget(self.msg)
        l.addStretch()
        sa = scroll_page(inner)
        self.side_sa = sa
        sa.setFixedWidth(218)
        sa.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        return sa

    def _strip(self):
        f = QFrame()
        f.setObjectName("hdr")
        f.setFixedHeight(112)
        h = QHBoxLayout(f)
        h.setContentsMargins(10, 6, 10, 6)
        self.lw = QListWidget()
        self.lw.setObjectName("strip")
        self.lw.setViewMode(QListView.ViewMode.IconMode)
        self.lw.setFlow(QListView.Flow.LeftToRight)
        self.lw.setWrapping(False)
        self.lw.setMovement(QListView.Movement.Static)
        self.lw.setIconSize(QSize(56, 56))
        self.lw.setSpacing(6)
        self.lw.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.lw.currentRowChanged.connect(lambda r: r >= 0 and self.c.set_cur(r))
        h.addWidget(self.lw, 1)
        v = QVBoxLayout()
        v.setSpacing(6)
        r1 = QHBoxLayout()
        r1.setSpacing(5)
        for txt, key, fn in (("＋", "f_add", self.c.add_frame), ("⧉", "f_dup", self.c.dup_frame),
                             ("🗑", "f_del", self.c.del_frame), ("◀", "f_left", lambda: self.c.move_frame(-1)),
                             ("▶", "f_right", lambda: self.c.move_frame(1))):
            b = QToolButton()
            b.setText(txt)
            b.setFixedSize(40, 32)
            bind(b.setToolTip, key)
            b.clicked.connect(lambda _, fn=fn: fn())
            r1.addWidget(b)
        v.addLayout(r1)
        r2 = QHBoxLayout()
        self.onion = FitCheck(flex=False)
        bind(self.onion.setText, "onion")
        self.onion.toggled.connect(lambda on: (setattr(self.c, "onion", on), self.c.update()))
        r2.addWidget(self.onion)
        v.addLayout(r2)
        r3 = QHBoxLayout()
        dl = QLabel()
        bind(dl.setText, "delay")
        self.spin = QSpinBox()
        self.spin.setRange(20, 3000)
        self.spin.setSingleStep(10)
        self.spin.setValue(100)
        self.spin.valueChanged.connect(self.on_delay)
        ab = FB("delay_all", flex=False)
        ab.clicked.connect(self.delay_all)
        r3.addWidget(dl)
        r3.addWidget(self.spin)
        r3.addWidget(ab)
        v.addLayout(r3)
        h.addLayout(v)
        return f

    def _tools(self):
        f = QFrame()
        f.setObjectName("tools")
        h = QHBoxLayout(f)
        h.setContentsMargins(12, 10, 12, 10)
        h.setSpacing(18)
        # tools grid + actions
        left = QVBoxLayout()
        left.setSpacing(6)
        grid = QGridLayout()
        grid.setSpacing(5)
        self.tb, grp = {}, QButtonGroup(self)
        for i, tid in enumerate(TOOLS):
            b = QToolButton()
            b.setCheckable(True)
            b.setFixedSize(40, 40)
            b.setIconSize(QSize(26, 26))
            bind(b.setToolTip, "t_" + tid)
            b.clicked.connect(lambda _, t=tid: self.set_tool(t))
            grp.addButton(b)
            grid.addWidget(b, i // 5, i % 5)
            self.tb[tid] = b
        left.addLayout(grid)
        acts = QHBoxLayout()
        acts.setSpacing(5)
        for txt, key, fn in (("↶", "undo", self.c.undo), ("↷", "redo", self.c.redo), ("🗑", "clear", self.c.clear),
                             ("⇋", "flip_h", lambda: self.c.flip(True, False)), ("⇵", "flip_v", lambda: self.c.flip(False, True))):
            b = QToolButton()
            b.setText(txt)
            b.setFixedSize(36, 30)
            bind(b.setToolTip, key)
            b.clicked.connect(lambda _, fn=fn: fn())
            acts.addWidget(b)
        left.addLayout(acts)
        h.addLayout(left)
        # options
        opt = QVBoxLayout()
        opt.setSpacing(6)
        self.size_l = QLabel()
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(1, 64)
        self.slider.setValue(3)
        self.slider.valueChanged.connect(self.on_size)
        bindf(self.on_size)
        opt.addWidget(self.size_l)
        opt.addWidget(self.slider)
        sl = QLabel()
        sl.setObjectName("sub")
        bind(sl.setText, "shape_mode")
        self.mode = QComboBox()
        self.mode.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.mode.setMinimumContentsLength(6)
        for m in ("outline", "fill", "both"):
            self.mode.addItem("", m)
        bindf(lambda: [self.mode.setItemText(i, tr("m_" + m)) for i, m in enumerate(("outline", "fill", "both"))])
        self.mode.currentIndexChanged.connect(lambda _: setattr(self.c, "mode", self.mode.currentData()))
        opt.addWidget(sl)
        opt.addWidget(self.mode)
        self.chk_grid = FitCheck()
        bind(self.chk_grid.setText, "grid")
        self.chk_grid.setChecked(S["grid"])
        self.chk_grid.toggled.connect(self.on_grid)
        self.chk_smooth = FitCheck()
        bind(self.chk_smooth.setText, "smooth")
        self.chk_smooth.setChecked(S["smooth"])
        self.chk_smooth.toggled.connect(self.on_smooth)
        opt.addWidget(self.chk_grid)
        opt.addWidget(self.chk_smooth)
        cl = QLabel()
        cl.setObjectName("sub")
        bind(cl.setText, "canvas_px")
        self.csize = QComboBox()
        for n in (32, 48, 64, 128, 256):
            self.csize.addItem(str(n), n)
        self.csize.setCurrentIndex(2)
        self.csize.currentIndexChanged.connect(lambda _: self.c.set_size(self.csize.currentData()))
        opt.addWidget(cl)
        opt.addWidget(self.csize)
        opt.addStretch()
        w = QWidget()
        w.setFixedWidth(150)
        w.setLayout(opt)
        h.addWidget(w)
        # colour
        col = QHBoxLayout()
        col.setSpacing(12)
        self.wheel = ColorWheel()
        self.wheel.changed.connect(self.on_wheel)
        col.addWidget(self.wheel)
        r = QVBoxLayout()
        r.setSpacing(6)
        sw = QHBoxLayout()
        self.sw = [Swatch(self.cols[0]), Swatch(self.cols[1])]
        sg = QButtonGroup(self)
        for i, s in enumerate(self.sw):
            sg.addButton(s)
            s.clicked.connect(lambda _, i=i: self.pick_slot(i))
            sw.addWidget(s)
        bind(self.sw[0].setToolTip, "primary")
        bind(self.sw[1].setToolTip, "secondary")
        self.sw[0].setChecked(True)
        r.addLayout(sw)
        self.hex = QLineEdit()
        self.hex.setMaxLength(7)
        self.hex.setFixedWidth(92)
        self.hex.editingFinished.connect(self.on_hex)
        r.addWidget(self.hex)
        al = QLabel()
        al.setObjectName("sub")
        bind(al.setText, "opacity")
        self.alpha = QSlider(Qt.Orientation.Horizontal)
        self.alpha.setRange(0, 255)
        self.alpha.setValue(255)
        self.alpha.valueChanged.connect(self.on_alpha)
        r.addWidget(al)
        r.addWidget(self.alpha)
        self.rgrid = QGridLayout()
        self.rgrid.setSpacing(4)
        r.addLayout(self.rgrid)
        r.addStretch()
        col.addLayout(r)
        h.addLayout(col)
        h.addStretch()
        self.rebuild_recent()
        return f

    # ---------- tools / colours ----------
    def set_tool(self, t):
        self.c.tool = t
        self.tb[t].setChecked(True)

    def refresh_icons(self):
        for tid, b in self.tb.items():
            ic = QIcon()
            ic.addPixmap(tool_icon(tid, P("text")), QIcon.Mode.Normal, QIcon.State.Off)
            ic.addPixmap(tool_icon(tid, "#ffffff"), QIcon.Mode.Normal, QIcon.State.On)
            b.setIcon(ic)
        if self.animated:
            self.rebuild_strip()

    def on_size(self, *_):
        self.c.size = self.slider.value()
        self.size_l.setText(f"{tr('size')}: {self.slider.value()} px")

    def on_grid(self, on):
        S["grid"] = on
        self.c.grid = on
        self.c.update()
        save_settings()

    def on_smooth(self, on):
        S["smooth"] = on
        self.c.smooth = on
        save_settings()

    def pick_slot(self, i):
        self.slot = i
        self.sync_color_ui()

    def set_color(self, c, slot=None, from_wheel=False):
        slot = self.slot if slot is None else slot
        self.cols[slot] = QColor(c)
        self.c.c1, self.c.c2 = QColor(self.cols[0]), QColor(self.cols[1])
        self.sw[slot].set_color(c)
        if slot == self.slot:
            self.sync_color_ui(from_wheel)

    def sync_color_ui(self, skip_wheel=False):
        c = self.cols[self.slot]
        if not skip_wheel:
            self.wheel.setColor(c)
        self.hex.blockSignals(True)
        self.hex.setText(c.name())
        self.hex.blockSignals(False)
        self.alpha.blockSignals(True)
        self.alpha.setValue(c.alpha())
        self.alpha.blockSignals(False)

    def on_wheel(self, c):
        nc = QColor(c)
        nc.setAlpha(self.cols[self.slot].alpha())
        self.set_color(nc, from_wheel=True)

    def on_hex(self):
        t = self.hex.text().strip()
        c = QColor(t if t.startswith("#") else "#" + t)
        if c.isValid():
            c.setAlpha(self.cols[self.slot].alpha())
            self.set_color(c)

    def on_alpha(self, v):
        c = QColor(self.cols[self.slot])
        c.setAlpha(v)
        self.set_color(c, from_wheel=True)

    def add_recent(self, c):
        n = c.name()
        if n in self.recent:
            self.recent.remove(n)
        self.recent.insert(0, n)
        del self.recent[12:]
        self.rebuild_recent()

    def rebuild_recent(self):
        while self.rgrid.count():
            it = self.rgrid.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
        for i, n in enumerate(self.recent):
            b = QPushButton()
            b.setFixedSize(20, 20)
            b.setStyleSheet(f"QPushButton{{background:{n};border:1px solid {qcol(P('border'))};border-radius:4px;padding:0}}"
                            f"QPushButton:hover{{border:2px solid {P('accent')}}}")
            b.clicked.connect(lambda _, n=n: self.set_color(QColor(n)))
            self.rgrid.addWidget(b, i // 6, i % 6)

    # ---------- frames ----------
    def thumb(self, img):
        pm = QPixmap(56, 56)
        pm.fill(QColor(P("ck1")))
        p = QPainter(pm)
        p.drawImage(QRectF(2, 2, 52, 52), img)
        p.end()
        return pm

    def rebuild_strip(self):
        self.lw.blockSignals(True)
        self.lw.clear()
        for i, f in enumerate(self.c.frames):
            self.lw.addItem(QListWidgetItem(QIcon(self.thumb(f)), f"{i + 1} · {self.c.delays[i]}ms"))
        self.lw.setCurrentRow(self.c.cur)
        self.lw.blockSignals(False)
        self.sync_delay()

    def sync_delay(self):
        self.spin.blockSignals(True)
        self.spin.setValue(self.c.delays[self.c.cur])
        self.spin.blockSignals(False)

    def on_delay(self, v):
        self.c.delays[self.c.cur] = v
        it = self.lw.item(self.c.cur)
        if it:
            it.setText(f"{self.c.cur + 1} · {v}ms")
        self.pv_timer.start(150)

    def delay_all(self):
        self.c.push()
        self.c.delays = [self.spin.value()] * len(self.c.frames)
        self.rebuild_strip()
        self.pv_timer.start(150)

    def sync_cur(self):
        if self.animated:
            self.lw.blockSignals(True)
            self.lw.setCurrentRow(self.c.cur)
            self.lw.blockSignals(False)
            self.sync_delay()

    def sync_all(self):
        self.csize.blockSignals(True)
        self.csize.setCurrentIndex(max(0, self.csize.findData(self.c.n)))
        self.csize.blockSignals(False)
        if self.animated:
            self.rebuild_strip()

    def on_modified(self):
        if self.animated:
            self.rebuild_strip()
        self.pv_timer.start(120)

    # ---------- preview & export ----------
    def target_size(self):
        return S["cur_size"] if S["autofit"] else None

    def refresh_preview(self):
        imgs, delays, hot = self.c.export(self.target_size(), self.animated)
        self.pv.set_frames(imgs, delays, hot)
        self.hot_l.setText(f"{tr('hot')}: {hot[0]}, {hot[1]}  ·  {imgs[0].width()}×{imgs[0].height()}")

    def settings_changed(self):
        for chk, k in ((self.chk_grid, "grid"), (self.chk_smooth, "smooth")):
            chk.blockSignals(True)
            chk.setChecked(S[k])
            chk.blockSignals(False)
        self.c.grid, self.c.smooth = S["grid"], S["smooth"]
        self.c.update()
        self.refresh_preview()

    def build_bytes(self):
        imgs, delays, hot = self.c.export(self.target_size(), self.animated)
        curs = [cur_bytes(dib_from_image(im), im.width(), im.height(), *hot) for im in imgs]
        if len(curs) > 1:
            return ani_bytes(curs, delays), ".ani"
        return curs[0], ".cur"

    def say(self, t):
        self.msg.setText(t)

    def do_save(self):
        data, ext = self.build_bytes()
        path, _ = QFileDialog.getSaveFileName(self, tr("save"), "my_cursor" + ext, f"Cursor (*{ext})")
        if path:
            try:
                Path(path).write_bytes(data)
                self.say(tr("saved") + path)
            except Exception as ex:
                QMessageBox.critical(self, tr("err"), str(ex))

    def do_apply(self):
        self._apply(self.role.currentData())

    def do_apply_all(self):
        self._apply("ALL")

    def _apply(self, role):
        data, ext = self.build_bytes()
        try:
            ok, path = install_cursor(data, ext, role)
            if ok:
                self.say(tr("applied"))
            else:
                QMessageBox.information(self, "UCCC", tr("only_win") + str(path))
        except Exception as ex:
            QMessageBox.critical(self, tr("err"), str(ex))

    def do_restore(self):
        try:
            if os.name == "nt":
                win_restore()
            self.say(tr("restored"))
        except Exception as ex:
            QMessageBox.critical(self, tr("err"), str(ex))

    # ---------- library ----------
    def save_to_library(self):
        dflt = f"{'ACC' if self.animated else 'Cursor'} {time.strftime('%d.%m %H:%M')}"
        name, ok = QInputDialog.getText(self, tr("lib_save"), tr("lib_name_q"), text=dflt)
        name = name.strip()
        if not ok or not name:
            return
        try:
            data, ext = self.build_bytes()
            imgs, delays, hot = self.c.export(self.target_size(), self.animated)
            frames = list(self.c.frames) if self.animated else [self.c.frames[self.c.cur]]
            lib_add(name, data, ext, imgs[0].width(), hot, self.c.hot, delays if self.animated else [100],
                    frames, self.c.n, imgs[0])
            self.librarySaved.emit()
            self.say(tr("lib_saved") + name)
        except Exception as ex:
            QMessageBox.critical(self, tr("err"), str(ex))

    def load_project(self, frames, delays, chot, n):
        c = self.c
        c.push()
        c.n = n
        c.frames = [f.convertToFormat(QImage.Format.Format_ARGB32_Premultiplied) for f in frames]
        c.delays = list(delays)
        if not self.animated:
            c.frames, c.delays = c.frames[:1], [100]
        c.cur, c.hot = 0, (int(chot[0]), int(chot[1]))
        c._changed(True)

    def adapt(self):
        adapt_column(self.side_sa, self.pv, self.side_btns, 175)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.adapt()

    # ---------- import ----------
    def do_import(self):
        path, _ = QFileDialog.getOpenFileName(self, tr("import"), "", "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp *.ico *.cur)")
        if path:
            self.import_path(path)

    def import_path(self, path):
        imgs, delays = [], []
        if path.lower().endswith(".gif"):
            m, i = QMovie(path), 0
            while i < 120 and m.jumpToFrame(i):
                imgs.append(m.currentImage().copy())
                delays.append(max(20, m.nextFrameDelay() or 100))
                i += 1
        if not imgs:
            im = QImage(path)
            if im.isNull():
                QMessageBox.warning(self, tr("err"), path)
                return
            imgs, delays = [im], [100]
        if self.animated:
            self.c.set_frames(imgs, delays)
        else:
            self.c.set_image(imgs[0])

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        u = e.mimeData().urls()
        if u:
            self.import_path(u[0].toLocalFile())

    # ---------- tutorial ----------
    def open_tutorial(self):
        TutorialDialog(self.window()).exec()

    def showEvent(self, e):
        super().showEvent(e)
        QTimer.singleShot(0, self.adapt)
        if self.animated and not S["tut_done"] and not self._tut:
            self._tut = True
            QTimer.singleShot(300, self.open_tutorial)


# ───────────────────────── settings & about ─────────────────────────
class BgFrame(QFrame):
    """Window body: solid theme colour, or the animated pattern for the gradient theme."""

    def __init__(self):
        super().__init__()
        self.setObjectName("frame")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)

    def sync(self):
        self.timer.start(70) if is_gradient() else self.timer.stop()
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(r, 14, 14)
        p.setClipPath(path)
        if is_gradient():
            paint_pattern(p, r, S["grad_pattern"], QColor(S["grad_c1"]), QColor(S["grad_c2"]), pattern_t())
        else:
            p.fillPath(path, QColor(P("bg")))
        p.setClipping(False)
        p.setPen(QPen(QColor(P("fborder")), 2))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)


class PatternPreview(QWidget):
    def __init__(self, getter):
        super().__init__()
        self.get = getter
        self.setFixedHeight(56)
        self.setMinimumWidth(260)
        t = QTimer(self)
        t.timeout.connect(lambda: self.isVisible() and self.update())
        t.start(40)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(r, 10, 10)
        p.setClipPath(path)
        pat, c1, c2 = self.get()
        paint_pattern(p, r, pat, c1, c2, pattern_t())
        p.setClipping(False)
        p.setPen(QPen(QColor(P("border")), 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)


class ColorPicker(QWidget):
    changed = pyqtSignal(QColor)

    def __init__(self, c="#ffffff"):
        super().__init__()
        h = QHBoxLayout(self)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(12)
        self.wheel = ColorWheel()
        self.wheel.changed.connect(self._wheel)
        h.addWidget(self.wheel)
        v = QVBoxLayout()
        self.hex = QLineEdit()
        self.hex.setMaxLength(7)
        self.hex.setFixedWidth(92)
        self.hex.editingFinished.connect(self._hex)
        v.addWidget(self.hex)
        v.addStretch()
        h.addLayout(v)
        h.addStretch()
        self.set(c)

    def color(self):
        return QColor(self._c)

    def set(self, c):
        self._c = QColor(c)
        self.wheel.setColor(self._c)
        self.hex.setText(self._c.name())

    def _wheel(self, c):
        self._c = QColor(c)
        self.hex.setText(self._c.name())
        self.changed.emit(self._c)

    def _hex(self):
        t = self.hex.text().strip()
        c = QColor(t if t.startswith("#") else "#" + t)
        if c.isValid():
            self.set(c)
            self.changed.emit(self._c)


class GradientEditor(QWidget):
    """Two colours picked with a wheel + a pattern, live preview, explicit Save."""
    PATTERNS = ("amber", "smooth", "waves", "stripes")

    def __init__(self, c1, c2, pattern, on_save, save_key="btn_save", on_reset=None):
        super().__init__()
        self.cols, self.slot = [QColor(c1), QColor(c2)], 0
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(8)
        top = QHBoxLayout()
        self.sw, grp = [Swatch(c1), Swatch(c2)], QButtonGroup(self)
        for i, s in enumerate(self.sw):
            grp.addButton(s)
            s.clicked.connect(lambda _, i=i: self.pick_slot(i))
            top.addWidget(s)
        bind(self.sw[0].setToolTip, "col_a")
        bind(self.sw[1].setToolTip, "col_b")
        self.sw[0].setChecked(True)
        top.addSpacing(12)
        pl = QLabel()
        bind(pl.setText, "s_pattern")
        self.pat = QComboBox()
        for k in self.PATTERNS:
            self.pat.addItem("", k)
        bindf(lambda: [self.pat.setItemText(i, tr("pt_" + k)) for i, k in enumerate(self.PATTERNS)])
        self.pat.setCurrentIndex(max(0, self.pat.findData(pattern)))
        top.addWidget(pl)
        top.addWidget(self.pat)
        top.addStretch()
        v.addLayout(top)
        self.pick = ColorPicker(c1)
        self.pick.changed.connect(self._changed)
        v.addWidget(self.pick)
        v.addWidget(PatternPreview(lambda: (self.pat.currentData(), self.cols[0], self.cols[1])))
        br = QHBoxLayout()
        b = FB(save_key, "primary", 13, True, flex=False)
        b.clicked.connect(lambda: on_save(self.cols[0].name(), self.cols[1].name(), self.pat.currentData()))
        br.addWidget(b)
        if on_reset:
            b2 = FB("btn_reset", flex=False)
            b2.clicked.connect(lambda: on_reset())
            br.addWidget(b2)
        br.addStretch()
        v.addLayout(br)

    def pick_slot(self, i):
        self.slot = i
        self.pick.set(self.cols[i])

    def set(self, c1, c2, pattern):
        self.cols = [QColor(c1), QColor(c2)]
        for sw, c in zip(self.sw, self.cols):
            sw.set_color(c)
        self.pat.setCurrentIndex(max(0, self.pat.findData(pattern)))
        self.pick.set(self.cols[self.slot])

    def _changed(self, c):
        self.cols[self.slot] = QColor(c)
        self.sw[self.slot].set_color(c)


def card(title_key):
    f = QFrame()
    f.setObjectName("card")
    v = QVBoxLayout(f)
    v.setContentsMargins(18, 14, 18, 14)
    v.setSpacing(10)
    t = QLabel()
    t.setObjectName("h2")
    bind(t.setText, title_key)
    v.addWidget(t)
    return f, v


def row(label_key, widget):
    h = QHBoxLayout()
    l = QLabel()
    bind(l.setText, label_key)
    h.addWidget(l)
    h.addStretch()
    h.addWidget(widget)
    return h


def hint(key):
    l = QLabel()
    l.setObjectName("sub")
    l.setWordWrap(True)
    bind(l.setText, key)
    return l


def scroll_page(inner):
    sa = QScrollArea()
    sa.setWidgetResizable(True)
    sa.setFrameShape(QFrame.Shape.NoFrame)
    sa.setStyleSheet("QScrollArea,QScrollArea>QWidget>QWidget{background:transparent;border:none}")
    sa.viewport().setAutoFillBackground(False)
    inner.setAutoFillBackground(False)
    sa.setWidget(inner)
    return sa


class SettingsPage(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        inner = QWidget()
        outer = QVBoxLayout(inner)
        outer.setContentsMargins(30, 20, 30, 20)
        outer.setSpacing(12)
        t = QLabel()
        t.setObjectName("h1")
        bind(t.setText, "s_title")
        outer.addWidget(t)
        # --- appearance
        f, v = card("s_look")
        self.lang = QComboBox()
        self.lang.addItem("English", "en")
        self.lang.addItem("Русский", "ru")
        self.lang.setCurrentIndex(0 if S["lang"] == "en" else 1)
        self.lang.currentIndexChanged.connect(self.on_lang)
        v.addLayout(row("s_lang", self.lang))
        self.theme = QComboBox()
        for k in THEME_KEYS:
            self.theme.addItem("", k)
        bindf(lambda: [self.theme.setItemText(i, tr("th_" + k)) for i, k in enumerate(THEME_KEYS)])
        self.theme.setCurrentIndex(max(0, self.theme.findData(S["theme"])))
        self.theme.currentIndexChanged.connect(self.on_theme)
        v.addLayout(row("s_theme", self.theme))
        self.note = QLabel()
        self.note.setObjectName("sub")
        self.note.setWordWrap(True)
        self.note.hide()
        v.addWidget(self.note)
        self.rb = QSlider(Qt.Orientation.Horizontal)
        self.rb.setRange(5, 100)
        self.rb.setValue(int(S["rainbow"]))
        self.rb.setFixedWidth(200)
        self.rb.valueChanged.connect(lambda x: (S.__setitem__("rainbow", x), save_settings()))
        v.addLayout(row("s_speed", self.rb))
        outer.addWidget(f)
        # --- interface colour
        f, v = card("s_accent")
        v.addWidget(hint("s_accent_h"))
        self.acc = ColorPicker(S.get("accent") or PAL["accent"])
        v.addWidget(self.acc)
        r = QHBoxLayout()
        b = FB("btn_save", "primary", 13, True, flex=False)
        b.clicked.connect(self.save_accent)
        b2 = FB("btn_reset", flex=False)
        b2.clicked.connect(self.reset_accent)
        r.addWidget(b)
        r.addWidget(b2)
        r.addStretch()
        v.addLayout(r)
        outer.addWidget(f)
        # --- title bar
        f, v = card("s_bar")
        self.barmode = QComboBox()
        self.barmode.addItem("", "rainbow")
        self.barmode.addItem("", "gradient")
        bindf(lambda: (self.barmode.setItemText(0, tr("bar_rainbow")), self.barmode.setItemText(1, tr("bar_grad"))))
        self.barmode.setCurrentIndex(1 if S["bar_mode"] == "gradient" else 0)
        self.barmode.currentIndexChanged.connect(self.on_barmode)
        v.addWidget(self.barmode)
        self.bared = GradientEditor(S["bar_c1"], S["bar_c2"], S["bar_pattern"], self.save_bar, on_reset=self.reset_bar)
        self.bared.setVisible(S["bar_mode"] == "gradient")
        v.addWidget(self.bared)
        outer.addWidget(f)
        # --- gradient theme
        f, v = card("s_gtheme")
        v.addWidget(hint("s_gtheme_h"))
        self.gted = GradientEditor(S["grad_c1"], S["grad_c2"], S["grad_pattern"], self.save_gtheme, "btn_save_apply",
                                   on_reset=self.reset_gtheme)
        v.addWidget(self.gted)
        outer.addWidget(f)
        # --- cursor size
        f, v = card("s_cur")
        self.auto = FitCheck()
        bind(self.auto.setText, "s_autofit")
        self.auto.setChecked(S["autofit"])
        self.auto.toggled.connect(self.on_auto)
        v.addWidget(self.auto)
        v.addWidget(hint("s_autofit_h"))
        self.cs = QComboBox()
        for n in (32, 48, 64, 96, 128):
            self.cs.addItem(f"{n} × {n}", n)
        self.cs.setCurrentIndex(max(0, self.cs.findData(S["cur_size"])))
        self.cs.setEnabled(S["autofit"])
        self.cs.currentIndexChanged.connect(self.on_cs)
        v.addLayout(row("s_size", self.cs))
        outer.addWidget(f)
        # --- tools
        f, v = card("s_tools")
        b1 = FB("s_folder")
        b1.clicked.connect(lambda: (CURSOR_DIR.mkdir(parents=True, exist_ok=True),
                                    QDesktopServices.openUrl(QUrl.fromLocalFile(str(CURSOR_DIR)))))
        b2 = FB("restore")
        b2.clicked.connect(self.main.draw.do_restore)
        b3 = FB("s_tut")
        b3.clicked.connect(self.main.acc.open_tutorial)
        b4 = FB("rs_all")
        b4.clicked.connect(self.reset_all)
        for b in (b1, b2, b3, b4):
            v.addWidget(b)
        outer.addWidget(f)
        outer.addStretch()
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll_page(inner))

    def on_lang(self):
        global LANG
        S["lang"] = LANG = self.lang.currentData()
        save_settings()
        retranslate()

    def on_theme(self):
        key = self.theme.currentData()
        if key == "gradient" and not S["grad_saved"]:
            self.note.setText(tr("gt_need"))
            self.note.show()
            self.theme.blockSignals(True)
            self.theme.setCurrentIndex(max(0, self.theme.findData(S["theme"])))
            self.theme.blockSignals(False)
            return
        self.note.hide()
        S["theme"] = key
        save_settings()
        self.main.refresh_theme()

    def save_accent(self):
        S["accent"] = self.acc.color().name()
        save_settings()
        self.main.refresh_theme()

    def reset_accent(self):
        S["accent"] = ""
        save_settings()
        self.main.refresh_theme()
        self.acc.set(PAL["accent"])

    def on_barmode(self):
        m = self.barmode.currentData()
        self.bared.setVisible(m == "gradient")
        if m == "rainbow":
            S["bar_mode"] = "rainbow"
            save_settings()

    def save_bar(self, c1, c2, pat):
        S.update(bar_mode="gradient", bar_c1=c1, bar_c2=c2, bar_pattern=pat)
        save_settings()

    def save_gtheme(self, c1, c2, pat):
        S.update(theme="gradient", grad_saved=True, grad_c1=c1, grad_c2=c2, grad_pattern=pat)
        save_settings()
        self.theme.blockSignals(True)
        self.theme.setCurrentIndex(self.theme.findData("gradient"))
        self.theme.blockSignals(False)
        self.note.hide()
        self.main.refresh_theme()

    def reload(self):
        """Sync every control with S (used after a full reset)."""
        for w in (self.lang, self.theme, self.barmode, self.rb, self.auto, self.cs):
            w.blockSignals(True)
        self.lang.setCurrentIndex(0 if S["lang"] == "en" else 1)
        self.theme.setCurrentIndex(max(0, self.theme.findData(S["theme"])))
        self.barmode.setCurrentIndex(1 if S["bar_mode"] == "gradient" else 0)
        self.rb.setValue(int(S["rainbow"]))
        self.auto.setChecked(S["autofit"])
        self.cs.setCurrentIndex(max(0, self.cs.findData(S["cur_size"])))
        self.cs.setEnabled(S["autofit"])
        for w in (self.lang, self.theme, self.barmode, self.rb, self.auto, self.cs):
            w.blockSignals(False)
        self.note.hide()
        self.acc.set(S.get("accent") or PAL["accent"])
        self.bared.set(S["bar_c1"], S["bar_c2"], S["bar_pattern"])
        self.bared.setVisible(S["bar_mode"] == "gradient")
        self.gted.set(S["grad_c1"], S["grad_c2"], S["grad_pattern"])

    def reset_bar(self):
        S.update({k: DEFAULTS[k] for k in ("bar_mode", "bar_c1", "bar_c2", "bar_pattern")})
        save_settings()
        self.barmode.blockSignals(True)
        self.barmode.setCurrentIndex(0)
        self.barmode.blockSignals(False)
        self.bared.set(S["bar_c1"], S["bar_c2"], S["bar_pattern"])
        self.bared.setVisible(False)

    def reset_gtheme(self):
        S.update({k: DEFAULTS[k] for k in ("grad_saved", "grad_c1", "grad_c2", "grad_pattern")})
        if S["theme"] == "gradient":
            S["theme"] = "dark"
        save_settings()
        self.theme.blockSignals(True)
        self.theme.setCurrentIndex(max(0, self.theme.findData(S["theme"])))
        self.theme.blockSignals(False)
        self.gted.set(S["grad_c1"], S["grad_c2"], S["grad_pattern"])
        self.note.hide()
        self.main.refresh_theme()

    def reset_all(self):
        global LANG
        q = QMessageBox.question(self, tr("rs_title"), tr("rs_all_q"),
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                 QMessageBox.StandardButton.No)
        if q != QMessageBox.StandardButton.Yes:
            return
        S.clear()
        S.update(DEFAULTS)
        S["lang"] = "en"
        LANG = S["lang"]
        save_settings()
        retranslate()
        self.main.refresh_theme()
        self.reload()
        self.main.settings_changed()

    def on_auto(self, on):
        S["autofit"] = on
        self.cs.setEnabled(on)
        save_settings()
        self.main.settings_changed()

    def on_cs(self):
        S["cur_size"] = self.cs.currentData()
        save_settings()
        self.main.settings_changed()


class AboutPage(QWidget):
    def __init__(self):
        super().__init__()
        inner = QWidget()
        v = QVBoxLayout(inner)
        v.setContentsMargins(40, 26, 40, 26)
        v.setSpacing(10)
        big = QLabel('<span style="font-size:54px;font-weight:900;letter-spacing:4px;color:#a78bfa">UC'
                     '<span style="color:#22d3ee">C</span><span style="color:#34d399">C</span></span>')
        v.addWidget(big)
        t = QLabel()
        t.setObjectName("h1")
        bind(t.setText, "ab_title")
        v.addWidget(t)
        body = QLabel()
        body.setWordWrap(True)
        body.setTextFormat(Qt.TextFormat.RichText)
        body.setAlignment(Qt.AlignmentFlag.AlignTop)
        bind(body.setText, "ab_text")
        v.addWidget(body)
        pf, pv = card("ab_patch_t")
        pl = QLabel()
        pl.setWordWrap(True)
        pl.setTextFormat(Qt.TextFormat.RichText)
        pl.setAlignment(Qt.AlignmentFlag.AlignTop)
        bind(pl.setText, "ab_patch")
        pv.addWidget(pl)
        v.addWidget(pf)
        f, cv = card("ab_author_t")
        al = QLabel()
        al.setWordWrap(True)
        al.setTextFormat(Qt.TextFormat.RichText)
        al.setAlignment(Qt.AlignmentFlag.AlignTop)
        al.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        bind(al.setText, "ab_author")
        cv.addWidget(al)
        v.addWidget(f)
        v.addStretch()
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll_page(inner))


class LibraryPage(QWidget):
    """Saved cursors (static and animated): preview, apply in one click, reopen in the editor."""

    def __init__(self, main):
        super().__init__()
        self.main = main
        root = QHBoxLayout(self)
        root.setContentsMargins(20, 14, 14, 14)
        root.setSpacing(14)
        left = QVBoxLayout()
        left.setSpacing(8)
        t = QLabel()
        t.setObjectName("h1")
        bind(t.setText, "lib_title")
        left.addWidget(t)
        left.addWidget(hint("lib_hint"))
        self.count = QLabel()
        self.count.setObjectName("sub")
        left.addWidget(self.count)
        self.lw = QListWidget()
        self.lw.setObjectName("strip")
        self.lw.setViewMode(QListView.ViewMode.IconMode)
        self.lw.setResizeMode(QListView.ResizeMode.Adjust)
        self.lw.setMovement(QListView.Movement.Static)
        self.lw.setWrapping(True)
        self.lw.setIconSize(QSize(72, 72))
        self.lw.setGridSize(QSize(118, 122))
        self.lw.setWordWrap(True)
        self.lw.currentItemChanged.connect(lambda *_: self.on_sel())
        self.lw.itemDoubleClicked.connect(lambda *_: self.do_apply())
        left.addWidget(self.lw, 1)
        self.empty = QLabel()
        self.empty.setObjectName("sub")
        self.empty.setWordWrap(True)
        bind(self.empty.setText, "lib_empty")
        left.addWidget(self.empty)
        root.addLayout(left, 1)
        inner = QWidget()
        r = QVBoxLayout(inner)
        r.setContentsMargins(0, 0, 6, 0)
        r.setSpacing(6)
        self.pv = PreviewBox()
        r.addWidget(self.pv, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.info = QLabel()
        self.info.setObjectName("sub")
        self.info.setWordWrap(True)
        r.addWidget(self.info)
        rl = QLabel()
        bind(rl.setText, "role")
        self.role = QComboBox()
        self.role.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.role.setMinimumContentsLength(8)
        self.role.setIconSize(QSize(28, 28))
        for ro in ROLES:
            self.role.addItem(QIcon(role_icon(ro)), "", ro)
        bindf(lambda: [self.role.setItemText(i, tr("role_" + ro)) for i, ro in enumerate(ROLES)])
        r.addWidget(rl)
        r.addWidget(self.role)
        sl = QLabel()
        bind(sl.setText, "lib_size")
        r.addWidget(sl)
        self.size_cb = QComboBox()
        for n in (32, 48, 64, 96, 128, 192, 256):
            self.size_cb.addItem(f"{n} × {n}", n)
        r.addWidget(self.size_cb)
        self.btns, self.col_btns = [], []
        for key, fn, name in (("lib_apply", self.do_apply, "primary"), ("apply_all", self.do_apply_all, ""),
                              ("lib_resize", self.do_resize, ""), ("lib_edit", self.do_edit, ""),
                              ("lib_rename", self.do_rename, ""), ("lib_export", self.do_export, ""),
                              ("lib_delete", self.do_delete, ""), ("lib_folder", self.do_folder, "")):
            b = FB(key, name, 14 if name else 13, bool(name), pad=30)
            b.clicked.connect(fn)
            r.addWidget(b)
            self.col_btns.append(b)
            if key != "lib_folder":
                self.btns.append(b)
        self.msg = QLabel()
        self.msg.setObjectName("sub")
        self.msg.setWordWrap(True)
        r.addWidget(self.msg)
        r.addStretch()
        sa = scroll_page(inner)
        self.side_sa = sa
        sa.setFixedWidth(236)
        sa.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        root.addWidget(sa)
        self.reload()

    def cur_meta(self):
        it = self.lw.currentItem()
        return it.data(Qt.ItemDataRole.UserRole) if it else None

    def reload(self, keep=None):
        try:
            metas = lib_list()
        except Exception as ex:
            metas = []
            self.msg.setText(str(ex))
        keep = keep or (self.cur_meta() or {}).get("id")
        self.lw.blockSignals(True)
        self.lw.clear()
        row = 0
        for i, m in enumerate(metas):
            it = QListWidgetItem(QIcon(thumb_pixmap(img_from_b64(m["thumb"]))), m["name"])
            it.setData(Qt.ItemDataRole.UserRole, m)
            it.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.lw.addItem(it)
            if m["id"] == keep:
                row = i
        if metas:
            self.lw.setCurrentRow(row)
        self.lw.blockSignals(False)
        self.count.setText(tr("lib_count") + str(len(metas)))
        self.empty.setVisible(not metas)
        self.on_sel()

    def on_sel(self):
        m = self.cur_meta()
        for b in self.btns:
            b.setEnabled(m is not None)
        if not m:
            self.pv.set_frames([], [], (0, 0))
            self.info.setText(tr("lib_select"))
            return
        self.size_cb.setCurrentIndex(max(0, self.size_cb.findData(m["size"])))
        try:
            s = m["size"]
            imgs = [f.scaled(s, s, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    .convertToFormat(QImage.Format.Format_ARGB32) for f in lib_frames(m)]
            self.pv.set_frames(imgs, m["delays"], m["hot"])
        except Exception:
            self.pv.set_frames([], [], (0, 0))
        self.info.setText(f"{m['name']}\n{tr('lib_type_' + m['ext'][1:])} · {m['size']}×{m['size']} · {m['count']} · {m['created']}")

    def do_apply(self):
        self._apply(self.role.currentData())

    def do_apply_all(self):
        self._apply("ALL")

    def _apply(self, role):
        m = self.cur_meta()
        if not m:
            return
        try:
            data = (lib_dir() / (m["id"] + m["ext"])).read_bytes()
            ok, path = install_cursor(data, m["ext"], role)
            if ok:
                self.msg.setText(tr("applied"))
            else:
                QMessageBox.information(self, "UCCC", tr("only_win") + str(path))
        except Exception as ex:
            QMessageBox.critical(self, tr("err"), str(ex))

    def do_resize(self):
        """Re-render a saved cursor at another size (e.g. when it was drawn too small)."""
        m = self.cur_meta()
        if not m:
            return
        size = self.size_cb.currentData()
        try:
            data, ext, imgs, hot = render_cursor(lib_frames(m), m["delays"], m["n"], m.get("chot", [0, 0]), size)
            (lib_dir() / (m["id"] + m["ext"])).write_bytes(data)
            m.update(size=size, hot=list(hot), thumb=img_to_b64(small_thumb(imgs[0])))
            lib_save_meta(m)
            self.reload(m["id"])
            self.msg.setText(tr("lib_resized") + f"{size}×{size}")
        except Exception as ex:
            QMessageBox.critical(self, tr("err"), str(ex))

    def do_edit(self):
        m = self.cur_meta()
        if m:
            try:
                self.main.open_in_editor(m)
            except Exception as ex:
                QMessageBox.critical(self, tr("err"), str(ex))

    def do_rename(self):
        m = self.cur_meta()
        if not m:
            return
        name, ok = QInputDialog.getText(self, tr("lib_rename"), tr("lib_name_q"), text=m["name"])
        if ok and name.strip():
            m["name"] = name.strip()
            lib_save_meta(m)
            self.reload(m["id"])

    def do_export(self):
        m = self.cur_meta()
        if not m:
            return
        path, _ = QFileDialog.getSaveFileName(self, tr("lib_export"), m["name"] + m["ext"], f"Cursor (*{m['ext']})")
        if path:
            try:
                Path(path).write_bytes((lib_dir() / (m["id"] + m["ext"])).read_bytes())
                self.msg.setText(tr("saved") + path)
            except Exception as ex:
                QMessageBox.critical(self, tr("err"), str(ex))

    def do_delete(self):
        m = self.cur_meta()
        if m and QMessageBox.question(self, tr("lib_delete"), tr("lib_del_q"),
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                      QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            lib_delete(m)
            self.reload()

    def do_folder(self):
        try:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(lib_dir())))
        except Exception as ex:
            QMessageBox.critical(self, tr("err"), str(ex))

    def adapt(self):
        adapt_column(self.side_sa, self.pv, self.col_btns, 245)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.adapt()

    def showEvent(self, e):
        super().showEvent(e)
        QTimer.singleShot(0, self.adapt)


# ───────────────────────── main window ─────────────────────────
class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle("UCCC - Ultimate Custom Cursor Creator")
        self.resize(1220, 840)
        self.setMinimumSize(1060, 740)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self.frame = BgFrame()
        outer.addWidget(self.frame)
        fl = QVBoxLayout(self.frame)
        fl.setContentsMargins(2, 2, 2, 2)
        fl.setSpacing(0)
        self.bar = TitleBar(self)
        fl.addWidget(self.bar)
        body = QHBoxLayout()
        body.setSpacing(0)
        fl.addLayout(body, 1)
        self.stack = QStackedWidget()
        self.draw, self.acc = Studio(False), Studio(True)
        self.about = AboutPage()
        self.settings = SettingsPage(self)
        self.library = LibraryPage(self)
        for st in (self.draw, self.acc):
            st.librarySaved.connect(self.library.reload)
        for w in (self.draw, self.acc, self.library, self.settings, self.about):
            self.stack.addWidget(w)
        body.addWidget(self._sidebar())
        body.addWidget(self.stack, 1)
        self.grip = QSizeGrip(self.frame)
        self.frame.sync()

    def _sidebar(self):
        f = QFrame()
        f.setObjectName("sidebar")
        f.setFixedWidth(188)
        v = QVBoxLayout(f)
        v.setContentsMargins(10, 8, 10, 12)
        v.setSpacing(6)
        v.addWidget(Logo())
        self.nav = []
        for i, (emo, key) in enumerate((("✏️", "nav_draw"), ("🎞️", "nav_acc"), ("📚", "nav_lib"),
                                        ("⚙️", "nav_set"), ("💡", "nav_about"))):
            b = FitButton(14, 36, True)
            b.setObjectName("nav")
            b.setCheckable(True)
            b.setAutoExclusive(True)
            b.setChecked(i == 0)
            self.nav.append(b)
            bindf(lambda b=b, emo=emo, key=key: b.setText(f"{emo}  {tr(key)}"))
            b.clicked.connect(lambda _, i=i: self.stack.setCurrentIndex(i))
            v.addWidget(b)
        v.addStretch()
        ver = QLabel("v1.1.1 · free & open")
        ver.setObjectName("sub")
        v.addWidget(ver)
        return f

    def open_in_editor(self, m):
        st = self.acc if m["count"] > 1 else self.draw
        st.load_project(lib_frames(m), m["delays"], m.get("chot", [0, 0]), m["n"])
        idx = 1 if st is self.acc else 0
        self.stack.setCurrentIndex(idx)
        self.nav[idx].setChecked(True)

    def settings_changed(self):
        self.draw.settings_changed()
        self.acc.settings_changed()

    def refresh_theme(self):
        refresh_palette()
        QApplication.instance().setStyleSheet(make_qss())
        self.frame.sync()
        for s in (self.draw, self.acc):
            s.refresh_icons()
            s.rebuild_recent()
        for w in self.findChildren(QWidget):
            w.update()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.grip.move(self.frame.width() - self.grip.width() - 4, self.frame.height() - self.grip.height() - 4)
        self.grip.raise_()


def main():
    app = QApplication(sys.argv)
    load_settings()
    app.setApplicationName("UCCC")
    app.setWindowIcon(app_icon())
    if "--make-icon" in sys.argv:                      # used by build.bat
        app_icon().pixmap(256, 256).toImage().save(str(APP_DIR / "uccc.ico"), "ICO")
        return
    refresh_palette()
    app.setStyleSheet(make_qss())
    w = Main()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
