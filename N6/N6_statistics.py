import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Dicionários de mapeamento para opções visuais e de leitura
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

class ApplicationHistogramaNormal:
    def __init__(self, root):
        self.root = root
        self.root.title("Análise Estatística - Histograma (Sturges) e Curva Normal")
        self.root.geometry("1150x900")

        self.df = None
        self.caminho_arquivo = None
        self.fig, self.ax = plt.subplots(figsize=(8, 5))

        self.criar_interface()

    def criar_interface(self):
        # ------------------------------------------------------------------
        # Painel Superior Geral - Controles de Entrada
        # ------------------------------------------------------------------
        control_frame = ttk.LabelFrame(self.root, text=" Configurações e Arquivo ", padding=10)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Linha 0: Leitura de Arquivo
        btn_load = ttk.Button(control_frame, text="📁 Abrir Arquivo CSV/TXT", command=self.carregar_arquivo)
        btn_load.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        ttk.Label(control_frame, text="Separador:").grid(row=0, column=1, padx=(10, 2), pady=5, sticky="e")
        self.combo_sep = ttk.Combobox(control_frame, values=list(SEPARADORES.keys()), state="readonly", width=18)
        self.combo_sep.set("; (Ponto e vírgula)")
        self.combo_sep.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.combo_sep.bind("<<ComboboxSelected>>", lambda e: self.ler_dados())

        ttk.Label(control_frame, text="Coluna das Amostras:").grid(row=0, column=3, padx=(15, 2), pady=5, sticky="e")
        self.combo_coluna = ttk.Combobox(control_frame, state="readonly", width=22)
        self.combo_coluna.grid(row=0, column=4, padx=5, pady=5, sticky="w")

        # Linha 1: Indicador de arquivo
        self.lbl_file = ttk.Label(control_frame, text="Nenhum arquivo selecionado", font=("Arial", 9, "italic"))
        self.lbl_file.grid(row=1, column=0, columnspan=5, padx=5, pady=(0, 5), sticky="w")

        # ------------------------------------------------------------------
        # Painel Intermediário - Estilização do Histograma e Curva Normal
        # ------------------------------------------------------------------
        style_frame = ttk.LabelFrame(self.root, text=" Parâmetros Visuais e Agrupamento ", padding=10)
        style_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Controle de Bins com Regra de Sturges
        self.var_sturges = tk.BooleanVar(value=True)
        self.chk_sturges = ttk.Checkbutton(
            style_frame, 
            text="Regra de Sturges (Auto)", 
            variable=self.var_sturges,
            command=self.atualizar_estado_bins
        )
        self.chk_sturges.grid(row=0, column=0, padx=5, pady=2, sticky="w")

        ttk.Label(style_frame, text="Nº Bins:").grid(row=0, column=1, padx=2, pady=2, sticky="e")
        self.spin_bins = ttk.Spinbox(style_frame, from_=3, to=300, width=6, state="disabled")
        self.spin_bins.grid(row=0, column=2, padx=5, pady=2, sticky="w")

        ttk.Label(style_frame, text="Cor Histograma:").grid(row=0, column=3, padx=10, pady=2, sticky="e")
        self.combo_cor_hist = ttk.Combobox(style_frame, values=list(CORES.keys()), state="readonly", width=10)
        self.combo_cor_hist.set("Azul")
        self.combo_cor_hist.grid(row=0, column=4, padx=5, pady=2)

        # Curva Normal
        ttk.Label(style_frame, text="Cor Curva Normal:").grid(row=0, column=5, padx=10, pady=2, sticky="e")
        self.combo_cor_curva = ttk.Combobox(style_frame, values=list(CORES.keys()), state="readonly", width=10)
        self.combo_cor_curva.set("Vermelho")
        self.combo_cor_curva.grid(row=0, column=6, padx=5, pady=2)

        ttk.Label(style_frame, text="Estilo Curva:").grid(row=1, column=0, padx=2, pady=2, sticky="e")
        self.combo_estilo_curva = ttk.Combobox(style_frame, values=list(ESTILOS_LINHA.keys()), state="readonly", width=14)
        self.combo_estilo_curva.set("Contínua (-)")
        self.combo_estilo_curva.grid(row=1, column=1, padx=5, pady=2)

        # Opções adicionais
        self.var_mostrar_media = tk.BooleanVar(value=True)
        self.chk_mostrar_media = ttk.Checkbutton(
            style_frame, text="Exibir linha vertical da Média (μ)", variable=self.var_mostrar_media
        )
        self.chk_mostrar_media.grid(row=1, column=2, columnspan=3, padx=10, pady=2, sticky="w")

        # Botões de Ação
        btn_plot = ttk.Button(style_frame, text="📊 Gerar Histograma", command=self.gerar_grafico)
        btn_plot.grid(row=1, column=5, padx=5, pady=5)

        btn_save = ttk.Button(style_frame, text="💾 Salvar Imagem", command=self.salvar_grafico)
        btn_save.grid(row=1, column=6, padx=5, pady=5)

        # ------------------------------------------------------------------
        # Painel de Resultados Estatísticos
        # ------------------------------------------------------------------
        self.stats_frame = ttk.LabelFrame(self.root, text=" Estatísticas Calculadas ", padding=10)
        self.stats_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.lbl_stats = ttk.Label(
            self.stats_frame, 
            text="Carregue um arquivo e selecione uma coluna para visualizar a Média, Desvio Padrão e o valor de Bins.", 
            font=("Arial", 10, "bold"), 
            foreground="#333333"
        )
        self.lbl_stats.pack(anchor="w")

        # ------------------------------------------------------------------
        # Frame Inferior - Exibição do Gráfico
        # ------------------------------------------------------------------
        self.plot_frame = ttk.Frame(self.root)
        self.plot_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()

    def atualizar_estado_bins(self):
        """Habilita ou desabilita o campo de Spinbox de acordo com o Checkbutton de Sturges."""
        if self.var_sturges.get():
            self.spin_bins.config(state="disabled")
        else:
            self.spin_bins.config(state="normal")

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
            self.combo_coluna.current(0)

            nome_arquivo = self.caminho_arquivo.split('/')[-1]
            self.lbl_file.config(
                text=f"Arquivo: {nome_arquivo} | Separador: '{separador}' | Colunas numéricas: {len(colunas_numericas)}",
                font=("Arial", 9, "bold")
            )

            if exibir_mensagem:
                messagebox.showinfo("Sucesso", f"Arquivo '{nome_arquivo}' carregado com sucesso!")

        except Exception as e:
            messagebox.showerror("Erro de Leitura", f"Falha ao processar o arquivo:\n{e}")

    def calcular_estatisticas(self, serie):
        """Calcula parâmetros estatísticos básicos da série numérica."""
        media = serie.mean()
        desvio_padrao = serie.std(ddof=1)
        n = serie.count()
        mediana = serie.median()
        v_min = serie.min()
        v_max = serie.max()
        
        return {
            "media": media,
            "std": desvio_padrao,
            "n": n,
            "mediana": mediana,
            "min": v_min,
            "max": v_max
        }

    def gerar_grafico(self):
        if self.df is None:
            messagebox.showwarning("Atenção", "Carregue um arquivo TXT/CSV antes de gerar o gráfico.")
            return

        coluna_amostras = self.combo_coluna.get()
        if not coluna_amostras or coluna_amostras not in self.df.columns:
            messagebox.showwarning("Atenção", "Selecione uma coluna numérica válida.")
            return

        dados = self.df[coluna_amostras].dropna()
        n_amostras = len(dados)

        if n_amostras < 2:
            messagebox.showerror("Erro", "A coluna selecionada precisa ter pelo menos 2 valores numéricos válidos.")
            return

        # 1. Definição do número de bins (Regra de Sturges vs Manual)
        if self.var_sturges.get():
            # Regra de Sturges: k = ceil(1 + log2(N))
            num_bins = int(np.ceil(1 + np.log2(n_amostras)))
            
            # Atualiza o Spinbox visualmente com o valor calculado por Sturges
            self.spin_bins.config(state="normal")
            self.spin_bins.delete(0, tk.END)
            self.spin_bins.insert(0, str(num_bins))
            self.spin_bins.config(state="disabled")
        else:
            try:
                num_bins = int(self.spin_bins.get())
            except ValueError:
                num_bins = 30

        # 2. Cálculo dos parâmetros estatísticos
        stats = self.calcular_estatisticas(dados)
        mu = stats["media"]
        sigma = stats["std"]

        # Atualização do painel estatístico
        metodo_bins = "Sturges (Auto)" if self.var_sturges.get() else "Manual"
        texto_stats = (
            f"N: {stats['n']}   |   "
            f"Bins: {num_bins} [{metodo_bins}]   |   "
            f"Média (μ): {mu:.4f}   |   "
            f"Desvio Padrão (σ): {sigma:.4f}   |   "
            f"Mediana: {stats['mediana']:.4f}"
        )
        self.lbl_stats.config(text=texto_stats)

        # 3. Estilização visual
        cor_hist = CORES[self.combo_cor_hist.get()]
        cor_curva = CORES[self.combo_cor_curva.get()]
        estilo_curva = ESTILOS_LINHA[self.combo_estilo_curva.get()]

        # 4. Plotagem
        self.ax.clear()

        # Plot do Histograma Normalizado (Densidade)
        self.ax.hist(
            dados, 
            bins=num_bins, 
            density=True, 
            alpha=0.6, 
            color=cor_hist, 
            edgecolor='black', 
            label=f"Histograma ({num_bins} Bins)"
        )

        # Curva Normal Teórica
        x_teorico = np.linspace(stats["min"] - 0.5 * sigma, stats["max"] + 0.5 * sigma, 500)
        y_teorico = (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_teorico - mu) / sigma) ** 2)

        self.ax.plot(
            x_teorico, 
            y_teorico, 
            color=cor_curva, 
            linestyle=estilo_curva, 
            linewidth=2.5, 
            label=f"Curva Normal Teórica\n(μ={mu:.2f}, σ={sigma:.2f})"
        )

        if self.var_mostrar_media.get():
            self.ax.axvline(mu, color="black", linestyle="--", linewidth=1.5, label=f"Média (μ = {mu:.2f})")

        # Formatação do eixo e títulos
        self.ax.set_title(f"Histograma (Sturges) e Curva Normal - '{coluna_amostras}'", fontsize=12, fontweight='bold')
        self.ax.set_xlabel(coluna_amostras, fontsize=10, fontweight='bold')
        self.ax.set_ylabel("Densidade de Probabilidade", fontsize=10, fontweight='bold')
        self.ax.grid(True, linestyle='--', alpha=0.5)
        self.ax.legend(loc='best')

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
            title="Salvar Histograma Como"
        )
        
        if file_path:
            try:
                self.fig.savefig(file_path, dpi=300)
                messagebox.showinfo("Sucesso", f"Gráfico salvo com sucesso em:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar a imagem:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ApplicationHistogramaNormal(root)
    root.mainloop()