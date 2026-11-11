# N3 LoRa Site Survey - Versão 28/01/2026 - WissTek-IoT UNICAMP
# Versão Final - Modo Real + Aplicação (Comentários Originais Restaurados)
# Versão Teste - Adição do Envio Configurações de Rádio LoRa para devices LoRa - Anderson Fumachi

# ========= Bibliotecas =================================
import serial
import math
import time
import struct
from time import localtime, strftime
import os
import random

#========== Criação de Variáveis Duplicadas =========================

numero_de_medidas = 0
rota = [] 
condicao_start = 0
medida_atual = 0 

# Camada Física (Geral)
tamanho_do_pacote = 14

# --- Variáveis Sensor 1 ---
rssi_DL1 = 0; rssi_UL1 = 0 

snr_DL1 = 0; snr_UL1 = 0

contador_DL1 = 0; contador_UL_recebidos1 = 0
ultimo_pacote_DL1 = 0; ultimo_pacote_UL1 = 0

psr_DL1 = 0; 
psr_UL1 = 0; 
psr_geral1 = 0 
perdas_DL1 = 0; 
perdas_UL1 = 0; 
perda_geral1 = 0

# --- Variáveis Sensor 2 ---
rssi_DL2 = 0; rssi_UL2 = 0 
snr_DL2 = 0; snr_UL2 = 0
contador_DL2 = 0; contador_UL_recebidos2 = 0
ultimo_pacote_DL2 = 0; ultimo_pacote_UL2 = 0
psr_DL2 = 0; psr_UL2 = 0; psr_geral2 = 0 
perdas_DL2 = 0; perdas_UL2 = 0; perda_geral2 = 0

# Camada MAC
tempo_entre_medidas = 8 # Fixo em 8 segundos para enviar ao firmware (evita timeout antecipado)
ID_base = 0

#========== Criação de Pacotes
Pacote_UL = [0] * tamanho_do_pacote
Pacote_DL = [0] * tamanho_do_pacote

#========== Configuração da Porta Serial ==================
ser = None 

#========== Criação de Arquivos de Gerência ===============
dir_nivel4 = os.path.join(os.path.dirname(__file__), '../N4/')

if os.path.exists(os.path.join(dir_nivel4, 'dados_gerencia.tmp')): 
   os.remove(os.path.join(dir_nivel4, 'dados_gerencia.tmp')) 

if os.path.exists(os.path.join(dir_nivel4, 'dados_aplicacao.tmp')):
   os.remove(os.path.join(dir_nivel4, 'dados_aplicacao.tmp')) 

arquivo_parametros = os.path.join(dir_nivel4, 'PARAMETROS.txt')
Parametros = open(arquivo_parametros, 'w')
Parametros.write("0\n0\n12\n500000\n5\n17\n") 
Parametros.close()

# Variáveis de Arquivo Duplicadas
arquivo_LOG_pacote1 = ""; arquivo_LOG_gerencia1 = ""; arquivo_LOG_aplicacao1 = ""
arquivo_LOG_pacote2 = ""; arquivo_LOG_gerencia2 = ""; arquivo_LOG_aplicacao2 = ""


# =====================================================================
#                        FUNÇÕES PARA O SENSOR 1
# =====================================================================
def downlink_1():
   global rssi_DL1, rssi_UL1, contador_UL_recebidos1, contador_DL1, ultimo_pacote_DL1, ultimo_pacote_UL1, Pacote_DL, snr_DL1, snr_UL1, tempo_entre_medidas, ID_base
   # Criação do Pacote
   for i in range(tamanho_do_pacote):
       Pacote_DL[i] = 0

   if(medida_atual == numero_de_medidas):
       Pacote_DL[9] = 1
       Pacote_DL[0] = 1

   Pacote_DL[8] = 1 # Endereço Fixo do Sensor 1
   Pacote_DL[7] = ID_base  
   Pacote_DL[6] = int((tempo_entre_medidas))

   if (ser is not None):
       ser.write(bytearray(Pacote_DL))
       contador_DL1 = contador_DL1 + 1
       
   print("[Nível 3 - Borda] - Física - Pacote de Downlink (SENSOR 1)")
   print(*Pacote_DL)
   print("================================================")        
   print('##### Pacote enviado para Nó Sensor 1 (Downlink)')

