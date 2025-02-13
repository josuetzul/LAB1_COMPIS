import re

# Definición de tokens. 
TOKEN_REGEX = {
    'TYPE': re.compile(r'\b(bin|oct|hex)\b'),
    'ID': re.compile(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
    'EQUAL': re.compile(r'='),
    'NUM': re.compile(r'0b[01]+|0o[0-7]+|0x[0-9A-Fa-f]*|[0-9A-Fa-f]+|\d+'),
    'PLUS': re.compile(r'\+'), # A partir de acá fue generado con CHAT GPT las siguientes expresiones regulares.
    'MINUS': re.compile(r'-'),
    'TIMES': re.compile(r'\*'),
    'DIVIDE': re.compile(r'/'),
    'LPAREN': re.compile(r'\('),
    'RPAREN': re.compile(r'\)'),
    'SEMICOLON': re.compile(r';')
}

# Lexer (Tokenizador). Realizado en base a ejemplo en la clase y chat para adaptar a python. 
def lexer(input_text):
    tokens = []
    while input_text:
        input_text = input_text.lstrip()
        matched = False
        for token_type, pattern in TOKEN_REGEX.items():
            match = pattern.match(input_text)
            if match:
                tokens.append((token_type, match.group(0)))
                input_text = input_text[match.end():]
                matched = True
                break
        if not matched:
            raise SyntaxError(f"Error léxico en: {input_text}")
    tokens.append(('EOF', '')) 
    print("Tokens generados:", tokens)
    return tokens

# Validación de valores según el tipo de base. Generado con CHAT GPT
def is_valid_value(type_, value):
    if type_ == 'bin' and not re.fullmatch(r'[01]+', value):
        return False
    if type_ == 'oct' and not re.fullmatch(r'[0-7]+', value):
        return False
    if type_ == 'hex' and not re.fullmatch(r'[0-9A-Fa-f]*|[0-9A-Fa-f]+', value):
        return False
    return True

# Parser LL(1) para expresiones aritméticas. Generada con CHAT GPT en base a nuestra tabla realizada en el EXCEL
PARSE_TABLE = {
    'S': {'ID': ['E', 'EOF'], 'NUM': ['E', 'EOF'], 'LPAREN': ['E', 'EOF']},
    'E': {'ID': ['T', "E'"], 'NUM': ['T', "E'"], 'LPAREN': ['T', "E'"]},
    "E'": {'PLUS': ['PLUS', 'T', "E'"], 'MINUS': ['MINUS', 'T', "E'"], 'RPAREN': ['ε'], 'EOF': ['ε']},
    'T': {'ID': ['F', "T'"], 'NUM': ['F', "T'"], 'LPAREN': ['F', "T'"]},
    "T'": {'TIMES': ['TIMES', 'F', "T'"], 'DIVIDE': ['DIVIDE', 'F', "T'"], 'PLUS': ['ε'], 'MINUS': ['ε'], 'RPAREN': ['ε'], 'EOF': ['ε']},
    'F': {'ID': ['ID'], 'NUM': ['NUM'], 'LPAREN': ['LPAREN', 'E', 'RPAREN']}
}

# Parser LL(1) para expresiones

def parser(tokens):
    stack = ['S']
    index = 0

    while stack:
        top = stack.pop()
        token_type, token_value = tokens[index]

        if top in PARSE_TABLE:
            if token_type in PARSE_TABLE[top]:
                production = PARSE_TABLE[top][token_type]

                if production != ['ε']:
                    stack.extend(reversed(production))
            else:
                raise SyntaxError(f"Error de sintaxis cerca de {token_value}")
        elif top == token_type:
            print(f"Coincidencia: {top} == {token_type}")
            index += 1
        else:
            raise SyntaxError(f"Error de sintaxis: se esperaba {top}, pero se encontró {token_value}")
    print("Análisis sintáctico completado sin errores.")
    return True

# Evaluación de expresiones aritméticas
def evaluate_expression(expression, variables):
    for var in variables:
        expression = expression.replace(var, str(variables[var]))
    return eval(expression, {"__builtins__": None}, {})

# Entrada del usuario
def main():
    variables = {}
    print("Ingrese sus declaraciones de variables y luego su expresión matemática (escriba 'END' para finalizar las declaraciones):")
    
    while True:
        line = input(">> ")
        if line.strip().upper() == "END":
            break
        tokens = lexer(line)
        if len(tokens) >= 4 and tokens[0][0] == 'TYPE' and tokens[1][0] == 'ID' and tokens[2][0] == 'EQUAL':
            var_name = tokens[1][1]
            var_value = tokens[3][1]
            if tokens[0][1] == 'bin':
                variables[var_name] = int(var_value, 2)
            elif tokens[0][1] == 'oct':
                variables[var_name] = int(var_value, 8)
            elif tokens[0][1] == 'hex':
                variables[var_name] = int(var_value, 16)
            else:
                variables[var_name] = int(var_value)
            print(f"Variable {var_name} almacenada con valor {variables[var_name]}")
        else:
            print("Error en la declaración de variable.")
    
    print("Ingrese la expresión aritmética para evaluar:")
    expression = input(">> ")
    tokens = lexer(expression)
    parser(tokens)
    result = evaluate_expression(expression, variables)
    print("Resultado:", result)

if __name__ == "__main__":
    main()