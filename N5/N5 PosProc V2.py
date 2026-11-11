import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib.pyplot as plt

# ==============================================================================
# Funções de Cálculo do Protocolo N3
# ==============================================================================

def calcular_rssi(val_byte):
    """Calcula o RSSI a partir do byte bruto (Lógica original N3)."""
    if val_byte > 127:
        return ((val_byte - 256) / 2.0) - 74.0
    else:
        return (val_byte / 2.0) - 74.0

def calcular_snr(val_byte):
    """Calcula o SNR a partir do byte bruto (Lógica original N3)."""
    return round((val_byte / 4.0) - 30.0, 2)

# ==============================================================================
# Núcleo do Processamento de Logs
# ==============================================================================

def processar_log(caminho_entrada, caminho_saida):
    """
    Lê o log no formato: 'DD/MM/AAAA HH:MM:SS ; [b0, b1, ..., b13]'
    Processa os pacotes, grava o arquivo de saída e retorna as séries temporais.
    """
    medida_atual = 0
    contador_UL_recebidos = 0
    contador_DL_enviados = 0
    perdas_DL = 0
    perdas_UL = 0

    linhas_processadas = 0

    # Dicionário para armazenar os dados numéricos e alimentar o gráfico
    dados = {
        "Medida": [],
        "RSSI_DL": [],
        "RSSI_UL": [],
        "SNR_DL": [],
        "SNR_UL": [],
        "PSR_DL(%)": [],
        "PSR_UL(%)": []
    }

    with open(caminho_entrada, 'r', encoding='utf-8') as f_in, \
         open(caminho_saida, 'w', encoding='utf-8') as f_out:

        # Escreve o cabeçalho no arquivo de saída
        f_out.write('Time stamp;Medida;RSSI_DL;RSSI_UL;SNR_DL;SNR_UL;PSR_DL(%);PSR_UL(%)\n')

        for linha in f_in:
            linha = linha.strip()
            if not linha:
                continue

            medida_atual += 1
            contador_DL_enviados += 1

            # Regex para extrair timestamp e o vetor de bytes
            match = re.search(r'^(.*?)\s*;\s*\[(.*?)\]', linha)

            is_valid_packet = False
            pacote_UL = []

            if match:
                raw_bytes = match.group(2).strip()
                try:
                    if raw_bytes:
                        pacote_UL = [int(x.strip()) for x in raw_bytes.split(',')]
                        if len(pacote_UL) == 14:
                            is_valid_packet = True
                except ValueError:
                    is_valid_packet = False

            if is_valid_packet:
                contador_UL_recebidos += 1
                
                # Uplink
                val_rssi_ul = pacote_UL[3]
                val_snr_ul = pacote_UL[4]
                rssi_UL = calcular_rssi(val_rssi_ul)
                snr_UL = calcular_snr(val_snr_ul)

                # Downlink
                perda_dl_flag = pacote_UL[11]
                if perda_dl_flag == 1:
                    perdas_DL += 1
                    rssi_DL = -130.0
                    snr_DL = -30.0
                else:
                    val_rssi_dl = pacote_UL[0]
                    val_snr_dl = pacote_UL[1]
                    rssi_DL = calcular_rssi(val_rssi_dl)
                    snr_DL = calcular_snr(val_snr_dl)

            else:
                # Caso de FALHA no Uplink
                perdas_UL += 1
                rssi_UL = -130.0
                snr_UL = -30.0
                rssi_DL = -130.0
                snr_DL = -30.0

            # Cálculo do PSR
            psr_DL = ((contador_DL_enviados - perdas_DL) / contador_DL_enviados) * 100.0 if contador_DL_enviados > 0 else 0.0
            psr_UL = (contador_UL_recebidos / medida_atual) * 100.0 if medida_atual > 0 else 0.0

            psr_DL = round(psr_DL, 2)
            psr_UL = round(psr_UL, 2)

            # Registra no dicionário para a plotagem
            dados["Medida"].append(medida_atual)
            dados["RSSI_DL"].append(rssi_DL)
            dados["RSSI_UL"].append(rssi_UL)
            dados["SNR_DL"].append(snr_DL)
            dados["SNR_UL"].append(snr_UL)
            dados["PSR_DL(%)"].append(psr_DL)
            dados["PSR_UL(%)"].append(psr_UL)

            # Grava no arquivo final
            timestamp = match.group(1).strip() if match else "N/A"
            f_out.write(f"{timestamp};{medida_atual};{rssi_DL};{rssi_UL};{snr_DL};{snr_UL};{psr_DL};{psr_UL}\n")
            linhas_processadas += 1

    return linhas_processadas, dados

