import qrcode

# Ссылка на вашего бота
bot_link = "https://t.me/aygo_zoo_bot"

# Создание объекта QRCode
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=2,
)

# Добавление данных в QRCode
qr.add_data(bot_link)
qr.make(fit=True)

# Создание изображения QR-кода
img = qr.make_image(fill_color="black", back_color="white")

# Сохранение изображения QR-кода
img.save("bot_qr_code.png")
