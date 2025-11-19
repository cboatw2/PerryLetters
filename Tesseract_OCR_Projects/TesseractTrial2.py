import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from collections import defaultdict

def ocr_pdf(pdf_path, output_txt='ocr_with_confidence.txt'):
    images = convert_from_path(pdf_path, dpi=300)

    all_text = ''
    for i, img in enumerate(images):
        print(f'OCR-ing page {i + 1}...')
        ocr_data = pytesseract.image_to_data(img, lang='eng', output_type=pytesseract.Output.DICT)
        lines = defaultdict(list)
        for j in range(len(ocr_data['text'])):
            if int(ocr_data['conf'][j]) > 0 and ocr_data['text'][j].strip():
                line_id = ocr_data['line_num'][j]
                lines[line_id].append(ocr_data['text'][j])
        text = '\n'.join([' '.join(lines[line_id]) for line_id in sorted(lines)])
        all_text += f'\n--- PAGE {i + 1} ---\n{text}'

        # Calculate average confidence (ignore -1 values)
        confidences = []
        for conf in ocr_data['conf']:
            try:
                conf_int = int(conf)
                if conf_int >= 0:
                    confidences.append(conf_int)
            except Exception:
                continue
        avg_conf = sum(confidences) / len(confidences) if confidences else 0
        print(f'Average confidence for page {i + 1}: {avg_conf:.2f}')

        with open(output_txt, 'w', encoding='utf-8') as f:
            f.write(all_text)

    print(f'OCR complete. Text saved to {output_txt}.')

ocr_pdf('Legislative_Proceedings_1838_Extra_Session.pdf')