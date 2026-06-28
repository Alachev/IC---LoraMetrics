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

#========== Criação de Variáveis =========================
global rssi_DL, rssi_UL, contador_UL_recebidos, contador_DL, ultimo_pacote_DL, ultimo_pacote_UL, air_quality_indicator 
 # definições de teste: configurações importantes para a bateria de testes extraídas do arquivo de parâmetros

numero_de_medidas = 0
rota = [] # neste momento é um enlace ponto a ponto, que futuramente poderá ser usada para roteamento
condicao_start = 0
medida_atual = 0 # Variáveis Auxiliares

 # Camada Física
tamanho_do_pacote = 14
rssi_DL = 0
rssi_UL = 0 
snr_DL = 0
snr_UL = 0

 # Camada MAC
tempo_entre_medidas = 1 # original = 1 # alterado para 10 pior caso SF12/vw125k/cr8/pw17
 # Camada de Rede
ID_base = 0
ID_sensor = 1

 # Camada de Transporte
contador_DL = 0
ultimo_pacote_DL = 0
contador_UL_recebidos = 0
ultimo_pacote_UL = 0

 # Contabilização de PSR
psr_DL = 0
psr_UL = 0
psr_geral = 0 #Utilizada temporariamente, antes de implementar a 'separação' da PSR de Downlink e Uplink
perdas_DL = 0
perdas_UL = 0
perda_geral = 0


#========== Criação de Pacotes
Pacote_UL = [0] * tamanho_do_pacote
Pacote_DL = [0] * tamanho_do_pacote

#========== Configuração da Porta Serial ==================
ser = None # Inicializa vazia, será configurada no loop

#========== Criação de Arquivos de Gerência ===============
# Este conjunto de linhas serve para deletar os arquivos temporários de armazenamento para observação de dados em tempo real

dir_nivel4 = os.path.join(os.path.dirname(__file__), '../N4/')

if os.path.exists(os.path.join(dir_nivel4, 'dados_gerencia.tmp')): # Procura no Nível 4 se há um arquivo de gerência
   os.remove(os.path.join(dir_nivel4, 'dados_gerencia.tmp')) # Se há um arquivo de gerência, ele é deletado

if os.path.exists(os.path.join(dir_nivel4, 'dados_aplicacao.tmp')):# Procura no Nível 4 se há um arquivo de aplicação
   os.remove(os.path.join(dir_nivel4, 'dados_aplicacao.tmp')) # Se há um arquivo de aplicação, ele é deletado

# Cria o arquivo de parâmetros zerado para garantir estado inicial
arquivo_parametros = os.path.join(dir_nivel4, 'PARAMETROS.txt')
Parametros = open(arquivo_parametros, 'w')
Parametros.write("0\n0\n12\n500000\n5\n17\n") # Adicionadas as linhas n12\n125000\n5\n17 no arquivo temporário de SF\BW\CR\PW
Parametros.close()

# Variáveis de Arquivo (serão definidas no loop ao iniciar o teste)
arquivo_LOG_pacote = ""
arquivo_LOG_gerencia = ""
arquivo_LOG_aplicacao = ""

def downlink():
   global rssi_DL, rssi_UL, contador_UL_recebidos, contador_DL, ultimo_pacote_DL, ultimo_pacote_UL, air_quality_indicator, Pacote_DL, snr_DL, snr_UL, tempo_entre_medidas, ID_sensor, ID_base
   
   # Limpa o pacote para garantir que não tem lixo
   for i in range(tamanho_do_pacote):
       Pacote_DL[i] = 0


   # Camada de Aplicação

   # Camada de Transporte
   if(medida_atual==numero_de_medidas):
       Pacote_DL[9] = 1
   # Camada de Rede
   Pacote_DL[8] = ID_sensor # Endereço do nó sensor vai ser colocado no Byte 8
   Pacote_DL[7] = ID_base  # Endereço da base vai ser colocado no Byte 7
   
   # Camada MAC
   Pacote_DL[6] = tempo_entre_medidas # Tempo entre pacotes (em segundos) - byte 6
   
   # Camada Física
   if(medida_atual==numero_de_medidas):
       Pacote_DL[0] = 1 # Indica que é o último pacote do teste, para o nó sensor parar de enviar dados
   #if(medida_atual >= 4 and medida_atual<=6):
    #   Pacote_DL[3] = 1
     #  print('perda gerada')

  # Envio para o Hardware (Modo Real)
   if (ser is not None):
       ser.write(bytearray(Pacote_DL))
       contador_DL = contador_DL + 1
      # Imprime Pacote_DL na Serial Para DEBUG
   print("[Nível 3 - Borda] - Física - Pacote de Downlink")
   print(*Pacote_DL)
   print("================================================")        
   print('##### Pacote enviado para Nó Sensor (Downlink)')

