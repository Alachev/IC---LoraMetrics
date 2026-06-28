//================ CAMADA MAC DL ========
void Mac_radio_receive_DL() { 
  Serial.println("MAC DL");
  // No pacote MOT são os bytes 4, 5, 6, 7 do DL, que serão utilizados para alguma função de MAC
  // Um exemplo é o comando para o nó sensor dormir e o tempo que ele vai dormir
  if (PacoteDL[6] != 0) {
      timeout_ms = (unsigned long)((PacoteDL[6] * 1000));  // converte para milissegundos
      Serial.println("timeout");
      Serial.println(timeout_ms);
    } else {
      timeout_ms = 1000;  // se for zero, mantém o padrão
    }

  start_flag = true;  
  // =========== CHAMA A CAMADA DE REDE NET DL
  Net_radio_receive_DL();
}

//================ CAMADA MAC UL ========
void Mac_radio_send_UL() {
  // Pode passar na MAC o status do sleep
  Serial.println("MAC UL");
  //============ CHAMA CAMADA FÍSICA UL
  Phy_radio_send_UL();
}
