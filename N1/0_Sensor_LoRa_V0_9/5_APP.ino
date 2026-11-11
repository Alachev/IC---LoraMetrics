//======== CAMADA DE APLICAÇÃO DO NÓ SENSOR
//====== COMANDOS
void App_radio_receive_DL() {
  // Acionamento do LED amarelo se o byte 34 está com valor 1
  //if (PacoteDL[34] == 1){
    //digitalWrite(LED_AMARELO_PIN, HIGH);
  //}
  //else{
   // digitalWrite(LED_AMARELO_PIN, LOW);
  //}
  Serial.println("APP DL");
//=============== CHAMA DA APLICAÇÃO DE UL 
  App_radio_send_UL();  // Chama a função da camada de Aplicação de UL
}

//============== COMEÇA A CRIAR O PACOTE DE UL
void App_radio_send_UL() {
  Serial.println("APP UL");
  // Neste ponto zeramos o pacote de UL para garantir que ele não está carregando nenhuma informação de comunicação anterior.
  for (int i = 0; i < TAMANHO_PACOTE; i++) {
    PacoteUL[i] = 0;
  }

  // Armazene as informações no PacoteUL[] ele é que será enviado no pacote de UL
  
  //luminosidade = analogRead(LDR_PIN); // Leitura da luminosidade no LDR_PIN que é o pino 36 do ESP32
  
  //PacoteUL[16] = 31; // Aqui vai um código do tipo de hardware PK-LoRa v31, que no caso é a PK-LoRa
  
  // O ESP32 possui conversor analógico de 12 bits (0 a 4095). 
  // A quebra do valor em dois bytes em função de ser um ADC de 12 bits
  //PacoteUL[17] = (luminosidade/256); // Valor inteiro da divisão da luminosidade por 256
  //PacoteUL[18] = (luminosidade%256); // Resto da divisão
  
  //================== CHAMA A CAMADA DE TRANSPORTE DE UL
  Transp_radio_send_UL();
}