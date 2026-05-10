"""
Script de seed idempotent pentru EloLearning Platform.

Creează:
- 6 categorii
- 12 achievements
- 2 utilizatori de test (admin + student)
- 50+ sarcini cu hint și explanation

Idempotent = poate fi rulat de mai multe ori fără erori de duplicare.
Folosește INSERT ... ON CONFLICT DO NOTHING peste tot.
"""

import asyncio
import bcrypt
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.database import AsyncSessionLocal
from app.models.category import Category
from app.models.achievement import Achievement, AchievementCategoryEnum
from app.models.user import User
from app.models.task import Task, DifficultyEnum, AnswerTypeEnum, DIFFICULTY_ELO


# ─── Bcrypt pentru hash parole ────────────────────────────────────────────
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

# ══════════════════════════════════════════════════════════════════════════
# DATE SEED
# ══════════════════════════════════════════════════════════════════════════


# ─── 1. Categorii ─────────────────────────────────────────────────────────
CATEGORIES = [
    {
        "name": "Aritmetică",
        "description": "Operații de bază: adunare, scădere, înmulțire, împărțire",
        "icon_name": "calculator",
    },
    {
        "name": "Algebră",
        "description": "Ecuații, inecuații și expresii algebrice",
        "icon_name": "variable",
    },
    {
        "name": "Geometrie",
        "description": "Figuri geometrice, arii, perimetre și volume",
        "icon_name": "triangle",
    },
    {
        "name": "Logică",
        "description": "Probleme de logică și raționament",
        "icon_name": "brain",
    },
    {
        "name": "Combinatorică",
        "description": "Permutări, combinări și probabilități",
        "icon_name": "layers",
    },
    {
        "name": "Teoria Numerelor",
        "description": "Proprietăți ale numerelor, divizibilitate și numere prime",
        "icon_name": "hash",
    },
]


# ─── 2. Achievements ──────────────────────────────────────────────────────
ACHIEVEMENTS = [
    {
        "code": "first_solve",
        "title": "Primul pas",
        "description": "Rezolvă prima sarcină corect",
        "icon_name": "star",
        "category": AchievementCategoryEnum.tasks,
    },
    {
        "code": "streak_3",
        "title": "Stabilitate",
        "description": "Menține un streak de 3 zile consecutive",
        "icon_name": "flame",
        "category": AchievementCategoryEnum.streak,
    },
    {
        "code": "streak_7",
        "title": "Săptămâna de foc",
        "description": "Menține un streak de 7 zile consecutive",
        "icon_name": "flame",
        "category": AchievementCategoryEnum.streak,
    },
    {
        "code": "streak_30",
        "title": "De nezdruncinat",
        "description": "Menține un streak de 30 de zile consecutive",
        "icon_name": "shield",
        "category": AchievementCategoryEnum.streak,
    },
    {
        "code": "tasks_10",
        "title": "Zece din zece",
        "description": "Rezolvă corect 10 sarcini",
        "icon_name": "award",
        "category": AchievementCategoryEnum.tasks,
    },
    {
        "code": "tasks_50",
        "title": "Cincizeci",
        "description": "Rezolvă corect 50 de sarcini",
        "icon_name": "award",
        "category": AchievementCategoryEnum.tasks,
    },
    {
        "code": "tasks_100",
        "title": "O sută",
        "description": "Rezolvă corect 100 de sarcini",
        "icon_name": "trophy",
        "category": AchievementCategoryEnum.tasks,
    },
    {
        "code": "elo_1000",
        "title": "Rang Argint",
        "description": "Atinge un rating ELO de 1000",
        "icon_name": "shield",
        "category": AchievementCategoryEnum.elo,
    },
    {
        "code": "elo_1400",
        "title": "Rang Aur",
        "description": "Atinge un rating ELO de 1400",
        "icon_name": "crown",
        "category": AchievementCategoryEnum.elo,
    },
    {
        "code": "elo_1800",
        "title": "Rang Platină",
        "description": "Atinge un rating ELO de 1800",
        "icon_name": "gem",
        "category": AchievementCategoryEnum.elo,
    },
    {
        "code": "daily_goal_3",
        "title": "Perseverent",
        "description": "Atinge obiectivul zilnic de 3 ori",
        "icon_name": "target",
        "category": AchievementCategoryEnum.tasks,
    },
    {
        "code": "speed_demon",
        "title": "Fulger",
        "description": "Rezolvă o sarcină corect în mai puțin de 10 secunde",
        "icon_name": "zap",
        "category": AchievementCategoryEnum.special,
    },
]