# ==============================================================================
# Interface Gráfica Tkinter
# ==============================================================================

class AppLogProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Processador de Logs LoRa N3 - Site Survey")
        self.root.geometry("620x450")
        self.root.resizable(False, False)

        self.dados_processados = None

        # Estilo de UI
        style = ttk.Style()
        style.theme_use('clam')

        # Frame Principal
        main_frame = ttk.Frame(root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Seleção de Arquivo de Entrada
        ttk.Label(main_frame, text="Arquivo de Log de Entrada:").grid(row=0, column=0, sticky=tk.W, pady=(0, 2))
        self.entry_input = ttk.Entry(main_frame, width=50)
        self.entry_input.grid(row=1, column=0, padx=(0, 5), pady=(0, 10))
        ttk.Button(main_frame, text="Buscar...", command=self.selecionar_entrada).grid(row=1, column=1)

        # Seleção de Local de Saída
        ttk.Label(main_frame, text="Local para Salvar o Resultado:").grid(row=2, column=0, sticky=tk.W, pady=(0, 2))
        self.entry_output = ttk.Entry(main_frame, width=50)
        self.entry_output.grid(row=3, column=0, padx=(0, 5), pady=(0, 10))
        ttk.Button(main_frame, text="Salvar Como...", command=self.selecionar_saida).grid(row=3, column=1)

        # Botão de Processamento
        self.btn_process = ttk.Button(main_frame, text="Processar Arquivo", command=self.executar_processamento)
        self.btn_process.grid(row=4, column=0, columnspan=2, pady=10)

        # Separador Visual
        ttk.Separator(main_frame, orient='horizontal').grid(row=5, column=0, columnspan=2, sticky='ew', pady=10)

        # Configurações de Plotagem
        opcoes_grandezas = ["RSSI_DL", "RSSI_UL", "SNR_DL", "SNR_UL", "PSR_DL(%)", "PSR_UL(%)"]

        # Eixo Y1 (Esquerda)
        ttk.Label(main_frame, text="Eixo Y1 (Esquerda):").grid(row=6, column=0, sticky=tk.W)
        self.cb_eixo_y1 = ttk.Combobox(main_frame, values=opcoes_grandezas, state="readonly", width=25)
        self.cb_eixo_y1.set("RSSI_UL")
        self.cb_eixo_y1.grid(row=7, column=0, sticky=tk.W, pady=(0, 10))

        # Eixo Y2 (Direita)
        ttk.Label(main_frame, text="Eixo Y2 (Direita):").grid(row=6, column=1, sticky=tk.W)
        self.cb_eixo_y2 = ttk.Combobox(main_frame, values=opcoes_grandezas, state="readonly", width=25)
        self.cb_eixo_y2.set("SNR_UL")
        self.cb_eixo_y2.grid(row=7, column=1, sticky=tk.W, pady=(0, 10))

        # Botão de Gerar Gráfico
        self.btn_plot = ttk.Button(main_frame, text="Gerar Gráfico", command=self.gerar_grafico, state=tk.DISABLED)
        self.btn_plot.grid(row=8, column=0, columnspan=2, pady=10)

        # Label de Status
        self.lbl_status = ttk.Label(main_frame, text="Aguardando seleção de arquivos...", font=("Helvetica", 9, "italic"))
        self.lbl_status.grid(row=9, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))

    def selecionar_entrada(self):
        caminho = filedialog.askopenfilename(
            title="Selecione o arquivo de log do pacote",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Arquivos de Log", "*.log"), ("Todos os Arquivos", "*.*")]
        )
        if caminho:
            self.entry_input.delete(0, tk.END)
            self.entry_input.insert(0, caminho)
            
            if not self.entry_output.get():
                diretorio, nome_arq = os.path.split(caminho)
                nome_base, _ = os.path.splitext(nome_arq)
                sugestao = os.path.join(diretorio, f"{nome_base}_PROCESSADO.txt")
                self.entry_output.insert(0, sugestao)

    def selecionar_saida(self):
        caminho = filedialog.asksaveasfilename(
            title="Selecione onde salvar o arquivo processado",
            defaultextension=".txt",
            filetypes=[("Arquivo de Texto", "*.txt"), ("Arquivo CSV", "*.csv"), ("Todos os Arquivos", "*.*")]
        )
        if caminho:
            self.entry_output.delete(0, tk.END)
            self.entry_output.insert(0, caminho)

    def executar_processamento(self):
        ent = self.entry_input.get().strip()
        sai = self.entry_output.get().strip()

        if not ent or not os.path.exists(ent):
            messagebox.showerror("Erro", "Por favor, selecione um arquivo de log de entrada válido.")
            return

        if not sai:
            messagebox.showerror("Erro", "Por favor, especifique o caminho do arquivo de saída.")
            return

        try:
            total, self.dados_processados = processar_log(ent, sai)
            self.lbl_status.config(text=f"Concluído! {total} medidas processadas com sucesso.", foreground="green")
            self.btn_plot.config(state=tk.NORMAL)
            messagebox.showinfo("Sucesso", f"Log processado com sucesso!\nTotal de registros: {total}\nSalvo em: {sai}")
        except Exception as e:
            self.lbl_status.config(text="Erro ao processar o arquivo.", foreground="red")
            messagebox.showerror("Erro no Processamento", f"Ocorreu um erro ao ler o arquivo:\n{str(e)}")

    def gerar_grafico(self):
        if not self.dados_processados or not self.dados_processados["Medida"]:
            messagebox.showwarning("Aviso", "Processe um arquivo de log válido primeiro!")
            return

        var_y1 = self.cb_eixo_y1.get()
        var_y2 = self.cb_eixo_y2.get()

        x = self.dados_processados["Medida"]
        y1 = self.dados_processados[var_y1]
        y2 = self.dados_processados[var_y2]

        # Criando a figura e os eixos
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Eixo Y1 (Esquerda)
        cor_y1 = 'tab:blue'
        ax1.set_xlabel('Medida (Amostras)', fontsize=10, fontweight='bold')
        ax1.set_ylabel(var_y1, color=cor_y1, fontsize=10, fontweight='bold')
        line1 = ax1.plot(x, y1, color=cor_y1, linewidth=1.5, marker='o', markersize=3, label=var_y1)
        ax1.tick_params(axis='y', labelcolor=cor_y1)
        ax1.grid(True, linestyle='--', alpha=0.5)

        # Eixo Y2 (Direita - Escala independente)
        ax2 = ax1.twinx()
        cor_y2 = 'tab:red'
        ax2.set_ylabel(var_y2, color=cor_y2, fontsize=10, fontweight='bold')
        line2 = ax2.plot(x, y2, color=cor_y2, linewidth=1.5, linestyle='--', marker='s', markersize=3, label=var_y2)
        ax2.tick_params(axis='y', labelcolor=cor_y2)

        # Agrupamento das legendas dos dois eixos em um único quadro
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper left', framealpha=0.9)

        plt.title(f'Análise de Sinal LoRa N3: {var_y1} vs {var_y2}', fontsize=12, fontweight='bold', pad=12)
        fig.tight_layout()
        plt.show()

# ==============================================================================
# Execução da Aplicação
# ==============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = AppLogProcessor(root)
    root.mainloop()