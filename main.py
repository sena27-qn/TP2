from noeud import Noeud

# Question 4 : exp(2 + y)
somme = Noeud("+")
somme.ajouter_enfant(Noeud(2))
somme.ajouter_enfant(Noeud("y"))
expr = Noeud("exp")
expr.ajouter_enfant(somme)

print(expr)  # exp + 2 y

# Question 5 : évaluation
print(expr.evaluer({"y": 1}))  # e^3 ≈ 20.0855
try:
    expr.evaluer({})
except ValueError as e:
    print("Erreur :", e)

# Question 6 : tracé de 3 * sin(x)
f = Noeud("*", [Noeud(3), Noeud("sin", [Noeud("x")])])
xs = [i * 0.1 for i in range(0, 63)]
f.tracer("x", xs)

# Question 7 : simplification de 1 + exp(0) -> 2 et de (x * 1) + 0 -> x
print(Noeud("+", [Noeud(1), Noeud("exp", [Noeud(0)])]).simplifiee())  # 2.0
print(Noeud("+", [Noeud("*", [Noeud("x"), Noeud(1)]), Noeud(0)]).simplifiee())  # x

# Question 8 : dérivée de 3 * sin(x) par rapport à x
print(f.derivee("x"))  # * 3 cos x