import re

with open('VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("--- AUDIT 1: ORDER LOOPS & CLOSES ---")
for i, line in enumerate(lines):
    if 'OrdersTotal' in line or 'OrdersHistoryTotal' in line:
        print(f"Line {i+1}: {line.strip()}")
        # print next 5 lines
        for j in range(1, 6):
            if i+j < len(lines):
                print(f"   +{j}: {lines[i+j].strip()}")

print("\n--- AUDIT 2: ALL OrderClose CALLS ---")
for i, line in enumerate(lines):
    if 'OrderClose(' in line:
        print(f"Line {i+1}: {line.strip()}")

print("\n--- AUDIT 3: ALL OrderModify CALLS ---")
for i, line in enumerate(lines):
    if 'OrderModify(' in line:
        print(f"Line {i+1}: {line.strip()}")

print("\n--- AUDIT 4: ALL OrderSend CALLS ---")
for i, line in enumerate(lines):
    if 'OrderSend(' in line:
        print(f"Line {i+1}: {line.strip()}")
