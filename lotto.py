import random
import tkinter as tk
from datetime import datetime

SETS = 5
NUMS_PER_SET = 6

# 로또 공식 번호대별 색상: (배경, 글자)
RANGE_COLORS = [
    (10, "#FBC400", "black"),  # 1~10  노랑
    (20, "#69C8F2", "black"),  # 11~20 파랑
    (30, "#FF7272", "white"),  # 21~30 빨강
    (40, "#AAAAAA", "white"),  # 31~40 회색
    (45, "#B0D840", "black"),  # 41~45 초록
]


def ball_colors(number):
    for limit, bg, fg in RANGE_COLORS:
        if number <= limit:
            return bg, fg


class LottoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("로또 번호 생성기")
        self.resizable(False, False)
        self.configure(padx=20, pady=20)

        self.date_label = tk.Label(self, font=("맑은 고딕", 12))
        self.date_label.pack()

        tk.Button(
            self,
            text="번호 뽑기",
            font=("맑은 고딕", 14, "bold"),
            command=self.generate,
        ).pack(pady=12)

        self.canvas = tk.Canvas(self, width=380, height=SETS * 50, highlightthickness=0)
        self.canvas.pack()

        self.generate()

    def generate(self):
        self.date_label.config(text=datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S"))
        self.canvas.delete("all")

        for row in range(SETS):
            numbers = sorted(random.sample(range(1, 46), NUMS_PER_SET))
            y = row * 50 + 25
            self.canvas.create_text(
                15, y, text=chr(ord("A") + row), font=("맑은 고딕", 12, "bold")
            )
            for col, n in enumerate(numbers):
                x = 60 + col * 55
                bg, fg = ball_colors(n)
                self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill=bg, outline="")
                self.canvas.create_text(
                    x, y, text=str(n), fill=fg, font=("맑은 고딕", 13, "bold")
                )


if __name__ == "__main__":
    LottoApp().mainloop()
