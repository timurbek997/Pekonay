# Python 3.10 asosidagi rasm
FROM python:3.10-slim

# Ishchi katalogni o'rnatish
WORKDIR /app

# Fayllarni konteynerga nusxalash
COPY . .

# Kerakli kutubxonalarni o'rnatish
RUN pip install --no-cache-dir -r requirements.txt

# Botni ishga tushirish komandasi
CMD ["python", "main.py"]
