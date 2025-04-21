import spacy
import re
import gc
from spacy.tokens import Doc, Span
from spacy.language import Language

nlp = spacy.load("es_dep_news_trf")

@Language.component("post_parser_es_legal")
def post_parser_es_legal(doc: Doc) -> Doc:
    pattern = re.compile(
        r"^(Artículo\s+\d+[°º]?[\.-]?|T[Íi]tulo\s+[IVXLCDM]+|Cap[Íi]tulo\s+[IVXLCDM]+)",
        re.IGNORECASE
    )

    sent_starts = [0]
    for i in range(len(doc) - 3):  # Ajustamos el loop para iterar de forma directa
        # Tomamos una ventana de 4 tokens como máximo
        window = " ".join([t.text for t in doc[i:i+4]])
        if pattern.match(window):
            sent_starts.append(i)

    # Eliminar duplicados y ordenar
    sent_starts = sorted(set(sent_starts))

    # Construir los spans de oraciones
    spans = [Span(doc, start, sent_starts[idx + 1] if idx + 1 < len(sent_starts) else len(doc))
             for idx, start in enumerate(sent_starts)]

    doc.spans["sentences"] = spans
    doc._.custom_sents = spans
    return doc


Doc.set_extension("custom_sents", default=None)
nlp.add_pipe("post_parser_es_legal", after="parser")


def fragment_text(text: str, max_chunk_size: int = 4098) -> list[str]:
    fragments = []
    # procesar el texto en chunks variables
    while text:
        chunk_size = __get_chunk_size(text, max_chunk_size)
        # descartar chunks pequeños
        chunk = text[:chunk_size]
        text = text[chunk_size:]
        # Procesar el chunk y fragmentarlo
        __process_chunk(chunk, fragments)
    return fragments


def __process_chunk(chunk: str, fragments: list[str]):
    # Procesar el chunk y fragmentarlo
    doc = nlp(chunk)
    spans = [span.text.strip() for span in doc._.custom_sents]
    
    # Agregar los fragmentos completos solo si no están vacíos
    spans = [span for span in spans if span != ""]
    fragments.extend(spans)
    
    # Liberar memoria
    del doc
    gc.collect()


def __get_chunk_size(text: str, max_chunk_size) -> int:
    if len(text) <= max_chunk_size:
        return len(text)
    
    stop_symbols = ['\n']
    for i in range(max_chunk_size, 0, -1):
        if text[i] in stop_symbols:
            return i


def normalize_text(text: str):
    max_chars_per_line = __calculate_max_line_size(text)
    normalized_text = __clean_text(text, max_chars_per_line)
    return normalized_text


def __clean_text(text, max_caracteres_por_linea):
    # Paso 1: Eliminar saltos múltiples consecutivos (más de 2 seguidos)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Paso 2: Identificar y unir líneas rotas por formato (basado en longitud)
    lines = text.split('\n')
    result = []
    buffer = ""

    for i, line in enumerate(lines):
        line = line.rstrip()
        if not line:
            if buffer:
                result.append(buffer)
                buffer = ""
            result.append("")
            continue

        if (
                line.endswith(('.', '!', '?', ':', ';'))  # Termina en puntuación
                or i == len(lines) - 1  # Última línea
                or len(line) >= max_caracteres_por_linea
        ):
            buffer += line
            result.append(buffer)
            buffer = ""
        else:
            buffer += line + " "

    if buffer:
        result.append(buffer)

    # Paso 4: si hay un parentesis cerrado, añadir un espacio luego de este
    result = [re.sub(r'\)\s*', ') ', linea) for linea in result]

    # Paso 3: Eliminar espacios múltiples consecutivos
    result = [re.sub(r'\s+', ' ', linea).strip() for linea in result]
    return "\n".join(result)


def __calculate_max_line_size(text):
    if not text:
        return 0

    lines = text.split('\n')
    # Eliminar espacios en blanco al final de cada línea
    lengths = [len(linea.rstrip()) for linea in lines if linea.strip()]

    return max(lengths) if lengths else 0
