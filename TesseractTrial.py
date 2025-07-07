import pytesseract
from pdf2image import convert_from_path
from PIL import Image

def ocr_pdf (pdf_path, output_txt='output.txt'):
    images = convert_from_path(pdf_path, dpi = 300)

    all_text = ''
    for i, img in enumerate(images):
        print(f'OCR-ing page {i + 1}...')
        text = pytesseract.image_to_string(img, lang='eng')
        all_text += f'\n--- PAGE {i + 1} ---\n{text}'

        with open(output_txt, 'w', encoding='utf-8') as f:
            f.write(all_text)
        
        print(f'OCR complete. Text saved to {output_txt}.')
    
    
ocr_pdf('Legislative_Proceedings_1838_Extra_Session.pdf')

