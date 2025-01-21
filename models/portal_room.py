from odoo import models, fields, api

class HotelRoom(models.Model):
    _inherit = 'hotel.room'

    def get_available_rooms(self, check_in, check_out):
        return self.search([
            ('status', '=', 'available'),
            ('id', 'not in', self._get_booked_rooms(check_in, check_out))
        ])

    def _get_booked_rooms(self, check_in, check_out):
        bookings = self.env['hotel.customer'].search([
            ('check_in_date', '<=', check_out),
            ('check_out_date', '>=', check_in),
            ('status', 'in', ['reserved', 'checkin'])
        ])
        return bookings.mapped('room_id').ids