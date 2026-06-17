#!/usr/bin/env python3
"""Worked example — a small layered architecture diagram demonstrating the toolkit.

Run it to (re)generate the canonical sample shipped with the skill:
    python example_diagram.py
Writes example-architecture.excalidraw + (with render_preview) example-architecture.png
into the skill root. Use it as a reference for what "good" looks like.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from excalidraw_snetor import (Scene, SKILL_ROOT, GREEN, GREEN_DARK, GREEN05, GREEN10, GREEN20,
                               NAVY, EMERALD, BLUE_GREEN, SUBTLE, MUTED, WHITE)

def build():
    s = Scene()
    # Header: brand logo + title
    s.image(100, 48, 42, "snetor_full_logo.png")
    s.text(260, 28, "Exemple — architecture applicative (Snetor)", size=24, color=NAVY)
    s.text(260, 62, "Socle commun + applications, icônes de service embarquées", size=14, color=SUBTLE)

    # External actor
    s.boxlabel(40, 250, 180, 60, "Utilisateurs", fill=GREEN05, stroke=GREEN, size=15)

    # Subscription container
    s.rect(260, 110, 700, 510, fill=GREEN05, stroke=GREEN, sw=3)
    s.text(282, 124, "Abonnement Azure (exemple)", size=16, color=GREEN_DARK)
    s.image(920, 140, 32, "azure.png")

    # Socle band
    s.rect(285, 168, 650, 175, fill=WHITE, stroke=GREEN20)
    s.text(305, 178, "Socle commun", size=14, color=GREEN_DARK)
    socle = [("Réseau privé", "azure-subnet.png"),
             ("Coffre-fort\nde secrets", "azure-key-vault.png"),
             ("Supervision", "azure-log-analytics.png")]
    cw = 200; cg = 14; cx = 305
    for i, (t, ic) in enumerate(socle):
        s.card(cx+i*(cw+cg), 214, cw, 115, t, icon=ic, fill=GREEN10, stroke=EMERALD,
               size=13, icon_h=40, icon_frac=0.30, title_frac=0.62)

    # Applications band
    s.rect(285, 375, 650, 215, fill=WHITE, stroke=GREEN20)
    s.text(305, 385, "Applications", size=14, color=GREEN_DARK)
    aw = 300; ag = 20; ax = 305; ay = 425; ah = 150
    # App 1
    s.rect(ax, ay, aw, ah, fill=GREEN10, stroke=EMERALD)
    s.image(ax+aw/2, ay+44, 42, "azure-aca.png")
    s.text(ax+6, ay+90, "App web", size=15, color=NAVY, align="center", w=aw-12)
    s.icon_row(ax+aw/2, ay+ah-26, ["azure-aca.png", "postgresql.png", "redis.png"], ih=26, gap=16)
    # App 2
    x2 = ax+(aw+ag)
    s.rect(x2, ay, aw, ah, fill=GREEN10, stroke=EMERALD)
    s.image(x2+aw/2, ay+44, 42, "azure-sql.png")
    s.text(x2+6, ay+90, "Données", size=15, color=NAVY, align="center", w=aw-12)
    s.icon_row(x2+aw/2, ay+ah-26, ["azure-sql.png", "azure-blob-storage.png"], ih=26, gap=16)

    # Flows — short orthogonal arrow into the apps band; internal app->data link
    s.arrowp([(220, 280), (245, 280), (245, 500), (285, 500)], color=BLUE_GREEN, label="HTTPS")
    s.arrow(ax+aw, ay+ah/2, x2, ay+ah/2, color=BLUE_GREEN, label="lit / écrit")

    out = os.path.join(SKILL_ROOT, "example-architecture.excalidraw")
    s.save(out)
    return out

if __name__ == "__main__":
    build()
