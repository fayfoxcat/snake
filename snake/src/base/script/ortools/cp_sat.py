from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import IntVar


class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):

    def __init__(self,variables: list[cp_model.IntVar]) -> None:
        super().__init__()
        self.__variables = variables  # 存储要跟踪的变量列表
        self.__solution_count = 0    # 解计数器初始化为0

    def OnSolutionCallback(self) -> None:
        """每当找到新解时自动调用"""
        self.__solution_count += 1   # 解计数加1
        for item in self.__variables:
            # 打印每个变量的值，使用self.value()获取变量在当前解中的值
            print(f"{item}={self.value(item)}", end=" ")
        print()

    @property
    def solution_count(self) -> int:
        """返回找到的解的数量"""
        return self.__solution_count


def search_for_all_solutions_sample_sat():
    """展示调用求解器以搜索所有解决方案的案例。"""
    # 创建模型。
    model = cp_model.CpModel()

    # 创建变量。
    num_vals = 3
    x:IntVar = model.new_int_var(0, num_vals - 1, "x")
    y:IntVar = model.new_int_var(0, num_vals - 1, "y")
    z:IntVar = model.new_int_var(0, num_vals - 1, "z")

    # 创建约束。
    model.add(x != y)

    # 创建求解器并求解。
    solver = cp_model.CpSolver()
    solution_printer = VarArraySolutionPrinter([x, y, z])
    #列举所有解决方案。
    solver.parameters.enumerate_all_solutions = True
    # 解
    status = solver.solve(model, solution_printer)

    print(f"状态 = {solver.status_name(status)}")
    print(f"找到的解决方案数量： {solution_printer.solution_count}")


search_for_all_solutions_sample_sat()