import os
import barcode
from barcode.writer import ImageWriter
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

# === Configuration ===
df = pd.DataFrame({'code': ['3KPRG2501716', '3KPRG2501717', '3KPRG2501718', '3KPRG2501719', '3KPRG2501720',
                            '3KPRG2501721', '3KPRG2501722', '3KPRG2501723', '3KPRG2501724', '3KPRG2501725',
                            '3KPRG2501726', '3KPRG2501727', '3KPRG2501728', '3KPRG2501729', '3KPRG2501730',
                            '3KPRG2501731', '3KPRG2501732', '3KPRG2501733', '3KPRG2501734', '3KPRG2501735',
                            '3KPRG2501736', '3KPRG2501737', '3KPRG2501738', '3KPRG2501739', '3KPRG2501740']})

codes= df['code'].unique().tolist()

copies_per_code = 3  # Number of copies per code per row
output_dir = "StarPOWER_Barcodes_QR"
os.makedirs(output_dir, exist_ok=True)

# PDF output file
pdf_file = os.path.join(output_dir, "V3_Starpowerbarcodes_with_qr.pdf")

# === Generate Barcodes & QR Codes ===
print("🔄 Generating barcodes and QR codes...")
label_images = []
for code in codes:

    # Generate Barcode
    BarcodeClass = barcode.get_barcode_class("code128")
    writer = ImageWriter()
    barcode_filename = os.path.join(output_dir, f"{code}_barcode")
    my_barcode = BarcodeClass(code, writer=writer)
    my_barcode.save(barcode_filename, options={
        'module_width': 0.2,
        'module_height': 15,    # Taller bars
        'font_size': 10,        # Larger text under barcode
        'text_distance': 6,     # More space between bars & text
        'quiet_zone': 1.0,
        'dpi': 300,
        'write_text': True      # Ensure numbers are included
    })
    barcode_filename += ".png"

    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2
    )
    qr.add_data(code)
    qr.make(fit=True)
    qr_filename = os.path.join(output_dir, f"{code}_qr.png")
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img.save(qr_filename)

    # Store for PDF creation
    label_images.append({
        "barcode": barcode_filename,
        "qr": qr_filename
    })

# === Create PDF with Barcodes + QR Codes ===
print("📦 Creating PDF with barcodes and QR codes...")

c = canvas.Canvas(pdf_file, pagesize=A4)
page_width, page_height = A4

# Label size
label_width = 60 * mm  # Wider for barcode + QR side by side
label_height = 30 * mm  # Taller to avoid overlap

# Margins and spacing
margin_x = 15 * mm
margin_y = 15 * mm
padding_x = 5 * mm
padding_y = 5 * mm

x = margin_x
y = page_height - margin_y - label_height

for item in label_images:
    for copy in range(copies_per_code):
        try:
            # Draw Barcode (left side)
            c.drawImage(
                item["barcode"],
                x, y + 5 * mm,  # Leave room for possible text (removed now)
                width=30 * mm,
                height=20 * mm,  # Taller for bars + numbers
                preserveAspectRatio=True,
                mask='auto'
            )

            # Draw QR Code (right side)
            c.drawImage(
                item["qr"],
                x + 35 * mm, y + 5 * mm,  # Position next to barcode
                width=20 * mm,
                height=20 * mm,
                preserveAspectRatio=True,
                mask='auto'
            )

        except Exception as e:
            print(f"❌ Error adding label to PDF: {e}")

        # Move x for next copy
        x += label_width + padding_x

    # Reset x, move y for next row
    x = margin_x
    y -= label_height + padding_y

    # Start new page if rows run out
    if y < margin_y:
        c.showPage()
        x = margin_x
        y = page_height - margin_y - label_height

c.save()
print(f"🎉 PDF created: {pdf_file}")
print("📄 Ready for printing!")


from glob import glob
import os

for i in glob(f'{output_dir}/*.png'):
  # print(i)
  os.remove(i)
