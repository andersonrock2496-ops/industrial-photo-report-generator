from pathlib import Path
import re
import math
from PIL import Image, ImageOps
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


EXTENSOES = [".jpg", ".jpeg", ".png", ".webp"]


CODIGOS_STATUS = {
    "a": "APROVADO",
    "ap": "APROVADO",
    "p": "PINTURA",
    "r": "REPARO",
    "k": "REPROVADO",
}

PESOS_STATUS = {
    "APROVADO": 100,
    "PINTURA": 75,
    "REPARO": 50,
    "REPROVADO": 0,
}


DICIONARIO = {
    "esq": "Lado Esquerdo",
    "dir": "Lado Direito",
    "cent": "Região Central",
    "cen": "Região Central",
    "central": "Região Central",
    "entre": "Vão entre",
    "base_2": "Suporte da Treliça 02",
    "sup": "Superior",
    "inf": "Inferior",

    # Novos códigos de vista
    "vs": "Vista",
    "fro": "Frontal",
    "int": "Interna",
    "fun": "Fundo",

    # Identificação do galpão
    "s5": "Galpão S-5",
    "s6": "Galpão S-6",
    "s7": "Galpão S-7",
    "s8": "Galpão S-8",
}


def cor_status(status):
    cores = {
        "APROVADO": (0.15, 0.55, 0.15),
        "PINTURA": (0.10, 0.25, 0.85),
        "REPARO": (0.95, 0.55, 0.05),
        "REPROVADO": (0.80, 0.10, 0.10),
    }
    return cores.get(status, (0.25, 0.25, 0.25))


def cor_indice(indice):
    if indice >= 70:
        return (0.15, 0.55, 0.15)
    if indice >= 50:
        return (0.95, 0.55, 0.05)
    return (0.80, 0.10, 0.10)


def chave_ordenacao_natural(caminho):
    texto = caminho.stem.lower()
    return [
        int(parte) if parte.isdigit() else parte
        for parte in re.split(r"(\d+)", texto)
    ]


def limpar_nome(nome_arquivo):
    nome = Path(nome_arquivo).stem.lower()
    nome = nome.replace("-", "_").replace(" ", "_")
    nome = re.sub(r"\(\d+\)", "", nome)
    return [p for p in nome.split("_") if p]


def formatar_numero(numero):
    return str(numero).zfill(2)


def juntar_numeros(numeros):
    if not numeros:
        return ""

    numeros = [formatar_numero(n) for n in numeros]

    if len(numeros) == 1:
        return numeros[0]

    if len(numeros) == 2:
        return f"{numeros[0]} e {numeros[1]}"

    return ", ".join(numeros[:-1]) + f" e {numeros[-1]}"


def coletar_numeros(partes, indice):
    numeros = []

    while indice < len(partes) and partes[indice].isdigit():
        numeros.append(partes[indice])
        indice += 1

    return numeros, indice


def interpretar_elemento(elemento, numeros):
    texto_numeros = juntar_numeros(numeros)

    if elemento == "trelica":
        if not texto_numeros:
            return "Treliça"
        if len(numeros) == 1:
            return f"Treliça {texto_numeros}"
        return f"Treliças {texto_numeros}"

    if elemento == "terca":
        if not texto_numeros:
            return "Terça"
        if len(numeros) == 1:
            return f"Terça {texto_numeros}"
        return f"Terças {texto_numeros}"

    if elemento == "base":
        if not texto_numeros:
            return "Suporte"
        if len(numeros) == 1:
            return f"Suporte da Treliça {texto_numeros}"
        return f"Suporte no Vão entre Treliças {texto_numeros}"

    if elemento == "viga":
        if not texto_numeros:
            return "Viga"
        if len(numeros) == 1:
            return f"Viga {texto_numeros}"
        return f"Vigas {texto_numeros}"

    if elemento == "calha":
        if not texto_numeros:
            return "Calha"
        if len(numeros) == 1:
            return f"Calha {texto_numeros}"
        return f"Calhas {texto_numeros}"

    if elemento == "telhado":
        return "Telhado"

    if elemento == "suporte":
        if not texto_numeros:
            return "Suporte"
        if len(numeros) == 1:
            return f"Suporte {texto_numeros}"
        return f"Suportes {texto_numeros}"

    return elemento.capitalize()


