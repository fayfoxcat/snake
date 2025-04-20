"""
密码算术谜题。

第一次尝试求解方程 CP + IS + FUN = TRUE
其中每个字母代表一个唯一的数字。

这个问题有 72 种不同的解决方案，以 10 为基数。
"""
from ortools.sat.python import cp_model


class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    """打印过程解"""

    def __init__(self, variables: list[cp_model.IntVar]):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0

    def on_solution_callback(self) -> None:
        self.__solution_count += 1
        for v in self.__variables:
            print(f"{v}={self.value(v)}", end=" ")
        print()

    @property
    def solution_count(self) -> int:
        return self.__solution_count


def main() -> None:
    """解开 CP+IS+FUN==TRUE 密码法。"""
    # 约束规划引擎
    model = cp_model.CpModel()

    base = 10

    c = model.new_int_var(1, base - 1, "C")
    p = model.new_int_var(0, base - 1, "P")
    i = model.new_int_var(1, base - 1, "I")
    s = model.new_int_var(0, base - 1, "S")
    f = model.new_int_var(1, base - 1, "F")
    u = model.new_int_var(0, base - 1, "U")
    n = model.new_int_var(0, base - 1, "N")
    t = model.new_int_var(1, base - 1, "T")
    r = model.new_int_var(0, base - 1, "R")
    e = model.new_int_var(0, base - 1, "E")

    # 我们需要将变量分组到一个列表中，以使用约束 AllDifferent。
    letters = [c, p, i, s, f, u, n, t, r, e]

    # 验证我们是否有足够的数字: 如果有10个字母(base=10)，每个数字0-9刚好被使用一次；如果字母超过10个，就无法满足唯一性要求
    assert base >= len(letters)

    # 定义约束。
    model.add_all_different(letters)

    # CP + IS + FUN = TRUE
    model.add(
        c * base + p + i * base + s + f * base * base + u * base + n
        == t * base * base * base + r * base * base + u * base + e
    )

    # 创建求解器并求解模型。
    solver = cp_model.CpSolver()
    solution_printer = VarArraySolutionPrinter(letters)
    # 列举所有解决方案。
    solver.parameters.enumerate_all_solutions = True
    #解
    status = solver.solve(model, solution_printer)

    # Statistics.
    print("\n统计")
    print(f"  状态   : {solver.status_name(status)}")
    print(f"  冲突: {solver.num_conflicts}")
    print(f"  分支 : {solver.num_branches}")
    print(f"  wall time: {solver.wall_time} s")
    print(f"  sol found: {solution_printer.solution_count}")


if __name__ == "__main__":
    main()