def uplink_1():
   global perdas_DL1, perdas_UL1, rssi_DL1, rssi_UL1, snr_DL1, snr_UL1, contador_UL_recebidos1, ultimo_pacote_DL1, ultimo_pacote_UL1, Pacote_UL
   # Verifica Integridade do Pacote
   if (ser is not None):
       if(ser.in_waiting > 0):
           Pacote_UL_bytes = ser.read(tamanho_do_pacote) 
           if len(Pacote_UL_bytes) == tamanho_do_pacote: 
               Pacote_UL = [0] * tamanho_do_pacote
               for i in range(tamanho_do_pacote): 
                   Pacote_UL[i] = Pacote_UL_bytes[i]
           else:
               Pacote_UL = [] 
       else:
           Pacote_UL = [] 
    # Retira a RSSI UL e DL
   if(len(Pacote_UL) == tamanho_do_pacote): 
      val_rssi_dl = Pacote_UL[0]
      val_rssi_ul = Pacote_UL[3]
      
      print("[Nível 3 - Borda] - Física - Pacote de Uplink (SENSOR 1)")
      print(*Pacote_UL)
      print("================================================")
      # Converte a RSSI para o número real em dBm
      if val_rssi_dl > 127: rssi_DL1 = ((val_rssi_dl - 256) / 2.0) - 74.0
      else: rssi_DL1 = (val_rssi_dl / 2.0) - 74.0
      
      if val_rssi_ul > 127: rssi_UL1 = ((val_rssi_ul - 256) / 2.0) - 74.0
      else: rssi_UL1 = (val_rssi_ul / 2.0) - 74.0
      
      snr_DL1 = round((Pacote_UL[1] / 4) - 30, 2)
      snr_UL1 = round((Pacote_UL[4] / 4) - 30, 2)

      if(Pacote_UL[7] == 1 and Pacote_UL[8] == ID_base):
         print("##### OK - Pacote recebido (Uplink) Sensor 1")

         contador_UL_recebidos1 = contador_UL_recebidos1 + 1
         ultimo_pacote_UL1 = int(Pacote_UL[12]*256) + Pacote_UL[13] 
         ultimo_pacote_DL1 = int(Pacote_UL[9]*256) + Pacote_UL[10]
         
         if(Pacote_UL[11] == 1):
             perdas_DL1 = perdas_DL1 + 1   
   else:
      perdas_UL1 = perdas_UL1 + 1
      print("##### FALHA - Pacote não recebido do Sensor 1")

def calculaPSR_1():
    global psr_DL1, psr_UL1, psr_geral1
    total_esperado_ul = numero_de_medidas  
    if contador_DL1 > 0:
        psr_DL1 = ((contador_DL1 - perdas_DL1) / contador_DL1) * 100
    if total_esperado_ul > 0:
        psr_UL1 = ((contador_UL_recebidos1) / medida_atual) * 100
    psr_geral1 = (psr_DL1 + psr_UL1) / 2

def gravaLOG_Pacote_1():
   log = open(arquivo_LOG_pacote1, 'a')
   print(strftime("%d/%m/%Y %H:%M:%S"),";",Pacote_UL, file=log)
   log.close()
        
def gravaLOG_Gerencia_1():
     global rssi_DL1, rssi_UL1, snr_DL1, snr_UL1, perda_geral1, psr_DL1, psr_UL1, medida_atual 

     gerencia = open(os.path.join(dir_nivel4, 'dados_gerencia.tmp'), 'a')
     print(medida_atual, ";", rssi_DL1, ";", round(psr_DL1, 2), ";", round(psr_UL1, 2), ";", rssi_UL1, ";", snr_DL1, ";", snr_UL1, file=gerencia, sep='')
     gerencia.close()
     
     log_def = open(arquivo_LOG_gerencia1, 'a')
     print(strftime("%d/%m/%Y %H:%M:%S"), ";", medida_atual, ";", rssi_DL1, ";", rssi_UL1, ";", snr_DL1, ";", snr_UL1, ";", round(psr_DL1,2), ";", round(psr_UL1, 2), file=log_def, sep='')
     log_def.close()

     print("S1 | Rssi DL: ", rssi_DL1, " | RSSI UL: ", rssi_UL1, " | SNR DL: ", snr_DL1, " | SNR UL: ", snr_UL1, " | PSR DL: ", round(psr_DL1, 2), " | PSR UL: ", round(psr_UL1, 2), "%")


# =====================================================================
#                        FUNÇÕES PARA O SENSOR 2
# =====================================================================
def downlink_2():
   global rssi_DL2, rssi_UL2, contador_UL_recebidos2, contador_DL2, ultimo_pacote_DL2, ultimo_pacote_UL2, Pacote_DL, snr_DL2, snr_UL2, tempo_entre_medidas, ID_base
   
   for i in range(tamanho_do_pacote):
       Pacote_DL[i] = 0

   if(medida_atual == numero_de_medidas):
       Pacote_DL[9] = 1
       Pacote_DL[0] = 1

   Pacote_DL[8] = 2 # Endereço Fixo do Sensor 2
   if(medida_atual == 5):
       Pacote_DL[8] = 9
   Pacote_DL[7] = ID_base  
   Pacote_DL[6] = int((tempo_entre_medidas)) 

   if (ser is not None):
       ser.write(bytearray(Pacote_DL))
       contador_DL2 = contador_DL2 + 1
       
   print("[Nível 3 - Borda] - Física - Pacote de Downlink (SENSOR 2)")
   print(*Pacote_DL)
   print("================================================")        
   print('##### Pacote enviado para Nó Sensor 2 (Downlink)')