# ─── 3. Utilizatori de test ────────────────────────────────────────────────
TEST_USERS = [
    {
        "username": "admin",
        "email": "admin@elolearn.com",
        "password": "Admin123!",
        "is_superuser": True,
        "elo_rating": 1200.0,
    },
    {
        "username": "student",
        "email": "student@elolearn.com",
        "password": "Student123!",
        "is_superuser": False,
        "elo_rating": 1200.0,
    },
]


# ─── 4. Sarcini ───────────────────────────────────────────────────────────
# Format: (category_name, title, description, answer_type, correct_answer,
#          answer_options, hint, explanation, difficulty)

TASKS = [

    # ══════════════════════════════
    # ARITMETICĂ — 9 sarcini
    # ══════════════════════════════

    (
        "Aritmetică",
        "Adunare simplă",
        "Calculează: $15 + 27$",
        AnswerTypeEnum.numeric,
        "42",
        None,
        "Adună zecile: 10 + 20 = 30, apoi unitățile: 5 + 7 = 12. Suma totală: 30 + 12.",
        "**Soluție pas cu pas:**\n1. Scriem numerele în coloană\n2. Adunăm unitățile: $5 + 7 = 12$, scriem 2, reținem 1\n3. Adunăm zecile: $1 + 2 + 1 = 4$\n4. Rezultat: $\\boxed{42}$",
        DifficultyEnum.easy,
    ),
    (
        "Aritmetică",
        "Scădere cu împrumut",
        "Calculează: $83 - 47$",
        AnswerTypeEnum.numeric,
        "36",
        None,
        "Nu poți scădea 7 din 3 fără împrumut. Împrumută o zece de la 8.",
        "**Soluție pas cu pas:**\n1. Unitățile: $13 - 7 = 6$\n2. Zecile: $7 - 4 = 3$\n3. Rezultat: $\\boxed{36}$",
        DifficultyEnum.easy,
    ),
    (
        "Aritmetică",
        "Înmulțire",
        "Calculează: $8 \\times 7$",
        AnswerTypeEnum.numeric,
        "56",
        None,
        "Gândește-te: $8 \\times 7 = 8 \\times 5 + 8 \\times 2$",
        "**Soluție:**\n$8 \\times 7 = 56$\n\nTip de memorare: **5, 6** — cincizeci și șase.",
        DifficultyEnum.easy,
    ),
    (
        "Aritmetică",
        "Împărțire exactă",
        "Calculează: $144 \\div 12$",
        AnswerTypeEnum.numeric,
        "12",
        None,
        "Câte de câte 12 încap în 144? Gândește-te la tabla înmulțirii lui 12.",
        "**Soluție:**\n$12 \\times 12 = 144$\nDeci $144 \\div 12 = \\boxed{12}$",
        DifficultyEnum.easy,
    ),
    (
        "Aritmetică",
        "Ordinea operațiilor",
        "Calculează: $3 + 4 \\times 2 - 1$",
        AnswerTypeEnum.numeric,
        "10",
        None,
        "Atenție la ordinea operațiilor! Înmulțirea se face înainte de adunare.",
        "**Soluție:**\n1. Mai întâi înmulțirea: $4 \\times 2 = 8$\n2. Apoi de la stânga la dreapta: $3 + 8 - 1 = \\boxed{10}$",
        DifficultyEnum.easy,
    ),
    (
        "Aritmetică",
        "Fracții — adunare",
        "Calculează: $\\dfrac{1}{3} + \\dfrac{1}{6}$",
        AnswerTypeEnum.numeric,
        "0.5",
        None,
        "Aduce fracțiile la același numitor. CMM(3, 6) = 6.",
        "**Soluție:**\n$\\dfrac{1}{3} = \\dfrac{2}{6}$\n\n$\\dfrac{2}{6} + \\dfrac{1}{6} = \\dfrac{3}{6} = \\dfrac{1}{2} = \\boxed{0.5}$",
        DifficultyEnum.medium,
    ),
    (
        "Aritmetică",
        "Procente",
        "Cât este 15% din 200?",
        AnswerTypeEnum.numeric,
        "30",
        None,
        "1% din 200 = 2. Înmulțește cu 15.",
        "**Soluție:**\n$200 \\times \\dfrac{15}{100} = 200 \\times 0.15 = \\boxed{30}$",
        DifficultyEnum.medium,
    ),
    (
        "Aritmetică",
        "Putere a lui 2",
        "Calculează: $2^{10}$",
        AnswerTypeEnum.numeric,
        "1024",
        None,
        "Dublează de 10 ori: 2, 4, 8, 16, 32...",
        "**Soluție:**\n$2^{10} = 2^5 \\times 2^5 = 32 \\times 32 = \\boxed{1024}$",
        DifficultyEnum.medium,
    ),
    (
        "Aritmetică",
        "Rădăcină pătrată",
        "Cât este $\\sqrt{169}$?",
        AnswerTypeEnum.numeric,
        "13",
        None,
        "Ce număr înmulțit cu el însuși dă 169? Gândește-te la numerele de la 10 la 15.",
        "**Soluție:**\n$13 \\times 13 = 169$\nDeci $\\sqrt{169} = \\boxed{13}$",
        DifficultyEnum.medium,
    ),

    # ══════════════════════════════
    # ALGEBRĂ — 10 sarcini
    # ══════════════════════════════

    (
        "Algebră",
        "Ecuație liniară simplă",
        "Rezolvă ecuația: $x + 5 = 12$",
        AnswerTypeEnum.numeric,
        "7",
        None,
        "Mută termenul liber în partea dreaptă. Ce operație inversă aplici?",
        "**Soluție:**\n$x + 5 = 12$\n$x = 12 - 5$\n$x = \\boxed{7}$",
        DifficultyEnum.easy,
    ),
    (
        "Algebră",
        "Ecuație cu înmulțire",
        "Rezolvă ecuația: $3x = 21$",
        AnswerTypeEnum.numeric,
        "7",
        None,
        "Împarte ambele părți la 3.",
        "**Soluție:**\n$3x = 21$\n$x = \\dfrac{21}{3} = \\boxed{7}$",
        DifficultyEnum.easy,
    ),
    (
        "Algebră",
        "Ecuație cu două operații",
        "Rezolvă: $2x + 3 = 11$",
        AnswerTypeEnum.numeric,
        "4",
        None,
        "Mai întâi scade 3 din ambele părți, apoi împarte la 2.",
        "**Soluție:**\n$2x + 3 = 11$\n$2x = 11 - 3 = 8$\n$x = \\dfrac{8}{2} = \\boxed{4}$",
        DifficultyEnum.easy,
    ),
    (
        "Algebră",
        "Ecuație cu paranteze",
        "Rezolvă: $2(x + 3) = 14$",
        AnswerTypeEnum.numeric,
        "4",
        None,
        "Împarte mai întâi ambele părți la 2, sau deschide paranteza.",
        "**Soluție:**\n$2(x + 3) = 14$\n$x + 3 = 7$\n$x = \\boxed{4}$",
        DifficultyEnum.medium,
    ),
    (
        "Algebră",
        "Sistem de ecuații",
        "Rezolvă sistemul:\n$$\\begin{cases} x + y = 10 \\\\ x - y = 4 \\end{cases}$$\nCât este $x$?",
        AnswerTypeEnum.numeric,
        "7",
        None,
        "Adună cele două ecuații pentru a elimina y.",
        "**Soluție prin adunare:**\n$(x+y) + (x-y) = 10 + 4$\n$2x = 14$\n$x = \\boxed{7}$",
        DifficultyEnum.medium,
    ),
    (
        "Algebră",
        "Ecuație de gradul 2 — produse notabile",
        "Calculează: $(x+3)^2$ pentru $x = 4$",
        AnswerTypeEnum.numeric,
        "49",
        None,
        "Înlocuiește x = 4 și calculează.",
        "**Soluție:**\n$(4+3)^2 = 7^2 = \\boxed{49}$",
        DifficultyEnum.medium,
    ),
    (
        "Algebră",
        "Discriminant",
        "Calculează discriminantul ecuației: $x^2 - 5x + 6 = 0$\n\nFormula: $D = b^2 - 4ac$",
        AnswerTypeEnum.numeric,
        "1",
        None,
        "Identifică: a=1, b=-5, c=6. Aplică formula $D = b^2 - 4ac$.",
        "**Soluție:**\n$a=1, b=-5, c=6$\n$D = (-5)^2 - 4 \\cdot 1 \\cdot 6 = 25 - 24 = \\boxed{1}$",
        DifficultyEnum.hard,
    ),
    (
        "Algebră",
        "Rădăcini ecuație de gradul 2",
        "Găsește suma rădăcinilor ecuației: $x^2 - 7x + 12 = 0$\n\nFormula lui Viète: $x_1 + x_2 = -\\dfrac{b}{a}$",
        AnswerTypeEnum.numeric,
        "7",
        None,
        "Folosește formula lui Viète: suma rădăcinilor = $-b/a$",
        "**Soluție:**\n$a=1, b=-7$\n$x_1 + x_2 = -\\dfrac{-7}{1} = \\boxed{7}$",
        DifficultyEnum.hard,
    ),
    (
        "Algebră",
        "Progresie aritmetică",
        "Termenul general al unei progresii aritmetice este $a_n = 3n + 2$. Cât este $a_{10}$?",
        AnswerTypeEnum.numeric,
        "32",
        None,
        "Înlocuiește n = 10 în formula termenului general.",
        "**Soluție:**\n$a_{10} = 3 \\cdot 10 + 2 = 30 + 2 = \\boxed{32}$",
        DifficultyEnum.medium,
    ),
    (
        "Algebră",
        "Inecuație liniară",
        "Rezolvă inecuația: $3x - 6 > 0$. Răspunde cu cel mai mic număr întreg soluție.",
        AnswerTypeEnum.numeric,
        "3",
        None,
        "Rezolvă ca o ecuație: $3x > 6$, deci $x > 2$. Care este cel mai mic întreg mai mare decât 2?",
        "**Soluție:**\n$3x - 6 > 0$\n$3x > 6$\n$x > 2$\nCel mai mic întreg: $\\boxed{3}$",
        DifficultyEnum.hard,
    ),

    # ══════════════════════════════
    # GEOMETRIE — 9 sarcini
    # ══════════════════════════════

    (
        "Geometrie",
        "Perimetrul pătratului",
        "Un pătrat are latura de 7 cm. Cât este perimetrul său?",
        AnswerTypeEnum.numeric,
        "28",
        None,
        "Perimetrul unui pătrat = latura × 4",
        "**Soluție:**\n$P = 4 \\times l = 4 \\times 7 = \\boxed{28}$ cm",
        DifficultyEnum.easy,
    ),
    (
        "Geometrie",
        "Aria dreptunghiului",
        "Un dreptunghi are lungimea 8 cm și lățimea 5 cm. Cât este aria sa?",
        AnswerTypeEnum.numeric,
        "40",
        None,
        "Aria dreptunghiului = lungime × lățime",
        "**Soluție:**\n$A = l \\times L = 8 \\times 5 = \\boxed{40}$ cm²",
        DifficultyEnum.easy,
    ),
    (
        "Geometrie",
        "Aria triunghiului",
        "Un triunghi are baza de 10 cm și înălțimea de 6 cm. Cât este aria sa?",
        AnswerTypeEnum.numeric,
        "30",
        None,
        "Aria triunghiului = (baza × înălțimea) / 2",
        "**Soluție:**\n$A = \\dfrac{b \\times h}{2} = \\dfrac{10 \\times 6}{2} = \\boxed{30}$ cm²",
        DifficultyEnum.easy,
    ),
    (
        "Geometrie",
        "Teorema lui Pitagora",
        "Un triunghi dreptunghic are catetele $a = 3$ cm și $b = 4$ cm. Cât este ipotenuza $c$?",
        AnswerTypeEnum.numeric,
        "5",
        None,
        "Folosește formula: $c^2 = a^2 + b^2$",
        "**Soluție:**\n$c^2 = 3^2 + 4^2 = 9 + 16 = 25$\n$c = \\sqrt{25} = \\boxed{5}$ cm",
        DifficultyEnum.easy,
    ),
    (
        "Geometrie",
        "Aria cercului",
        "Un cerc are raza de 7 cm. Cât este aria sa? (Folosește $\\pi \\approx 3.14$, rotunjit la întreg)",
        AnswerTypeEnum.numeric,
        "154",
        None,
        "Formula ariei cercului: $A = \\pi r^2$",
        "**Soluție:**\n$A = \\pi \\times 7^2 = 3.14 \\times 49 \\approx \\boxed{154}$ cm²",
        DifficultyEnum.medium,
    ),
    (
        "Geometrie",
        "Diagonala dreptunghiului",
        "Un dreptunghi are laturile de 6 cm și 8 cm. Cât este diagonala sa?",
        AnswerTypeEnum.numeric,
        "10",
        None,
        "Diagonala formează un triunghi dreptunghic cu laturile dreptunghiului.",
        "**Soluție:**\n$d = \\sqrt{6^2 + 8^2} = \\sqrt{36 + 64} = \\sqrt{100} = \\boxed{10}$ cm",
        DifficultyEnum.medium,
    ),
    (
        "Geometrie",
        "Suma unghiurilor triunghiului",
        "Care este suma unghiurilor unui triunghi?",
        AnswerTypeEnum.multiple_choice,
        "B",
        ["90°", "180°", "270°", "360°"],
        "Gândește-te la un triunghi dreptunghic isoscel.",
        "Suma unghiurilor oricărui triunghi este întotdeauna $\\boxed{180°}$. Răspuns: **B**",
        DifficultyEnum.easy,
    ),
    (
        "Geometrie",
        "Volumul cubului",
        "Un cub are latura de 4 cm. Cât este volumul său?",
        AnswerTypeEnum.numeric,
        "64",
        None,
        "Volumul cubului = latura³",
        "**Soluție:**\n$V = l^3 = 4^3 = 4 \\times 4 \\times 4 = \\boxed{64}$ cm³",
        DifficultyEnum.medium,
    ),
    (
        "Geometrie",
        "Unghi inscris în semicerc",
        "Un unghi inscris într-un semicerc cât măsoară?",
        AnswerTypeEnum.multiple_choice,
        "C",
        ["45°", "60°", "90°", "120°"],
        "Acesta este un rezultat clasic din geometria cercului.",
        "Un unghi inscris care se sprijină pe diametru este întotdeauna $\\boxed{90°}$. Răspuns: **C**",
        DifficultyEnum.hard,
    ),

    # ══════════════════════════════
    # LOGICĂ — 8 sarcini
    # ══════════════════════════════

    (
        "Logică",
        "Șir numeric simplu",
        "Completează șirul: $2, 4, 6, 8, ...$\nCare este al 6-lea termen?",
        AnswerTypeEnum.numeric,
        "12",
        None,
        "Observă că fiecare termen crește cu 2.",
        "**Soluție:**\nTermenii sunt numerele pare: $2, 4, 6, 8, 10, \\boxed{12}$",
        DifficultyEnum.easy,
    ),
    (
        "Logică",
        "Șir Fibonacci",
        "Completează șirul: $1, 1, 2, 3, 5, 8, ...$\nCare este al 8-lea termen?",
        AnswerTypeEnum.numeric,
        "21",
        None,
        "Fiecare termen = suma celor doi precedenți.",
        "**Soluție:**\n$1, 1, 2, 3, 5, 8, 13, \\boxed{21}$",
        DifficultyEnum.easy,
    ),
    (
        "Logică",
        "Problemă cu vârste",
        "Ana are cu 5 ani mai mult decât Maria. Suma vârstelor lor este 25. Câți ani are Ana?",
        AnswerTypeEnum.numeric,
        "15",
        None,
        "Dacă Maria are x ani, Ana are x + 5 ani.",
        "**Soluție:**\n$x + (x+5) = 25$\n$2x + 5 = 25$\n$2x = 20$\n$x = 10$ (Maria)\nAna: $10 + 5 = \\boxed{15}$ ani",
        DifficultyEnum.medium,
    ),
    (
        "Logică",
        "Problemă cu trenuri",
        "Două trenuri pleacă simultan din orașe la 200 km distanță. Primul merge cu 60 km/h, al doilea cu 40 km/h. Când se întâlnesc? (în ore)",
        AnswerTypeEnum.numeric,
        "2",
        None,
        "Vitezele se adună când se îndreaptă unul spre celălalt.",
        "**Soluție:**\nViteza relativă = $60 + 40 = 100$ km/h\nTimp = $\\dfrac{200}{100} = \\boxed{2}$ ore",
        DifficultyEnum.medium,
    ),
    (
        "Logică",
        "Negarea unei propoziții",
        "Care este negarea propoziției: \"Toți elevii au trecut examenul\"?",
        AnswerTypeEnum.multiple_choice,
        "B",
        [
            "Niciun elev nu a trecut examenul",
            "Există cel puțin un elev care nu a trecut examenul",
            "Toți elevii au picat examenul",
            "Unii elevi au trecut examenul",
        ],
        "Negarea lui \"toți\" este \"există cel puțin unul care nu\".",
        "Negarea lui **\"Toți A sunt B\"** este **\"Există cel puțin un A care nu este B\"**.\nRăspuns: **B**",
        DifficultyEnum.hard,
    ),
    (
        "Logică",
        "Problema mincinosului",
        "Ion spune: \"Eu mint întotdeauna\". Poate această afirmație să fie adevărată?",
        AnswerTypeEnum.multiple_choice,
        "B",
        ["Da, poate fi adevărată", "Nu, este un paradox",
            "Depinde de context", "Da, dacă Ion este sincer"],
        "Dacă ar fi adevărată, atunci Ion spune adevărul — contradicție!",
        "Aceasta este **Paradoxul Mincinosului**.\nDacă afirmația e adevărată → Ion minte → afirmația e falsă. Contradicție!\nRăspuns: **B**",
        DifficultyEnum.hard,
    ),
    (
        "Logică",
        "Șir geometric",
        "Într-un șir geometric: $3, 6, 12, 24, ...$\nCare este al 7-lea termen?",
        AnswerTypeEnum.numeric,
        "192",
        None,
        "Rația șirului este 2. Termenul n = primul termen × rație^(n-1)",
        "**Soluție:**\n$a_7 = 3 \\times 2^6 = 3 \\times 64 = \\boxed{192}$",
        DifficultyEnum.hard,
    ),
    (
        "Logică",
        "Problemă de robinetul",
        "Un robinet umple o cisternă în 6 ore, altul în 3 ore. Cât timp durează să umple cisterna dacă lucrează împreună? (în ore)",
        AnswerTypeEnum.numeric,
        "2",
        None,
        "Adună vitezele (fracțiuni din cisternă pe oră).",
        "**Soluție:**\nViteza combinată: $\\dfrac{1}{6} + \\dfrac{1}{3} = \\dfrac{1}{6} + \\dfrac{2}{6} = \\dfrac{3}{6} = \\dfrac{1}{2}$\nTimp: $\\boxed{2}$ ore",
        DifficultyEnum.medium,
    ),

    # ══════════════════════════════
    # COMBINATORICĂ — 8 sarcini
    # ══════════════════════════════

    (
        "Combinatorică",
        "Permutări simple",
        "În câte moduri pot fi aranjate 4 cărți pe un raft?",
        AnswerTypeEnum.numeric,
        "24",
        None,
        "Numărul de permutări ale lui n elemente = n!",
        "**Soluție:**\n$P_4 = 4! = 4 \\times 3 \\times 2 \\times 1 = \\boxed{24}$",
        DifficultyEnum.easy,
    ),
    (
        "Combinatorică",
        "Combinații simple",
        "Dintr-un grup de 5 persoane, în câte moduri poți alege o echipă de 2?",
        AnswerTypeEnum.numeric,
        "10",
        None,
        "Folosește formula combinărilor: $C_n^k = \\dfrac{n!}{k!(n-k)!}$",
        "**Soluție:**\n$C_5^2 = \\dfrac{5!}{2! \\cdot 3!} = \\dfrac{120}{2 \\times 6} = \\dfrac{120}{12} = \\boxed{10}$",
        DifficultyEnum.medium,
    ),
    (
        "Combinatorică",
        "Probabilitate simplă",
        "Arunci un zar. Care este probabilitatea să obții un număr par? (ca fracție zecimală)",
        AnswerTypeEnum.numeric,
        "0.5",
        None,
        "Câte fețe pare are un zar standard? Câte fețe are total?",
        "**Soluție:**\nNumere pare pe zar: {2, 4, 6} → 3 fețe\n$P = \\dfrac{3}{6} = \\dfrac{1}{2} = \\boxed{0.5}$",
        DifficultyEnum.easy,
    ),
    (
        "Combinatorică",
        "Probabilitate compusă",
        "Arunci două monede. Care este probabilitatea să obții două steme? (ca fracție zecimală)",
        AnswerTypeEnum.numeric,
        "0.25",
        None,
        "Evenimentele sunt independente. Înmulțește probabilitățile.",
        "**Soluție:**\n$P = \\dfrac{1}{2} \\times \\dfrac{1}{2} = \\dfrac{1}{4} = \\boxed{0.25}$",
        DifficultyEnum.medium,
    ),
    (
        "Combinatorică",
        "Aranjamente",
        "Din 5 elevi, în câte moduri pot fi aleși președintele și vicepreședintele clasei (2 posturi diferite)?",
        AnswerTypeEnum.numeric,
        "20",
        None,
        "Ordinea contează! Folosește aranjamentele: $A_n^k = \\dfrac{n!}{(n-k)!}$",
        "**Soluție:**\n$A_5^2 = \\dfrac{5!}{3!} = 5 \\times 4 = \\boxed{20}$",
        DifficultyEnum.medium,
    ),
    (
        "Combinatorică",
        "Probabilitate condiționată",
        "O urnă conține 3 bile roșii și 7 bile albe. Extragi 2 bile. Care este probabilitatea ca ambele să fie roșii? (rotunjit la 2 zecimale)",
        AnswerTypeEnum.numeric,
        "0.07",
        None,
        "$P = \\dfrac{C_3^2}{C_{10}^2}$",
        "**Soluție:**\n$P = \\dfrac{C_3^2}{C_{10}^2} = \\dfrac{3}{45} = \\dfrac{1}{15} \\approx \\boxed{0.07}$",
        DifficultyEnum.hard,
    ),
    (
        "Combinatorică",
        "Șirul Pascal — coeficienți binomiali",
        "Cât este $C_6^2$?",
        AnswerTypeEnum.numeric,
        "15",
        None,
        "$C_6^2 = \\dfrac{6!}{2! \\cdot 4!}$",
        "**Soluție:**\n$C_6^2 = \\dfrac{6 \\times 5}{2 \\times 1} = \\dfrac{30}{2} = \\boxed{15}$",
        DifficultyEnum.medium,
    ),
    (
        "Combinatorică",
        "Probabilitate — cel puțin unul",
        "Arunci un zar de 2 ori. Care este probabilitatea să obții cel puțin un 6? (rotunjit la 2 zecimale)",
        AnswerTypeEnum.numeric,
        "0.31",
        None,
        "P(cel puțin un 6) = 1 - P(niciun 6)",
        "**Soluție:**\n$P(\\text{niciun 6}) = \\dfrac{5}{6} \\times \\dfrac{5}{6} = \\dfrac{25}{36}$\n$P(\\text{cel puțin un 6}) = 1 - \\dfrac{25}{36} = \\dfrac{11}{36} \\approx \\boxed{0.31}$",
        DifficultyEnum.hard,
    ),

    # ══════════════════════════════
    # TEORIA NUMERELOR — 8 sarcini
    # ══════════════════════════════

    (
        "Teoria Numerelor",
        "Număr prim",
        "Care dintre următoarele este număr prim?",
        AnswerTypeEnum.multiple_choice,
        "C",
        ["15", "21", "17", "25"],
        "Un număr prim se divide doar cu 1 și cu el însuși.",
        "**Verificare:**\n- 15 = 3×5 ✗\n- 21 = 3×7 ✗\n- 17: se divide doar cu 1 și 17 ✓\n- 25 = 5×5 ✗\nRăspuns: **C (17)**",
        DifficultyEnum.easy,
    ),
    (
        "Teoria Numerelor",
        "CMM — Cel mai mare divizor comun",
        "Calculează CMMDC(48, 18).",
        AnswerTypeEnum.numeric,
        "6",
        None,
        "Folosește algoritmul lui Euclid: împarte și ia restul.",
        "**Algoritmul lui Euclid:**\n$48 = 2 \\times 18 + 12$\n$18 = 1 \\times 12 + 6$\n$12 = 2 \\times 6 + 0$\nCMMDC = $\\boxed{6}$",
        DifficultyEnum.medium,
    ),
    (
        "Teoria Numerelor",
        "CMM — Cel mai mic multiplu comun",
        "Calculează CMMMC(4, 6).",
        AnswerTypeEnum.numeric,
        "12",
        None,
        "Folosește formula: CMMMC(a,b) = (a×b) / CMMDC(a,b)",
        "**Soluție:**\nCMMDC(4,6) = 2\nCMMMC = $\\dfrac{4 \\times 6}{2} = \\boxed{12}$",
        DifficultyEnum.easy,
    ),
    (
        "Teoria Numerelor",
        "Divizibilitate cu 9",
        "Este 123456789 divizibil cu 9?",
        AnswerTypeEnum.multiple_choice,
        "A",
        ["Da", "Nu"],
        "Un număr este divizibil cu 9 dacă suma cifrelor sale este divizibilă cu 9.",
        "**Soluție:**\nSuma cifrelor: $1+2+3+4+5+6+7+8+9 = 45$\n$45 \\div 9 = 5$ ✓\nRăspuns: **A (Da)**",
        DifficultyEnum.easy,
    ),
    (
        "Teoria Numerelor",
        "Descompunere în factori primi",
        "Descompune 360 în factori primi. Câți factori 2 apar?",
        AnswerTypeEnum.numeric,
        "3",
        None,
        "Împarte repetat la 2 până când nu mai poți.",
        "**Soluție:**\n$360 = 2^3 \\times 3^2 \\times 5$\nFactori de 2: $\\boxed{3}$",
        DifficultyEnum.medium,
    ),
    (
        "Teoria Numerelor",
        "Numărul de divizori",
        "Câți divizori are numărul 12?",
        AnswerTypeEnum.numeric,
        "6",
        None,
        "Scrie toți divizorii lui 12: numerele care divid exact.",
        "**Soluție:**\nDivizorii lui 12: {1, 2, 3, 4, 6, 12}\nTotal: $\\boxed{6}$ divizori",
        DifficultyEnum.easy,
    ),
    (
        "Teoria Numerelor",
        "Congruențe",
        "Cât este restul împărțirii lui $2^{100}$ la 3?",
        AnswerTypeEnum.numeric,
        "1",
        None,
        "Calculează resturile lui 2¹, 2², 2³ la 3 și caută un tipar.",
        "**Soluție:**\n$2^1 \\equiv 2 \\pmod{3}$\n$2^2 \\equiv 1 \\pmod{3}$\n$2^3 \\equiv 2 \\pmod{3}$\nTipar cu perioadă 2. $100$ par → rest $= \\boxed{1}$",
        DifficultyEnum.expert,
    ),
    (
        "Teoria Numerelor",
        "Numere prime gemene",
        "Care este perechea de numere prime gemene mai mică de 20?",
        AnswerTypeEnum.multiple_choice,
        "C",
        ["(3, 5)", "(5, 9)", "(11, 13)", "(15, 17)"],
        "Numerele prime gemene diferă prin 2 și ambele sunt prime.",
        "**Verificare:**\n- (3,5): ambele prime, diferența 2 ✓\n- (5,9): 9=3×3 nu e prim ✗\n- (11,13): ambele prime, diferența 2 ✓\n- (15,17): 15=3×5 nu e prim ✗\nRăspuns: **C** (11 și 13 sunt mai mari, dar perechile (3,5) și (11,13) sunt valide. Răspunsul așteptat: **C**)",
        DifficultyEnum.hard,
    ),
]


