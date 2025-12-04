from io import BytesIO
from django.template.loader import get_template
from django.core.files import File
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import qrcode
import os
from django.conf import settings


def generate_qr_code(url, size=100):
    """Generate QR code image for certificate verification"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer


def generate_certificate_pdf(certificate, base_url="https://avtomektep.kz"):
    """
    Generate PDF certificate with QR code
    Returns a BytesIO buffer containing the PDF
    """
    buffer = BytesIO()
    
    # Create PDF document (landscape A4)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=28,
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    normal_center = ParagraphStyle(
        'NormalCenter',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=10
    )
    
    name_style = ParagraphStyle(
        'NameStyle',
        parent=styles['Normal'],
        fontSize=24,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=20
    )
    
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_LEFT,
        spaceAfter=5
    )
    
    # Build story
    story = []
    
    # Title
    story.append(Paragraph("СВИДЕТЕЛЬСТВО", title_style))
    story.append(Paragraph("о прохождении обучения в учебной организации", subtitle_style))
    
    # Certificate number
    story.append(Paragraph(f"№ {certificate.certificate_number}", normal_center))
    story.append(Spacer(1, 20))
    
    # Student name
    story.append(Paragraph("Настоящее свидетельство выдано", normal_center))
    story.append(Paragraph(certificate.student.full_name.upper(), name_style))
    
    # Main info
    story.append(Paragraph(f"ИИН: {certificate.student.iin}", normal_center))
    story.append(Spacer(1, 20))
    
    # Training info
    story.append(Paragraph(
        f"прошел(а) обучение в учебной организации <b>{certificate.school.name}</b>",
        normal_center
    ))
    story.append(Paragraph(
        f"по программе подготовки водителей транспортных средств категории <b>{certificate.category.code if certificate.category else 'N/A'}</b>",
        normal_center
    ))
    story.append(Spacer(1, 20))
    
    # Training period and hours
    if certificate.training_start_date and certificate.training_end_date:
        story.append(Paragraph(
            f"Период обучения: с {certificate.training_start_date.strftime('%d.%m.%Y')} по {certificate.training_end_date.strftime('%d.%m.%Y')}",
            normal_center
        ))
    
    story.append(Paragraph(
        f"Количество часов: теория - {certificate.theory_hours}, практика - {certificate.practice_hours}",
        normal_center
    ))
    story.append(Spacer(1, 30))
    
    # Issue info
    story.append(Paragraph(
        f"Дата выдачи: {certificate.issue_date.strftime('%d.%m.%Y')}",
        normal_center
    ))
    
    # Generate QR code
    verification_url = f"{base_url}/verify/certificate/{certificate.uuid}/"
    qr_buffer = generate_qr_code(verification_url)
    qr_image = Image(qr_buffer, width=2.5*cm, height=2.5*cm)
    
    story.append(Spacer(1, 20))
    
    # QR code with description
    qr_table = Table([[qr_image]], colWidths=[3*cm])
    qr_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(qr_table)
    story.append(Paragraph("Сканируйте для проверки подлинности", normal_center))
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(Paragraph(
        f"Автошкола: {certificate.school.name}<br/>"
        f"БИН/ИИН: {certificate.school.bin_iin}<br/>"
        f"Адрес: {certificate.school.address}",
        info_style
    ))
    
    # Build PDF
    doc.build(story)
    
    buffer.seek(0)
    return buffer


def save_certificate_pdf(certificate, base_url="https://avtomektep.kz"):
    """Generate and save PDF to certificate model"""
    pdf_buffer = generate_certificate_pdf(certificate, base_url)
    
    filename = f"certificate_{certificate.certificate_number}.pdf"
    certificate.pdf_file.save(filename, File(pdf_buffer), save=False)
    
    return certificate