def uplink():
   global perdas_DL, perdas_UL, rssi_DL, rssi_UL, snr_DL, snr_UL, contador_UL_recebidos, ultimo_pacote_DL, ultimo_pacote_UL, Pacote_UL, perda_UL_ultimo_pacote
   
   # Camada Física
   # Leitura do Hardware
   #Se existe um objeto serial configurado
   if (ser is not None):
       #Existe ao menos 1 byte esperando na serial?
       if(ser.in_waiting > 0):
           #Realiza a a leitura da serial
           Pacote_UL_bytes = ser.read(tamanho_do_pacote) 
           if len(Pacote_UL_bytes) == tamanho_do_pacote: 
               
               # Cria novamente um pacote vazio para receber os dados
               Pacote_UL = [0] * tamanho_do_pacote
               
               # Copia para o um vetor (lista) com números, pois o que chega da serial são bytes
               for i in range(tamanho_do_pacote): 
                   Pacote_UL[i] = Pacote_UL_bytes[i]
           else:
               Pacote_UL = [] 
       else:
           Pacote_UL = [] 
           
   if(len(Pacote_UL)==tamanho_do_pacote): 
      val_rssi_dl = Pacote_UL[0]
      val_rssi_ul = Pacote_UL[3]
      
      # Imprime Pacote_UL na Serial Para DEBUG
      # ----------------------------------------------------------------------
      print("[Nível 3 - Borda] - Física - Pacote de Uplink")
      # ----------------------------------------------------------------------
      print(*Pacote_UL)
      print("================================================")
      
      # Conversão de Byte para RSSI (Cálculo Ajustado)
      # Fórmula: dbm = ((rssi_int - 256) / 2.0) - 74.0 (se > 127) ou (rssi_int / 2.0) - 74.0
      
      # Cálculo para Downlink
      if val_rssi_dl > 127:
          rssi_DL = ((val_rssi_dl - 256) / 2.0) - 74.0
      else:
          rssi_DL = (val_rssi_dl / 2.0) - 74.0
      
      # Cálculo para Uplink
      if val_rssi_ul > 127:
          rssi_UL = ((val_rssi_ul - 256) / 2.0) - 74.0
      else:
          rssi_UL = (val_rssi_ul / 2.0) - 74.0
      #SNR Downlink
      snr_DL = int(Pacote_UL[1]*256 + Pacote_UL[2])/100

         #SNR Uplink
      snr_UL = int(Pacote_UL[4]*256 + Pacote_UL[5])/100

   # Camada MAC

   # Camada de Rede
      if(Pacote_UL[7]== 1 and Pacote_UL[8] ==0):
         print("##### OK - Pacote recebido (Uplink)")

   # Camada de Transporte
         contador_UL_recebidos = contador_UL_recebidos + 1
         ultimo_pacote_UL = int(Pacote_UL[12]*256) + Pacote_UL[13] 
         ultimo_pacote_DL = int(Pacote_UL[9]*256) + Pacote_UL[10]
         if(Pacote_UL[11]==1):
             perdas_DL = perdas_DL + 1   

   # Camada de Aplicação      
         # Processamento da Luminosidade (LDR)
         # Reconstrói valor de 10 bits 
         
   else:
      perdas_UL = perdas_UL+1
      print("##### FALHA - Pacote não recebido")

def calculaPSR():
    global psr_DL, psr_UL, psr_geral
    total_esperado_ul = numero_de_medidas   # ou outra variável que conte os UL enviados
    if contador_DL > 0:
        psr_DL = ((contador_DL - perdas_DL) / contador_DL) * 100
        #print('contador dl',contador_DL,'perdas DL',perdas_DL)
    if total_esperado_ul > 0:
        psr_UL = ((contador_UL_recebidos) / medida_atual) * 100
        #print('contador de ul recebidos',contador_UL_recebidos, 'perdas ul',perdas_UL)
    psr_geral = (psr_DL + psr_UL) / 2

def gravaLOG_Pacote():
   log = open(arquivo_LOG_pacote, 'a')
   print(strftime("%d/%m/%Y %H:%M:%S"),";",Pacote_UL, file=log)
   log.close()
        
