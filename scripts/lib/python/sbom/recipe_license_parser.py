import re

def strip_outer_parentheses(text):
    text = text.strip()
    while text.startswith('(') and text.endswith(')'):
        depth = 0
        is_outer = True
        for i, char in enumerate(text[:-1]):
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            if depth == 0 and i > 0:
                is_outer = False
                break

        if is_outer:
            text = text[1:-1].strip()
        else:
            break
    return text

def parse_to_license_array(expression):
    tokens = re.split(r'(\(|\)|\s+)', expression)
    
    elements = []
    current_element = []
    depth = 0

    for token in tokens:
        if not token:
            continue

        if token == '(':
            depth += 1
            current_element.append(token)
        elif token == ')':
            depth -= 1
            current_element.append(token)
        elif depth == 0 and token.strip().upper() == 'AND':
            elem_str = "".join(current_element).strip()
            if elem_str:
                elements.append(elem_str)
            current_element = []
        else:
            current_element.append(token)

    last_elem_str = "".join(current_element).strip()
    if last_elem_str:
        elements.append(last_elem_str)

    return [strip_outer_parentheses(elem) for elem in elements]

def normalize_license_name(raw_name, license_mapping):
    cleaned = raw_name.strip()
    lower_name = cleaned.lower()

    if lower_name in license_mapping:
        return license_mapping[lower_name]

    return raw_name

def tokenize(expression: str):
    pattern = r'(\(|\)|&|\||(?<![^\s()])(?:AND|OR)(?![^\s()]))'
    raw_tokens = re.split(pattern, expression, flags=re.IGNORECASE)
        
    tokens = []
    for t in raw_tokens:
        if not t or t.isspace():
            continue
        t_str = t.strip()
        if t_str == '&':
            tokens.append('AND')
        elif t_str == '|':
           tokens.append('OR')
        elif t_str.upper() in ('AND', 'OR'):
           tokens.append(t_str.upper())
        else:
           tokens.append(t_str)
    return tokens

def parse_to_ast(tokens, license_mapping):
    precedence = {'OR': 1, 'AND': 2}
    output_stack = []
    operator_stack = []
    licenses = []

    for token in tokens:
        if token in ('AND', 'OR'):
            while (operator_stack and operator_stack[-1] != '(' and
                   precedence.get(operator_stack[-1], 0) >= precedence[token]):
                op = operator_stack.pop()
                right = output_stack.pop()
                left = output_stack.pop()
                output_stack.append((op, left, right))
            operator_stack.append(token)
        elif token == '(':
            operator_stack.append(token)
        elif token == ')':
            while operator_stack and operator_stack[-1] != '(':
                op = operator_stack.pop()
                right = output_stack.pop()
                left = output_stack.pop()
                output_stack.append((op, left, right))
            if operator_stack and operator_stack[-1] == '(':
                operator_stack.pop()
        else:
            normalized_id = normalize_license_name(token, license_mapping)
            output_stack.append(normalized_id)
            licenses.append(normalized_id)

    while operator_stack:
       op = operator_stack.pop()
       right = output_stack.pop()
       left = output_stack.pop()
       output_stack.append((op, left, right))

    return output_stack[0] if output_stack else ""

def ast_to_spdx(node, parent_op=None):
    if isinstance(node, str):
        return node

    op, left, right = node
    left_str = ast_to_spdx(left, op)
    right_str = ast_to_spdx(right, op)

    res = f"{left_str} {op} {right_str}"

    precedence = {'OR': 1, 'AND': 2}
    if parent_op and precedence[op] < precedence[parent_op]:
        res = f"({res})"
    elif parent_op and parent_op != op:
        res = f"({res})"

    return res

def normalize_licese_field(raw_license, license_mapping):
    tokens = tokenize(raw_license)
    ast = parse_to_ast(tokens, license_mapping)
    return ast_to_spdx(ast)

def split_license_for_imager_bom_pkgs(licenses):
    return licenses 

