🛡️ Sentinel Project - Price Tracker Pro
Sentinel Project là một ứng dụng web mạnh mẽ được xây dựng bằng Python (Flask), cho phép người dùng theo dõi biến động giá sản phẩm từ các sàn thương mại điện tử (Shopee) và các cửa hàng trực tuyến (Haravan, Sapo) một cách tự động. Hệ thống cung cấp cái nhìn trực quan thông qua biểu đồ để bạn biết khi nào là thời điểm tốt nhất để mua sắm.

✨ Tính năng nổi bật
Shopee Intelligence: Sử dụng API nội bộ của Shopee để lấy giá chính xác và siêu tốc (dưới 1 giây).

Hybrid Scraping Engine: Kết hợp giữa Requests và Selenium (Headless mode) để vượt qua các lớp bảo mật của các shop thời trang như XIXEOSHOP (Haravan).

Trực quan hóa dữ liệu: Tích hợp Chart.js để vẽ biểu đồ lịch sử giá cho từng sản phẩm, giúp theo dõi xu hướng tăng giảm.

Quản lý thông minh: Giao diện hiện đại với Tailwind CSS, hỗ trợ thêm, xóa và cập nhật giá hàng loạt chỉ với một cú click.

🛠️ Công nghệ sử dụng
Backend: Python 3.x, Flask.

Database: SQLite (SQLAlchemy ORM).

Crawler: Selenium, BeautifulSoup4, Requests.

Frontend: Tailwind CSS, Chart.js, Jinja2.

🚀 Hướng dẫn cài đặt
Clone dự án:

Bash
git clone https://github.com/baothangtbt/Sentinel_Project.git
cd Sentinel_Project
Cài đặt thư viện:

Bash
pip install flask flask_sqlalchemy requests selenium webdriver-manager
Chạy ứng dụng:

Bash
python app.py
Truy cập: http://127.0.0.1:5000

📈 Lộ trình phát triển (Roadmap)
[ ] Tự động gửi thông báo qua Telegram khi giá giảm sâu.

[ ] Hỗ trợ thêm các sàn thương mại điện tử khác (Lazada, Tiki, TikTok Shop).

[ ] Chế độ Dark Mode cho giao diện người dùng.