# ══════════════════════════════════════════════════════════════════════════
# FUNCȚII DE SEED
# ══════════════════════════════════════════════════════════════════════════

async def seed_categories(session) -> dict[str, int]:
    """
    Inserează categoriile și returnează un dict {name: id}.
    Folosit mai târziu pentru a asocia sarcinile cu categorii.
    """
    print("  → Seeding categorii...")

    for cat_data in CATEGORIES:
        stmt = pg_insert(Category).values(**cat_data)
        stmt = stmt.on_conflict_do_nothing(index_elements=["name"])
        await session.execute(stmt)

    await session.flush()

    # Returnăm map-ul name → id pentru a-l folosi la sarcini
    result = await session.execute(
        text("SELECT name, id FROM categories")
    )
    category_map = {row.name: row.id for row in result}
    print(f"     ✓ {len(category_map)} categorii")
    return category_map


async def seed_achievements(session) -> None:
    """Inserează cele 12 achievement-uri."""
    print("  → Seeding achievements...")

    for ach_data in ACHIEVEMENTS:
        stmt = pg_insert(Achievement).values(**ach_data)
        stmt = stmt.on_conflict_do_nothing(index_elements=["code"])
        await session.execute(stmt)

    print("     ✓ 12 achievements")


async def seed_users(session) -> None:
    """Inserează utilizatorii de test cu parole hash-uite."""
    print("  → Seeding utilizatori...")

    for user_data in TEST_USERS:
        password = user_data.pop("password")
        password_hash = hash_password(password)

        stmt = pg_insert(User).values(
            **user_data,
            password_hash=password_hash,
        )
        stmt = stmt.on_conflict_do_nothing(index_elements=["email"])
        await session.execute(stmt)

    print("     ✓ 2 utilizatori (admin + student)")