def uplink_2():
   global perdas_DL2, perdas_UL2, rssi_DL2, rssi_UL2, snr_DL2, snr_UL2, contador_UL_recebidos2, ultimo_pacote_DL2, ultimo_pacote_UL2, Pacote_UL
   
   if (ser is not None):
       if(ser.in_waiting > 0):
           Pacote_UL_bytes = ser.read(tamanho_do_pacote) 
           if len(Pacote_UL_bytes) == tamanho_do_pacote: 
               Pacote_UL = [0] * tamanho_do_pacote
               for i in range(tamanho_do_pacote): 
                   Pacote_UL[i] = Pacote_UL_bytes[i]
           else:
               Pacote_UL = [] 
       else:
           Pacote_UL = [] 
           
   if(len(Pacote_UL) == tamanho_do_pacote): 
      val_rssi_dl = Pacote_UL[0]
      val_rssi_ul = Pacote_UL[3]
      
      print("[Nível 3 - Borda] - Física - Pacote de Uplink (SENSOR 2)")
      print(*Pacote_UL)
      print("================================================")
      
      if val_rssi_dl > 127: rssi_DL2 = ((val_rssi_dl - 256) / 2.0) - 74.0
      else: rssi_DL2 = (val_rssi_dl / 2.0) - 74.0
      
      if val_rssi_ul > 127: rssi_UL2 = ((val_rssi_ul - 256) / 2.0) - 74.0
      else: rssi_UL2 = (val_rssi_ul / 2.0) - 74.0
      
      snr_DL2 = round((Pacote_UL[1] / 4) - 30, 2)
      snr_UL2 = round((Pacote_UL[4] / 4) - 30, 2)

      if(Pacote_UL[7] == 2 and Pacote_UL[8] == ID_base):
         print("##### OK - Pacote recebido (Uplink) Sensor 2")

         contador_UL_recebidos2 = contador_UL_recebidos2 + 1
         ultimo_pacote_UL2 = int(Pacote_UL[12]*256) + Pacote_UL[13] 
         ultimo_pacote_DL2 = int(Pacote_UL[9]*256) + Pacote_UL[10]
         
         if(Pacote_UL[11] == 1):
             perdas_DL2 = perdas_DL2 + 1   
   else:
      perdas_UL2 = perdas_UL2 + 1
      print("##### FALHA - Pacote não recebido do Sensor 2")

def calculaPSR_2():
    global psr_DL2, psr_UL2, psr_geral2
    total_esperado_ul = numero_de_medidas  
    if contador_DL2 > 0:
        psr_DL2 = ((contador_DL2 - perdas_DL2) / contador_DL2) * 100
    if total_esperado_ul > 0:
        psr_UL2 = ((contador_UL_recebidos2) / medida_atual) * 100
    psr_geral2 = (psr_DL2 + psr_UL2) / 2

def gravaLOG_Pacote_2():
   log = open(arquivo_LOG_pacote2, 'a')
   print(strftime("%d/%m/%Y %H:%M:%S"),";",Pacote_UL, file=log)
   log.close()
        
def gravaLOG_Gerencia_2():
     global rssi_DL2, rssi_UL2, snr_DL2, snr_UL2, perda_geral2, psr_DL2, psr_UL2, medida_atual 

     gerencia = open(os.path.join(dir_nivel4, 'dados_gerencia.tmp'), 'a')
     print(medida_atual, ";", rssi_DL2, ";", round(psr_DL2, 2), ";", round(psr_UL2, 2), ";", rssi_UL2, ";", snr_DL2, ";", snr_UL2, file=gerencia, sep='')
     gerencia.close()
     
     log_def = open(arquivo_LOG_gerencia2, 'a')
     print(strftime("%d/%m/%Y %H:%M:%S"), ";", medida_atual, ";", rssi_DL2, ";", rssi_UL2, ";", snr_DL2, ";", snr_UL2, ";", round(psr_DL2,2), ";", round(psr_UL2, 2), file=log_def, sep='')
     log_def.close()

     print("S2 | Rssi DL: ", rssi_DL2, " | RSSI UL: ", rssi_UL2, " | SNR DL: ", snr_DL2, " | SNR UL: ", snr_UL2, " | PSR DL: ", round(psr_DL2, 2), " | PSR UL: ", round(psr_UL2, 2), "%")


# =====================================================================
#                        LOOP PRINCIPAL
# =====================================================================

