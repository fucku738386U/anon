
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
    def fire(t): return AnonFX.gradient(t, (255,50,0), (255,200,0))
    @staticmethod
    def ice(t): return AnonFX.gradient(t, (0,255,255), (255,255,255))
    @staticmethod
    def blood(t): return AnonFX.gradient(t, (139,0,0), (255,0,0))
    @staticmethod
    def neon(t): return AnonFX.gradient(t, (255,0,255), (0,255,255))
    @staticmethod
    def green(t): return AnonFX.gradient(t, (0,255,0), (50,255,150))
    @staticmethod
    def gold(t): return AnonFX.gradient(t, (255,215,0), (255,140,0))

    @staticmethod
    def box(text, color=CYAN, w=70, style="double"):
        if style == "double":
            return f"{color}╔{'═'*(w-2)}╗\n║{text.center(w-2)}║\n╚{'═'*(w-2)}╝{AnonFX.RESET}"
        elif style == "heavy":
            return f"{color}{'█'*w}\n█{text.center(w-2)}█\n{'█'*w}{AnonFX.RESET}"
        else:
            return f"{color}┌{'─'*(w-2)}┐\n│{text.center(w-2)}│\n└{'─'*(w-2)}┘{AnonFX.RESET}"

    @staticmethod
    def progress(c, t, w=40, color=GREEN):
        p = c/t
        f = int(w*p)
        b = "█"*f + "░"*(w-f)
        return f"{color}[{b}] {p*100:.1f}%{AnonFX.RESET}"

    @staticmethod
    def spinner(d=1, msg="Loading"):
        frames = ["◐","◓","◑","◒","🌀","💀","🔥","🚀"]
        e = time.time() + d
        i = 0
        while time.time() < e:
            sys.stdout.write(f"\r{AnonFX.CYAN}{frames[i%len(frames)]} {msg}...{AnonFX.RESET}")
            sys.stdout.flush()
            time.sleep(0.08)
            i += 1
        sys.stdout.write("\r" + " "*50 + "\r")

    @staticmethod
    def typefx(text, delay=0.015, color=WHITE):
        for c in text:
            sys.stdout.write(f"{color}{c}{AnonFX.RESET}")
            sys.stdout.flush()
            time.sleep(delay)
        print()

    @staticmethod
    def glitch(text, iters=3):
        g = ["█","▓","▒","░","▀","▄","▌","▐","▖","▗","▘","▙","▚","▛","▜","▝","▞","▟"]
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
            AnonFX.blood("    ░█████╗░███╗░░██╗░█████╗░███╗░░██╗"),
            AnonFX.fire("    ██╔══██╗████╗░██║██╔══██╗████╗░██║"),
            AnonFX.neon("    ███████║██╔██╗██║██║░░██║██╔██╗██║"),
            AnonFX.ice("    ██╔══██║██║╚████║██║░░██║██║╚████║"),
            AnonFX.blood("    ██║░░██║██║░╚███║╚█████╔╝██║░╚███║"),
            AnonFX.fire("    ╚═╝░░╚═╝╚═╝░░╚══╝░╚════╝░╚═╝░░╚══╝"),
            "",
            AnonFX.gradient("         🌀 ADVANCED SCRAPER v2.0 🕳️", (255,0,128), (0,255,128)),
            AnonFX.DIM + AnonFX.CYAN + "         Created by anonymous | anonymous.world" + AnonFX.RESET,
            ""
        ]
        for l in lines:
            print(l)
            time.sleep(0.05)

    @staticmethod
    def status(site, status, color=GREEN):
        ts = time.strftime("%H:%M:%S")
        icons = {"running":"▶️","success":"✅","error":"❌","warning":"⚠️","found":"💳","scanning":"🔍","done":"🏁"}
        return f"{AnonFX.DIM}[{ts}]{AnonFX.RESET} {color}{icons.get(status.lower(),'⏳')} {site:<30} {status.upper()}{AnonFX.RESET}"

    @staticmethod
    def cccard(num, exp, cvv, name="", bank=""):
        return f"""
{AnonFX.BG_BLACK}{AnonFX.CYAN}╔══════════════════════════════════════╗{AnonFX.RESET}
{AnonFX.BG_BLACK}{AnonFX.CYAN}║  {AnonFX.YELLOW}💳 {AnonFX.WHITE}{num:<32}{AnonFX.CYAN}║{AnonFX.RESET}
{AnonFX.BG_BLACK}{AnonFX.CYAN}║  {AnonFX.DIM}EXP: {AnonFX.WHITE}{exp:<8}  CVV: {AnonFX.WHITE}{cvv:<8}{AnonFX.CYAN}     ║{AnonFX.RESET}
{AnonFX.BG_BLACK}{AnonFX.CYAN}║  {AnonFX.DIM}NAME: {AnonFX.WHITE}{name:<29}{AnonFX.CYAN}║{AnonFX.RESET}
{AnonFX.BG_BLACK}{AnonFX.CYAN}║  {AnonFX.DIM}BANK: {AnonFX.ORANGE}{bank:<28}{AnonFX.CYAN}║{AnonFX.RESET}
{AnonFX.BG_BLACK}{AnonFX.CYAN}╚══════════════════════════════════════╝{AnonFX.RESET}
"""


    # Aliases for backward compatibility
    typing_effect = typefx
    fire_gradient = fire
    ice_gradient = ice
    blood_gradient = blood
    neon_gradient = neon
    green_gradient = green
    gold_gradient = gold
    glitch_text = glitch
fx = AnonFX()
