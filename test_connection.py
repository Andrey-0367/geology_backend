import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5)
try:
    s.connect(('hmsdhjfgvjtbcmkecknq.supabase.co', 5432))
    print("Порт 5432 открыт")
except Exception as e:
    print(f"Ошибка: {e}")
finally:
    s.close()
