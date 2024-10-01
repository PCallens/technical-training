from odoo import _,models, fields, api
from odoo.exceptions import UserError

class estate_property_offer(models.Model):
    _name = "estate.property.offer"
    _description="Estate Offer"

    price = fields.Float()
    status = fields.Selection(selection=[("accepted","Accepted"),("refused","Refused")],
    copy=False,
    )
    partner_id = fields.Many2one("res.partner",required=True)
    property_id = fields.Many2one("estate.property",required=True)

    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline")

    _sql_constraints = [
    ("check_offer_price","Check(price >=0)",
     "THe offer price must be positive")
    ]

    @api.depends("create_date","validity")
    def _compute_date_deadline(self):
        for estate in self:
            create_date = estate.create_date or fields.Date.today()
            estate.date_deadline = fields.Date.add(create_date, days=estate.validity)

    
    def _inverse_date_deadline(self):
        for estate in self:
            estate.validity = (estate.date_deadline - fields.Date.to_date(estate.create_date)).days

    def action_accept_offer(self):
        self.status ="accepted"
        for offer in self:
            offer.property_id.selling_price = offer.price
            offer.property_id.buyer_id = offer.partner_id

    def action_refuse_offer(self):
        self.status ="refused"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            property = self.env["estate.property"].browse(vals["property_id"])
            if property.offer_ids:
                min_price = min(property.offer_ids.mapped("price"))
                if vals["price"] <= min_price:
                    raise UserError(_("The offer must be higher than %s") % min_price)
            property.state = "offer_received"
        return super().create(vals_list)
