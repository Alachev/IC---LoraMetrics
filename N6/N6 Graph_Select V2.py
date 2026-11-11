import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Dicionários de mapeamento para opções visuais e de leitura
SEPARADORES = {
    "; (Ponto e vírgula)": ";",
    ", (Vírgula)": ",",
    ". (Ponto)": "."
}

ESTILOS_LINHA = {
    "Contínua (-)": "-",
    "Tracejada (--)": "--",
    "Ponto-Traço (-.)": "-.",
    "Pontilhada (:)": ":",
    "Sem Linha": "None"
}

MARCADORES = {
    "Nenhum": "",
    "Círculo (o)": "o",
    "Quadrado (s)": "s",
    "Triângulo (^)": "^",
    "Estrela (*)": "*",
    "Diamante (D)": "D",
    "X (x)": "x"
}

CORES = {
    "Azul": "#1f77b4",
    "Vermelho": "#d62728",
    "Verde": "#2ca02c",
    "Laranja": "#ff7f0e",
    "Roxo": "#9467bd",
    "Preto": "#000000",
    "Cinza": "#7f7f7f"
}

class ApplicationGraficos:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador e Gerador de Gráficos Customizados (Dual Y)")
        self.root.geometry("1100x880")

        self.df = None
        self.caminho_arquivo = None  # Armazena o caminho do arquivo carregado
        self.fig, self.ax = plt.subplots(figsize=(8, 5))
        self.ax2 = None  # Eixo Y secundário (direita)

        self.criar_interface()

    def criar_interface(self):
        # Frame Superior Geral - Controles
        control_frame = ttk.LabelFrame(self.root, text=" Painel de Configurações ", padding=10)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # ------------------------------------------------------------------
        # Linha 0: Arquivo, Separador e Eixo X
        # ------------------------------------------------------------------
        btn_load = ttk.Button(control_frame, text="📁 Abrir Arquivo", command=self.carregar_arquivo)
        btn_load.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        ttk.Label(control_frame, text="Separador:").grid(row=0, column=1, padx=(10, 2), pady=5, sticky="e")
        self.combo_sep = ttk.Combobox(control_frame, values=list(SEPARADORES.keys()), state="readonly", width=18)
        self.combo_sep.set("; (Ponto e vírgula)")
        self.combo_sep.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        # Ao alterar o separador, recarrega os dados automaticamente se um arquivo já estiver aberto
        self.combo_sep.bind("<<ComboboxSelected>>", lambda e: self.ler_dados())

        ttk.Label(control_frame, text="Eixo X:").grid(row=0, column=3, padx=(15, 2), pady=5, sticky="e")
        self.combo_x = ttk.Combobox(control_frame, state="readonly", width=18)
        self.combo_x.grid(row=0, column=4, padx=5, pady=5, sticky="w")

        # ------------------------------------------------------------------
        # Linha 1: Label com Nome do Arquivo
        # ------------------------------------------------------------------
        self.lbl_file = ttk.Label(control_frame, text="Nenhum arquivo selecionado", font=("Arial", 9, "italic"))
        self.lbl_file.grid(row=1, column=0, columnspan=5, padx=5, pady=(0, 5), sticky="w")

        # ------------------------------------------------------------------
        # Linha 2: Personalização do Eixo Y1 (Esquerda)
        # ------------------------------------------------------------------
        frame_y1 = ttk.LabelFrame(control_frame, text=" Eixo Y1 (Esquerda) ", padding=8)
        frame_y1.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        ttk.Label(frame_y1, text="Coluna:").grid(row=0, column=0, padx=2, pady=2, sticky="e")
        self.combo_y1 = ttk.Combobox(frame_y1, state="readonly", width=16)
        self.combo_y1.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(frame_y1, text="Cor:").grid(row=0, column=2, padx=2, pady=2, sticky="e")
        self.combo_cor_y1 = ttk.Combobox(frame_y1, values=list(CORES.keys()), state="readonly", width=10)
        self.combo_cor_y1.set("Azul")
        self.combo_cor_y1.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(frame_y1, text="Estilo:").grid(row=1, column=0, padx=2, pady=2, sticky="e")
        self.combo_estilo_y1 = ttk.Combobox(frame_y1, values=list(ESTILOS_LINHA.keys()), state="readonly", width=16)
        self.combo_estilo_y1.set("Contínua (-)")
        self.combo_estilo_y1.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(frame_y1, text="Marcador:").grid(row=1, column=2, padx=2, pady=2, sticky="e")
        self.combo_marcador_y1 = ttk.Combobox(frame_y1, values=list(MARCADORES.keys()), state="readonly", width=10)
        self.combo_marcador_y1.set("Nenhum")
        self.combo_marcador_y1.grid(row=1, column=3, padx=5, pady=2)

        ttk.Label(frame_y1, text="Tam. Marcador:").grid(row=2, column=0, padx=2, pady=2, sticky="e")
        self.spin_tam_marcador_y1 = ttk.Spinbox(frame_y1, from_=1, to=30, width=8)
        self.spin_tam_marcador_y1.set(6)
        self.spin_tam_marcador_y1.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        # ------------------------------------------------------------------
        # Linha 2: Personalização do Eixo Y2 (Direita)
        # ------------------------------------------------------------------
        frame_y2 = ttk.LabelFrame(control_frame, text=" Eixo Y2 (Direita / Opcional) ", padding=8)
        frame_y2.grid(row=2, column=3, columnspan=3, padx=5, pady=5, sticky="ew")

        ttk.Label(frame_y2, text="Coluna:").grid(row=0, column=0, padx=2, pady=2, sticky="e")
        self.combo_y2 = ttk.Combobox(frame_y2, state="readonly", width=16)
        self.combo_y2.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(frame_y2, text="Cor:").grid(row=0, column=2, padx=2, pady=2, sticky="e")
        self.combo_cor_y2 = ttk.Combobox(frame_y2, values=list(CORES.keys()), state="readonly", width=10)
        self.combo_cor_y2.set("Vermelho")
        self.combo_cor_y2.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(frame_y2, text="Estilo:").grid(row=1, column=0, padx=2, pady=2, sticky="e")
        self.combo_estilo_y2 = ttk.Combobox(frame_y2, values=list(ESTILOS_LINHA.keys()), state="readonly", width=16)
        self.combo_estilo_y2.set("Tracejada (--)")
        self.combo_estilo_y2.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(frame_y2, text="Marcador:").grid(row=1, column=2, padx=2, pady=2, sticky="e")
        self.combo_marcador_y2 = ttk.Combobox(frame_y2, values=list(MARCADORES.keys()), state="readonly", width=10)
        self.combo_marcador_y2.set("Nenhum")
        self.combo_marcador_y2.grid(row=1, column=3, padx=5, pady=2)

        ttk.Label(frame_y2, text="Tam. Marcador:").grid(row=2, column=0, padx=2, pady=2, sticky="e")
        self.spin_tam_marcador_y2 = ttk.Spinbox(frame_y2, from_=1, to=30, width=8)
        self.spin_tam_marcador_y2.set(6)
        self.spin_tam_marcador_y2.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        # ------------------------------------------------------------------
        # Linha 3: Opções de Eixo e Botões de Ação
        # ------------------------------------------------------------------
        self.var_segundo_eixo = tk.BooleanVar(value=True)
        self.chk_segundo_eixo = ttk.Checkbutton(
            control_frame, 
            text="Usar escala independente para Y2 (2º eixo na direita)", 
            variable=self.var_segundo_eixo
        )
        self.chk_segundo_eixo.grid(row=3, column=0, columnspan=3, padx=5, pady=10, sticky="w")

        btn_plot = ttk.Button(control_frame, text="📈 Gerar Gráfico", command=self.gerar_grafico)
        btn_plot.grid(row=3, column=4, padx=5, pady=10)

        btn_save = ttk.Button(control_frame, text="💾 Salvar Imagem", command=self.salvar_grafico)
        btn_save.grid(row=3, column=5, padx=5, pady=10)

        # ------------------------------------------------------------------
        # Frame Inferior - Exibição do Gráfico
        # ------------------------------------------------------------------
        self.plot_frame = ttk.Frame(self.root)
        self.plot_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()

    def carregar_arquivo(self):
        file_path = filedialog.askopenfilename(
            title="Selecione o arquivo de dados",
            filetypes=[("Arquivos Texto/CSV", "*.txt *.csv"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            self.caminho_arquivo = file_path
            self.ler_dados(exibir_mensagem=True)

    def ler_dados(self, exibir_mensagem=False):
        """Lê ou re-lê o arquivo com o separador atualmente selecionado."""
        if not self.caminho_arquivo:
            return

        separador_selecionado = SEPARADORES[self.combo_sep.get()]

        try:
            self.df = pd.read_csv(self.caminho_arquivo, sep=separador_selecionado)
            
            # Trata automaticamente a coluna de data/hora se existir
            if 'Time stamp' in self.df.columns:
                self.df['Time stamp'] = pd.to_datetime(
                    self.df['Time stamp'], 
                    format='%d/%m/%Y %H:%M:%S', 
                    errors='coerce'
                )

            colunas = list(self.df.columns)
            colunas_y2 = ["(Nenhum)"] + colunas

            self.combo_x['values'] = colunas
            self.combo_y1['values'] = colunas
            self.combo_y2['values'] = colunas_y2

            if len(colunas) > 0:
                self.combo_x.current(0)
            if len(colunas) > 1:
                self.combo_y1.current(1)
            else:
                self.combo_y1.current(0)

            if len(colunas) > 2:
                self.combo_y2.current(3)
            else:
                self.combo_y2.current(0)

            nome_arquivo = self.caminho_arquivo.split('/')[-1]
            self.lbl_file.config(text=f"Arquivo: {nome_arquivo} | Separador: '{separador_selecionado}'", font=("Arial", 9, "bold"))

            if exibir_mensagem:
                messagebox.showinfo("Sucesso", f"Arquivo '{nome_arquivo}' carregado com sucesso!")

        except Exception as e:
            messagebox.showerror("Erro de Leitura", f"Falha ao processar o arquivo com o separador '{separador_selecionado}':\n{e}")

    def gerar_grafico(self):
        if self.df is None:
            messagebox.showwarning("Atenção", "Carregue um arquivo TXT/CSV antes de gerar o gráfico.")
            return

        eixo_x = self.combo_x.get()
        eixo_y1 = self.combo_y1.get()
        eixo_y2 = self.combo_y2.get()

        if not eixo_x or not eixo_y1:
            messagebox.showwarning("Atenção", "Selecione as colunas para o Eixo X e o Eixo Y1.")
            return

        # Limpa o eixo secundário anterior se ele existir
        if self.ax2 is not None:
            self.ax2.remove()
            self.ax2 = None

        # Limpa o gráfico principal
        self.ax.clear()

        # ------------------------------------------------------------------
        # Obter estilizações do Eixo Y1
        # ------------------------------------------------------------------
        cor_y1 = CORES[self.combo_cor_y1.get()]
        estilo_y1 = ESTILOS_LINHA[self.combo_estilo_y1.get()]
        marcador_y1 = MARCADORES[self.combo_marcador_y1.get()]
        
        try:
            tam_marcador_y1 = float(self.spin_tam_marcador_y1.get())
        except ValueError:
            tam_marcador_y1 = 6.0

        line1 = self.ax.plot(
            self.df[eixo_x], 
            self.df[eixo_y1], 
            color=cor_y1, 
            linestyle=estilo_y1,
            marker=marcador_y1,
            markersize=tam_marcador_y1,
            linewidth=1.5, 
            label=eixo_y1
        )
        
        self.ax.set_xlabel(eixo_x, fontsize=10, fontweight='bold')
        self.ax.set_ylabel(eixo_y1, fontsize=10, fontweight='bold', color=cor_y1)
        self.ax.tick_params(axis='y', labelcolor=cor_y1)
        self.ax.grid(True, linestyle='--', alpha=0.6)

        lines = line1

        # ------------------------------------------------------------------
        # Obter estilizações e plotar o Eixo Y2 (se selecionado)
        # ------------------------------------------------------------------
        if eixo_y2 and eixo_y2 != "(Nenhum)":
            cor_y2 = CORES[self.combo_cor_y2.get()]
            estilo_y2 = ESTILOS_LINHA[self.combo_estilo_y2.get()]
            marcador_y2 = MARCADORES[self.combo_marcador_y2.get()]

            try:
                tam_marcador_y2 = float(self.spin_tam_marcador_y2.get())
            except ValueError:
                tam_marcador_y2 = 6.0

            if self.var_segundo_eixo.get():
                # 2º Eixo Y na direita (Escala independente)
                self.ax2 = self.ax.twinx()
                line2 = self.ax2.plot(
                    self.df[eixo_x], 
                    self.df[eixo_y2], 
                    color=cor_y2, 
                    linestyle=estilo_y2,
                    marker=marcador_y2,
                    markersize=tam_marcador_y2,
                    linewidth=1.5, 
                    label=eixo_y2
                )
                self.ax2.set_ylabel(eixo_y2, fontsize=10, fontweight='bold', color=cor_y2)
                self.ax2.tick_params(axis='y', labelcolor=cor_y2)
                lines += line2
            else:
                # Plota no mesmo eixo Y da esquerda
                line2 = self.ax.plot(
                    self.df[eixo_x], 
                    self.df[eixo_y2], 
                    color=cor_y2, 
                    linestyle=estilo_y2,
                    marker=marcador_y2,
                    markersize=tam_marcador_y2,
                    linewidth=1.5, 
                    label=eixo_y2
                )
                lines += line2

            self.ax.set_title(f"Gráfico de {eixo_y1} e {eixo_y2} vs {eixo_x}", fontsize=12, fontweight='bold')
        else:
            self.ax.set_title(f"Gráfico de {eixo_y1} vs {eixo_x}", fontsize=12, fontweight='bold')

        # ------------------------------------------------------------------
        # Legenda Unificada
        # ------------------------------------------------------------------
        labels = [l.get_label() for l in lines]
        self.ax.legend(lines, labels, loc='best')

        # Ajusta formatação caso o eixo X seja datetime
        if pd.api.types.is_datetime64_any_dtype(self.df[eixo_x]):
            self.fig.autofmt_xdate()

        self.fig.tight_layout()
        self.canvas.draw()

    def salvar_grafico(self):
        if self.df is None:
            messagebox.showwarning("Atenção", "Gere um gráfico antes de tentar salvar.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("Imagem PNG", "*.png"),
                ("Imagem JPEG", "*.jpg"),
                ("Documento PDF", "*.pdf"),
                ("Vetor SVG", "*.svg")
            ],
            title="Salvar Gráfico Como"
        )
        
        if file_path:
            try:
                self.fig.savefig(file_path, dpi=300)
                messagebox.showinfo("Sucesso", f"Gráfico salvo com sucesso em:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar a imagem:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ApplicationGraficos(root)
    root.mainloop()