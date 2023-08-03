import json
import os
import sys
import time
import shutil
import ctypes
import pygments
import subprocess
from tkinter import *
from pygments.lexers import PythonLexer
from tkinter.scrolledtext import ScrolledText

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
elif __file__:
    application_path = os.path.dirname(__file__)

root = Tk()
root.title("Python Compiler")
root.iconbitmap(default=os.path.join(application_path, 'favicon.ico'))
root.geometry("1100x850")
root.resizable(False, False)

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

TEMP_FOLDER_PATH = os.path.join(application_path, ".codedumps")

def br(master=root):
    Label(master, text="").pack()

def highlightCode(*_):
    for tag in CODE.tag_names(index=None):
        if tag != "sel":
            CODE.tag_remove(tag, "1.0", "end")

    for line in range(int(CODE.index(END).split(".")[0])):
        if line is None:
            line = int(CODE.index("insert").split(".")[0])
        line_text = CODE.get(f"{line}.0", f"{line}.end")
        start = f"{line}.0"

        for tag in CODE.tag_names(index=None):
            if tag != "sel":
                CODE.tag_remove(tag, f"{line}.0", f"{line}.end")

        for token, content in pygments.lex(line_text, PythonLexer()):
            end = f"{start.split('.')[0]}.{int(start.split('.')[1]) + len(content)}"
            CODE.tag_add(str(token), start, end)
            start = end

def generate_font_list(self, input_dict: dict) -> list:
        font_dict = {"-family": self.font_family, "-size": self.font_size}

        for style_key, style_value in input_dict.items():
            if style_key == "family":
                font_dict["-family"] = style_value
            elif style_key == "size":
                font_dict["-size"] = style_value
            elif style_key == "bold":
                font_dict["-weight"] = "bold" if style_value else "normal"
            elif style_key == "italic":
                font_dict["-slant"] = "italic" if style_value else "roman"
            elif style_key == "underline":
                font_dict["-underline"] = style_value
            elif style_key == "strikethrough":
                font_dict["-overstrike"] = style_value

        font_list = []
        for x, y in zip(font_dict.keys(), font_dict.values()):
            font_list.extend([x, y])

        return font_list

def update_highlighter(highlighter: str="mariana") -> None:
    highlight_file = highlighter

    if highlighter in [
        x.split(".")[0] for x in os.listdir(os.path.join(application_path, "schemes"))
    ]:
        highlight_file = os.path.join(
            application_path, "schemes", highlighter + ".json"
        )
    try:
        with open(highlight_file) as file:
            CODE.configuration = json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Style configuration file not found: '{highlight_file}'"
        )

    general_props = CODE.configuration.pop("general")
    selection_props = CODE.configuration.pop("selection")
    syntax_props = CODE.configuration.pop("syntax")

    CODE.config(**general_props)
    CODE.tag_configure("sel", **selection_props)

    for key, value in syntax_props.items():
        if isinstance(value, str):
            CODE.tag_configure(key, foreground=value)
        else:
            if "font" in value:
                value["font"] = generate_font_list(value["font"])
            CODE.tag_configure(key, **value)

def paste(*_):
    if CODE.tag_ranges("sel"):
        sel_start = CODE.index("sel.first")
        CODE.delete(sel_start, CODE.index("sel.last"))
        CODE.mark_set("insert", sel_start)

    try:
        CODE.insert(INSERT, root.clipboard_get())
    except:
        pass

    CODE.event_generate("<<TextPasted>>")
    return "break"

def compile_nd_run():
    code = CODE.get(1.0, END)
    input = INPUT.get(1.0, END)
    suid = str(time.time()).replace('.', '')

    if not os.path.isdir(TEMP_FOLDER_PATH):
        os.mkdir(TEMP_FOLDER_PATH)

    USER_FOLDER = os.path.join(application_path, suid)
    os.mkdir(USER_FOLDER)

    with open(f"{USER_FOLDER}\\code.py", "w") as code_file:
        code_file.write(code)
        code_file.close()

    with open(f"{USER_FOLDER}\\input.txt", "w") as input_file:
        input_file.write(input)
        input_file.close()

    result = subprocess.run(["python", f"{USER_FOLDER}\\code.py", "<", f"{USER_FOLDER}\\input.txt"], shell=True, capture_output=True, text=True)
    OUTPUT.config(state='normal')
    OUTPUT.delete(1.0, END)
    if result.stderr:
        OUTPUT.config(fg='Red')
        OUTPUT.insert(INSERT, result.stderr)
    else:
        OUTPUT.config(fg="Green")
        OUTPUT.insert(INSERT, result.stdout)
    OUTPUT.config(state='disabled')

    if os.path.exists(f"{USER_FOLDER}") and os.path.isdir(f"{USER_FOLDER}"):
        shutil.rmtree(f"{USER_FOLDER}")

Label(root, text="Python Compiler", fg="Blue", font=("Cooper Black", 45)).pack()

br()

APP_FRAME = Frame(root)

CODE_FRAME = Frame(APP_FRAME)
Label(CODE_FRAME, text="Enter your python code below.", fg="Black", font=("Cooper Black", 20), justify=CENTER).pack()
CODE = ScrolledText(CODE_FRAME, height=9, width=45, font=("Cooper", 18))
CODE.pack()
CODE.bind("<KeyRelease>", highlightCode, add=True)
CODE.bind("<<Paste>>", paste, add=True)
highlightCode()
update_highlighter()
CODE.focus_set()
CODE_FRAME.pack()

br(APP_FRAME)

INPUT_ND_OUTPUT_FRAME = Frame(APP_FRAME)

INPUT_FRAME = Frame(INPUT_ND_OUTPUT_FRAME)
Label(INPUT_FRAME, text="Input", font=("Cooper Black", 20)).pack()
INPUT = ScrolledText(INPUT_FRAME, height=9, width=40, font=("Cooper", 18))
INPUT.pack()
INPUT_FRAME.pack(side=LEFT, padx=10)

OUTPUT_FRAME = Frame(INPUT_ND_OUTPUT_FRAME)
Label(OUTPUT_FRAME, text="Output", font=("Cooper Black", 20)).pack()
OUTPUT = ScrolledText(OUTPUT_FRAME, height=10, width=40, font=("Cooper", 16), state="disabled")
OUTPUT.pack()
OUTPUT_FRAME.pack(side=LEFT, padx=10)

INPUT_ND_OUTPUT_FRAME.pack()

br(APP_FRAME)

COMPILE_BTN = Button(APP_FRAME, text="Compile & Run", font=("Cooper Black", 20), command=compile_nd_run)

if sys.platform == "darwin" and COMPILE_BTN['command']:
    COMPILE_BTN.configure(cursor="pointinghand")
elif sys.platform.startswith("win") and COMPILE_BTN['command']:
    COMPILE_BTN.configure(cursor="hand2")

COMPILE_BTN.pack()

APP_FRAME.pack()

Label(root, text="Made with 💝 by @MrHydroCoder", font=("Cooper Black", 25)).pack(side=BOTTOM)
root.mainloop()