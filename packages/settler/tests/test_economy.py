"""Settler helpers that do not call Circle or peaq."""

from __future__ import annotations

import unittest

from economy import machine_id_bytes32


class MachineIdTest(unittest.TestCase):
    def test_decimal_machine_id_to_bytes32(self) -> None:
        wallets = {
            "actors": [
                {
                    "label": "servebot-1",
                    "peaqMachineId": "59328440066796600542199572455408389928436277639102769462180386810815539058720",
                }
            ]
        }
        value = machine_id_bytes32(wallets)
        self.assertTrue(value.startswith("0x"))
        self.assertEqual(len(value), 66)
        self.assertEqual(
            int(value, 16),
            59328440066796600542199572455408389928436277639102769462180386810815539058720,
        )

    def test_override_wins(self) -> None:
        override = "0x" + "ab" * 32
        self.assertEqual(machine_id_bytes32({"actors": []}, override), override)


if __name__ == "__main__":
    unittest.main()
