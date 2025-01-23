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
            ('sale_ok', '=', True),
            ('detailed_type', '=', 'service')
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
            'room_type':post.get('room_type'),
            'check_in_date': post.get('check_in'),
            'check_out_date': post.get('check_out'),
            'status': 'new',
        })
        
        # Retrieve and validate service data
        service_product_ids = request.httprequest.form.getlist('service_product_id[]')
        quantities = request.httprequest.form.getlist('quantity[]')

        service_data = []
        for product_id, quantity in zip(service_product_ids, quantities):
            if not product_id or not quantity:
                continue
            try:
                product_id = int(product_id)
                quantity = float(quantity)
                if quantity <= 0:
                    raise ValueError("Quantity must be positive")
                service_data.append((product_id, quantity))
            except (ValueError, TypeError) as e:
                _logger.error("Invalid service data: product_id=%s, quantity=%s. Error: %s", 
                            product_id, quantity, str(e))
                continue

        # Create service lines
        for product_id, quantity in service_data:
            product = request.env['product.product'].sudo().browse(product_id)
            if product.detailed_type != 'service':
                _logger.warning("Product %s is not a service. Skipping.", product.name)
                continue

            request.env['hotel.service.line'].sudo().create({
                'customer_id': booking.id,
                'product_id': product.id,
                'quantity': quantity,
                'price_unit': product.lst_price,
            })
            _logger.info("Added service %s (Qty: %s) to booking %s", product.name, quantity, booking.id)

        return request.redirect('/my/bookings')

    @http.route('/my/booking/<int:booking_id>', type='http', auth="user", website=True)
    def portal_booking_details(self, booking_id, **kw):
        booking = request.env['hotel.customer'].sudo().browse(booking_id)
        # Ensure the booking belongs to the current user
        if booking.partner_id != request.env.user.partner_id:
            return request.redirect('/my/bookings')
        return request.render("hotel_portal.portal_my_booking_details", {
            'booking': booking,
            'services': booking.service_line_ids,
            'page_name': 'booking_details',
        })