import operator

from src.data_structure.structure.BinaryTree import BinaryTree
from src.data_structure.structure.Stack import Stack


def build_parse_tree(exp: str):
    exp_list = [item for item in list(exp) if item != ' ']
    stack = Stack()
    t = BinaryTree('')
    stack.push(t)
    current_tree = t
    for item in exp_list:
        if item == '(':
            current_tree.insert_left('')
            stack.push(current_tree)
            current_tree = current_tree.get_left_child()
        elif item not in '+-*/)':
            current_tree.set_root_value(int(item))
            current_tree = stack.pop()
        elif item in '+-*/':
            current_tree.set_root_value(item)
            current_tree.insert_right('')
            stack.push(current_tree)
            current_tree = current_tree.get_right_child()
        elif item == ')':
            current_tree = stack.pop()
        else:
            raise ValueError('未知的操作符：' + item)
    return t


def evaluate(t: BinaryTree):
    operators = {'+': operator.add, '-': operator.sub, '*': operator.mul, '/': operator.truediv}
    left_c = t.get_left_child()
    right_c = t.get_right_child()
    if left_c and right_c:
        fn = operators[t.get_root_value()]
        return fn(evaluate(left_c), evaluate(right_c))
    else:
        return t.get_root_value()


def post_order_eval(t: BinaryTree):
    operators = {'+': operator.add, '-': operator.sub, '*': operator.mul, '/': operator.truediv}
    if t:
        result_a = post_order_eval(t.get_left_child())
        result_b = post_order_eval(t.get_right_child())
        if result_a and result_b:
            return operators[t.get_root_value()](result_a, result_b)
        else:
            return t.get_root_value()


s_exp = '( 3 + ( 4 * 5 ) )'
tree = build_parse_tree(s_exp)
result = post_order_eval(tree)
print(result)
