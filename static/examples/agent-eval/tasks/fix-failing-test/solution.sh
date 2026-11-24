#!/usr/bin/env bash
# Reference solution: multiply before dividing.
sed -i 's|subtotal \* (discount_percent // 100)|subtotal * discount_percent // 100|' cart.py
