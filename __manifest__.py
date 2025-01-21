{
    'name': 'Hotel Portal',
    'version': '1.0',
    'category': 'Services',
    'summary': 'Portal for Hotel Room Booking',
    'description': """
        Allows portal users to view available rooms and make bookings
    """,
    'depends': [
        'portal',
        'hotel_management'
    ],
    'data': [
        'views/portal_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'hotel_portal/static/src/css/portal.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}