def interpretar_nome(nome_arquivo):
    partes = limpar_nome(nome_arquivo)

    legenda = []
    status = None
    i = 0

    elementos = {
        "trelica": "trelica",
        "treliça": "trelica",
        "terca": "terca",
        "terça": "terca",
        "base": "base",
        "viga": "viga",
        "calha": "calha",
        "telhado": "telhado",
        "suporte": "suporte",
    }

    codigos_vista = {"vs", "fro", "int", "fun"}
    codigos_galpao = {"s5", "s6", "s7", "s8"}

    eh_foto_vista = any(p in codigos_vista for p in partes)

    while i < len(partes):
        parte = partes[i]

        # Status só entra quando NÃO for foto de vista/identificação
        if parte in CODIGOS_STATUS and not eh_foto_vista:
            status = CODIGOS_STATUS[parte]
            i += 1
            continue

        if parte in elementos:
            elemento = elementos[parte]
            numeros, novo_i = coletar_numeros(partes, i + 1)
            legenda.append(interpretar_elemento(elemento, numeros))
            i = novo_i
            continue

        if parte == "entre":
            i += 1

            if i < len(partes) and partes[i] in elementos:
                elemento = elementos[partes[i]]
                numeros, novo_i = coletar_numeros(partes, i + 1)

                if elemento == "trelica":
                    legenda.append(f"Vão entre Treliças {juntar_numeros(numeros)}")
                elif elemento == "terca":
                    legenda.append(f"Vão entre Terças {juntar_numeros(numeros)}")
                else:
                    legenda.append(f"Vão entre {interpretar_elemento(elemento, numeros)}")

                i = novo_i
                continue

            numeros, novo_i = coletar_numeros(partes, i)

            if numeros:
                legenda.append(f"Vão entre Treliças {juntar_numeros(numeros)}")
                i = novo_i
                continue

            legenda.append("Vão entre")
            continue

        if parte in DICIONARIO:
            legenda.append(DICIONARIO[parte])
            i += 1
            continue

        if parte.isdigit():
            legenda.append(formatar_numero(parte))
            i += 1
            continue

        legenda.append(parte.capitalize())
        i += 1

    texto = " - ".join(legenda)
    return texto, status
    partes = limpar_nome(nome_arquivo)

    legenda = []
    status = None
    i = 0

    elementos = {
        "trelica": "trelica",
        "treliça": "trelica",
        "terca": "terca",
        "terça": "terca",
        "base": "base",
        "viga": "viga",
        "calha": "calha",
        "telhado": "telhado",
        "suporte": "suporte",
    }

    while i < len(partes):
        parte = partes[i]

        if parte in CODIGOS_STATUS:
            status = CODIGOS_STATUS[parte]
            i += 1
            continue

        if parte in elementos:
            elemento = elementos[parte]
            numeros, novo_i = coletar_numeros(partes, i + 1)
            legenda.append(interpretar_elemento(elemento, numeros))
            i = novo_i
            continue

        if parte == "entre":
            i += 1

            if i < len(partes) and partes[i] in elementos:
                elemento = elementos[partes[i]]
                numeros, novo_i = coletar_numeros(partes, i + 1)

                if elemento == "trelica":
                    legenda.append(f"Vão entre Treliças {juntar_numeros(numeros)}")
                elif elemento == "terca":
                    legenda.append(f"Vão entre Terças {juntar_numeros(numeros)}")
                else:
                    legenda.append(f"Vão entre {interpretar_elemento(elemento, numeros)}")

                i = novo_i
                continue

            numeros, novo_i = coletar_numeros(partes, i)

            if numeros:
                legenda.append(f"Vão entre Treliças {juntar_numeros(numeros)}")
                i = novo_i
                continue

            legenda.append("Vão entre")
            continue

        if parte in DICIONARIO:
            legenda.append(DICIONARIO[parte])
            i += 1
            continue

        if parte.isdigit():
            legenda.append(formatar_numero(parte))
            i += 1
            continue

        legenda.append(parte.capitalize())
        i += 1

    texto = " - ".join(legenda)
    return texto, status


