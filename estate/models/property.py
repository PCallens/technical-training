from odoo import _,models, fields, api
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero,float_compare

class estate_property(models.Model):
    _name = "estate.property"
    _description="Estate Property"

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False,default=fields.Date.add(fields.Date.today(), months= 3))
    expected_price = fields.Float(required = True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    fascades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection([('north', 'North'), ('south', 'South'),('east', 'East'),('west', 'West')])
    active = fields.Boolean(default=False)
    state = fields.Selection(selection=[("new","New"),("offer_received","Offer received"),("offer_accepted","Offer accepted"),("sold","Sold"),("cancelled","Cancelled")],
    default="new",
    copy=False,
    required=True,
    )
    property_type_id = fields.Many2one("estate.property.type")
    salesperson_id = fields.Many2one("res.users",default=lambda self: self.env.user)
    buyer_id = fields.Many2one("res.partner", copy=False)
    tag_ids = fields.Many2many("estate.property.tag")
    offer_ids = fields.One2many("estate.property.offer","property_id")

    total_area = fields.Integer(compute="_compute_total_area")
    best_price = fields.Float(compute="_compute_best_price")

    _sql_constraints = [
    ("check_expected_price","Check(expected_price >=0)",
     "THe expected price must be positive"),
    ("check_selling_price","Check(selling_price >=0)",
     "THe selling price must be positive")
    ]

    @api.constrains("selling_price","expected_price")
    def _check_selling_price(self):
        for property in self:
            if (not float_is_zero(property.selling_price, precision_rounding=0.01) and
                float_compare(property.selling_price,0.9* property.expected_price, precision_rounding=0.01)<0
               ):
                raise ValidationError(_('THe selling price sould not be lower than 90% of the expected price'))
    
    @api.depends("garden_area","living_area")
    def _compute_total_area(self):
        for property in self:
            property.total_area = property.living_area + property.garden_area

    @api.depends("garden_area")
    def _compute_best_price(self):
        for property in self:
            if property.offer_ids:
                property.best_price = max(property.offer_ids.mapped("price"))
            else:
                property.best_price=0

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = self.garden_orientation = False

    def action_sell_property(self):
        for property in self:
            if property.state =="cancelled":
                raise UserError(_("Cancelled properties cannot be sold"))
            property.state = "sold"

    def action_cancel_property(self):
        self.state ="cancelled"

    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_cancelled(self):
        for property in self:
            if property.state not in ("new","cancelled"):
                raise UserError(_("Only new or cancelled property can be deleted"))
            