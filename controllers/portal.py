from odoo import http
from odoo.http import request
from datetime import datetime

class HotelPortal(http.Controller):
    
    @http.route('/my/rooms', type='http', auth="user", website=True)
    def portal_rooms(self, **kw):
        rooms = request.env['hotel.room'].sudo().search([('status', '=', 'available')])
        return request.render("hotel_portal.portal_my_rooms", {
            'rooms': rooms,
            'page_name': 'rooms',
        })

    @http.route('/my/bookings', type='http', auth="user", website=True)
    def portal_bookings(self, **kw):
        bookings = request.env['hotel.customer'].sudo().search([
            ('partner_id', '=', request.env.user.partner_id.id)
        ])
        return request.render("hotel_portal.portal_my_bookings", {
            'bookings': bookings,
            'page_name': 'bookings',
        })

    @http.route('/room/book', type='http', auth="user", website=True)
    def book_room(self, **post):
        room = request.env['hotel.room'].sudo().browse(int(post.get('room_id')))
        services = request.env['product.product'].sudo().search([
            ('available', '=', True),
            ('detailed_type', '=', 'product')
        ])
        return request.render("hotel_portal.booking_form", {
            'room': room,
            'available_services': services,
            'min_date': datetime.now().strftime('%Y-%m-%d'),
        })

    @http.route('/room/confirm', type='http', auth="user", website=True, csrf=False)
    def confirm_booking(self, **post):
        room = request.env['hotel.room'].sudo().browse(int(post.get('room_id')))
        
        # Create booking
        booking = request.env['hotel.customer'].sudo().create({
            'partner_id': request.env.user.partner_id.id,
            'hotel_id': room.hotel_id.id,
            'room_id': room.id,
            'check_in_date': post.get('check_in'),
            'check_out_date': post.get('check_out'),
            'status': 'new',
        })
        
        # Retrieve multi-value fields using request.httprequest.form
        service_product_ids = request.httprequest.form.getlist('service_product_id[]')
        quantities = request.httprequest.form.getlist('quantity[]')
        
        service_data = zip(service_product_ids, quantities)
        
        for product_id, quantity in service_data:
            if product_id and quantity:
                product = request.env['product.product'].sudo().browse(int(product_id))
                request.env['hotel.service.line'].sudo().create({
                    'customer_id': booking.id,
                    'product_id': product.id,
                    'quantity': float(quantity),
                    'price_unit': product.lst_price,
                })
        
        return request.redirect('/my/bookings')