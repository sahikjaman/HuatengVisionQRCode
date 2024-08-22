import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
import mvsdk
import platform

class AplikasiQRScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Scanner - Kamera Industri")
        self.root.geometry("1200x800")

        # Inisialisasi kamera industri
        self.camera_initialized = False
        self.init_camera()

        # Panel pengaturan kamera
        self.frame_settings = ttk.LabelFrame(root, text="Pengaturan Kamera")
        self.frame_settings.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self.create_settings_panel()

        # Panel tampilan kamera
        self.frame_display = ttk.LabelFrame(root, text="Tampilan Kamera")
        self.frame_display.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.canvas = tk.Canvas(self.frame_display, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Panel hasil inspeksi
        self.frame_results = ttk.LabelFrame(root, text="Hasil Pembacaan QR Code")
        self.frame_results.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        self.label_result = ttk.Label(self.frame_results, text="QR Code: ")
        self.label_result.pack(padx=10, pady=5)

        # Mulai update frame kamera
        self.update_frame()

    def init_camera(self):
        # Menemukan dan menampilkan daftar kamera yang tersedia
        daftarPerangkat = mvsdk.CameraEnumerateDevice()
        jumlahPerangkat = len(daftarPerangkat)
        if jumlahPerangkat < 1:
            print("Tidak ada kamera yang ditemukan!")
            return

        # Membuka kamera yang dipilih
        infoPerangkat = daftarPerangkat[0]
        try:
            self.hCamera = mvsdk.CameraInit(infoPerangkat, -1, -1)
            self.camera_initialized = True
        except mvsdk.CameraException as e:
            print(f"Gagal menginisialisasi kamera ({e.error_code}): {e.message}")
            return

        # Mendapatkan deskripsi kemampuan kamera
        kemampuanKamera = mvsdk.CameraGetCapability(self.hCamera)

        # Menentukan apakah kamera hitam putih atau berwarna
        self.kameraMono = (kemampuanKamera.sIspCapacity.bMonoSensor != 0)

        # Mengatur format output ISP berdasarkan jenis kamera
        if self.kameraMono:
            mvsdk.CameraSetIspOutFormat(self.hCamera, mvsdk.CAMERA_MEDIA_TYPE_MONO8)
        else:
            mvsdk.CameraSetIspOutFormat(self.hCamera, mvsdk.CAMERA_MEDIA_TYPE_BGR8)

        # Mengatur mode kamera menjadi pengambilan gambar terus menerus
        mvsdk.CameraSetTriggerMode(self.hCamera, 0)

        # Mengatur eksposur manual, waktu eksposur 30ms
        mvsdk.CameraSetAeState(self.hCamera, 0)
        mvsdk.CameraSetExposureTime(self.hCamera, 30 * 1000)

        # Memulai pengambilan gambar oleh SDK
        mvsdk.CameraPlay(self.hCamera)

        # Menghitung ukuran buffer untuk menyimpan data gambar
        ukuranBufferFrame = kemampuanKamera.sResolutionRange.iWidthMax * kemampuanKamera.sResolutionRange.iHeightMax * (1 if self.kameraMono else 3)
        self.penyanggaFrame = mvsdk.CameraAlignMalloc(ukuranBufferFrame, 16)

    def create_settings_panel(self):
        ttk.Label(self.frame_settings, text="Kecepatan Rana:").pack(padx=10, pady=5)
        self.shutter_speed = ttk.Scale(self.frame_settings, from_=1, to=100, command=self.update_shutter_speed)
        self.shutter_speed.pack(fill=tk.X, padx=10, pady=5)

    def update_shutter_speed(self, value):
        if self.camera_initialized:
            exposure_time = int(float(value) * 1000)
            mvsdk.CameraSetExposureTime(self.hCamera, exposure_time)

    def update_frame(self):
        if not self.camera_initialized:
            return
        
        try:
            # Mengambil gambar dari kamera
            pRawData, FrameHead = mvsdk.CameraGetImageBuffer(self.hCamera, 200)
            mvsdk.CameraImageProcess(self.hCamera, pRawData, self.penyanggaFrame, FrameHead)
            mvsdk.CameraReleaseImageBuffer(self.hCamera, pRawData)

            # Membalik buffer frame jika di Windows
            if platform.system() == "Windows":
                mvsdk.CameraFlipFrameBuffer(self.penyanggaFrame, FrameHead, 1)

            # Konversi buffer frame menjadi format gambar OpenCV
            dataFrame = (mvsdk.c_ubyte * FrameHead.uBytes).from_address(self.penyanggaFrame)
            frame = np.frombuffer(dataFrame, dtype=np.uint8)
            frame = frame.reshape((FrameHead.iHeight, FrameHead.iWidth, 1 if self.kameraMono else 3))

            # Resize gambar untuk ditampilkan
            frame = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_LINEAR)

            # Tampilkan gambar menggunakan Tkinter
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            img_tk = ImageTk.PhotoImage(image=img_pil)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
            self.canvas.image = img_tk

            # Pembacaan QR Code
            decoded_objects = cv2.QRCodeDetector().detectAndDecode(frame)
            if decoded_objects[0]:
                self.label_result.config(text=f"QR Code: {decoded_objects[0]}")

        except mvsdk.CameraException as e:
            if e.error_code != mvsdk.CAMERA_STATUS_TIME_OUT:
                print(f"CameraGetImageBuffer gagal ({e.error_code}): {e.message}")

        self.root.after(10, self.update_frame)

    def on_closing(self):
        if self.camera_initialized:
            mvsdk.CameraUnInit(self.hCamera)
            mvsdk.CameraAlignFree(self.penyanggaFrame)
        self.root.destroy()

def main():
    root = tk.Tk()
    app = AplikasiQRScanner(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
