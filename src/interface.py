import customtkinter as ctk
from tkinter import filedialog, messagebox
from motor_relatorio import montar_pdf


def gerar_relatorio():
    pasta = entrada_pasta.get()
    galpao = entrada_galpao.get()
    cliente = entrada_cliente.get()
    revisao = entrada_revisao.get()
    arquivo_saida = entrada_saida.get()

    if not pasta:
        messagebox.showerror("Erro", "Selecione a pasta das fotos.")
        return

    if not galpao:
        messagebox.showerror("Erro", "Informe o galpão.")
        return

    if not arquivo_saida:
        arquivo_saida = "relatorio_fotografico.pdf"

    try:
        montar_pdf(
            pasta_fotos=pasta,
            arquivo_saida=arquivo_saida,
            titulo_anexo="ANEXO D",
            titulo_relatorio="RELATÓRIO FOTOGRÁFICO",
            galpao=galpao,
            cliente=cliente,
            descricao_rodape="Relatório de Inspeção Visual da Cobertura Metálica",
            revisao=revisao,
        )

        messagebox.showinfo("Sucesso", "Relatório gerado com sucesso!")

    except Exception as e:
        messagebox.showerror("Erro ao gerar relatório", str(e))


def selecionar_pasta():
    pasta = filedialog.askdirectory(title="Selecionar pasta das fotos")

    if pasta:
        entrada_pasta.delete(0, "end")
        entrada_pasta.insert(0, pasta)


def selecionar_saida():
    arquivo = filedialog.asksaveasfilename(
        title="Salvar relatório como",
        defaultextension=".pdf",
        filetypes=[("PDF", "*.pdf")]
    )

    if arquivo:
        entrada_saida.delete(0, "end")
        entrada_saida.insert(0, arquivo)


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

janela = ctk.CTk()
janela.title("Gerador de Relatório Fotográfico")
janela.geometry("720x460")

titulo = ctk.CTkLabel(
    janela,
    text="Gerador de Relatório Fotográfico",
    font=("Arial", 22, "bold")
)
titulo.pack(pady=20)

frame = ctk.CTkFrame(janela)
frame.pack(padx=20, pady=10, fill="both", expand=True)

ctk.CTkLabel(frame, text="Pasta das fotos:").grid(row=0, column=0, padx=10, pady=10, sticky="w")

entrada_pasta = ctk.CTkEntry(frame, width=430)
entrada_pasta.grid(row=0, column=1, padx=10, pady=10)

botao_pasta = ctk.CTkButton(frame, text="Selecionar", command=selecionar_pasta)
botao_pasta.grid(row=0, column=2, padx=10, pady=10)

ctk.CTkLabel(frame, text="Galpão:").grid(row=1, column=0, padx=10, pady=10, sticky="w")

entrada_galpao = ctk.CTkEntry(frame, width=430)
entrada_galpao.insert(0, "GALPÃO S-5")
entrada_galpao.grid(row=1, column=1, padx=10, pady=10, columnspan=2, sticky="w")

ctk.CTkLabel(frame, text="Cliente:").grid(row=2, column=0, padx=10, pady=10, sticky="w")

entrada_cliente = ctk.CTkEntry(frame, width=430)
entrada_cliente.insert(0, "PETROBRAS – REDUC")
entrada_cliente.grid(row=2, column=1, padx=10, pady=10, columnspan=2, sticky="w")

ctk.CTkLabel(frame, text="Revisão:").grid(row=3, column=0, padx=10, pady=10, sticky="w")

entrada_revisao = ctk.CTkEntry(frame, width=430)
entrada_revisao.insert(0, "Rev.00")
entrada_revisao.grid(row=3, column=1, padx=10, pady=10, columnspan=2, sticky="w")

ctk.CTkLabel(frame, text="Arquivo de saída:").grid(row=4, column=0, padx=10, pady=10, sticky="w")

entrada_saida = ctk.CTkEntry(frame, width=430)
entrada_saida.insert(0, "relatorio_fotografico.pdf")
entrada_saida.grid(row=4, column=1, padx=10, pady=10)

botao_saida = ctk.CTkButton(frame, text="Salvar como", command=selecionar_saida)
botao_saida.grid(row=4, column=2, padx=10, pady=10)

botao_gerar = ctk.CTkButton(
    janela,
    text="GERAR RELATÓRIO",
    height=45,
    font=("Arial", 15, "bold"),
    command=gerar_relatorio
)
botao_gerar.pack(pady=20)

janela.mainloop()