import math
import matplotlib.pyplot as plt

OPERATEURS_BINAIRES = {"+", "-", "*", "/"}
OPERATEURS_UNAIRES = {"exp", "log", "sin", "cos"}


class Noeud:
    """Noeud d'un arbre d'expression mathématique."""

    # Question 1 : constructeur
    def __init__(self, valeur, enfants=None):
        # valeur : str (variable ou opérateur) ou int/float (constante)
        self.valeur = valeur
        # enfants : liste d'objets Noeud
        self.enfants = list(enfants) if enfants else []

    # Question 2 : ajout d'un enfant
    def ajouter_enfant(self, noeud):
        if not isinstance(noeud, Noeud):
            raise TypeError("L'enfant doit être de type Noeud")
        self.enfants.append(noeud)

    # Question 3 : affichage en notation polonaise (préfixe)
    def __str__(self):
        elements = [str(self.valeur)] + [str(e) for e in self.enfants]
        return " ".join(elements)

    # --- Fonctions utilitaires ---
    def est_constante(self):
        return isinstance(self.valeur, (int, float))

    def est_operateur(self):
        return isinstance(self.valeur, str) and (
            self.valeur in OPERATEURS_BINAIRES or self.valeur in OPERATEURS_UNAIRES
        )

    def est_variable(self):
        return isinstance(self.valeur, str) and not self.est_operateur()

    def variables(self):
        """Ensemble des noms de variables présentes dans l'arbre."""
        if self.est_variable():
            return {self.valeur}
        resultat = set()
        for e in self.enfants:
            resultat |= e.variables()
        return resultat

    # Question 5 : évaluation
    def evaluer(self, valeurs):
        if self.est_constante():
            return float(self.valeur)

        if self.est_variable():
            if self.valeur not in valeurs:
                raise ValueError(f"La variable '{self.valeur}' n'a pas de valeur associée")
            return float(valeurs[self.valeur])

        op = self.valeur
        if op in OPERATEURS_BINAIRES:
            if len(self.enfants) != 2:
                raise ValueError(f"L'opérateur '{op}' attend 2 opérandes")
            a = self.enfants[0].evaluer(valeurs)
            b = self.enfants[1].evaluer(valeurs)
            if op == "+":
                return a + b
            if op == "-":
                return a - b
            if op == "*":
                return a * b
            if b == 0:
                raise ValueError("Division par zéro")
            return a / b

        if len(self.enfants) != 1:
            raise ValueError(f"L'opérateur '{op}' attend 1 opérande")
        a = self.enfants[0].evaluer(valeurs)
        if op == "exp":
            return math.exp(a)
        if op == "log":
            if a <= 0:
                raise ValueError("Logarithme d'un nombre négatif ou nul")
            return math.log(a)
        if op == "sin":
            return math.sin(a)
        return math.cos(a)  # op == "cos"

    # Question 6 : tracé
    def tracer(self, variable, liste_valeurs, autres_valeurs=None):
        """Trace l'expression en fonction de `variable` prenant les valeurs de `liste_valeurs`.
        `autres_valeurs` : dictionnaire pour les éventuelles autres variables."""
        autres_valeurs = dict(autres_valeurs) if autres_valeurs else {}
        ys = []
        for v in liste_valeurs:
            autres_valeurs[variable] = v
            ys.append(self.evaluer(autres_valeurs))
        plt.plot(liste_valeurs, ys)
        plt.xlabel(variable)
        plt.ylabel(str(self))
        plt.grid(True)
        plt.show()

    # Question 7 : simplification
    def simplifiee(self):
        # Constante ou variable : on renvoie une copie
        if not self.enfants:
            return Noeud(self.valeur)

        enfants = [e.simplifiee() for e in self.enfants]
        noeud = Noeud(self.valeur, enfants)

        # Aucune variable : on remplace par la constante évaluée
        if not noeud.variables():
            try:
                return Noeud(noeud.evaluer({}))
            except (ValueError, OverflowError):
                return noeud

        def est(n, v):
            return n.est_constante() and n.valeur == v

        if self.valeur in OPERATEURS_BINAIRES:
            a, b = enfants
            op = self.valeur
            if op == "*":
                if est(a, 0) or est(b, 0):
                    return Noeud(0)
                if est(a, 1):
                    return b
                if est(b, 1):
                    return a
            elif op == "/":
                if est(a, 0):
                    return Noeud(0)
                if est(b, 1):
                    return a
            elif op == "+":
                if est(a, 0):
                    return b
                if est(b, 0):
                    return a
            elif op == "-":
                if est(b, 0):
                    return a
        return noeud

    # Question 8 : dérivation
    def derivee(self, variable):
        return self._deriver(variable).simplifiee()

    def _deriver(self, v):
        if self.est_constante():
            return Noeud(0)
        if self.est_variable():
            return Noeud(1 if self.valeur == v else 0)

        op = self.valeur
        if op in OPERATEURS_BINAIRES:
            a, b = self.enfants
            da, db = a._deriver(v), b._deriver(v)
            if op == "+":
                return Noeud("+", [da, db])
            if op == "-":
                return Noeud("-", [da, db])
            if op == "*":  # (ab)' = a'b + ab'
                return Noeud("+", [Noeud("*", [da, b]), Noeud("*", [a, db])])
            # (a/b)' = (a'b - ab') / b^2
            num = Noeud("-", [Noeud("*", [da, b]), Noeud("*", [a, db])])
            return Noeud("/", [num, Noeud("*", [b, b])])

        a = self.enfants[0]
        da = a._deriver(v)
        if op == "exp":
            return Noeud("*", [Noeud("exp", [a]), da])
        if op == "log":
            return Noeud("/", [da, a])
        if op == "sin":
            return Noeud("*", [Noeud("cos", [a]), da])
        # cos : (cos a)' = -sin(a) * a'
        moins_sin = Noeud("-", [Noeud(0), Noeud("sin", [a])])
        return Noeud("*", [moins_sin, da])