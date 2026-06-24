//================ CAMADA FÍSICA DL ========
void Phy_radio_receive_DL() {
  uint8_t packetSize = LoRa.parsePacket();
  tempo
  if (packetSize) {
    if (packetSize >= TAMANHO_PACOTE) { // Checa se o pacote recebido tem o tamanho em bytes da variável TAMANHO_PACOTE
       for (int i = 0; i < TAMANHO_PACOTE; i++) {
        PacoteDL[i] = LoRa.read();  // Faz a leitura do pacote recebido de DL pelo RFM95 pelo ESP32 no vetor PacoteDL
       }

          digitalWrite(LED_VERDE_PIN, HIGH);
          delay(100);
          digitalWrite(LED_VERDE_PIN, LOW);

      RSSI_dBm_DL = LoRa.packetRssi(); // Faz a leitura da RSSI medida pelo RFM95 em dBm
      SNR_DL = LoRa.packetSnr();       // Faz a leitura da SNR medida pelo RFM95
      
      //======== CHAMA A CAMADA MAC DL
      Mac_radio_receive_DL(); 
    }
  }
}

//================ CAMADA FÍSICA UL ========
void Phy_radio_send_UL() {

  //--- Bloco que faz adequação da leitura de RSSI para um byte ---
  if(RSSI_dBm_DL > -10.5)  // Caso a RSSI medida esteja acima do valor superior -10,5 dBm
  {
   RSSI_DL = 127; // equivalente a -10,5 dBm 
  }

  if(RSSI_dBm_DL <= -10.5 && RSSI_dBm_DL >= -74) // Caso a RSSI medida esteja no intervalo [-10,5 dBm e -74 dBm]
  {
   RSSI_DL = ((RSSI_dBm_DL +74)*2) ;
  }

  if(RSSI_dBm_DL < -74) // Caso a RSSI medida esteja no intervalo ]-74 dBm e -138 dBm]
  {
   RSSI_DL = (((RSSI_dBm_DL +74)*2)+256) ;
  }

  // =================Informações de gerência do pacote Início da montagem do pacote de UL
  PacoteUL[0] = RSSI_DL;
  SNR_DL = SNR_DL * 10; // O valor da SNR tem uma casa decimal e ao multiplicar por 10 fica inteiro
  SNR_DL_inteiro = (int)SNR_DL;
  PacoteUL[1] = (SNR_DL_inteiro/256);
  PacoteUL[2] = (SNR_DL_inteiro%256);
  Serial.println(SNR_DL_inteiro);
  // Esse condição considera que a SNR sempre será positiva e caso seja negativa deve ser tratada
 
 // ================= TRANMISSÃO DO PACOTE ENVIDADO PELO ESP32 PARA O RFM95
  LoRa.beginPacket();                 // Inicia o RFM95 que vai transmitir o pacote de 52 bytes
  for (int i = 0; i < TAMANHO_PACOTE; i++) {
    LoRa.write(PacoteUL[i]);          // Envia byte a byte as informações para o RFM95
  }
  LoRa.endPacket();                   // Finaliza o envio do pacote e o RFM95 transmite o pacote para o Gateway
  
  // Pisca o LED Vermelho indicando transmissão de pacote UL (se permitido)
  //if (modo_tx_vermelho == 1) {
      digitalWrite(LED_VERMELHO_PIN, HIGH);
      delay(100);
      digitalWrite(LED_VERMELHO_PIN, LOW);
  //}
}