def quebrar_texto(pdf, texto, largura_max, fonte, tamanho):
    palavras = texto.split()
    linhas = []
    linha = ""

    for palavra in palavras:
        teste = f"{linha} {palavra}".strip()

        if pdf.stringWidth(teste, fonte, tamanho) <= largura_max:
            linha = teste
        else:
            if linha:
                linhas.append(linha)
            linha = palavra

    if linha:
        linhas.append(linha)

    return linhas


def desenhar_texto_quebrado(pdf, texto, x, y, largura_max, fonte="Helvetica-Bold", tamanho=9):
    pdf.setFont(fonte, tamanho)
    linhas = quebrar_texto(pdf, texto, largura_max, fonte, tamanho)

    for linha in linhas:
        pdf.drawString(x, y, linha)
        y -= 0.40 * cm

    return y


def redimensionar_imagem(caminho, largura_max, altura_max):
    img = Image.open(caminho)
    img = ImageOps.exif_transpose(img)

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    img.thumbnail((largura_max, altura_max))
    return ImageReader(img), img.width, img.height


def desenhar_cabecalho(pdf, largura_pagina, altura_pagina, margem, total_paginas, contexto):
    pagina = pdf.getPageNumber()

    titulo_anexo = contexto["titulo_anexo"]
    titulo_relatorio = contexto["titulo_relatorio"]
    galpao = contexto["galpao"]

    pdf.setFillColorRGB(0, 0, 0)
    pdf.setStrokeColorRGB(0, 0, 0)

    if pagina == 1:
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawCentredString(largura_pagina / 2, altura_pagina - 0.9 * cm, titulo_anexo)

        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawCentredString(largura_pagina / 2, altura_pagina - 1.55 * cm, titulo_relatorio)

        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawCentredString(largura_pagina / 2, altura_pagina - 2.15 * cm, galpao)

        linha_y = altura_pagina - 3.15 * cm

    else:
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(margem, altura_pagina - 1.2 * cm, titulo_relatorio)

        linha_y = altura_pagina - 1.55 * cm

    pdf.setFont("Helvetica", 9)
    pdf.drawRightString(
        largura_pagina - margem,
        linha_y + 0.25 * cm,
        f"Página {pagina} de {total_paginas}"
    )

    pdf.setLineWidth(0.8)
    pdf.line(margem, linha_y, largura_pagina - margem, linha_y)


def desenhar_rodape(pdf, largura_pagina, margem, contexto):
    y = 1.05 * cm

    cliente = contexto["cliente"]
    descricao_rodape = contexto["descricao_rodape"]
    galpao = contexto["galpao"]
    titulo_anexo = contexto["titulo_anexo"]
    titulo_relatorio = contexto["titulo_relatorio"]
    revisao = contexto["revisao"]

    pdf.setStrokeColorRGB(0.55, 0.55, 0.55)
    pdf.setLineWidth(0.5)
    pdf.line(margem, y + 0.55 * cm, largura_pagina - margem, y + 0.55 * cm)

    pdf.setFillColorRGB(0, 0, 0)
    pdf.setFont("Helvetica", 7.5)

    pdf.drawString(margem, y + 0.18 * cm, cliente)
    pdf.drawString(margem, y - 0.12 * cm, f"{descricao_rodape} - {galpao}")

    pdf.drawRightString(
        largura_pagina - margem,
        y + 0.18 * cm,
        f"{titulo_anexo} - {titulo_relatorio}"
    )

    pdf.drawRightString(largura_pagina - margem, y - 0.12 * cm, revisao)


