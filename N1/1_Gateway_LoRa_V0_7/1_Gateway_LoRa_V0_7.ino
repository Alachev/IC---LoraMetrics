/*
  MoT LoRa | WissTek IoT
  Última versão: Branquinho e Felipe (Adaptado para ESP32 - Gateway - Kit PKLORa)
*/

//=======================================================================
//                     1 - Bibliotecas
//=======================================================================
#include <SPI.h>
#include <LoRa.h>

//=======================================================================
//                     2 - Variáveis e Mapeamento
//=======================================================================
// As variávies utlizadas estão no arquivo de bibliotecas

// ============= Pinagem na placa da PK-LoRa da ligação do RFM95 com o ESP32
#define SCK_PIN    5
#define MISO_PIN  19
#define MOSI_PIN  27
#define NSS_PIN   18
#define RST_PIN   14
#define DIO0_PIN  26

// ============= CAMADA FÍSICA
// Parâmetros do LoRa
#define FREQUENCY_IN_HZ       915E6   // LoRa Frequency
#define txPower               17      // TX power in dBm, defaults to 17
#define spreadingFactor       7       // ranges from 6-12,default 7
#define signalBandwidth       500E3   // signal bandwidth in Hz
#define codingRateDenominator 5       // denominator of the coding rate

// Pinos de Saída Digitais (Opcional, mas útil para debug no Gateway)
#define LED_VERMELHO_PIN 15
#define LED_VERDE_PIN     4
#define RESET_PIN 2

// ============== Variáveis usadas no código do gateway
int RSSI_dBm_UL; // Variável com a potência rádio recebida (RSSI) no UL em dBm medida pelo RFM95
int RSSI_UL; // Variável de mapeamento da RSSI medida em um valor de 0 a 255 para colocar no pacote UL
float SNR_UL; // Variável com a relação sinal ruído de DL
int SNR_UL_inteiro; // Variável inteira para enviar a SNR, que será convertida para a SNR original no Python
// ============== CAMADA MAC
#define TAMANHO_PACOTE 14
byte PacoteDL[TAMANHO_PACOTE];
byte PacoteUL[TAMANHO_PACOTE];
int ID_gateway;    // Variável com o ID_gateway que estará no pacote de DL byte 10
bool reset_flag = false;
void(* resetFunc) (void) = 0; //declare reset function @ address 0
//=======================================================================
//                     3 - Setup de inicialização
//=======================================================================
void setup() {
  void(* resetFunc) (void) = 0; //declare reset function @ address 0
  //================= INICIALIZA SERIAL
  Serial.begin(115200);

   // Define as funções como OUTPUT dos pinos dos LEDs
  pinMode(LED_VERMELHO_PIN, OUTPUT);
  pinMode(LED_VERDE_PIN, OUTPUT);
  pinMode(RESET_PIN, OUTPUT);
  
  // Garante que os LEDs iniciem desligados
  digitalWrite(LED_VERMELHO_PIN, LOW);
  digitalWrite(LED_VERDE_PIN, LOW);
  digitalWrite(RESET_PIN, HIGH);

  //-------------------- INICIALIZAÇÃO MÓDULO RF95
  
  // 1. Remapeia o barramento SPI para os pinos do Kit LORa
  SPI.begin(SCK_PIN, MISO_PIN, MOSI_PIN, NSS_PIN);

  // 2. Informa à biblioteca LoRa os pinos de controle
  LoRa.setPins(NSS_PIN, RST_PIN, DIO0_PIN);

  if (!LoRa.begin(FREQUENCY_IN_HZ)) {
  //Serial.println("Erro ao iniciar LoRa");
  }
  
  //Serial.println("Módulo LoRa iniciado normalmente");
  LoRa.setTxPower(txPower); 
  LoRa.setSpreadingFactor(spreadingFactor); 
  LoRa.setSignalBandwidth(signalBandwidth); 
  LoRa.setCodingRate4(codingRateDenominator); 
  
  //Serial.println("Gateway LoRa Inicializado com Sucesso!");
  digitalWrite(LED_VERDE_PIN, HIGH);
  delay(1000);
  digitalWrite(LED_VERDE_PIN, LOW);
}

//=======================================================================
//                     4 - Loop de repetição
//=======================================================================
void loop() {
  Phy_serial_receive_DL();
  Phy_radio_receive_UL();
}