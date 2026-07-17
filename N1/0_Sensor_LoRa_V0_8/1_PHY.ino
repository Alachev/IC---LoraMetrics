//================ CAMADA FÍSICA DL ========
void Phy_radio_receive_DL() {
  // --- Verificação de timeout ---
  if(start_flag == 1 && stop_flag == 0){
    unsigned long agora = millis();
    timeout_flag = 0;
   if (agora - last_packet_time >= (timeout_ms+500)) {
      if (!timeout_flag) {               // evita repetir a flag a cada ciclo
        timeout_flag = true;
        Serial.println("perdeu pacote DL por timeout");
        Serial.println(agora-last_packet_time);
        App_radio_send_UL();
     }
      last_packet_time = agora;          // reinicia a contagem para o próximo período
  }
  }
  // --- Verificação de pacote LoRa ---
  uint8_t packetSize = LoRa.parsePacket();
  if (packetSize) {
    if (packetSize >= TAMANHO_PACOTE) {
      for (int i = 0; i < TAMANHO_PACOTE; i++) {
        PacoteDL[i] = LoRa.read();
      }
      
      digitalWrite(LED_VERDE_PIN, HIGH);
      delay(100);
      digitalWrite(LED_VERDE_PIN, LOW);

      RSSI_dBm_DL = LoRa.packetRssi();
      SNR_DL = LoRa.packetSnr();

      // Atualiza o tempo do último pacote recebido (reset do timeout)
      last_packet_time = millis();

      // Chama a camada MAC
      Mac_radio_receive_DL();
    }
  }
}

//================ CAMADA FÍSICA UL ========
void Phy_radio_send_UL() {
  Serial.println("PHY UL");
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
  if(timeout_flag == false){
    PacoteUL[0] = RSSI_DL;
    /*SNR_DL = SNR_DL * 100; // O valor da SNR tem uma casa decimal e ao multiplicar por 10 fica inteiro
    SNR_DL_inteiro = (int)SNR_DL;
    PacoteUL[1] = (SNR_DL_inteiro/256);
    PacoteUL[2] = (SNR_DL_inteiro%256);*/
    //Serial.println(SNR_DL_inteiro);
     // 1. Trava o valor entre -30 e +30 para evitar que o byte estoure
    if (SNR_DL < -30.0) {
      SNR_DL = -30.0;
    }
    if (SNR_DL > 30.0) 
    {
      SNR_DL = 30.0;
    }
  // Usamos uint8_t (byte) para ocupar apenas 1 byte na memória.
  // Usamos a função round() para garantir que o número float seja 
  // arredondado corretamente antes de virar inteiro.
    SNR_DL_inteiro = (uint8_t)round((SNR_DL + 30.0) * 4.0); // Offset de 30.0dB e passo de 0.25dB (* 4.0)

  // --- Armazena informações de gerência no pacote UL ---
    PacoteUL[1] = (byte)SNR_DL_inteiro;
  }
  if(timeout_flag == true){
    PacoteUL[0] = 0;
    PacoteUL[1] = 0;
    PacoteUL[2] = 0;
    Serial.println("dados zerados de SNR e RSSI");
  }
  // Esse condição considera que a SNR sempre será positiva e caso seja negativa deve ser tratada
 
 // ================= TRANMISSÃO DO PACOTE ENVIDADO PELO ESP32 PARA O RFM95
  LoRa.beginPacket();                 // Inicia o RFM95 que vai transmitir o pacote de 52 bytes
  for (int i = 0; i < TAMANHO_PACOTE; i++) {
    LoRa.write(PacoteUL[i]);          // Envia byte a byte as informações para o RFM95
  }
  LoRa.endPacket();                   // Finaliza o envio do pacote e o RFM95 transmite o pacote para o Gateway
  Serial.println("Flag de Envio de timeout");
  Serial.println(PacoteUL[11]);
  Serial.println("Pacote Enviado");
  Serial.println("========================================");
  // Pisca o LED Vermelho indicando transmissão de pacote UL (se permitido)
  if (PacoteUL[11] == 0) {
      digitalWrite(LED_VERMELHO_PIN, HIGH);
      delay(100);
      digitalWrite(LED_VERMELHO_PIN, LOW);
  }
      if (PacoteUL[11] == 1) {
      digitalWrite(LED_AMARELO_PIN, HIGH);
      delay(100);
      digitalWrite(LED_AMARELO_PIN, LOW);
      }
    if(stop_flag == true){
      digitalWrite(LED_VERMELHO_PIN, HIGH);
      digitalWrite(LED_VERDE_PIN, HIGH);
      delay(1000);
      ESP.restart();
    }
  //}
}