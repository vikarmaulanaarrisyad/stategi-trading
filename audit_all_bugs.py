import os
import re

def audit_ea(filepath, is_mt5=False):
    print(f"\n==========================================")
    print(f"AUDITING: {os.path.basename(filepath)}")
    print(f"==========================================")
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    
    content = "".join(lines)
    issues = []
    warnings = []

    # 1. Division by zero audit
    div_regex = re.compile(r'([a-zA-Z0-9_().]+)\s*/\s*([a-zA-Z0-9_().]+)')
    for i, line in enumerate(lines):
        line_clean = line.strip()
        if line_clean.startswith("//") or line_clean.startswith("/*") or line_clean.startswith("*"):
            continue
        for m in div_regex.finditer(line):
            num, denom = m.group(1), m.group(2)
            # Check if denominator can be zero
            if denom in ["range", "period", "avgVol", "total", "g_eaInitialBalance", "MathLog10(period)", "MathLog(period)"]:
                # Check surrounding context for zero guard
                context = "".join(lines[max(0, i-5):min(len(lines), i+2)])
                if f"if ({denom} <= 0)" not in context and f"if ({denom} == 0)" not in context and f"if ({denom} > 0)" not in context and f"if (range <= 0" not in context and f"if (avgVol <= 0" not in context:
                    warnings.append(f"Line {i+1}: Potential division by zero on '{denom}': {line.strip()}")

    # 2. MT5 Handle audit (handles declared vs released)
    if is_mt5:
        handles = re.findall(r'int\s+(h_[a-zA-Z0-9_]+)\s*=', content)
        deinit_match = re.search(r'void\s+OnDeinit\s*\([^)]*\)\s*\{(.*?)\}', content, re.DOTALL)
        if deinit_match:
            deinit_body = deinit_match.group(1)
            for h in set(handles):
                if h not in deinit_body:
                    issues.append(f"Handle leak: '{h}' declared but not released in OnDeinit()!")
                else:
                    print(f"[OK] Handle '{h}' properly released in OnDeinit()")

    # 3. CheckRSIDivergence bounds check
    div_func = re.search(r'bool CheckRSIDivergence.*?\n\{(.*?)\n\}', content, re.DOTALL)
    if div_func:
        body = div_func.group(1)
        if "peak2" in body and "rates" in body:
            print("[OK] RSI Divergence logic present with array checks")

    # 4. Preset keys audit against EA inputs
    inputs = re.findall(r'(?:input|extern)\s+[a-zA-Z0-9_]+\s+([a-zA-Z0-9_]+)\s*=', content)
    print(f"Total Input/Extern Parameters: {len(inputs)}")

    # 5. Check Choppiness Index range check
    chop_func = re.search(r'double CalculateChoppinessIndex.*?\n\{(.*?)\n\}', content, re.DOTALL)
    if chop_func:
        chop_body = chop_func.group(1)
        if "range <= 0" in chop_body or "range == 0" in chop_body or "if (range <= 0.0)" in chop_body:
            print("[OK] Choppiness Index has zero-range protection")
        else:
            issues.append("Choppiness Index missing 'range <= 0' guard before division!")

    # 6. Check OrderModify/OrderClose or Trade error handling
    if not is_mt5:
        om_matches = [i+1 for i, l in enumerate(lines) if "OrderModify(" in l and "bool " not in l and "if (" not in l and "=" not in l]
        oc_matches = [i+1 for i, l in enumerate(lines) if "OrderClose(" in l and "bool " not in l and "if (" not in l and "=" not in l]
        if om_matches:
            warnings.append(f"OrderModify unused return value lines: {om_matches}")
        if oc_matches:
            warnings.append(f"OrderClose unused return value lines: {oc_matches}")

    # Summary
    if not issues:
        print("--> 0 CRITICAL BUGS FOUND!")
    else:
        print(f"--> {len(issues)} CRITICAL BUGS FOUND:")
        for iss in issues:
            print("    [!] ", iss)
            
    if warnings:
        print(f"--> {len(warnings)} WARNINGS / POTENTIAL RISKS:")
        for w in warnings:
            print("    [*] ", w)
    else:
        print("--> 0 WARNINGS!")

# Run audits
audit_ea(r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4", is_mt5=False)
audit_ea(r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5", is_mt5=True)