def desenhar_status_caixa(pdf, status, x, y):
    if not status:
        return

    r, g, b = cor_status(status)

    largura = 4.3 * cm
    altura = 0.52 * cm

    pdf.setFillColorRGB(r, g, b)
    pdf.setStrokeColorRGB(r, g, b)
    pdf.roundRect(x, y - altura + 0.08 * cm, largura, altura, 4, stroke=0, fill=1)

    pdf.setFillColorRGB(1, 1, 1)
    pdf.setFont("Helvetica-Bold", 8.5)
    pdf.drawCentredString(x + largura / 2, y - 0.28 * cm, f"STATUS: {status}")

    pdf.setFillColorRGB(0, 0, 0)


def desenhar_foto(pdf, foto, codigo, legenda, status, x, y_topo, largura_foto, altura_foto):
    imagem, w, h = redimensionar_imagem(foto, largura_foto, altura_foto)

    x_img = x + (largura_foto - w) / 2
    y_img = y_topo - h

    pdf.drawImage(imagem, x_img, y_img, width=w, height=h)

    y_texto = y_img - 0.38 * cm

    pdf.setFillColorRGB(0, 0, 0)

    y_texto = desenhar_texto_quebrado(
        pdf,
        f"{codigo} - {legenda}",
        x,
        y_texto,
        largura_foto,
        "Helvetica-Bold",
        8.6
    )

    y_texto -= 0.08 * cm
    desenhar_status_caixa(pdf, status, x, y_texto)


def desenhar_tabela_resumo(pdf, contagem, total_avaliadas, margem, y):
    col_status = margem
    col_qtd = margem + 7.3 * cm
    col_perc = margem + 10.2 * cm

    largura_tabela = 13.5 * cm
    altura_linha = 0.72 * cm

    pdf.setFillColorRGB(0.90, 0.90, 0.90)
    pdf.rect(margem, y - 0.2 * cm, largura_tabela, altura_linha, stroke=0, fill=1)

    pdf.setFillColorRGB(0, 0, 0)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(col_status, y, "Situação")
    pdf.drawString(col_qtd, y, "Quantidade")
    pdf.drawString(col_perc, y, "Percentual")

    y -= altura_linha

    for status in ["APROVADO", "PINTURA", "REPARO", "REPROVADO"]:
        quantidade = contagem.get(status, 0)
        percentual = (quantidade / total_avaliadas * 100) if total_avaliadas else 0

        r, g, b = cor_status(status)

        pdf.setFillColorRGB(r, g, b)
        pdf.roundRect(col_status, y - 0.1 * cm, 0.35 * cm, 0.35 * cm, 2, stroke=0, fill=1)

        pdf.setFillColorRGB(0, 0, 0)
        pdf.setFont("Helvetica", 10)
        pdf.drawString(col_status + 0.55 * cm, y, status)
        pdf.drawString(col_qtd, y, str(quantidade))
        pdf.drawString(col_perc, y, f"{percentual:.1f}%")

        y -= altura_linha

    return y


def desenhar_barra_indice(pdf, x, y, largura, altura, indice):
    indice_limitado = max(0, min(indice, 100))
    largura_preenchida = largura * (indice_limitado / 100)

    r, g, b = cor_indice(indice)

    pdf.setFillColorRGB(0.90, 0.90, 0.90)
    pdf.roundRect(x, y, largura, altura, 5, stroke=0, fill=1)

    pdf.setFillColorRGB(r, g, b)
    pdf.roundRect(x, y, largura_preenchida, altura, 5, stroke=0, fill=1)

    pdf.setFillColorRGB(0, 0, 0)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawCentredString(x + largura / 2, y + 0.22 * cm, f"{indice:.1f}%")


def desenhar_barra_distribuicao(pdf, x, y, largura, status, percentual):
    r, g, b = cor_status(status)
    altura = 0.35 * cm

    pdf.setFillColorRGB(0.90, 0.90, 0.90)
    pdf.rect(x, y, largura, altura, stroke=0, fill=1)

    pdf.setFillColorRGB(r, g, b)
    pdf.rect(x, y, largura * (percentual / 100), altura, stroke=0, fill=1)

    pdf.setFillColorRGB(0, 0, 0)
    pdf.setFont("Helvetica", 9)
    pdf.drawString(x + largura + 0.35 * cm, y + 0.06 * cm, f"{status}: {percentual:.1f}%")


