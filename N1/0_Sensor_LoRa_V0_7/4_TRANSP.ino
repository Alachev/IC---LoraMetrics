//================ CAMADA DE TRANSPORT DL ========
void Transp_radio_receive_DL() { 
  Serial.println("Transp DL");
  // Faz o controle fluzo entre o nó sensor e o gateway
  // Por exemplo contagem de pacotes recedidos de DL
  contador_pkt_DL = contador_pkt_DL + 1;
  if(PacoteDL[9]==1)
  {
    stop_flag = true;
  }

  //============== CHAMA A CAMADA DE APLICAÇÃO DE DL
  App_radio_receive_DL();
}

//================ CAMADA DE TRANSPORTE DE UL ========
void Transp_radio_send_UL() { 
  Serial.println("Transp UL");
  // Aloca no pacote de UL o valor contador de pacotes de DL
  PacoteUL[9] = (contador_pkt_DL/256);
  PacoteUL[10] = (contador_pkt_DL%256);
  PacoteUL[11] = timeout_flag;
  contador_pkt_UL = contador_pkt_UL + 1;
  PacoteUL[12] = (contador_pkt_UL/256);
  PacoteUL[13] = (contador_pkt_UL%256);
  Serial.println("contador de UL");
  Serial.println(contador_pkt_UL);
  Serial.println("contador de DL");
  Serial.println(contador_pkt_DL);

//============ CHAMA A CAMADA DE REDE DE UL
  Net_radio_send_UL();
}
