import ast
import math
import operator

import flet as ft


def calculate(expression: str) -> str:
    """
    دالة آمنة لحساب النتيجة بدون استخدام eval مباشرة.
    """
    expression = expression.strip()
    if not expression:
        return ""

    tree = ast.parse(expression, mode="eval")

    def eval_node(node):
        if isinstance(node, ast.Expression):
            return eval_node(node.body)

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("قيمة غير مسموحة")

        if isinstance(node, ast.BinOp):
            operations = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.FloorDiv: operator.floordiv,
                ast.Mod: operator.mod,
                ast.Pow: operator.pow,
            }

            op = operations.get(type(node.op))
            if op is None:
                raise ValueError("عملية غير مسموحة")

            return op(eval_node(node.left), eval_node(node.right))

        if isinstance(node, ast.UnaryOp):
            value = eval_node(node.operand)

            if isinstance(node.op, ast.UAdd):
                return +value

            if isinstance(node.op, ast.USub):
                return -value

            raise ValueError("عملية غير مسموحة")

        raise ValueError("تعبير غير مسموح")

    result = eval_node(tree)

    if isinstance(result, float):
        if not math.isfinite(result):
            raise OverflowError("النتيجة غير صالحة")

        if result.is_integer():
            result = int(result)
        else:
            result = round(result, 10)

    return str(result)


def main(page: ft.Page):
    page.title = "آلة حاسبة"
    page.bgcolor = "#111111"
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    expression = ""

    display = ft.Text(
        value="0",
        size=42,
        color="#FFFFFF",
        text_align=ft.TextAlign.RIGHT,
        width=320,
        max_lines=1,
    )

    def update_display():
        display.value = expression if expression else "0"
        page.update()

    def press(key: str):
        nonlocal expression

        if expression.startswith("خطأ"):
            expression = ""

        if key == "C":
            expression = ""

        elif key == "⌫":
            expression = expression[:-1]

        elif key == "=":
            if expression:
                try:
                    expression = calculate(expression)
                except ZeroDivisionError:
                    expression = "خطأ: قسمة على صفر"
                except Exception:
                    expression = "خطأ"

        elif key == ".":
            last_operator_index = -1

            for op in "+-*/":
                index = expression.rfind(op)
                if index > last_operator_index:
                    last_operator_index = index

            current_part = expression[last_operator_index + 1:]

            if "." in current_part:
                return

            if current_part:
                expression += "."
            else:
                expression += "0."

        elif key in "+-*/":
            if not expression:
                if key == "-":
                    expression = "-"
                update_display()
                return

            if expression[-1] in "+-*/":
                if key == "-" and expression[-1] in "*/":
                    expression += key
                else:
                    expression = expression[:-1] + key
            else:
                expression += key

        else:
            expression += key

        update_display()

    def btn(text: str, bg: str = "#2D2D2D", fg: str = "#FFFFFF", width: int = 80):
        return ft.ElevatedButton(
            text=text,
            width=width,
            height=65,
            style=ft.ButtonStyle(
                bgcolor=bg,
                color=fg,
                text_style=ft.TextStyle(size=24),
            ),
            on_click=lambda e, t=text: press(t),
        )

    display_container = ft.Container(
        content=display,
        width=360,
        bgcolor="#1E1E1E",
        border_radius=15,
        padding=15,
    )

    calculator = ft.Column(
        controls=[
            display_container,
            ft.Row(
                controls=[
                    btn("C", bg="#E53935"),
                    btn("⌫", bg="#555555"),
                    btn("/", bg="#FF9500"),
                    btn("*", bg="#FF9500"),
                ],
                spacing=8,
            ),
            ft.Row(
                controls=[
                    btn("7"),
                    btn("8"),
                    btn("9"),
                    btn("-", bg="#FF9500"),
                ],
                spacing=8,
            ),
            ft.Row(
                controls=[
                    btn("4"),
                    btn("5"),
                    btn("6"),
                    btn("+", bg="#FF9500"),
                ],
                spacing=8,
            ),
            ft.Row(
                controls=[
                    btn("1"),
                    btn("2"),
                    btn("3"),
                    btn("=", bg="#4CAF50"),
                ],
                spacing=8,
            ),
            ft.Row(
                controls=[
                    btn("0", width=256),
                    btn(".", width=80),
                ],
                spacing=8,
            ),
        ],
        spacing=8,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    page.add(calculator)


if __name__ == "__main__":
    ft.app(target=main)