def desenhar_resumo(pdf, contagem, total_fotos, total_avaliadas, indice, total_paginas, contexto):
    largura_pagina, altura_pagina = A4
    margem = 2 * cm

    desenhar_cabecalho(pdf, largura_pagina, altura_pagina, margem, total_paginas, contexto)
    desenhar_rodape(pdf, largura_pagina, margem, contexto)

    area_total = contexto.get("area_total", "")

    y = altura_pagina - 3.0 * cm

    pdf.setFillColorRGB(0, 0, 0)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(largura_pagina / 2, y, "RESUMO DA INSPEÇÃO")

    y -= 1.2 * cm

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(margem, y, f"Total de fotografias no relatório: {total_fotos}")
    y -= 0.55 * cm
    pdf.drawString(margem, y, f"Total de fotografias avaliadas com status: {total_avaliadas}")

    if area_total:
        y -= 0.55 * cm
        pdf.drawString(margem, y, f"Área total inspecionada: {area_total}")

    y -= 1.0 * cm

    y = desenhar_tabela_resumo(pdf, contagem, total_avaliadas, margem, y)
    y -= 0.8 * cm

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(margem, y, "DISTRIBUIÇÃO DAS CONDIÇÕES")
    y -= 0.65 * cm

    largura_barra = 7.8 * cm

    for status in ["APROVADO", "PINTURA", "REPARO", "REPROVADO"]:
        quantidade = contagem.get(status, 0)
        percentual = (quantidade / total_avaliadas * 100) if total_avaliadas else 0
        desenhar_barra_distribuicao(pdf, margem, y, largura_barra, status, percentual)
        y -= 0.62 * cm

    y -= 0.7 * cm

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(margem, y, "ÍNDICE DE INTEGRIDADE")
    y -= 0.75 * cm

    desenhar_barra_indice(pdf, margem, y, 11.5 * cm, 0.8 * cm, indice)
    y -= 1.4 * cm

    if area_total:
        texto_area = f"na área total inspecionada de {area_total}"
    else:
        texto_area = "na área inspecionada"

    if indice >= 70:
        classificacao = "APROVADO"
        parecer = (
            f"Com base na inspeção fotográfica realizada {texto_area}, "
            f"a cobertura metálica apresenta índice de integridade de {indice:.1f}%, "
            "igual ou superior ao critério mínimo adotado. Recomenda-se aprovação da "
            "condição geral, com acompanhamento periódico e execução das correções "
            "pontuais identificadas."
        )
    else:
        classificacao = "REPROVADO"
        parecer = (
            f"Com base na inspeção fotográfica realizada {texto_area}, "
            f"a cobertura metálica apresenta índice de integridade de {indice:.1f}%, "
            "inferior ao critério mínimo adotado. Recomenda-se reprovação da condição "
            "atual, com necessidade de intervenção corretiva antes da aprovação da estrutura."
        )

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(margem, y, "PARECER TÉCNICO")
    y -= 0.65 * cm

    r, g, b = cor_indice(indice)
    pdf.setFillColorRGB(r, g, b)
    pdf.roundRect(margem, y - 0.35 * cm, 5.2 * cm, 0.62 * cm, 4, stroke=0, fill=1)

    pdf.setFillColorRGB(1, 1, 1)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawCentredString(margem + 2.6 * cm, y - 0.13 * cm, f"CLASSIFICAÇÃO: {classificacao}")

    y -= 0.95 * cm

    pdf.setFillColorRGB(0, 0, 0)
    pdf.setFont("Helvetica", 10)

    for linha in quebrar_texto(pdf, parecer, largura_pagina - 2 * margem, "Helvetica", 10):
        pdf.drawString(margem, y, linha)
        y -= 0.48 * cm

    y -= 0.6 * cm

    if total_avaliadas > 0:
        maior_status = max(contagem, key=contagem.get)
        maior_qtd = contagem[maior_status]

        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(margem, y, "OCORRÊNCIA PREDOMINANTE")
        y -= 0.55 * cm

        pdf.setFont("Helvetica", 10)
        pdf.drawString(
            margem,
            y,
            f"A condição com maior ocorrência foi: {maior_status}, com {maior_qtd} registro(s)."
        )

