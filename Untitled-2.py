
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import FancyArrowPatch, Circle

# ============================================================
# IPC ANIMATION — PIPE / SOCKET / MEMORY MAPPING
# Плавная учебная анимация
# ============================================================

FPS = 24
FRAMES_PER_STEP = 48
STEPS = 6
SCENES = 3

TOTAL_FRAMES = FPS * 30

# Цвета
BG = "#f7f8fa"
DARK = "#334155"
MUTED = "#718096"
BLUE = "#4785bb"
GREEN = "#43966b"
ORANGE = "#df9348"

PROCESS = "#eaf1f8"
PROCESS_EDGE = "#8198ae"

BUFFER = "#fff2d5"
BUFFER_EDGE = "#d3a84c"

SHARED = "#e7f3e9"
SHARED_EDGE = "#6caa7b"

PURPLE = "#f0eafa"
PURPLE_EDGE = "#a18bc0"

fig, ax = plt.subplots(figsize=(14, 8))
fig.patch.set_facecolor(BG)

plt.subplots_adjust(
    left=0.04,
    right=0.96,
    top=0.88,
    bottom=0.16
)

# ------------------------------------------------------------
# РИСОВАНИЕ
# ------------------------------------------------------------

def box(x, y, w, h, text, color, edge, fontsize=10):
    rect = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.06,rounding_size=0.12",
        facecolor=color,
        edgecolor=edge,
        linewidth=1.5,
        zorder=3
    )
    ax.add_patch(rect)

    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        color=DARK,
        zorder=4
    )


def proc(x, y, name):
    box(
        x, y, 2.3, 1.15,
        name + "\nВиртуальная память",
        PROCESS,
        PROCESS_EDGE,
        10
    )


def arrow(start, end, color=BLUE, width=1.8):
    a = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=16,
        linewidth=width,
        color=color,
        zorder=2
    )
    ax.add_patch(a)


def moving_packet(start, end, t, text="DATA"):
    # Плавное ускорение и замедление
    t = np.clip(t, 0, 1)
    smooth = t * t * (3 - 2 * t)

    x = start[0] + (end[0] - start[0]) * smooth
    y = start[1] + (end[1] - start[1]) * smooth

    circle = Circle(
        (x, y),
        0.20,
        facecolor=ORANGE,
        edgecolor="#ad7139",
        linewidth=1.2,
        zorder=8
    )
    ax.add_patch(circle)

    ax.text(
        x, y,
        text,
        ha="center",
        va="center",
        fontsize=6,
        color="white",
        fontweight="bold",
        zorder=9
    )


def title(main, sub):
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9)
    ax.axis("off")
    ax.set_facecolor(BG)

    ax.text(
        6, 8.55,
        main,
        ha="center",
        fontsize=19,
        fontweight="bold",
        color=DARK
    )

    ax.text(
        6, 8.10,
        sub,
        ha="center",
        fontsize=10,
        color=MUTED
    )


def info(heading, description):
    # Отдельная область пояснений
    box(
        0.5, 0.25, 11, 1.05,
        "",
        "#ffffff",
        "#dce2e8"
    )

    ax.text(
        6, 0.91,
        heading,
        ha="center",
        fontsize=11,
        fontweight="bold",
        color=DARK
    )

    ax.text(
        6, 0.55,
        description,
        ha="center",
        fontsize=9,
        color=MUTED
    )


