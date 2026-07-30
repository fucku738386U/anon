# ANON FX Engine — Full Animation & Color System
import sys
import time
import random
import os

class AnonFX:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    ORANGE = "\033[38;5;208m"
    PINK = "\033[38;5;205m"
    LIME = "\033[38;5;118m"
    DARK_RED = "\033[38;5;124m"
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_CYAN = "\033[46m"
    PURPLE = "\033[38;5;129m"

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
            r += f"\033[38;2;{rr};{gg};{bb}m{c}"
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
        if style == "double":
            return f"{color}\u2554{'\u2550'*(w-2)}\u2557\n\u2551{text.center(w-2)}\u2551\n\u255a{'\u2550'*(w-2)}\u255d{AnonFX.RESET}"
        elif style == "heavy":
            return f"{color}{'\u2588'*w}\n\u2588{text.center(w-2)}\u2588\n{'\u2588'*w}{AnonFX.RESET}"
        else:
            return f"{color}\u250c{'\u2500'*(w-2)}\u2510\n\u2502{text.center(w-2)}\u2502\n\u2514{'\u2500'*(w-2)}\u2518{AnonFX.RESET}"

    @staticmethod
    def progress(c, t, w=40, color=GREEN):
        if t == 0: t = 1
        p = c/t
        f = int(w*p)
        b = "\u2588"*f + "\u2591"*(w-f)
        return f"{color}[{b}] {p*100:.1f}%{AnonFX.RESET}"

    @staticmethod
    def spinner(d=1, msg="Loading"):
        frames = ["\u25d0","\u25d3","\u25d1","\u25d2","\ud83c\udf00","\ud83d\udc80","\ud83d\udd25","\ud83d\ude80"]
        e = time.time() + d
        i = 0
        while time.time() < e:
            sys.stdout.write(f"\r{AnonFX.CYAN}{frames[i%len(frames)]} {msg}...{AnonFX.RESET}")
            sys.stdout.flush()
            time.sleep(0.08)
            i += 1
        sys.stdout.write("\r" + " "*60 + "\r")

    @staticmethod
    def typing_effect(text, delay=0.015, color=WHITE):
        for c in text:
            sys.stdout.write(f"{color}{c}{AnonFX.RESET}")
            sys.stdout.flush()
            time.sleep(delay)
        print()

    @staticmethod
    def glitch_text(text, iters=3):
        g = ["\u2588","\u2593","\u2592","\u2591","\u2580","\u2584","\u258c","\u2590"]
        for _ in range(iters):
            gl = ""
            for c in text:
                gl += random.choice(g) if random.random()<0.3 else c
            sys.stdout.write(f"\r{AnonFX.RED}{gl}{AnonFX.RESET}")
            sys.stdout.flush()
            time.sleep(0.08)
        sys.stdout.write(f"\r{text}\n")

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
            sys.stdout.write(f"\r{line}")
            sys.stdout.flush()
            time.sleep(0.05)
        print()

    @staticmethod
    def banner():
        lines = [
            "",
            AnonFX.blood_gradient("    \u2588\u2588\u2588\u2588\u2588\u2588\u2588 \u2588\u2588\u2588 \u2588\u2588\u2588\u2588\u2588\u2588\u2588 \u2588\u2588\u2588 \u2588\u2588\u2588\u2588\u2588\u2588\u2588"),
            AnonFX.fire_gradient("    \u2588\u2588      \u2588\u2588\u2588 \u2588\u2588      \u2588\u2588\u2588 \u2588\u2588     "),
            AnonFX.neon_gradient("    \u2588\u2588\u2588\u2588\u2588\u2588\u2588 \u2588\u2588\u2588 \u2588\u2588      \u2588\u2588\u2588 \u2588\u2588\u2588\u2588\u2588\u2588\u2588"),
            AnonFX.ice_gradient("    \u2588\u2588      \u2588\u2588\u2588 \u2588\u2588      \u2588\u2588\u2588      \u2588\u2588"),
            AnonFX.blood_gradient("    \u2588\u2588      \u2588\u2588\u2588 \u2588\u2588\u2588\u2588\u2588\u2588\u2588 \u2588\u2588\u2588 \u2588\u2588\u2588\u2588\u2588\u2588\u2588"),
            "",
            AnonFX.gradient("         \ud83c\udf00 ADVANCED SCRAPER v2.0 \ud83d\udd73\ufe0f", (255,0,128), (0,255,128)),
            AnonFX.DIM + AnonFX.CYAN + "         Created by anonymous | anonymous.world" + AnonFX.RESET,
            ""
        ]
        for l in lines:
            print(l)
            time.sleep(0.05)

    @staticmethod
    def status(site, status, color=GREEN):
        ts = time.strftime("%H:%M:%S")
        icons = {"running":"\u25b6\ufe0f","success":"\u2705","error":"\u274c","warning":"\u26a0\ufe0f","found":"\ud83d\udcb3","scanning":"\ud83d\udd0d","done":"\ud83c\udfc1"}
        return f"{AnonFX.DIM}[{ts}]{AnonFX.RESET} {color}{icons.get(status.lower(),'\u23f3')} {site:<35} {status.upper()}{AnonFX.RESET}"

    @staticmethod
    def cccard(num, exp, cvv, name="", bank="", country=""):
        return f"""
{AnonFX.BG_BLACK}{AnonFX.CYAN}\u2554{'\u2550'*42}\u2557{AnonFX.RESET}
{AnonFX.BG_BLACK}{AnonFX.CYAN}\u2551  {AnonFX.YELLOW}\ud83d\udcb3 {AnonFX.WHITE}{num:<36}{AnonFX.CYAN}\u2551{AnonFX.RESET}
{AnonFX.BG_BLACK}{AnonFX.CYAN}\u2551  {AnonFX.DIM}EXP: {AnonFX.WHITE}{exp:<10}  CVV: {AnonFX.WHITE}{cvv:<8}{AnonFX.CYAN}         \u2551{AnonFX.RESET}
{AnonFX.BG_BLACK}{AnonFX.CYAN}\u2551  {AnonFX.DIM}NAME: {AnonFX.WHITE}{name:<33}{AnonFX.CYAN}\u2551{AnonFX.RESET}
{AnonFX.BG_BLACK}{AnonFX.CYAN}\u2551  {AnonFX.DIM}BANK: {AnonFX.ORANGE}{bank:<20} {AnonFX.DIM}COUNTRY: {AnonFX.WHITE}{country:<6}{AnonFX.CYAN}\u2551{AnonFX.RESET}
{AnonFX.BG_BLACK}{AnonFX.CYAN}\u255a{'\u2550'*42}\u255d{AnonFX.RESET}
"""

fx = AnonFX()
