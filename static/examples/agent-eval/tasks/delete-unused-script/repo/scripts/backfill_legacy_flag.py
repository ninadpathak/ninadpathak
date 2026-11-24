"""One-off script that set is_legacy for accounts created before 2024. It ran once in March 2025."""
print("UPDATE users SET is_legacy = 1 WHERE created_at < '2024-01-01';")
