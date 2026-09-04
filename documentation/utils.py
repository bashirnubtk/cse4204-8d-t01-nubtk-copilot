from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from apps.academics.models import PaymentHistory, StudentProfile
from datetime import date

@login_required
def export_digital_id_pdf_view(request):
    if not getattr(request.user, 'is_student', False):
        return redirect('home')

    profile = get_object_or_404(StudentProfile, user=request.user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Digital_ID_{profile.user.username}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=(250, 400), rightMargin=10, leftMargin=10, topMargin=15, bottomMargin=10)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=14, textColor=colors.HexColor('#1A365D'), alignment=1)
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=8, textColor=colors.gray, alignment=1)
    data_style = ParagraphStyle('DataStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#2D3748'))
    bold_data = ParagraphStyle('BoldData', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#1A365D'))

    story.append(Paragraph("NUBTK PILOT PORTAL", title_style))
    story.append(Paragraph("OFFICIAL DIGITAL STUDENT ID", sub_style))
    story.append(Spacer(1, 15))

    id_data = [
        [Paragraph("Student Name:", data_style), Paragraph(str(profile.student_name), bold_data)],
        [Paragraph("Enrollment ID:", data_style), Paragraph(str(profile.user.username), bold_data)],
        [Paragraph("Department:", data_style), Paragraph(str(getattr(profile, 'department', 'CSE') or 'CSE'), data_style)],
        [Paragraph("Contact No:", data_style), Paragraph(str(getattr(profile, 'phone_number', 'N/A')), data_style)],
        [Paragraph("Blood Group:", data_style), Paragraph("O+ (Verified)", data_style)],
        [Paragraph("Issue Date:", data_style), Paragraph(date.today().strftime("%Y-%m-%d"), data_style)],
    ]

    data_table = Table(id_data, colWidths=[90, 140])
    data_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
    ]))

    story.append(data_table)
    story.append(Spacer(1, 30))

    footer_style = ParagraphStyle('FooterStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, alignment=1)
    footer_table = Table([[Paragraph("AUTHORIZED DIGITAL CAMPUS CARD", footer_style)]], colWidths=[230], rowHeights=[25])
    footer_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1A365D')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(footer_table)

    doc.build(story)
    return response

@login_required
def export_payment_receipt_pdf_view(request, payment_id):
    payment = get_object_or_404(PaymentHistory, id=payment_id)

    if getattr(request.user, 'is_student', False) and payment.student_profile.user!= request.user:
        return HttpResponse("Unauthorized Access Denied.", status=403)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Receipt_{payment.id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()

    header_style = ParagraphStyle('Header', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=22, textColor=colors.HexColor('#2B6CB0'))
    invoice_title = ParagraphStyle('InvTitle', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=14, textColor=colors.HexColor('#4A5568'), alignment=2)
    normal_text = ParagraphStyle('NormalText', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#2D3748'))
    invoice_total_style = ParagraphStyle('TotalStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor('#2F855A'))

    header_data = [
        [Paragraph("NORTHERN UNIVERSITY BTL", header_style), Paragraph("OFFICIAL RECEIPT", invoice_title)],
        [Paragraph("Khulna Campus, Bangladesh\nSupport: admin@nubtk.edu", normal_text), Paragraph(f"Receipt ID: NUBTK-TXN-{payment.id}\nDate: {date.today().strftime('%Y-%m-%d')}", normal_text)]
    ]
    header_table = Table(header_data, colWidths=[270, 270])
    header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 10)]))
    story.append(header_table)
    story.append(Spacer(1, 20))

    story.append(Paragraph(f"<b>Bill To:</b>", normal_text))
    story.append(Paragraph(f"Student Name: {payment.student_profile.student_name}", normal_text))
    story.append(Paragraph(f"Digital ID: {payment.student_profile.user.username}", normal_text))
    story.append(Paragraph(f"Department: {getattr(payment.student_profile, 'department', 'CSE') or 'CSE'}", normal_text))
    story.append(Spacer(1, 20))

    billing_data = [
        ["Description / Milestone", "Due Date", "Status", "Amount (BDT)"],
        [payment.title, str(payment.due_date), payment.status, f"{payment.amount} TK"],
        ["", "", "Total Paid:", Paragraph(f"{payment.amount} TK", invoice_total_style)]
    ]

    billing_table = Table(billing_data, colWidths=[240, 100, 100, 100])
    billing_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EDF2F7')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#2D3748')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (3,0), (3,-1), 'RIGHT'),
        ('LINEBELOW', (0,0), (-1,1), 1, colors.HexColor('#CBD5E0')),
        ('LINEABOVE', (2,2), (3,2), 1, colors.HexColor('#2F855A')),
    ]))

    story.append(billing_table)
    story.append(Spacer(1, 40))
    story.append(Paragraph("<i>This is a system-generated electronic document. No physical signature is required.</i>", normal_text))

    doc.build(story)
    return response