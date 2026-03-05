import streamlit as st
import pandas as pd
import os
import barcode
from barcode.writer import ImageWriter
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from glob import glob
import tempfile
import shutil
from datetime import datetime as dt

now= dt.now().strftime("%Y-%m-%d_%H-%M-%S")
# now= str(now)

# === Streamlit App ===
st.set_page_config(page_title="QR & Barcode Generator", layout="centered")
st.title("📦 QR & Barcode Generator")
st.write("Upload a CSV, Excel, or TXT file containing your codes. This app will generate barcodes & QR codes and give you a PDF ready for printing.")

# File upload
uploaded_file = st.file_uploader("📂 Upload your file", type=["csv", "xlsx", "xls", "txt"])

if uploaded_file is not None:
    try:
        # Read file into DataFrame
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
            # shutil.copy(uploaded_file, "Data")
        elif uploaded_file.name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith(".txt"):
            df = pd.read_csv(uploaded_file, delimiter="\t", header=None, names=["code"])
        else:
            st.error("Unsupported file format!")
            st.stop()

        # Show preview
        st.subheader("📄 Data Preview")
        st.dataframe(df.head(20))
        # st.dataframe(df)

        # Select column with codes
        code_column = st.selectbox("Select column containing codes:", df.columns)

        # Number of copies per code per row
        # copies_per_code = st.number_input("Number of copies per code per row:", min_value=1, max_value=10, value=3)

        copies_per_code= 3
        
        if st.button("🚀 Generate PDF"):
            with st.spinner("Generating barcodes, QR codes & PDF..."):
                # Temporary directory
                temp_dir = tempfile.mkdtemp()
                output_dir = os.path.join(temp_dir, "Barcodes_QR")
                os.makedirs(output_dir, exist_ok=True)

                codes = df[code_column].dropna().unique().tolist()
                pdf_file = os.path.join(output_dir, f"Generated_Barcodes_QR.pdf")
                

                label_images = []
                for code in codes:
                    # Generate Barcode
                    BarcodeClass = barcode.get_barcode_class("code128")
                    writer = ImageWriter()
                    barcode_filename = os.path.join(output_dir, f"{code}_barcode")
                    my_barcode = BarcodeClass(str(code), writer=writer)
                    my_barcode.save(barcode_filename, options={
                        'module_width': 0.2,
                        'module_height': 15,
                        'font_size': 10,
                        'text_distance': 6,
                        'quiet_zone': 1.0,
                        'dpi': 300,
                        'write_text': True
                    })
                    barcode_filename += ".png"

                    # Generate QR Code
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=2
                    )
                    qr.add_data(str(code))
                    qr.make(fit=True)
                    qr_filename = os.path.join(output_dir, f"{code}_qr.png")
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    qr_img.save(qr_filename)

                    label_images.append({
                        "barcode": barcode_filename,
                        "qr": qr_filename
                    })

                # === Create PDF with adjusted layout ===
                c = canvas.Canvas(pdf_file, pagesize=A4)
                page_width, page_height = A4

                # Label size (adjusted for 8 rows)
                label_width = 60 * mm
                label_height = 26 * mm  # reduced height to fit 8 rows

                # Margins and spacing
                margin_x = 15 * mm
                margin_y = 10 * mm      # reduced margin
                padding_x = 5 * mm
                padding_y = 3 * mm      # reduced padding

                x = margin_x
                y = page_height - margin_y - label_height

                for item in label_images:
                    for copy in range(copies_per_code):
                        try:
                            # Draw Barcode (left)
                            c.drawImage(
                                item["barcode"],
                                x, y + 5 * mm,
                                width=30 * mm,
                                height=20 * mm,
                                preserveAspectRatio=True,
                                mask='auto'
                            )
                            # Draw QR Code (right)
                            c.drawImage(
                                item["qr"],
                                x + 35 * mm, y + 5 * mm,
                                width=20 * mm,
                                height=20 * mm,
                                preserveAspectRatio=True,
                                mask='auto'
                            )
                        except Exception as e:
                            print(f"Error adding label: {e}")

                        x += label_width + padding_x  # Move right for next copy

                    x = margin_x  # Reset x
                    y -= label_height + padding_y  # Move down for next row

                    if y < margin_y:
                        c.showPage()
                        x = margin_x
                        y = page_height - margin_y - label_height

                c.save()

                # Clean up PNG files
                for img_file in glob(f'{output_dir}/*.png'):
                    os.remove(img_file)

                # Provide download link
                st.success("🎉 PDF generated successfully!")
                with open(pdf_file, "rb") as f:
                    st.download_button("📥 Download PDF", f, file_name=f"Generated_Barcodes_QR_For_{code_column}_{str(now)}.pdf", mime="application/pdf")

            # Cleanup temp folder
            shutil.rmtree(temp_dir)

    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.info("Upload a file to start.")
