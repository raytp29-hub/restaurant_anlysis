"""
Unit tests for restaurant_scraper.categorization.categorize().

Run with:
    pytest test_categorization.py -v
"""
import pytest

from restaurant_scraper.categorization import categorize, normalize


class TestNormalize:
    def test_lowercase(self):
        assert normalize("PIZZA MARGHERITA") == "pizza margherita"

    def test_punctuation_removed(self):
        assert normalize("Spaghetti, al pesto!") == "spaghetti al pesto"

    def test_collapse_whitespace(self):
        assert normalize("  Tiramisù   della    casa  ") == "tiramisù della casa"

    def test_none_returns_empty(self):
        assert normalize(None) == ""

    def test_empty_string(self):
        assert normalize("") == ""


@pytest.mark.parametrize("dish, expected", [
    # --- Pizze (highest priority: 'pizza X' stays Pizze even if X is fish/meat) ---
    ("Pizza Margherita", "Pizze"),
    ("Marinara", "Pizze"),
    ("Diavola con salame piccante", "Pizze"),
    ("Calzone al forno", "Pizze"),
    ("Pizza al tonno", "Pizze"),
    ("Pizza ai frutti di mare", "Pizze"),
    ("Pizza prosciutto e funghi", "Pizze"),
    ("Focaccia messinese", "Pizze"),
    ("Sfincione palermitano", "Pizze"),
    ("Quattro Stagioni", "Pizze"),

    # --- Primi (priority over Pesce for pasta-with-fish dishes) ---
    ("Spaghetti alle vongole", "Primi"),
    ("Spaghetti alla carbonara", "Primi"),
    ("Pasta alla Norma", "Primi"),
    ("Risotto ai frutti di mare", "Primi"),
    ("Tagliatelle al ragù", "Primi"),
    ("Linguine allo scoglio", "Primi"),
    ("Gnocchi al pesto", "Primi"),
    ("Ravioli di ricotta e spinaci", "Primi"),
    ("Lasagne al forno", "Primi"),
    ("Cous cous di pesce", "Primi"),
    ("Arancini alla carne", "Primi"),
    ("Arancino al ragù", "Primi"),
    ("Pappardelle al cinghiale", "Primi"),

    # --- Dolci ---
    ("Tiramisù della casa", "Dolci"),
    ("Cannolo siciliano", "Dolci"),
    ("Cassata al forno", "Dolci"),
    ("Gelato artigianale", "Dolci"),
    ("Torta al cioccolato", "Dolci"),
    ("Panna cotta ai frutti di bosco", "Dolci"),
    ("Sfogliatella napoletana", "Dolci"),
    ("Semifreddo al pistacchio", "Dolci"),
    ("Granita al limone", "Dolci"),

    # --- Bevande ---
    ("Vino della casa", "Bevande"),
    ("Birra media", "Bevande"),
    ("Acqua naturale 1L", "Bevande"),
    ("Spritz Aperol", "Bevande"),
    ("Coca cola", "Bevande"),
    ("Caffè espresso", "Bevande"),
    ("Prosecco flute", "Bevande"),
    ("Limoncello", "Bevande"),
    ("Chinotto in bottiglia", "Bevande"),

    # --- Pesce ---
    ("Tonno rosso alla griglia", "Pesce"),
    ("Orata al forno", "Pesce"),
    ("Branzino in crosta di sale", "Pesce"),
    ("Frittura di paranza", "Pesce"),
    ("Polpo alla brace", "Pesce"),
    ("Gamberi rossi crudi", "Pesce"),
    ("Baccalà alla ghiotta", "Pesce"),
    ("Cozze al vino bianco", "Pesce"),
    ("Sushi misto", "Pesce"),
    ("Tartare di tonno", "Pesce"),

    # --- Carne ---
    ("Bistecca fiorentina", "Carne"),
    ("Tagliata di manzo con rucola", "Carne"),
    ("Pollo alla cacciatora", "Carne"),
    ("Coniglio all'ischitana", "Carne"),
    ("Salsiccia alla brace", "Carne"),
    ("Cotoletta alla milanese", "Carne"),
    ("Involtini di vitello", "Carne"),
    ("Hamburger di manzo", "Carne"),
    ("Ossobuco alla milanese", "Carne"),

    # --- Antipasti ---
    ("Antipasto misto della casa", "Antipasti"),
    ("Bruschetta al pomodoro", "Antipasti"),
    ("Tagliere di salumi e formaggi", "Antipasti"),
    ("Caprese con bufala", "Antipasti"),
    ("Carpaccio di manzo", "Antipasti"),
    ("Insalata mista", "Antipasti"),
    ("Burrata pugliese", "Antipasti"),

    # --- Contorni ---
    ("Patate al forno", "Contorni"),
    ("Verdure grigliate", "Contorni"),
    ("Spinaci saltati", "Contorni"),
    ("Broccoli con aglio", "Contorni"),
    ("Carciofi alla romana", "Contorni"),
    ("Zucchine grigliate", "Contorni"),

    # --- Altro (no keyword match) ---
    ("Menu degustazione", "Altro"),
    ("Coperto", "Altro"),
    ("Piatto del giorno", "Altro"),
    ("Specialità dello chef", "Altro"),

    # --- Edge cases ---
    (None, "Altro"),
    ("", "Altro"),
    ("   ", "Altro"),
])
def test_categorize(dish, expected):
    assert categorize(dish) == expected, f"Failed for {dish!r}"


def test_priority_pizza_over_fish():
    """A pizza with fish topping must be categorized as Pizze, not Pesce."""
    assert categorize("Pizza al tonno") == "Pizze"
    assert categorize("Pizza ai frutti di mare") == "Pizze"


def test_priority_primi_over_fish():
    """Pasta with fish must be categorized as Primi, not Pesce."""
    assert categorize("Spaghetti alle vongole") == "Primi"
    assert categorize("Linguine allo scoglio") == "Primi"
    assert categorize("Risotto ai frutti di mare") == "Primi"


def test_all_categories_are_reachable():
    """Every category (except Altro) should be reachable via at least one keyword."""
    expected = {"Pizze", "Primi", "Dolci", "Bevande",
                "Pesce", "Carne", "Antipasti", "Contorni"}
    samples = {
        "Pizza Margherita": "Pizze",
        "Spaghetti": "Primi",
        "Tiramisù": "Dolci",
        "Vino rosso": "Bevande",
        "Orata": "Pesce",
        "Bistecca": "Carne",
        "Bruschetta": "Antipasti",
        "Patate fritte": "Contorni",
    }
    for dish, cat in samples.items():
        assert categorize(dish) == cat
    assert set(samples.values()) == expected
