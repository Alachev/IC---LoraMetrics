import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

SEPARADORES = {
    "; (Ponto e vírgula)": ";",
    ", (Vírgula)": ",",
    "Tabulação (\\t)": "\t",
    "Espaço": r"\s+"
}

ESTILOS_LINHA = {
    "Contínua (-)": "-",
    "Tracejada (--)": "--",
    "Ponto-Traço (-.)": "-.",
    "Pontilhada (:)": ":"
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

class ApplicationAnaliseJanelada:
    def __init__(self, root):
        self.root = root
        self.root.title("Análise Estatística Janelada - RSSI / SNR")
        self.root.geometry("1180x920")

        self.df = None
        self.caminho_arquivo = None
        self.fig, self.ax1 = plt.subplots(figsize=(8, 5))
        self.ax2 = None  # Eixo Y secundário para Desvio Padrão Janelado

        self.criar_interface()

    def criar_interface(self):
        # ------------------------------------------------------------------
        # Painel Superior - Configurações de Arquivo
        # ------------------------------------------------------------------
        control_frame = ttk.LabelFrame(self.root, text=" Configurações de Leitura ", padding=10)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        btn_load = ttk.Button(control_frame, text="📁 Abrir Arquivo CSV/TXT", command=self.carregar_arquivo)
        btn_load.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        ttk.Label(control_frame, text="Separador:").grid(row=0, column=1, padx=(10, 2), pady=5, sticky="e")
        self.combo_sep = ttk.Combobox(control_frame, values=list(SEPARADORES.keys()), state="readonly", width=18)
        self.combo_sep.set("; (Ponto e vírgula)")
        self.combo_sep.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.combo_sep.bind("<<ComboboxSelected>>", lambda e: self.ler_dados())

        ttk.Label(control_frame, text="Coluna do Sinal (RSSI/SNR):").grid(row=0, column=3, padx=(15, 2), pady=5, sticky="e")
        self.combo_coluna = ttk.Combobox(control_frame, state="readonly", width=22)
        self.combo_coluna.grid(row=0, column=4, padx=5, pady=5, sticky="w")

        self.lbl_file = ttk.Label(control_frame, text="Nenhum arquivo selecionado", font=("Arial", 9, "italic"))
        self.lbl_file.grid(row=1, column=0, columnspan=5, padx=5, pady=(0, 5), sticky="w")

        # ------------------------------------------------------------------
        # Painel Intermediário - Parâmetros da Janela e Estilização
        # ------------------------------------------------------------------
        style_frame = ttk.LabelFrame(self.root, text=" Parâmetros de Análise Janelada e Visualização ", padding=10)
        style_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Tamanho da Janela (Intervalo Regulável)
        ttk.Label(style_frame, text="Tamanho da Janela (Amostras):").grid(row=0, column=0, padx=2, pady=2, sticky="e")
        self.spin_window = ttk.Spinbox(style_frame, from_=2, to=1000, width=8)
        self.spin_window.set(20)
        self.spin_window.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(style_frame, text="Cor Sinal Bruto:").grid(row=0, column=2, padx=10, pady=2, sticky="e")
        self.combo_cor_sinal = ttk.Combobox(style_frame, values=list(CORES.keys()), state="readonly", width=10)
        self.combo_cor_sinal.set("Cinza")
        self.combo_cor_sinal.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(style_frame, text="Cor Média Móvel:").grid(row=0, column=4, padx=10, pady=2, sticky="e")
        self.combo_cor_media = ttk.Combobox(style_frame, values=list(CORES.keys()), state="readonly", width=10)
        self.combo_cor_media.set("Azul")
        self.combo_cor_media.grid(row=0, column=5, padx=5, pady=2)

        # Opções visuais do desvio padrão
        self.var_banda_std = tk.BooleanVar(value=True)
        self.chk_banda_std = ttk.Checkbutton(
            style_frame, text="Exibir Sombreamento (μ ± σ)", variable=self.var_banda_std
        )
        self.chk_banda_std.grid(row=1, column=0, columnspan=2, padx=5, pady=2, sticky="w")

        self.var_eixo_std = tk.BooleanVar(value=True)
        self.chk_eixo_std = ttk.Checkbutton(
            style_frame, text="Plotar σ Janelado no 2º Eixo (Direita)", variable=self.var_eixo_std
        )
        self.chk_eixo_std.grid(row=1, column=2, columnspan=2, padx=5, pady=2, sticky="w")

        # Botões de Ação
        btn_plot = ttk.Button(style_frame, text="📈 Gerar Análise", command=self.gerar_grafico)
        btn_plot.grid(row=1, column=4, padx=5, pady=5)

        btn_save = ttk.Button(style_frame, text="💾 Salvar Imagem", command=self.salvar_grafico)
        btn_save.grid(row=1, column=5, padx=5, pady=5)

       # ------------------------------------------------------------------
        # Painel de Resultados Estatísticos Globais e Janelados
        # ------------------------------------------------------------------
        self.stats_frame = ttk.LabelFrame(self.root, text=" Conjunto Estatístico ", padding=10)
        self.stats_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.lbl_stats_global = ttk.Label(
            self.stats_frame, 
            text="Carregue os dados para exibir as estatísticas globais e janeladas.", 
            font=("Arial", 10, "bold"),  # Alterado de 9.5 para 10
            foreground="#222222"
        )
        self.lbl_stats_global.pack(anchor="w", pady=2)

        self.lbl_stats_rolling = ttk.Label(
            self.stats_frame, 
            text="", 
            font=("Arial", 9), 
            foreground="#444444"
        )
        self.lbl_stats_rolling.pack(anchor="w", pady=2)

        self.lbl_stats_rolling = ttk.Label(
            self.stats_frame, 
            text="", 
            font=("Arial", 9), 
            foreground="#444444"
        )
        self.lbl_stats_rolling.pack(anchor="w", pady=2)

        # ------------------------------------------------------------------
        # Frame Inferior - Exibição do Gráfico
        # ------------------------------------------------------------------
        self.plot_frame = ttk.Frame(self.root)
        self.plot_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=5)

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
        if not self.caminho_arquivo:
            return

        separador = SEPARADORES[self.combo_sep.get()]

        try:
            self.df = pd.read_csv(self.caminho_arquivo, sep=separador)
            colunas_numericas = self.df.select_dtypes(include=[np.number]).columns.tolist()

            if not colunas_numericas:
                messagebox.showwarning("Aviso", "O arquivo não contém colunas numéricas válidas.")
                return

            self.combo_coluna['values'] = colunas_numericas

            # Busca dinâmica por colunas comuns de sinal (RSSI / SNR)
            indice_padrao = 0
            for i, col in enumerate(colunas_numericas):
                if any(k in col.upper() for k in ["RSSI", "SNR", "SINAL", "SIGNAL"]):
                    indice_padrao = i
                    break
            self.combo_coluna.current(indice_padrao)

            nome_arquivo = self.caminho_arquivo.split('/')[-1]
            self.lbl_file.config(
                text=f"Arquivo: {nome_arquivo} | Separador: '{separador}' | Total de Amostras: {len(self.df)}",
                font=("Arial", 9, "bold")
            )

            if exibir_mensagem:
                messagebox.showinfo("Sucesso", f"Arquivo '{nome_arquivo}' carregado com sucesso!")

        except Exception as e:
            messagebox.showerror("Erro de Leitura", f"Falha ao processar o arquivo:\n{e}")

    def gerar_grafico(self):
        if self.df is None:
            messagebox.showwarning("Atenção", "Carregue um arquivo TXT/CSV antes de gerar o gráfico.")
            return

        coluna_sinal = self.combo_coluna.get()
        if not coluna_sinal or coluna_sinal not in self.df.columns:
            messagebox.showwarning("Atenção", "Selecione uma coluna válida.")
            return

        # Limpeza da série temporal/sinal
        sinal = self.df[coluna_sinal].dropna().reset_index(drop=True)
        n_amostras = len(sinal)

        if n_amostras < 2:
            messagebox.showerror("Erro", "A coluna deve conter no mínimo 2 amostras numéricas.")
            return

        # Obter tamanho da janela
        try:
            janela = int(self.spin_window.get())
            if janela < 2:
                janela = 2
        except ValueError:
            janela = 20

        # Eixo X como Contador de Amostras (0 até N-1)
        contador = np.arange(n_amostras)

        # 1. Cálculos Janelados (Média Móvel e Desvio Padrão Móvel)
        rolling_mean = sinal.rolling(window=janela, min_periods=1).mean()
        rolling_std = sinal.rolling(window=janela, min_periods=1).std().fillna(0)

        # 2. Conjunto Estatístico
        mu_global = sinal.mean()
        sigma_global = sinal.std(ddof=1)
        
        lbl_g = (
            f"ESTATÍSTICA GLOBAL (Total: {n_amostras} amostras)  =>  "
            f"Média Global (μ): {mu_global:.3f}  |  "
            f"Desvio Padrão Global (σ): {sigma_global:.3f}  |  "
            f"Mín: {sinal.min():.3f}  |  "
            f"Máx: {sinal.max():.3f}"
        )
        lbl_r = (
            f"ESTATÍSTICA JANELADA (Janela W = {janela} amostras)  =>  "
            f"Média das Médias Móveis: {rolling_mean.mean():.3f}  |  "
            f"Média de σ Móvel: {rolling_std.mean():.3f}  |  "
            f"σ Móvel Máximo: {rolling_std.max():.3f}  |  "
            f"σ Móvel Mínimo: {rolling_std.min():.3f}"
        )
        self.lbl_stats_global.config(text=lbl_g)
        self.lbl_stats_rolling.config(text=lbl_r)

        # 3. Limpeza e Inicialização de Eixos
        if self.ax2 is not None:
            self.ax2.remove()
            self.ax2 = None

        self.ax1.clear()

        # Cores e Estilos
        cor_sinal = CORES[self.combo_cor_sinal.get()]
        cor_media = CORES[self.combo_cor_media.get()]

        # Plot 1: Sinal Bruto
        line_sinal = self.ax1.plot(
            contador, sinal, color=cor_sinal, alpha=0.45, linewidth=1.0, label=f"Sinal Bruto ({coluna_sinal})"
        )

        # Plot 2: Média Móvel sobreposta
        line_media = self.ax1.plot(
            contador, rolling_mean, color=cor_media, linewidth=2.0, label=f"Média Móvel (W={janela})"
        )

        lines = line_sinal + line_media

        # Plot 3: Sombreamento da Banda de Desvio Padrão (μ ± σ)
        if self.var_banda_std.get():
            self.ax1.fill_between(
                contador, 
                rolling_mean - rolling_std, 
                rolling_mean + rolling_std, 
                color=cor_media, 
                alpha=0.2, 
                label="Banda μ ± σ Janelado"
            )

        self.ax1.set_xlabel("Contador de Amostras (Index)", fontsize=10, fontweight='bold')
        self.ax1.set_ylabel(coluna_sinal, fontsize=10, fontweight='bold', color=cor_media)
        self.ax1.tick_params(axis='y', labelcolor=cor_media)
        self.ax1.grid(True, linestyle='--', alpha=0.5)

        # Plot 4: Eixo Secundário para o Desvio Padrão Janelado (se ativado)
        if self.var_eixo_std.get():
            self.ax2 = self.ax1.twinx()
            line_std = self.ax2.plot(
                contador, rolling_std, color=CORES["Vermelho"], linestyle="--", linewidth=1.5, label=f"σ Móvel (W={janela})"
            )
            self.ax2.set_ylabel("Desvio Padrão (σ)", fontsize=10, fontweight='bold', color=CORES["Vermelho"])
            self.ax2.tick_params(axis='y', labelcolor=CORES["Vermelho"])
            lines += line_std

        # Legenda Unificada
        labels = [l.get_label() for l in lines]
        self.ax1.legend(lines, labels, loc='best')

        self.ax1.set_title(f"Análise Janelada do Sinal '{coluna_sinal}' vs Contador de Amostras", fontsize=12, fontweight='bold')
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
            title="Salvar Gráfico Janelado Como"
        )
        
        if file_path:
            try:
                self.fig.savefig(file_path, dpi=300)
                messagebox.showinfo("Sucesso", f"Gráfico salvo com sucesso em:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar a imagem:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ApplicationAnaliseJanelada(root)
    root.mainloop()