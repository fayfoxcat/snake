# 构建模型。
from ortools.math_opt.python import mathopt

model = mathopt.Model(name="abc")
x = model.add_variable(lb=-1.0, ub=1.5, name="x")
y = model.add_variable(lb=0.0, ub=1.0, name="y")
model.add_linear_constraint(x + y <= 1.5)
model.maximize(x + 2 * y)

# 设置参数，例如开启日志记录。
params = mathopt.SolveParameters(enable_output=False)

# 求解并确保找到没有错误的最佳解决方案。
# （mathopt.solve 可能会在无效的输入或内部求解器上引发 RuntimeError
# 错误。
result = mathopt.solve(model, mathopt.SolverType.GLOP, params=params)
if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
    raise RuntimeError(f"模型求解失败: {result.termination}")

# 打印结果中的一些信息。
print("MathOpt 求解成功")
print("目标值:", result.objective_value())
print("x:", result.variable_values()[x])
print("y:", result.variable_values()[y])
