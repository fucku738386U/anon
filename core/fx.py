# ANON FX Engine — Full Animation & Color System
import sys
import time
import random
import os

class AnonFX:
    RESET = "[0m"
    BOLD = "[1m"
    DIM = "[2m"
    RED = "[91m"
    GREEN = "[92m"
    YELLOW = "[93m"
    BLUE = "[94m"
    MAGENTA = "[95m"
    CYAN = "[96m"
    WHITE = "[97m"
    ORANGE = "[38;5;208m"
    PINK = "[38;5;205m"
    LIME = "[38;5;118m"
    DARK_RED = "[38;5;124m"
    BG_BLACK = "[40m"
    BG_RED = "[41m"
    BG_GREEN = "[42m"
    BG_CYAN = "[46m"
    PURPLE = "[38;5;129m"

    @staticmethod
    def gradient(text, sc=(255,0,0), ec=(0,255,255)):
        r = ""
        l = len(text)
        for i, c in enumerate(text):
            if c == " ":
                r += c
                continue
            rr = int(sc[0] + (ec[0]-sc[0])*i/l)
            gg = int(sc[1] + (ec[1]-sc[1])*i/l)
            bb = int(sc[2] + (ec[2]-sc[2])*i/l)
            r += f"[38;2;{rr};{gg};{bb}m{c}"
        return r + AnonFX.RESET

    @staticmethod
    def fire_gradient(t): return AnonFX.gradient(t, (255,50,0), (255,200,0))
    @staticmethod
    def ice_gradient(t): return AnonFX.gradient(t, (0,255,255), (255,255,255))
    @staticmethod
    def blood_gradient(t): return AnonFX.gradient(t, (139,0,0), (255,0,0))
    @staticmethod
    def neon_gradient(t): return AnonFX.gradient(t, (255,0,255), (0,255,255))
    @staticmethod
    def green_gradient(t): return AnonFX.gradient(t, (0,255,0), (50,255,150))
    @staticmethod
    def gold_gradient(t): return AnonFX.gradient(t, (255,215,0), (255,140,0))
    @staticmethod
    def purple_gradient(t): return AnonFX.gradient(t, (128,0,128), (255,0,255))
    @staticmethod
    def ocean_gradient(t): return AnonFX.gradient(t, (0,105,148), (0,255,255))

    @staticmethod
    def box(text, color=CYAN, w=75, style="double"):
        top = "=" * (w-2)
        mid = text.center(w-2)
        bot = "=" * (w-2)
        if style == "double":
            return color + "[" + top + "]" + AnonFX.RESET + "
" + color + "|" + mid + "|" + AnonFX.RESET + "
" + color + "[" + bot + "]" + AnonFX.RESET
        elif style == "heavy":
            return color + "#" * w + AnonFX.RESET + "
" + color + "#" + mid + "#" + AnonFX.RESET + "
" + color + "#" * w + AnonFX.RESET
        else:
            return color + "+" + "-" * (w-2) + "+" + AnonFX.RESET + "
" + color + "|" + mid + "|" + AnonFX.RESET + "
" + color + "+" + "-" * (w-2) + "+" + AnonFX.RESET

    @staticmethod
    def progress(c, t, w=40, color=GREEN):
        if t == 0: t = 1
        p = c/t
        f = int(w*p)
        b = "#"*f + "."*(w-f)
        return f"{color}[{b}] {p*100:.1f}%{AnonFX.RESET}"

    @staticmethod
    def spinner(d=1, msg="Loading"):
        frames = ["|", "/", "-", "\", "*", "+", "x", "o"]
        e = time.time() + d
        i = 0
        while time.time() < e:
            sys.stdout.write(f"
{AnonFX.CYAN}{frames[i%len(frames)]} {msg}...{AnonFX.RESET}")
            sys.stdout.flush()
            time.sleep(0.08)
            i += 1
        sys.stdout.write("
" + " "*60 + "
")

    @staticmethod
    def typing_effect(text, delay=0.015, color=WHITE):
        for c in text:
            sys.stdout.write(f"{color}{c}{AnonFX.RESET}")
            sys.stdout.flush()
            time.sleep(delay)
        print()

    @staticmethod
    def glitch_text(text, iters=3):
        g = ["#", "@", "$", "%", "&", "*", "!", "?"]
        for _ in range(iters):
            gl = ""
            for c in text:
                gl += random.choice(g) if random.random()<0.3 else c
            sys.stdout.write(f"
{AnonFX.RED}{gl}{AnonFX.RESET}")
            sys.stdout.flush()
            time.sleep(0.08)
        sys.stdout.write(f"
{text}
")

    @staticmethod
    def matrix(d=1.5, w=80):
        chars = "0123456789ABCDEF@#$%&*01anon"
        e = time.time() + d
        while time.time() < e:
            line = ""
            for _ in range(w):
                if random.random()<0.1:
                    line += f"{AnonFX.GREEN}{random.choice(chars)}{AnonFX.RESET}"
                else:
                    line += f"{AnonFX.DIM}{AnonFX.GREEN}{random.choice(chars)}{AnonFX.RESET}"
            sys.stdout.write(f"
{line}")
            sys.stdout.flush()
            time.sleep(0.05)
        print()

    @staticmethod
    def banner():
        lines = [
            "",
            AnonFX.blood_gradient("    ANON MONSTER SCRAPER v2.0"),
            AnonFX.fire_gradient("    =========================="),
            "",
            AnonFX.gradient("         ADVANCED EDITION", (255,0,128), (0,255,128)),
            AnonFX.DIM + AnonFX.CYAN + "         Created by anonymous | anonymous.world" + AnonFX.RESET,
            ""
        ]
        for l in lines:
            print(l)
            time.sleep(0.05)

    @staticmethod
    def status(site, status, color=GREEN):
        ts = time.strftime("%H:%M:%S")
        icons = {"running":">>","success":"OK","error":"XX","warning":"!!","found":"$$","scanning":"??","done":"=="}
        icon = icons.get(status.lower(), "--")
        return f"{AnonFX.DIM}[{ts}]{AnonFX.RESET} {color}{icon} {site:<35} {status.upper()}{AnonFX.RESET}"

    @staticmethod
    def cccard(num, exp, cvv, name="", bank="", country=""):
        top = "+" + "="*42 + "+"
        mid1 = "|  $$ " + num.ljust(36) + "|"
        mid2 = "|  EXP: " + exp.ljust(10) + "  CVV: " + cvv.ljust(8) + "         |"
        mid3 = "|  NAME: " + name.ljust(33) + "|"
        mid4 = "|  BANK: " + bank.ljust(20) + " COUNTRY: " + country.ljust(6) + "|"
        bot = "+" + "="*42 + "+"
        return f"
{AnonFX.CYAN}{top}{AnonFX.RESET}
{AnonFX.CYAN}{mid1}{AnonFX.RESET}
{AnonFX.CYAN}{mid2}{AnonFX.RESET}
{AnonFX.CYAN}{mid3}{AnonFX.RESET}
{AnonFX.CYAN}{mid4}{AnonFX.RESET}
{AnonFX.CYAN}{bot}{AnonFX.RESET}
"

fx = AnonFX()
