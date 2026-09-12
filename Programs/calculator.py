from __future__ import annotations
import ast
import operator
import os
import sys
from pathlib import Path

# Optional readline import for better terminal editing
try:
    import readline
except ImportError:
    pass  # readline not available on all platforms

PKGNAME = "CoreOS.Calculator"
PKGVER = "1.0"

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def eval_expr(node):
    if isinstance(node, ast.Expression):
        return eval_expr(node.body)
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        left = eval_expr(node.left)
        right = eval_expr(node.right)
        op = OPS[type(node.op)]
        return op(left, right)
    if isinstance(node, ast.UnaryOp):
        operand = eval_expr(node.operand)
        op = OPS[type(node.op)]
        return op(operand)
    raise ValueError("Unsupported expression")


def main() -> None:
    clear_screen()
    print("CoreOS Calculator")
    print("Type expressions like 2 + 3 * (4 - 1). Type 'exit' to quit.")
    try:
        while True:
            try:
                line = input("calc> ").strip()
            except EOFError:
                break
            if not line:
                continue
            if line.lower() in {"exit", "quit"}:
                break
            try:
                tree = ast.parse(line, mode="eval")
                result = eval_expr(tree)
                print(result)
            except Exception as exc:
                print(f"Error: {exc}")
    except KeyboardInterrupt:
        print("\n\nCalculator interrupted.")


if __name__ == "__main__":
    main()