def montar_pdf(
    pasta_fotos,
    arquivo_saida,
    titulo_anexo="ANEXO D",
    titulo_relatorio="RELATÓRIO FOTOGRÁFICO",
    galpao="GALPÃO S-7",
    cliente="PETROBRAS – REDUC",
    descricao_rodape="Relatório de Inspeção Visual da Cobertura Metálica",
    revisao="Rev.00",
    area_total="",
):
    contexto = {
        "titulo_anexo": titulo_anexo,
        "titulo_relatorio": titulo_relatorio,
        "galpao": galpao,
        "cliente": cliente,
        "descricao_rodape": descricao_rodape,
        "revisao": revisao,
        "area_total": area_total,
    }

    pasta = Path(pasta_fotos)

    if not pasta.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {pasta_fotos}")

    fotos = sorted(
        [f for f in pasta.iterdir() if f.suffix.lower() in EXTENSOES],
        key=chave_ordenacao_natural
    )

    if not fotos:
        raise ValueError("Nenhuma foto encontrada na pasta selecionada.")

    total_paginas_fotos = math.ceil(len(fotos) / 2)
    total_paginas = total_paginas_fotos + 1

    pdf = canvas.Canvas(arquivo_saida, pagesize=A4)

    largura_pagina, altura_pagina = A4
    margem = 1.0 * cm

    largura_foto = largura_pagina - 2 * margem
    altura_foto = 10.2 * cm

    posicoes_y_primeira_pagina = [
        altura_pagina - 4.4 * cm,
        altura_pagina - 16.5 * cm
    ]

    posicoes_y_demais_paginas = [
        altura_pagina - 3.6 * cm,
        altura_pagina - 15.7 * cm
    ]

    contagem = {
        "APROVADO": 0,
        "PINTURA": 0,
        "REPARO": 0,
        "REPROVADO": 0,
    }

    soma_pesos = 0
    total_com_status = 0

    for i, foto in enumerate(fotos):
        posicao = i % 2

        if posicao == 0:
            desenhar_cabecalho(
                pdf,
                largura_pagina,
                altura_pagina,
                margem,
                total_paginas,
                contexto
            )

            desenhar_rodape(
                pdf,
                largura_pagina,
                margem,
                contexto
            )

        pagina = pdf.getPageNumber()

        if pagina == 1:
            posicoes_y = posicoes_y_primeira_pagina
        else:
            posicoes_y = posicoes_y_demais_paginas

        codigo = f"RF-{i + 1:03d}"
        legenda, status = interpretar_nome(foto.name)

        if status:
            contagem[status] += 1
            soma_pesos += PESOS_STATUS[status]
            total_com_status += 1

        try:
            desenhar_foto(
                pdf,
                foto,
                codigo,
                legenda,
                status,
                margem,
                posicoes_y[posicao],
                largura_foto,
                altura_foto
            )

        except Exception as e:
            pdf.setFont("Helvetica", 10)
            pdf.setFillColorRGB(0.8, 0, 0)
            pdf.drawString(
                margem,
                posicoes_y[posicao],
                f"Erro ao carregar {foto.name}: {e}"
            )
            pdf.setFillColorRGB(0, 0, 0)

        if posicao == 1:
            pdf.showPage()

    if len(fotos) % 2 != 0:
        pdf.showPage()

    indice = (soma_pesos / total_com_status) if total_com_status else 0

    desenhar_resumo(
        pdf,
        contagem,
        total_fotos=len(fotos),
        total_avaliadas=total_com_status,
        indice=indice,
        total_paginas=total_paginas,
        contexto=contexto
    )

    pdf.save()

    return {
        "arquivo_saida": arquivo_saida,
        "total_fotos": len(fotos),
        "total_avaliadas": total_com_status,
        "indice_integridade": indice,
    }