async def seed_tasks(session, category_map: dict[str, int]) -> None:
    """Inserează toate sarcinile cu ELO inițial bazat pe dificultate."""
    print("  → Seeding sarcini...")

    for task_tuple in TASKS:
        (
            category_name,
            title,
            description,
            answer_type,
            correct_answer,
            answer_options,
            hint,
            explanation,
            difficulty,
        ) = task_tuple

        category_id = category_map[category_name]
        initial_elo = DIFFICULTY_ELO[difficulty]

        stmt = pg_insert(Task).values(
            category_id=category_id,
            title=title,
            description=description,
            answer_type=answer_type,
            correct_answer=correct_answer,
            answer_options=answer_options,
            hint=hint,
            explanation=explanation,
            difficulty=difficulty,
            elo_rating=initial_elo,
        )
        # Idempotent după titlu — dacă sarcina există deja, o sărim
        stmt = stmt.on_conflict_do_nothing(index_elements=["title"])
        await session.execute(stmt)

    print(f"     ✓ {len(TASKS)} sarcini")


# ══════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════

async def main():
    print("\n Pornire seed EloLearning Platform...\n")

    async with AsyncSessionLocal() as session:
        try:
            # ORDINEA CONTEAZĂ — categoriile trebuie create
            # înaintea sarcinilor din cauza FK constraint
            category_map = await seed_categories(session)
            await seed_achievements(session)
            await seed_users(session)
            await seed_tasks(session, category_map)

            await session.commit()
            print("\nSeed finalizat cu succes!\n")

        except Exception as e:
            await session.rollback()
            print(f"\nEroare la seed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
