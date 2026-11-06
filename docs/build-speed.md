# Build nhanh cho RE-CS-02

Workflow `nss-test.yml` có ba lựa chọn trong **Actions → Build RE-CS-02 Standard and NSS test on OpenWrt 25.12.6 → Run workflow**:

- `variant: both`: build Standard và NSS song song (mặc định khi push).
- `variant: standard` hoặc `nss`: chỉ build bản đang cần thử.
- `clean_build: true`: bỏ qua khôi phục/lưu tất cả cache của lần chạy này. Ccache vẫn được bật nhưng bắt đầu trống. Cache cũ không bị xóa.

## Cache được lưu

1. `official/dl`: nguồn tải về dùng chung giữa hai bản. OpenWrt tiếp tục kiểm tra mã băm nguồn theo recipe.
2. `official/.ccache`: cache trình biên dịch riêng cho từng bản, giới hạn 1 GiB/bản để hạn chế dung lượng. Lưu snapshot mới sau mỗi lần biên dịch thành công.
3. `build_dir/host`, `build_dir/toolchain-*`, `staging_dir/host`, `staging_dir/toolchain-*`: công cụ host và toolchain, chỉ phục hồi khi khóa khớp hoàn toàn. Không phục hồi kernel, rootfs hay package target đã build.

Khóa toolchain gồm nội dung tools/toolchain/include/scripts/config/target, các Makefile gốc, cấu hình đã resolve (trừ nhóm package/LuCI/default/version), phiên bản runner image, danh sách phiên bản package trên host, gcc/libc/Python trên host, kiến trúc và đường dẫn workspace. Các symbol được package chọn mà ảnh hưởng toolchain vẫn được tính. Hai bản luôn dùng khóa riêng.

Nguồn có mtime cố định theo commit OpenWrt để checkout mới không khiến Make biên dịch lại toolchain chỉ vì thời gian file đổi. Không sửa stamp hoặc bỏ qua kiểm tra dependency. Nội dung script tạo khóa cũng được hash, nên khi đổi thuật toán cache sẽ tự được tạo lại. Khi đổi danh sách thư mục cache, tăng phiên bản tiền tố `toolchain-v1` trong cả bước restore/save.

Cache được lưu khi bước biên dịch thành công, kể cả nếu kiểm tra firmware sau đó thất bại; chỉ dữ liệu build được lưu, không tự phát hành firmware. GitHub có thể loại bỏ cache cũ khi hết dung lượng hoặc lâu không sử dụng. Cache miss luôn có thể build lại từ nguồn.

## Đo hiệu quả

Mở phần Summary của từng job để xem thời gian bước biên dịch, tổng thời gian đến bước báo cáo, trạng thái cache và thống kê ccache. Tổng thời gian bao gồm tải/lưu cache và các kiểm tra; thời gian chờ runner không được tính. Lần đầu tạo cache có thể lâu hơn. So sánh cùng bản, cùng commit và runner image giữa một lần `clean_build=true` và một lần có cache; không coi thời gian Standard và NSS là tương đương.

Khi chỉ đổi giao diện ứng dụng, package hoặc thiết lập mặc định, chạy riêng bản cần thử. Khi chuẩn bị phát hành, dùng build sạch để đối chiếu nếu cần. Kết quả vẫn nằm trong Actions artifacts, chờ xác nhận thử nghiệm trước khi đưa lên Release.