#========== Armazenamento de Dados para Exibição
def gravaLOG_Gerencia():
     global rssi_DL, rssi_UL, snr_DL, snr_UL, perda_geral, psr_DL, psr_UL, medida_atual 

     # 1. Grava no arquivo temporário (.tmp) para o Nível 6 Rede ler
     gerencia = open(os.path.join(dir_nivel4, 'dados_gerencia.tmp'), 'a')
     print(medida_atual, ";", rssi_DL, ";", round(psr_DL, 2), ";", round(psr_UL, 2), ";", rssi_UL, ";", snr_DL, ";", snr_UL, file=gerencia, sep='')
     gerencia.close()
     
     # 2. Grava no arquivo de LOG definitivo
     log_def = open(arquivo_LOG_gerencia, 'a')
     print(strftime("%d/%m/%Y %H:%M:%S"), ";", medida_atual, ";", rssi_DL, ";", rssi_UL, ";", snr_DL, ";", snr_UL, ";", perda_geral, ";", round(psr_geral, 2), file=log_def, sep='')
     log_def.close()

     print("Rssi DL: ", rssi_DL, " | RSSI UL: ", rssi_UL, " | SNR DL: ", snr_DL, " | SNR UL: ", snr_UL, " | PSR DL: ", round(psr_DL, 2), " | PSR UL: ", round(psr_UL, 2), "%")



#==loop principal de execução do teste

while True:
   if ser is None:
    try:
        print("Configuração da porta serial (caminho completo)")
        print("Para Windows: COM3, COM4, etc")
        print("Para Linux: /dev/ttyUSB0 , /dev/ttyUSB1, etc")
        #porta_serial = input("Digite aqui:").strip()  # remove espaços extras
        ser = serial.Serial("/dev/ttyACM1", 115200, timeout=1)#, parity=serial.PARITY_NONE)
        numero_de_medidas = int(input("Digite o número de medidas a serem realizadas: "))
        condicao_start = 1
        print("Porta Serial Conectada")
    except Exception as e:
        print(f" Erro ao conectar na porta serial: {e}")
        ser = None          # Garante que permanece None para nova tentativa
        # condicao_start permanece 0, então o loop continua perguntando
   if (condicao_start == 1):
       
      #Apenas para imprimir um cabeçalho dos testes no terminal
      if (medida_atual == 0): # and (start_teste_site_suvey == 1)):
         print("################## Iniciando testes #################")
         
         # Reset de variáveis
         contador_DL = 0; contador_UL_recebidos = 0; psr_geral = 0; perda_geral = 0
         rssi_DL = 0; rssi_UL = 0; luminosidade = 0
         rssi_max_dl = -200; rssi_min_dl = 200; rssi_max_ul = -200; rssi_min_ul = 200
         
         # Criação do arquivo de LOG para armanezamento completo dos dados aquisitados
         arquivo_LOG_pacote = os.path.join(dir_nivel4, strftime("LOG_pacote_%Y_%m_%d_%H-%M-%S.txt"))
         arquivo_LOG_gerencia = os.path.join(dir_nivel4, strftime("LOG_gerencia_%Y_%m_%d_%H-%M-%S.txt"))
         
         print ("Arquivo de LOG de pacote: %s" % arquivo_LOG_pacote)
         print ("Arquivo de LOG de gerencia: %s" % arquivo_LOG_gerencia)
         
         # Inicializa arquivos físicos
         open(arquivo_LOG_pacote, 'w').close()
         
         f = open(arquivo_LOG_gerencia, 'w')
         print ('Time stamp;Contador;RSSI_DL;RSSI_UL;snr_DL;snr_UL;psr_DL;psr_UL', file=f)
         f.close()
         
         # Limpa temporários
         open(os.path.join(dir_nivel4, 'dados_gerencia.tmp'), 'w').close()

      
      if (medida_atual < numero_de_medidas):

         medida_atual = medida_atual + 1
         print("### Medida:",medida_atual, "de ",numero_de_medidas)
         t0 = time.time()
         downlink()
         time.sleep(tempo_entre_medidas-0.24)        
         uplink()
         print("Tempo entre DL e UL:",time.time()-t0)
         gravaLOG_Pacote()
         calculaPSR()
         gravaLOG_Gerencia()
         
         
      else:
         # Se atingiu o limite, para o script alterando o arquivo PARAMETROS
         print("################## Testes finalizados ##################")
         condicao_start = 0
         medida_atual = 0
         #Atualiza arquivo de Parâmetros   
         Parametros = open(arquivo_parametros, 'w')
         Parametros.write("0\n0\n") 
         Parametros.close()
   else:
     medida_atual = 0 # Garante que próximo teste comece do zero
     print("Script pausado") # Comentado para não poluir
     #time.sleep(1)
     break
       
