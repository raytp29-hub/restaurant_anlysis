"""
Menu item categorization.

Given a dish_name, returns one of:
Pizze, Primi, Dolci, Bevande, Pesce, Carne, Antipasti, Contorni, Altro.

Priority order matters: for example "pizza al tonno" is a pizza (not fish),
and "spaghetti alle vongole" is a primo (not fish). The first category whose
keyword list matches wins.
"""
import re
from typing import Optional

# Ordered by priority: first match wins.
# Keywords are matched case-insensitive as substrings on a normalized dish name.
CATEGORIES = [
    ("Pizze", [
        "pizza", "margherita", "marinara", "capricciosa",
        "diavola", "quattro stagioni", "quattro formaggi", "calzone",
        "sfincione", "boscaiola", "prosciutto e funghi",
        "salsiccia e friarielli", "focaccia",
    ]),
    ("Primi", [
        "spaghetti", "pasta", "risotto", "risotti", "tagliatelle", "linguine",
        "penne", "rigatoni", "gnocchi", "lasagne", "lasagna", "ravioli",
        "tortelli", "cannelloni", "orecchiette", "malloreddus", "paccheri",
        "bucatini", "fettuccine", "pappardelle", "fusilli", "farfalle", "ziti",
        "trofie", "cavatelli", "casarecce", "trenette", "conchiglie",
        "maccheroni", "vermicelli", "carbonara", "amatriciana", "cacio e pepe",
        "arrabbiata", "aglio e olio", "aglio olio", "pesto", "bolognese",
        "ragu", "ragu'", "ragù", "arancin", "cous cous", "couscous",
        "minestra", "zuppa", "risi e bisi", "spaghettoni",
        "pasta al forno", "pastasciutta",
        # piatti siciliani + cucina asiatica (thai/noodles)
        "norma", "keng", "wunsen", "noodles", "pad thai", "pad see", "phad",
    ]),
    ("Dolci", [
        "dolce", "dolci", "tiramis", "cannolo", "cannoli", "gelato",
        "cassata", "torta", "dessert", "semifreddo", "cheesecake",
        "panna cotta", "mousse", "sorbetto", "granita", "sfogliatella",
        "cassatelle", "biscotti", "biscotto", "crostata", "cioccolato",
        "profiterole", "bigne", "bignè", "baba", "babà", "millefoglie",
        "creme brulee", "creme brûlée", "affogato", "brownie",
        "budino", "zabaione", "zeppole", "zuccotto",
    ]),
    ("Antipasti", [
        "antipast", "bruschett", "carpaccio", "insalata",
        "caprese", "tagliere", "salumi", "formaggi", "mozzarella",
        "burrata", "prosciutto", "mortadella", "culatello", "salame",
        "pancetta", "pate", "paté", "supplì", "suppli", "crocchett",
        "affettati", "focaccina", "sfincionello",
        # tipici siciliani + inglese
        "caponata", "primosale", "salad",
    ]),
    ("Pesce", [
        "pesce", "tonno", "spigola", "orata", "gamber", "calamaro",
        "calamari", "polpo", "polpetti", "polipo", "branzino",
        "cozze", "vongole", "ostriche", "salmone", "ricciola",
        "sarda", "sardin", "alici", "acciughe", "seppie", "seppia",
        "moscardini", "scampi", "sgombro", "ricci di mare", "totani",
        "baccal", "stoccafisso", "frutti di mare", "frittura di paranza",
        "fritto misto", "crudo di", "sushi", "sashimi",
        "tartare di tonno", "tartare di salmone", "pescato",
        # inglese
        "salmon", "tuna",
    ]),
    ("Carne", [
        "carne", "bistecca", "tagliata", "filetto", "costata",
        "pollo", "maiale", "agnello", "cinghiale", "coniglio",
        "salsiccia", "salsicce", "hamburger", "burger", "wurstel",
        "tacchino", "anatra", "cotoletta", "milanese", "arrosto",
        "stinco", "brasato", "manzo", "vitello", "ossobuco",
        "involtini", "polpett", "spezzatino", "grigliata di carne",
        "carre", "carrè", "porchetta",
        # inglese
        "chicken", "beef", "pork",
    ]),
    ("Bevande", [
        "vino", "birra", "bevanda", "bevande", "acqua",
        "caffe", "caffè", "cappuccino", "spritz", "cocktail",
        "mojito", "aperol", "americano", "negroni", "gin tonic",
        "prosecco", "champagne", "limoncello", "amaro", "grappa",
        "coca cola", "coca-cola", "fanta", "sprite", "aranciata",
        "succo", "spremuta", "espresso", "corretto", "chinotto",
        "aperitivo", "digestivo",
        # vini siciliani e cantine (dal dataset)
        "etna", "d'avola", "d avola", "davola", "grillo",
        "brut", "spumante", "planeta", "tasca", "feudi", "rallo",
        "gambino", "eccher", "mirantur", "talee", "serafica",
        "donnafugata", "d'almerita", "d almerita", "dalmerita",
        # inglese
        "wine", "bottle", "water",
    ]),
    ("Contorni", [
        "patate", "fritte", "verdure", "spinaci", "broccoli", "melanzan",
        "peperoni", "funghi trifolati", "carciofi", "zucchin",
        "fagioli", "contorno", "puree", "purè", "asparagi", "rucola",
        # tipici siciliani + thai
        "parmigiana", "phak",
    ]),
]

_PUNCT_RE = re.compile(r"[^\w\s]", re.UNICODE)
_WS_RE = re.compile(r"\s+")


def normalize(name: Optional[str]) -> str:
    """Lowercase, replace punctuation with spaces, collapse whitespace, strip."""
    if not name:
        return ""
    n = name.lower()
    n = _PUNCT_RE.sub(" ", n)
    n = _WS_RE.sub(" ", n).strip()
    return n


def categorize(dish_name: Optional[str]) -> str:
    """
    Return the category label for a dish based on its name.

    Uses a priority-ordered list of (category, keywords): the first category
    whose any keyword appears as a substring of the normalized name wins.
    Fallback is "Altro".
    """
    n = normalize(dish_name)
    if not n:
        return "Altro"
    for category, keywords in CATEGORIES:
        for kw in keywords:
            if kw in n:
                return category
    return "Altro"
