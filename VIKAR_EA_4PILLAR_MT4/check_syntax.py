import re

with open('VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4', 'r', encoding='utf-8') as f:
    lines = f.readlines()

code_clean = []
in_block = False
for idx, line in enumerate(lines):
    clean = ""
    i = 0
    while i < len(line):
        if in_block:
            if line[i:i+2] == "*/":
                in_block = False
                i += 2
            else:
                i += 1
            continue
        if line[i:i+2] == "/*":
            in_block = True
            i += 2
            continue
        if line[i:i+2] == "//":
            break
        if line[i] == '"':
            # skip string
            i += 1
            while i < len(line) and line[i] != '"':
                if line[i] == '\\':
                    i += 1
                i += 1
            i += 1
            continue
        clean += line[i]
        i += 1
    code_clean.append((idx + 1, clean))

total_open = 0
total_close = 0
for lnum, cl in code_clean:
    total_open += cl.count('(')
    total_close += cl.count(')')

print(f"Clean parens: open={total_open}, close={total_close}, diff={total_open - total_close}")

total_b_open = 0
total_b_close = 0
for lnum, cl in code_clean:
    total_b_open += cl.count('{')
    total_b_close += cl.count('}')

print(f"Clean braces: open={total_b_open}, close={total_b_close}, diff={total_b_open - total_b_close}")
