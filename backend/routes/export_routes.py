"""
Export routes for exporting member data to Excel/CSV
"""
from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
from sqlalchemy import or_
import pandas as pd
import io
import os

from models import Member

export_bp = Blueprint('export', __name__)


@export_bp.route('/members', methods=['POST'])
def export_members():
    """
    Export members to Excel or CSV

    Request body:
        - format: 'excel' or 'csv' (default: excel)
        - member_ids: List of member IDs to export (optional, exports all if not provided)
        - filters: Optional filters (same as GET /members)
    """
    data = request.get_json() or {}

    export_format = data.get('format', 'excel')
    member_ids = data.get('member_ids', [])
    filters = data.get('filters', {})

    # Build query
    query = Member.query

    # If specific member IDs provided, filter by those
    if member_ids:
        query = query.filter(Member.id.in_(member_ids))
    else:
        # Otherwise apply filters
        search = filters.get('search', '').strip()
        status = filters.get('status')
        city = filters.get('city')
        state = filters.get('state')

        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                or_(
                    Member.full_name.ilike(search_pattern),
                    Member.first_name.ilike(search_pattern),
                    Member.last_name.ilike(search_pattern),
                    Member.phone_primary.ilike(search_pattern),
                    Member.email.ilike(search_pattern)
                )
            )

        if status:
            query = query.filter_by(membership_status=status)

        if city:
            query = query.filter_by(city=city)

        if state:
            query = query.filter_by(state=state)

    # Get members
    members = query.order_by(Member.full_name).all()

    if not members:
        return jsonify({'error': 'No members found to export'}), 404

    # Convert to DataFrame
    member_data = []
    for member in members:
        member_data.append({
            'ID': member.id,
            'First Name': member.first_name,
            'Last Name': member.last_name,
            'Full Name': member.full_name,
            'Address Line 1': member.address_line1 or '',
            'Address Line 2': member.address_line2 or '',
            'City': member.city or '',
            'State/Province': member.state or '',
            'Postal Code': member.postal_code or '',
            'Country': member.country or '',
            'Primary Phone': member.phone_primary or '',
            'Secondary Phone': member.phone_secondary or '',
            'Email': member.email or '',
            'Date of Birth': member.date_of_birth.isoformat() if member.date_of_birth else '',
            'Date Joined': member.date_joined.isoformat() if member.date_joined else '',
            'Membership Status': member.membership_status,
            'Notes': member.notes or '',
            'Created At': member.created_at.isoformat() if member.created_at else ''
        })

    df = pd.DataFrame(member_data)

    # Generate filename with timestamp
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

    if export_format == 'csv':
        # Export as CSV
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)

        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'members_export_{timestamp}.csv'
        )
    else:
        # Export as Excel
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Members', index=False)

            # Get workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['Members']

            # Format header row
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#667eea',
                'font_color': 'white',
                'border': 1
            })

            # Write headers with formatting
            for col_num, column in enumerate(df.columns):
                worksheet.write(0, col_num, column, header_format)

            # Auto-fit columns
            for i, col in enumerate(df.columns):
                max_len = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                ) + 2
                worksheet.set_column(i, i, min(max_len, 50))

        output.seek(0)

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'members_export_{timestamp}.xlsx'
        )


@export_bp.route('/sample', methods=['GET'])
def export_sample():
    """
    Export a sample CSV template for bulk import
    """
    # Create sample data
    sample_data = [{
        'First Name': 'John',
        'Last Name': 'Doe',
        'Address Line 1': '123 Main Street',
        'Address Line 2': 'Apt 4B',
        'City': 'Turlock',
        'State/Province': 'CA',
        'Postal Code': '95380',
        'Country': 'USA',
        'Primary Phone': '(209) 555-1234',
        'Secondary Phone': '',
        'Email': 'john.doe@example.com',
        'Date of Birth': '1990-01-15',
        'Date Joined': '2024-01-01',
        'Membership Status': 'active',
        'Notes': 'Sample member record'
    }]

    df = pd.DataFrame(sample_data)

    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='member_import_template.csv'
    )
