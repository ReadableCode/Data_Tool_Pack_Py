# %%
# Imports #

import io
import os
from os.path import expanduser

import matplotlib.pyplot as plt
from fpdf import FPDF

file_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
grandparent_dir = os.path.dirname(parent_dir)

data_dir = os.path.join(parent_dir, "data")
# Replace these placeholders with your actual content
chart_data = [(1, 2), (2, 3), (3, 5), (4, 8), (5, 10)]
image_path = os.path.join(data_dir, "screenshot.png")
text_content = "This is a sample paragraph of text."

# Create PDF using fpdf
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

# Add chart
plt.figure(figsize=(6, 4))
plt.plot(*zip(*chart_data), marker="o")
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.title("Sample Chart")
chart_image_path = os.path.join(data_dir, "chart.png")
plt.savefig(chart_image_path, format="png")
plt.close()

# Add image
pdf.ln(20)
pdf.image(image_path, x=10, y=pdf.get_y(), w=0, h=100)

# Add text
pdf.ln(110)
pdf.set_font("Arial", size=12)
pdf.multi_cell(0, 10, txt=text_content)

# Add chart image
pdf.ln(20)
pdf.image(chart_image_path, x=10, y=pdf.get_y(), w=0, h=100)

# Save PDF to file
pdf.output(os.path.join(data_dir, "output.pdf"))

print("PDF created successfully.")


# %%
