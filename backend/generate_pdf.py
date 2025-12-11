from fpdf import FPDF
import os

pdf = FPDF()
pdf.add_page()
pdf.set_font("helvetica", size=12)
pdf.cell(text="This is a test document for CorporateMemory.", new_x="LMARGIN", new_y="NEXT")
pdf.cell(text="Policy number 1: Work hours are 9 AM to 5 PM.", new_x="LMARGIN", new_y="NEXT")
pdf.cell(text="Policy number 2: Remote work is allowed on Fridays.", new_x="LMARGIN", new_y="NEXT")
pdf.cell(text="End of document.", new_x="LMARGIN", new_y="NEXT")

output_dir = "backend/sample_data"
os.makedirs(output_dir, exist_ok=True)
pdf.output(f"{output_dir}/sample_policy.pdf")
print(f"Created {output_dir}/sample_policy.pdf")