def phase(frame):
    index = min(frame // FRAMES_PER_STEP, STEPS - 1)
    t = (frame % FRAMES_PER_STEP) / FRAMES_PER_STEP

    return index, t


# ============================================================
# SCENE 1 — PIPE
# ============================================================

PIPE_TEXT = [
    ("Создание канала", "pipe() создаёт канал и два файловых дескриптора."),
    ("Подключение процессов", "Один конец используется для записи, другой — для чтения."),
    ("Запись данных", "Процесс A вызывает write() и помещает данные в канал."),
    ("Буфер ядра", "Переданные байты временно хранятся в буфере PIPE."),
    ("Чтение данных", "Процесс B вызывает read() и получает данные в свою память."),
    ("Завершение обмена", "После получения данных процесс B может продолжить работу.")
]


def draw_pipe(frame):
    s, t = phase(frame)

    title(
        "1. PIPE — взаимодействие через канал",
        "Два процесса обмениваются данными через буфер операционной системы"
    )

    proc(0.7, 5.1, "ПРОЦЕСС A")
    proc(9.0, 5.1, "ПРОЦЕСС B")

    # Буферы процессов
    box(
        0.9, 4.0, 1.9, 0.65,
        "Выходной буфер",
        "#f0f4fa", PROCESS_EDGE, 9
    )

    box(
        9.2, 4.0, 1.9, 0.65,
        "Входной буфер",
        "#f0f4fa", PROCESS_EDGE, 9
    )

    # Канал
    box(
        4.4, 3.85, 3.2, 1.0,
        "БУФЕР PIPE\nЯдро операционной системы",
        BUFFER, BUFFER_EDGE, 10
    )

    # Постоянные соединения
    if s >= 1:
        arrow((2.8, 4.3), (4.35, 4.3))
        arrow((7.65, 4.3), (9.15, 4.3))

        ax.text(3.55, 4.65, "write end",
                ha="center", fontsize=8, color=MUTED)

        ax.text(8.4, 4.65, "read end",
                ha="center", fontsize=8, color=MUTED)

    # Этап 0
    if s == 0:
        box(4.7, 2.4, 2.6, 0.65,
            "pipe()", "#edf3fa", BLUE, 12)

    # Этап 2 — запись
    if s == 2:
        moving_packet(
            (2.8, 4.3),
            (4.35, 4.3),
            t
        )

    # Этап 3 — данные внутри буфера
    if s >= 3:
        box(
            5.0, 4.15, 0.65, 0.35,
            "DATA",
            ORANGE, "#ad7139", 8
        )

        if s == 3:
            arrow((4.9, 3.65), (7.1, 3.65), GREEN)

    # Этап 4 — чтение
    if s == 4:
        moving_packet(
            (7.65, 4.3),
            (9.15, 4.3),
            t
        )

    if s >= 5:
        box(
            9.35, 2.85, 1.6, 0.6,
            "Данные получены",
            SHARED, SHARED_EDGE, 9
        )

    if s == 0:
        info(*PIPE_TEXT[0])
    elif s == 1:
        info(*PIPE_TEXT[1])
    elif s == 2:
        info(*PIPE_TEXT[2])
    elif s == 3:
        info(*PIPE_TEXT[3])
    elif s == 4:
        info(*PIPE_TEXT[4])
    else:
        info(*PIPE_TEXT[5])


# ============================================================
# SCENE 2 — SOCKET
# ============================================================

SOCKET_TEXT = [
    ("Создание серверного сокета", "socket() создаёт сокет для будущего взаимодействия."),
    ("Подготовка сервера", "bind() задаёт адрес, listen() переводит сокет в режим ожидания."),
    ("Запросы клиентов", "Клиенты создают сокеты и вызывают connect()."),
    ("Установление соединений", "accept() принимает подключение и возвращает отдельный сокет."),
    ("Передача данных", "send() помещает данные в буфер отправки сокета."),
    ("Получение данных", "recv() читает данные из буфера приёма серверного сокета.")
]


def draw_socket(frame):
    s, t = phase(frame)

    title(
        "2. SOCKET — клиент-серверное взаимодействие",
        "Один сервер может одновременно обслуживать несколько клиентов"
    )

    # Сервер
    proc(4.85, 6.45, "СЕРВЕР")

    # Клиенты
    proc(0.55, 1.75, "КЛИЕНТ 1")
    proc(4.85, 1.75, "КЛИЕНТ 2")
    proc(9.15, 1.75, "КЛИЕНТ 3")

    # Серверный сокет
    box(
        5.0, 5.65, 2.0, 0.55,
        "Listening socket",
        "#edf3fa", BLUE, 9
    )

    if s >= 1:
        arrow((5.85, 6.45), (6.0, 6.22))

    # Буферы соединений
    buffer_x = [0.8, 5.15, 9.5]

    if s >= 3:
        for i, x in enumerate(buffer_x):
            box(
                x, 3.8, 1.7, 0.8,
                f"Сокет {i+1}\nБуферы",
                BUFFER, BUFFER_EDGE, 9
            )

    # Соединения клиентов с сервером
    if s >= 3:
        for i, x in enumerate(buffer_x):
            arrow(
                (x + 0.85, 4.65),
                (5.95, 5.55),
                BLUE,
                1.4
            )

            arrow(
                (1.7 + i * 4.3, 2.9),
                (x + 0.85, 3.7),
                BLUE,
                1.4
            )

    # Запрос клиента 1
    if s == 2:
        box(
            4.7, 3.0, 2.6, 0.5,
            "connect()",
            "#edf3fa", BLUE, 10
        )

    # Передача данных от клиента 1
    if s == 4:
        moving_packet(
            (2.5, 4.15),
            (4.95, 4.15),
            t
        )

        arrow(
            (5.9, 4.7),
            (5.9, 5.6),
            GREEN
        )

    # Сервер получает данные
    if s >= 5:
        box(
            5.0, 5.0, 1.9, 0.45,
            "recv()",
            SHARED, SHARED_EDGE, 10
        )

    # Этапы
    info(*SOCKET_TEXT[s])


# ============================================================
# SCENE 3 — MEMORY MAPPING
# ============================================================

MEMORY_TEXT = [
    ("Создание объекта памяти", "Создаётся общий объект памяти: например, через shm_open()."),
    ("Первое отображение", "Процесс A вызывает mmap() и получает доступ к общей области."),
    ("Подключение остальных процессов", "B, C и D отображают тот же объект с MAP_SHARED."),
    ("Запись данных", "Процесс A изменяет содержимое общей области памяти."),
    ("Синхронизация", "Mutex или semaphore регулирует доступ к общим данным."),
    ("Чтение данных", "Другие процессы читают изменения через собственные отображения.")
]


def draw_memory(frame):
    s, t = phase(frame)

    title(
        "3. MEMORY MAPPING — отображение общей памяти",
        "Несколько процессов работают с одним общим объектом памяти"
    )

    # Четыре процесса
    proc(0.45, 6.3, "ПРОЦЕСС A")
    proc(9.25, 6.3, "ПРОЦЕСС B")
    proc(0.45, 1.7, "ПРОЦЕСС C")
    proc(9.25, 1.7, "ПРОЦЕСС D")

    # Общая память
    box(
        4.05, 3.45, 3.9, 1.45,
        "ОБЩАЯ ОБЛАСТЬ ПАМЯТИ\n\nShared Memory\nMAP_SHARED",
        SHARED, SHARED_EDGE, 12
    )

    # Отображения
    connections = [
        ((2.75, 6.3), (4.4, 4.9)),
        ((9.25, 6.3), (7.6, 4.9)),
        ((2.75, 2.85), (4.4, 3.45)),
        ((9.25, 2.85), (7.6, 3.45))
    ]

    if s >= 2:
        for start, end in connections:
            arrow(start, end, BLUE, 1.8)

    # Создание объекта
    if s == 0:
        box(
            4.7, 5.25, 2.6, 0.6,
            "shm_open()",
            "#edf3fa", BLUE, 11
        )

    # mmap
    if s == 1:
        box(
            4.7, 5.25, 2.6, 0.6,
            "mmap()",
            "#edf3fa", BLUE, 11
        )

    if s == 2:
        box(
            4.55, 5.25, 2.9, 0.6,
            "mmap() × 4",
            "#edf3fa", BLUE, 11
        )

    # Запись
    if s == 3:
        moving_packet(
            (2.75, 6.3),
            (4.4, 4.9),
            t
        )

    # Синхронизация
    if s >= 4:
        box(
            4.65, 5.25, 2.7, 0.6,
            "MUTEX / SEMAPHORE",
            PURPLE, PURPLE_EDGE, 9
        )

    # Чтение
    if s == 5:
        moving_packet(
            (7.6, 4.0),
            (9.25, 2.85),
            t
        )

    info(*MEMORY_TEXT[s])


# ============================================================
# ОБНОВЛЕНИЕ КАДРОВ
# ============================================================

FRAMES_PER_SCENE = STEPS * FRAMES_PER_STEP
TOTAL_FRAMES = SCENES * FRAMES_PER_SCENE


def update(frame):
    ax.clear()

    scene = frame // FRAMES_PER_SCENE
    local_frame = frame % FRAMES_PER_SCENE

    if scene == 0:
        draw_pipe(local_frame)

    elif scene == 1:
        draw_socket(local_frame)

    else:
        draw_memory(local_frame)

    return []


animation = FuncAnimation(
    fig,
    update,
    frames=TOTAL_FRAMES,
    interval=1000 / FPS,
    blit=False,
    repeat=True
)

# Сохранение
print("Создаём плавную анимацию...")

animation.save(
    "ipc_animation_smooth.gif",
    writer=PillowWriter(fps=FPS),
    dpi=110
)

print("Готово: ipc_animation_smooth.gif")

plt.show()
