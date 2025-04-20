from ortools.constraint_solver import pywrapcp

solver = pywrapcp.Solver('CP is fun!')

base = 10
digits = list(range(0, base))
digits_without_zero = list(range(1, base))

c = solver.IntVar(digits_without_zero, 'C')
p = solver.IntVar(digits, "P")
i = solver.IntVar(digits_without_zero, "I")
s = solver.IntVar(digits, "S")
f = solver.IntVar(digits_without_zero, "F")
u = solver.IntVar(digits, "U")
n = solver.IntVar(digits, "N")
t = solver.IntVar(digits_without_zero, "T")
r = solver.IntVar(digits, "R")
e = solver.IntVar(digits, "E")

# 我们需要将变量分组到一个列表中，以使用约束 AllDifferent。
letters = [c, p, i, s, f, u, n, t, r, e]

solver.Add(solver.AllDifferent(letters))

# CP + IS + FUN = TRUE
solver.Add(
    p + s + n + base * (c + i + u) + base * base * f
    == e + base * u + base * base * r + base * base * base * t
)

# 验证我们是否有足够的数字。
assert base >= len(letters)

solution_count = 0
db = solver.Phase(letters, solver.INT_VAR_DEFAULT, solver.INT_VALUE_DEFAULT)
solver.NewSearch(db)
while solver.NextSolution():
    print(letters)
    # Is CP + IS + FUN = TRUE?
    assert (
            base * c.Value()
            + p.Value()
            + base * i.Value()
            + s.Value()
            + base * base * f.Value()
            + base * u.Value()
            + n.Value()
            == base * base * base * t.Value()
            + base * base * r.Value()
            + base * u.Value()
            + e.Value()
    )
    solution_count += 1
solver.EndSearch()
print(f"Number of solutions found: {solution_count}")