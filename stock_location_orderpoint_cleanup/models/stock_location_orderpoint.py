# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockLocationOrderpoint(models.Model):

    _inherit = "stock.location.orderpoint"

    def _get_moves_to_cleanup_domain(self):
        self.ensure_one()
        return [
            ("location_orderpoint_id", "=", self.id),
            ("state", "not in", ("done", "cancel")),
            ("quantity_done", "<=", 0),
            ("picking_id.printed", "=", False),
        ]

    def _get_moves_to_cleanup(self):
        self.ensure_one()
        moves = self.env["stock.move"].search(self._get_moves_to_cleanup_domain())
        return moves

    def cleanup(self, run_after=False):
        """
        This method can be called externally

        run_after: Run the orderpoint after cleanup
        """

        moves = self._get_moves_to_cleanup()
        for picking, moves in moves.partition("picking_id").items():
            moves._action_cancel()
            picking._log_location_orderpoint_cleanup_message(self, moves)

        if run_after:
            self.run_replenishment()
