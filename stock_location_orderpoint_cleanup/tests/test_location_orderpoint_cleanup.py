# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.stock_location_orderpoint.tests.common import (
    TestLocationOrderpointCommon,
)


class TestLocationOrderpointCleanup(TestLocationOrderpointCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_obj = cls.env["product.product"]
        # Create some products in order to get a sample of several moves

        cls.product_2 = cls.product_obj.create(
            {
                "name": "Product 2",
                "type": "product",
            }
        )
        cls.product_3 = cls.product_obj.create(
            {
                "name": "Product 3",
                "type": "product",
            }
        )
        cls.product_4 = cls.product_obj.create(
            {
                "name": "Product 3",
                "type": "product",
            }
        )

    def test_orderpoint(self):
        """ """
        orderpoint, location_src = self._create_orderpoint_complete(
            "Reserve", trigger="manual"
        )

        # Create quantities on Reserve location
        self._create_quants(self.product, location_src, 20)
        self._create_quants(self.product_2, location_src, 20)
        self._create_quants(self.product_3, location_src, 20)
        self._create_quants(self.product_4, location_src, 20)

        move_1 = self._create_outgoing_move(12, product=self.product)
        move_2 = self._create_outgoing_move(13, product=self.product_2)
        move_3 = self._create_outgoing_move(14, product=self.product_3)
        move_4 = self._create_outgoing_move(15, product=self.product_4)

        moves = move_1 | move_2 | move_3 | move_4

        self.assertEqual({"confirmed"}, set(moves.mapped("state")))

        self._run_replenishment(orderpoint)

        replenish_move_1 = self._get_replenishment_move(orderpoint, self.product)
        replenish_move_2 = self._get_replenishment_move(orderpoint, self.product_2)
        replenish_move_3 = self._get_replenishment_move(orderpoint, self.product_3)
        replenish_move_4 = self._get_replenishment_move(orderpoint, self.product_4)

        replenish_moves = (
            replenish_move_1 | replenish_move_2 | replenish_move_3 | replenish_move_4
        )

        message_before = replenish_move_1.picking_id.message_ids
        orderpoint.cleanup()

        self.assertEqual({"cancel"}, set(replenish_moves.mapped("state")))
        message_after = replenish_move_1.picking_id.message_ids - message_before
        self.assertIn(
            "These moves have been cleaned up for location orderpoint",
            message_after.preview,
        )

    def test_orderpoint_run_after(self):
        """ """
        orderpoint, location_src = self._create_orderpoint_complete(
            "Reserve", trigger="manual"
        )

        # Create quantities on Reserve location
        self._create_quants(self.product, location_src, 20)
        self._create_quants(self.product_2, location_src, 20)
        self._create_quants(self.product_3, location_src, 20)
        self._create_quants(self.product_4, location_src, 20)

        move_1 = self._create_outgoing_move(12, product=self.product)
        move_2 = self._create_outgoing_move(13, product=self.product_2)
        move_3 = self._create_outgoing_move(14, product=self.product_3)
        move_4 = self._create_outgoing_move(15, product=self.product_4)

        moves = move_1 | move_2 | move_3 | move_4

        self.assertEqual({"confirmed"}, set(moves.mapped("state")))

        self._run_replenishment(orderpoint)

        replenish_move_1 = self._get_replenishment_move(orderpoint, self.product)
        replenish_move_2 = self._get_replenishment_move(orderpoint, self.product_2)
        replenish_move_3 = self._get_replenishment_move(orderpoint, self.product_3)
        replenish_move_4 = self._get_replenishment_move(orderpoint, self.product_4)

        replenish_moves = (
            replenish_move_1 | replenish_move_2 | replenish_move_3 | replenish_move_4
        )

        orderpoint.cleanup(True)

        self.assertEqual({"cancel"}, set(replenish_moves.mapped("state")))

        replenish_move_1 = self._get_replenishment_move(orderpoint, self.product)
        replenish_move_2 = self._get_replenishment_move(orderpoint, self.product_2)
        replenish_move_3 = self._get_replenishment_move(orderpoint, self.product_3)
        replenish_move_4 = self._get_replenishment_move(orderpoint, self.product_4)

        replenish_moves = (
            replenish_move_1 | replenish_move_2 | replenish_move_3 | replenish_move_4
        )

        self.assertEqual({"assigned"}, set(replenish_moves.mapped("state")))

    def test_orderpoint_run_after_partial(self):
        """ """
        orderpoint, location_src = self._create_orderpoint_complete(
            "Reserve", trigger="manual"
        )

        # Create quantities on Reserve location
        self._create_quants(self.product, location_src, 20)
        self._create_quants(self.product_2, location_src, 20)
        self._create_quants(self.product_3, location_src, 20)
        self._create_quants(self.product_4, location_src, 20)

        move_1 = self._create_outgoing_move(12, product=self.product)
        move_2 = self._create_outgoing_move(13, product=self.product_2)
        move_3 = self._create_outgoing_move(14, product=self.product_3)
        move_4 = self._create_outgoing_move(15, product=self.product_4)

        moves = move_1 | move_2 | move_3 | move_4

        self.assertEqual({"confirmed"}, set(moves.mapped("state")))

        self._run_replenishment(orderpoint)

        replenish_move_1 = self._get_replenishment_move(orderpoint, self.product)
        replenish_move_2 = self._get_replenishment_move(orderpoint, self.product_2)
        replenish_move_3 = self._get_replenishment_move(orderpoint, self.product_3)
        replenish_move_4 = self._get_replenishment_move(orderpoint, self.product_4)

        replenish_moves = (
            replenish_move_1 | replenish_move_2 | replenish_move_3 | replenish_move_4
        )

        # Cancel some outgoing moves
        (move_3 | move_4)._action_cancel()

        orderpoint.cleanup(True)

        self.assertEqual({"cancel"}, set(replenish_moves.mapped("state")))

        replenish_move_1 = self._get_replenishment_move(orderpoint, self.product)
        replenish_move_2 = self._get_replenishment_move(orderpoint, self.product_2)
        replenish_move_3 = self._get_replenishment_move(orderpoint, self.product_3)
        replenish_move_4 = self._get_replenishment_move(orderpoint, self.product_4)

        self.assertFalse(replenish_move_3 | replenish_move_4)

        self.assertTrue(replenish_move_1 | replenish_move_2)
