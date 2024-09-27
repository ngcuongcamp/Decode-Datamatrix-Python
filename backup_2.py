import cv2
from GUI.Ui_Scanner_UI import Ui_MainWindow
from src import (
    Camera_Thread,
    Serial_Thread,
    Worker,
    Reader,
    logger,
    config,
    config_update,
    get_current_date,
    format_current_time,
)
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QApplication, QMessageBox
from PyQt5.QtCore import Qt, QThreadPool
from PyQt5.QtGui import QIcon, QPixmap, QImage
import sys
import subprocess
import threading


class MyApplication(QMainWindow):

    def __init__(self):
        self.frame = None
        self.read_config()
        self.init_UI()
        self.reader = Reader()
        self.threadpool = QThreadPool()
        # self.data_scan = None

        # connect Camera
        self.THREAD_CAMERA = Camera_Thread(self.IDC1)
        self.THREAD_CAMERA.frame_received.connect(self.display_frame)
        self.THREAD_CAMERA.start()

        # connect PLC
        self.THREAD_PLC = Serial_Thread(self.COM_PLC, self.BAUDRATE_PLC)
        self.THREAD_PLC.data_received.connect(self.handle_data_plc)
        self.THREAD_PLC.start()

        # connect SFC PORT SEND
        self.THREAD_SFC_SEND = Serial_Thread(self.COM_SFC, self.BAUDRATE_SFC)
        # self.THREAD_SFC_SEND.data_received.connect(self.handle_data_plc)
        self.THREAD_SFC_SEND.start()

        # connect SFC PORT RECEIVE
        self.THREAD_SFC_RC = Serial_Thread(self.COM_SFC_RC, self.BAUDRATE_SFC)
        self.THREAD_SFC_RC.data_received.connect(self.handle_data_sfc)
        self.THREAD_SFC_RC.start()

        # connect READER PORT
        self.THREAD_READER = Serial_Thread(self.COM_READER, self.BAUDRATE_READER)
        self.THREAD_READER.data_received.connect(self.handle_data_gun)
        # self.THREAD_READER.start()

        # OPEN PROPS CAMERA
        if self.OPEN_CAMERA_PROPS == 1:
            self.THREAD_CAMERA.cap.set(cv2.CAP_PROP_SETTINGS, 1)

        # init EXPOSURE
        # self.THREAD_CAMERA.cap.set(cv2.CAP_PROP_SATURATION, 0)
        self.THREAD_CAMERA.cap.set(cv2.CAP_PROP_EXPOSURE, self.PROP_EXPOSURE)

        # update event
        self.uic.Update_Button.clicked.connect(self.handle_update)

    def init_UI(self):
        super().__init__()
        self.uic = Ui_MainWindow()
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.uic.setupUi(self)
        self.setWindowTitle("Scanner A184_CB509")
        self.setWindowIcon(QIcon(r"./src/icon/sd.ico"))
        screen_geometry = QDesktopWidget().availableGeometry()
        self.setGeometry(
            screen_geometry.width() - self.width(),
            screen_geometry.height() - self.height(),
            self.width(),
            self.height(),
        )
        self.uic.Camera_Frame.setText("CAMERA ERROR")
        self.show()

    def read_config(self):
        self.COM_PLC = config["SERIAL"]["COM_PLC"]
        self.BAUDRATE_PLC = int(config["SERIAL"]["BAUDRATE_PLC"])
        self.COM_SFC = config["SERIAL"]["COM_SFC"]
        self.COM_SFC_RC = config["SERIAL"]["COM_SFC_RC"]
        self.BAUDRATE_SFC = int(config["SERIAL"]["BAUDRATE_SFC"])
        self.COM_READER = config["SERIAL"]["COM_READER"]
        self.BAUDRATE_READER = int(config["SERIAL"]["BAUDRATE_READER"])

        self.IDC1 = int(config["CAMERA"]["IDC1"])
        self.IDC2 = int(config["CAMERA"]["IDC2"])
        self.PROP_EXPOSURE = float(config["CAMERA"]["PROP_EXPOSURE"])
        self.PROP_EXPOSURE_2 = float(config["CAMERA"]["PROP_EXPOSURE_2"])
        self.MIN_THRESHOLD = int(config["CAMERA"]["MIN_THRESHOLD"])
        self.MAX_THRESHOLD = int(config["CAMERA"]["MAX_THRESHOLD"])
        self.STEP_THRESHOLD = int(config["CAMERA"]["STEP_THRESHOLD"])
        self.SCAN_LIMIT = int(config["CAMERA"]["SCAN_LIMIT"])

        self.IMAGE_NG_DIR = config["PATH"]["IMAGE_NG_DIR"]
        self.FOLDER_TO_KEEP = int(config["PATH"]["FOLDER_TO_KEEP"])

        self.SAVE_IMAGE = int(config["OPTIONS"]["SAVE_IMAGE"])
        self.OPEN_CAMERA_PROPS = int(config["OPTIONS"]["OPEN_CAMERA_PROPS"])

        self.path_target = config_update["PATH_TARGET"]["path_target"]

    def display_frame(self, frame):
        self.frame = frame
        frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        img = QImage(
            frame_rgb.data,
            frame_rgb.shape[1],
            frame_rgb.shape[0],
            QImage.Format_RGB888,
        )
        scaled_pixmap = img.scaled(self.uic.Camera_Frame.size())
        pixmap = QPixmap.fromImage(scaled_pixmap)
        self.uic.Camera_Frame.setPixmap(pixmap)

    def closeEvent(self, event):
        req = QMessageBox.question(
            self,
            "Confirm Close",
            "Do you want to close the application?",
            QMessageBox.Yes | QMessageBox.Cancel,
            QMessageBox.Cancel,
        )
        if req == QMessageBox.Yes:
            event.accept()
            self.THREAD_CAMERA.stop()
            # self.THREAD_PLC.stop()
            print("--------------\nCLOSE")
            if self.THREAD_CAMERA.isRunning():
                self.THREAD_CAMERA.cap.release()
            cv2.destroyAllWindows()
        else:
            event.ignore()

    def handle_data_plc(self, data):
        if self.THREAD_PLC.is_running:
            # print("\n\n")
            # print("-----------DATA PLC ---------")
            # print(f"--> Received scan signal from PLC: {data}")

            # logger.info("\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            # logger.info(f"--> Received scan signal from PLC: {data}")

            if data in [
                b"1\x00",
                b"1",
                b"1\x00\r\n",
            ]:
                print("--> ------ SCAN SIGNAL -------")
                logger.info("--> ------ SCAN SIGNAL -------")

                ###############################################
                # TODO:
                self.worker = Worker(self.thread_scan_action)
                try:
                    self.worker.signals.data.connect(self.handle_decode_data)
                    self.worker.signals.notification.connect(self.handle_set_ui)
                    self.threadpool.start(self.worker)
                except Exception as E:
                    print(f"Error when scanning: {E}")
                    logger.error(f"Error when scanning: {E}")

            if data in [
                b"3\x00",
                b"3",
                b"3\x00\r\n",
            ]:
                print("--> ------ RESET SIGNAL -------")
                logger.info("--> ------ RESET SIGNAL -------")

                self.uic.Result_Label.setText("NONE")
                self.uic.Result_Label.setStyleSheet(
                    "background-color: #fff; color: #000"
                )
        else:
            print("Error: Received signal when the camera is not connected")
            print(f"Signal PLC: {data}")

    def handle_data_sfc(self, data):
        if self.THREAD_SFC_RC.is_running:
            print("\n\n")
            print("-----------DATA SFC ---------")
            print(f">>> Received scan signal from SFC: {data}")

            logger.info("\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            logger.info(f">>> Received scan signal from SFC: {data}")
            if data == b"1":
                print(">>> PASS SFC SIGNAL -------")
                logger.info(">>> PASS SFC SIGNAL -------")
                self.uic.Result_Label.setText("PASS SFC")
                self.uic.Result_Label.setStyleSheet(
                    "background-color: #32a852; color: #fff"
                )
            if data == b"2":
                print(">>> FAIL SFC SIGNAL")
                logger.error(">>> FAIL SFC SIGNAL")
                self.uic.Result_Label.setText("ERROR SFC")
                self.uic.Result_Label.setStyleSheet(
                    "background-color: #b84935; color: #fff"
                )
        else:
            print("Error: Received signal when SFC failed connected")

    def handle_data_gun(self, data):
        if self.THREAD_READER.is_running:
            print("\n\n")
            print("-----------DATA GUN ---------")
            print(f">>> Received scan signal from GUN: {data}")
            logger.info("\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            logger.info(f">>> Received scan signal from GUN: {data}")

            print(f">>> Send data gun to SFC: {data}")
            logger.info(f">>> Send data gun to SFC: {data}")
            self.THREAD_SFC_SEND.send_signal_serial_port(data)

        else:
            print("Error: Received signal when the GUN SERIAL is not connected")
            print(f"Signal GUN: {data}")

    def handle_decode_data(self, data_decoded):
        print(f"Decoded data: {data_decoded}")
        logger.info(f"Decoded data: {data_decoded}")
        if data_decoded == "2":
            print(">>> Failed to scan")
            logger.error(">>> Failed to scan")
            # TODO: Send fail data to PLC
            self.THREAD_PLC.send_signal_serial_port(b"2")
            print(f">>> Send data to PLC: 2")
            logger.info(f">>> Send data to PLC: 2")
        else:
            # TODO: send data decode to SFC
            self.THREAD_SFC_SEND.send_signal_serial_port(data_decoded.encode())
            print(f">>> Send data to SFC: {data_decoded}")
            logger.info(f">>> Send data to SFC: {data_decoded}")

    def handle_set_ui(self, data_notify):
        # print("NOTIFY EMIT: ", data_notify)
        type_notify = data_notify[0]
        msg_notify = data_notify[1]

        self.uic.Result_Label.setText(msg_notify)
        if type_notify == "ERROR":
            self.uic.Result_Label.setStyleSheet(
                "background-color: #b84935; color: #fff"
            )
        elif type_notify == "PASS":
            self.uic.Result_Label.setStyleSheet(
                "background-color: #32a852; color: #fff"
            )

    def thread_scan_action(self, progress, data_show, notification, data):
        try:
            if self.frame is not None:
                stop_flag = threading.Event()  # Cờ để dừng luồng còn lại
                counter_lock = threading.Lock()  # Khoá để đảm bảo đếm chính xác
                completed_threads = [0]  # Biến để đếm số luồng đã hoàn thành

                # process image here
                # 480 640
                # frame_crop = self.frame[50:450, 100:500]
                # resized_frame = self.reader._resize_image(frame_crop, 1.5)
                # images_processed = self.reader._process_image(
                #     resized_frame, option=1, ksize_value=3
                # )

                # test
                frame = cv2.imread("./lab/17.png")
                frame_crop = frame[70:350, 120:450]
                resized_frame = self.reader._resize_image(frame_crop, 1.5)
                images_processed = self.reader._process_image(
                    resized_frame, option=1, ksize_value=3
                )
                gray_processed = images_processed[0]

                # Tạo hai luồng giải mã
                pylibdmtx_pool = threading.Thread(
                    target=self.decode_wrapper,
                    args=(
                        self.reader._decode_pylibdmtx,
                        stop_flag,
                        completed_threads,
                        counter_lock,
                        data,
                        notification,
                        images_processed,
                    ),
                )

                zxingcpp_pool = threading.Thread(
                    target=self.decode_wrapper,
                    args=(
                        self.reader._decode_zxingcpp,
                        stop_flag,
                        completed_threads,
                        counter_lock,
                        data,
                        notification,
                        images_processed,
                    ),
                )

                loop_threshold_pool = threading.Thread(
                    target=self.decode_wrapper,
                    args=(
                        lambda img: self.reader._loop_threshold(
                            img, 50, 200, 10
                        ),  # Hàm gọi _loop_threshold
                        stop_flag,
                        completed_threads,
                        counter_lock,
                        data,
                        notification,
                        images_processed,
                    ),
                )

                # Bắt đầu cả hai luồng
                pylibdmtx_pool.start()
                zxingcpp_pool.start()
                # loop_threshold_pool.start()

                # Chờ cả hai luồng hoàn thành
                pylibdmtx_pool.join()
                zxingcpp_pool.join()
                # loop_threshold_pool.join()

        except Exception as e:
            logger.error(f"Error in scan action: {e}")
            return None

    def decode_wrapper(
        self,
        decode_func,
        stop_flag,
        completed_threads,
        counter_lock,
        data,
        notification,
        images_processed,
    ):
        if not stop_flag.is_set():
            data_decoded = None

            for image in images_processed:
                # cv2.imshow("test", resized_frame)
                # cv2.waitKey(1000)
                data_decoded = decode_func(image)
                if data_decoded is not None:
                    break

            # Nếu có kết quả, phát dữ liệu và dừng luồng kia
            if data_decoded and not stop_flag.is_set():
                stop_flag.set()  # Dừng luồng còn lại
                data.emit(data_decoded)  # Gửi kết quả
                notification.emit(("PASS", "PASS SCAN"))
            else:
                with counter_lock:
                    completed_threads[0] += 1  # Tăng biến đếm số luồng đã hoàn thành

                # Nếu cả hai luồng đã hoàn thành và không có kết quả, phát thông báo lỗi
                if completed_threads[0] == 2 and not stop_flag.is_set():
                    stop_flag.set()  # Đảm bảo không có luồng nào tiếp tục sau này
                    if self.SAVE_IMAGE == 1:
                        image_filename = "image_NG/{}/CAMERA1/{}.png".format(
                            get_current_date(), format_current_time()
                        )
                        cv2.imwrite(image_filename, self.frame)
                    notification.emit(("ERROR", "ERROR SCAN"))
                    data.emit("2")

    def handle_update(self, event):
        try:
            subprocess.Popen(
                [self.path_target + "Update.exe"], subprocess.CREATE_NEW_CONSOLE
            )
            logger.info("Open file Update.exe!")
            print("Open file Update.exe!")
        except Exception as e:
            logger.info("Can't Open Update.exe! -- {e}!")
            print(f"Can't Open Update.exe! -- {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApplication()
    sys.exit(app.exec_())
