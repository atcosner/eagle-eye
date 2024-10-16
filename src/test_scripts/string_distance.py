from rapidfuzz import process, fuzz, utils

from src.validation.util import ORNITHOLOGY_SPECIES_LIST

def main(text: str):
    match, ratio, edits = process.extractOne(
        text,
        ORNITHOLOGY_SPECIES_LIST,
        scorer=fuzz.WRatio,
        processor=utils.default_process,
    )
    print(f'Best match: "{text}" -> "{match}", ratio: {ratio}, edits: {edits}')


if __name__ == '__main__':
    main('Leuconotopicus villosus')