while True:
   if ser is None:
       try:
           print("Configuração da porta serial (caminho completo)")
           print("Para Windows: COM3, COM4, etc")
           print("Para Linux: /dev/ttyUSB0 , /dev/ttyUSB1, etc")
           porta_serial = input("Digite aqui:")
           ser = serial.Serial(porta_serial, 115200, timeout=1, parity=serial.PARITY_NONE)
           numero_de_medidas = int(input("Digite o número de medidas a serem realizadas: "))
           # O tempo entre medidas do input não é mais usado individualmente, ele é fixo no DL e intercalado no loop.
           condicao_start = 1
           print("Porta Serial Conectada")
       except:
           pass 
           
   if (condicao_start == 1):
      if (medida_atual == 0): 
         print("################## Iniciando testes S1 e S2 #################")
         
         # Reset de variáveis
         contador_DL1 = 0; contador_UL_recebidos1 = 0; psr_geral1 = 0; perda_geral1 = 0
         rssi_DL1 = 0; rssi_UL1 = 0
         contador_DL2 = 0; contador_UL_recebidos2 = 0; psr_geral2 = 0; perda_geral2 = 0
         rssi_DL2 = 0; rssi_UL2 = 0
         
         # Criação dos arquivos de LOG SENSOR 1
         arquivo_LOG_pacote1 = os.path.join(dir_nivel4, strftime("LOG_pacote_S1_%Y_%m_%d_%H-%M-%S.txt"))
         arquivo_LOG_gerencia1 = os.path.join(dir_nivel4, strftime("LOG_gerencia_S1_%Y_%m_%d_%H-%M-%S.txt"))
         
         # Criação dos arquivos de LOG SENSOR 2
         arquivo_LOG_pacote2 = os.path.join(dir_nivel4, strftime("LOG_pacote_S2_%Y_%m_%d_%H-%M-%S.txt"))
         arquivo_LOG_gerencia2 = os.path.join(dir_nivel4, strftime("LOG_gerencia_S2_%Y_%m_%d_%H-%M-%S.txt"))
         
         print ("Log Pacote S1: %s" % arquivo_LOG_pacote1)
         print ("Log Gerencia S1: %s" % arquivo_LOG_gerencia1)
         print ("Log Pacote S2: %s" % arquivo_LOG_pacote2)
         print ("Log Gerencia S2: %s" % arquivo_LOG_gerencia2)
         
         # Inicializa arquivos físicos
         open(arquivo_LOG_pacote1, 'w').close()
         open(arquivo_LOG_pacote2, 'w').close()
         
         f1 = open(arquivo_LOG_gerencia1, 'w')
         print ('Time stamp;Contador;RSSI_DL;RSSI_UL;snr_DL;snr_UL;psr_DL;psr_UL', file=f1)
         f1.close()
         
         f2 = open(arquivo_LOG_gerencia2, 'w')
         print ('Time stamp;Contador;RSSI_DL;RSSI_UL;snr_DL;snr_UL;psr_DL;psr_UL', file=f2)
         f2.close()
         
         open(os.path.join(dir_nivel4, 'dados_gerencia.tmp'), 'w').close()
         
      if (medida_atual < numero_de_medidas):
         t_s = time.time()
         medida_atual = medida_atual + 1
         print("### Medida Geral:",medida_atual, "de ",numero_de_medidas)

         # ================= BLOCO DO SENSOR 1 =================
         print("--> Iniciando comunicação Sensor 1")
         
         downlink_1()
         t0 =time.time()
         time.sleep(3) # Aguarda o RFM95 e o ESP32 enviarem o UL (Phy_radio_send_UL)
         t1 = time.time()
         print("tempo entre DL e UL S1",t1 - t0)
         uplink_1()
         gravaLOG_Pacote_1()
         calculaPSR_1()
         gravaLOG_Gerencia_1()
         
         
         time.sleep(1) # Tempo intercalado (espera restante para o S2)
         
         # ================= BLOCO DO SENSOR 2 =================
         print("--> Iniciando comunicação Sensor 2")
         downlink_2()
         time.sleep(3) # Aguarda o RFM95 e o ESP32 enviarem o UL
         uplink_2()
         gravaLOG_Pacote_2()
         calculaPSR_2()
         gravaLOG_Gerencia_2()
         
         time.sleep(1) # Tempo de espera até iniciar a próxima medida (Fecha o ciclo de 8s)
         t2 = time.time()
         t_rota = t2 - t1
         print("T entre envios:", t_rota)
      else:
         print("################## Testes finalizados ##################")
         condicao_start = 0
         medida_atual = 0
         Parametros = open(arquivo_parametros, 'w')
         Parametros.write("0\n0\n") 
         Parametros.close()
         
   else:
      medida_atual = 0 
      print("Script pausado") 
      break