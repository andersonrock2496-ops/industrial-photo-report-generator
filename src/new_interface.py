import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path

from motor_relatorio import montar_pdf
from motor_anexo_c import gerar_anexo_c_pdf


def gerar_relatorio():
    pasta = entrada_pasta.get()
    galpao = entrada_galpao.get()
    cliente = entrada_cliente.get()
    revisao = entrada_revisao.get()
    area_total = entrada_area.get()
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
            area_total=area_total,
        )

        caminho_pdf = Path(arquivo_saida)
        caminho_anexo_c = caminho_pdf.with_name(
            caminho_pdf.stem + "_ANEXO_C_MAPA_CRITICIDADE.xlsx"
        )

        gerar_anexo_c_pdf(
            pdf_entrada=str(caminho_pdf),
            xlsx_saida=str(caminho_anexo_c)
        )

        messagebox.showinfo(
            "Sucesso",
            f"Relatório e Anexo C gerados com sucesso!\n\n"
            f"Relatório:\n{arquivo_saida}\n\n"
            f"Anexo C:\n{caminho_anexo_c}"
        )

    except Exception as e:
        messagebox.showerror("Erro ao gerar arquivos", str(e))


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
janela.title("Gerador de Relatório Fotográfico e Anexo C")
janela.geometry("760x560")

titulo = ctk.CTkLabel(
    janela,
    text="Gerador de Relatório Fotográfico + Anexo C",
    font=("Arial", 22, "bold")
)
titulo.pack(pady=20)

frame = ctk.CTkFrame(janela)
frame.pack(padx=20, pady=10, fill="both", expand=True)

ctk.CTkLabel(frame, text="Pasta das fotos:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
entrada_pasta = ctk.CTkEntry(frame, width=430)
entrada_pasta.grid(row=0, column=1, padx=10, pady=10)
ctk.CTkButton(frame, text="Selecionar", command=selecionar_pasta).grid(row=0, column=2, padx=10, pady=10)

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

ctk.CTkLabel(frame, text="Área total:").grid(row=4, column=0, padx=10, pady=10, sticky="w")
entrada_area = ctk.CTkEntry(frame, width=430)
entrada_area.insert(0, "1.250 m²")
entrada_area.grid(row=4, column=1, padx=10, pady=10, columnspan=2, sticky="w")

ctk.CTkLabel(frame, text="Arquivo PDF de saída:").grid(row=5, column=0, padx=10, pady=10, sticky="w")
entrada_saida = ctk.CTkEntry(frame, width=430)
entrada_saida.insert(0, "relatorio_fotografico.pdf")
entrada_saida.grid(row=5, column=1, padx=10, pady=10)
ctk.CTkButton(frame, text="Salvar como", command=selecionar_saida).grid(row=5, column=2, padx=10, pady=10)

botao_gerar = ctk.CTkButton(
    janela,
    text="GERAR RELATÓRIO + ANEXO C",
    height=45,
    font=("Arial", 15, "bold"),
    command=gerar_relatorio
)
botao_gerar.pack(pady=20)

janela.mainloop()