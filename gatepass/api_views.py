from rest_framework import generics, permissions
from .models import GatepassRequest
from .serializers import GatepassRequestSerializer
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
import logging
import io
import qrcode
import base64
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse

import traceback

from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.utils.timezone import localtime
from PIL import Image as PILImage
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle, Image
import os


logger = logging.getLogger(__name__)
User = get_user_model()

# Your existing views here...
class MyGatepassRequestsView(generics.ListCreateAPIView):
    serializer_class = GatepassRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'department_head':
            return GatepassRequest.objects.filter(
                department=user.department,
                status='pending_department'
            )
        elif user.role == 'security_head':
            return GatepassRequest.objects.filter(
                status='pending_security'
            )
        return GatepassRequest.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, department=self.request.user.department)


class ApproveGatepassView(generics.UpdateAPIView):
    queryset = GatepassRequest.objects.all()
    serializer_class = GatepassRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        decision = request.data.get("decision")

        if not decision:
            return Response({"detail": "Decision (approve or reject) is required."}, status=status.HTTP_400_BAD_REQUEST)

        if user.role == 'department_head' and instance.status == 'pending_department':
           if decision == 'approve':
                instance.status = 'pending_security'
                instance.department_approver = user
                instance.department_approval_date = timezone.now()
           elif decision == 'reject':
                instance.status = 'rejected_department'
                instance.department_approver = user
                instance.department_approval_date = timezone.now()
        elif user.role == 'security_head' and instance.status == 'pending_security':
            if decision == 'approve':
                instance.status = 'approved_security'
                instance.security_approver = user
                instance.security_approval_date = timezone.now()
            elif decision == 'reject':
                instance.status = 'rejected_security'
                instance.security_approver = user
                instance.security_approval_date = timezone.now()
        else:
            return Response({"detail": "Invalid role or gatepass state for this action."}, status=status.HTTP_403_FORBIDDEN)        

        instance.save()
        return self.update(request, *args, **kwargs, partial=True)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_gatepass_pdf(request, pk):
    try:
        gatepass = GatepassRequest.objects.get(pk=pk)

        # Permission check
        if gatepass.user != request.user and request.user.role not in ['department_head', 'security_head']:
            return HttpResponse("Unauthorized", status=403)

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        #LOGO
        # Define logo dimensions
        logo_width = 180  # in points (approx 1.4 inch)
        logo_height = 70

        # Define position: bottom-right, just above the disclaimer
        logo_x = (width - logo_width) / 2  # 2 inch from the right
        logo_y = 55  # just above the footer text (30 & 45)
        logo_path = os.path.join(settings.BASE_DIR, 'gatepass', 'static', 'gatepass', 'image.png')
        p.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height,preserveAspectRatio=True)
       
       
       
        # Title
        p.setFont("Helvetica-Bold", 16)
        p.drawString(inch, height - inch, f"Gatepass #{gatepass.id}")

        # GATEPASS DETAILS HERE 
        p.setFont("Helvetica", 12)
        p.drawString(inch, height - inch - 30, f"Requested by: {gatepass.user.name}")
        p.drawString(inch, height - inch - 60, f"Department: {gatepass.department.name if gatepass.department else 'N/A'}")
        p.drawString(inch, height - inch - 90, f"Reason: {gatepass.reason}")                                                               
        p.drawString(inch, height - inch - 120, f"Exit Time: {gatepass.exit_time.strftime('%Y-%m-%d %H:%M')}")
        p.drawString(inch, height - inch - 150, f"Return Time: {gatepass.return_time.strftime('%Y-%m-%d %H:%M')}")
        p.drawString(inch, height - inch - 180, f"Status: {gatepass.get_status_display()}")
        p.drawString(inch, height - inch - 210, f"Department Approver: {gatepass.department_approver.name if gatepass.department_approver else 'N/A'}")
        p.drawString(inch, height - inch - 240, f"Department Approval Date: {gatepass.department_approval_date.strftime('%Y-%m-%d %H:%M') if gatepass.department_approval_date else 'N/A'}")
        p.drawString(inch, height - inch - 270, f"Security Approver: {gatepass.security_approver.name if gatepass.security_approver else 'N/A'}")
        p.drawString(inch, height - inch - 300, f"Security Approval Date: {gatepass.security_approval_date.strftime('%Y-%m-%d %H:%M') if gatepass.security_approval_date else 'N/A'}")
        p.drawString(inch, height - inch - 330, f"Comments: {gatepass.comments if gatepass.comments else 'N/A'}")
        # QR code generation

        if gatepass.department_approver and gatepass.security_approver:
               verification_status = "VERIFIED : can proceed to checkout ✅"
        else:
               verification_status = "UNVERIFIED: please complete approval process  ❌"

        qr_text = f"Gatepass ID: {gatepass.id}\nStatus: {verification_status}"

        qr = qrcode.QRCode(box_size=3, border=1)
        qr.add_data(qr_text)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

        # Draw QR code on PDF
        qr_x = width - 2*inch
        qr_y = height - 2*inch
        p.drawInlineImage(qr_img, qr_x, qr_y, 1.5*inch, 1.5*inch)

        # Table data for items
        data = [['Item Name', 'Quantity', 'Serial Number', 'Description']]
        for item in gatepass.items.all():
            data.append([
                item.item_name,
                str(item.quantity),
                item.serial_number or '-',
                item.description or '-',
            ])

        if len(data) == 1:  # no items case
            data.append(['No items', '', '', ''])

        # Create and style the table
        table = Table(data, colWidths=[2*inch, inch, 2*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ]))

        # Position table below text
        table_width, table_height = table.wrap(0, 0)
        table_x = inch
        table_y = height - inch - 360 - table_height
        table.drawOn(p, table_x, table_y)

        # Footer Disclaimer
        footer_text = "This gatepass is system-generated and valid only when used in accordance with company policy. It must be scanned and verified at the security checkpoint."
        p.setFont("Helvetica-Oblique", 9)
        p.setFillColor(colors.grey)
        p.drawCentredString(width / 2, 45, "This gatepass is system-generated and must be used in line with company policy.")
        p.drawCentredString(width / 2, 30, "Present it for verification at the security checkpoint.")
        
        # Finish the PDF
        p.showPage()
        p.save()

        buffer.seek(0)
        return HttpResponse(buffer.read(), content_type='application/pdf')

    except GatepassRequest.DoesNotExist:
        return HttpResponse("Gatepass not found", status=404)
    except Exception as e:
        return HttpResponse(f"Error generating PDF: {str(e)}", status=500)