with open('VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5', 'r', encoding='utf-8') as f:
    c = f.read()

target = '   CreateOrUpdateText("VIKAR_HUD_STATUS_VAL", panelX + 15, currY + 19, g_lastSignalType, clrWhite, 7, "Segoe UI Bold");'
replacement = '''   string statusDisplay = g_lastSignalType;
   if (openCount == 0 && StringFind(g_lastSignalType, "EXECUTED") >= 0)
      statusDisplay = "ORDER SELESAI (SUDAH HIT TP / SL+) | SCANNING SETUP";
   CreateOrUpdateText("VIKAR_HUD_STATUS_VAL", panelX + 15, currY + 19, statusDisplay, clrWhite, 7, "Segoe UI Bold");'''

assert target in c, 'Target not found'
c = c.replace(target, replacement, 1)

with open('VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5', 'w', encoding='utf-8') as f:
    f.write(c)

print('Updated dashboard statusDisplay successfully!')
