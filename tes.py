#coding=utf-8
import cv2
import numpy as np
import mvsdk
import time
import platform

class AplikasiKamera(object):
    def __init__(self):
        super(AplikasiKamera, self).__init__()
        self.penyanggaFrame = None
        self.berhenti = False

    def main(self):
        # Menemukan dan menampilkan daftar kamera yang tersedia
        daftarPerangkat = mvsdk.CameraEnumerateDevice()
        jumlahPerangkat = len(daftarPerangkat)
        if jumlahPerangkat < 1:
            print("Tidak ada kamera yang ditemukan!")
            return

        for i, infoPerangkat in enumerate(daftarPerangkat):
            print(f"{i}: {infoPerangkat.GetFriendlyName()} {infoPerangkat.GetPortType()}")
        
        pilihan = 0 if jumlahPerangkat == 1 else int(input("Pilih kamera: "))
        infoPerangkat = daftarPerangkat[pilihan]

        # Membuka kamera yang dipilih
        try:
            hCamera = mvsdk.CameraInit(infoPerangkat, -1, -1)
        except mvsdk.CameraException as e:
            print(f"Gagal menginisialisasi kamera ({e.error_code}): {e.message}")
            return

        # Mendapatkan deskripsi kemampuan kamera
        kemampuanKamera = mvsdk.CameraGetCapability(hCamera)

        # Menentukan apakah kamera hitam putih atau berwarna
        kameraMono = (kemampuanKamera.sIspCapacity.bMonoSensor != 0)

        # Mengatur format output ISP berdasarkan jenis kamera
        if kameraMono:
            mvsdk.CameraSetIspOutFormat(hCamera, mvsdk.CAMERA_MEDIA_TYPE_MONO8)
        else:
            mvsdk.CameraSetIspOutFormat(hCamera, mvsdk.CAMERA_MEDIA_TYPE_BGR8)

        # Mengatur mode kamera menjadi pengambilan gambar terus menerus
        mvsdk.CameraSetTriggerMode(hCamera, 0)

        # Mengatur eksposur manual, waktu eksposur 30ms
        mvsdk.CameraSetAeState(hCamera, 0)
        mvsdk.CameraSetExposureTime(hCamera, 30 * 1000)

        # Memulai pengambilan gambar oleh SDK
        mvsdk.CameraPlay(hCamera)

        # Menghitung ukuran buffer untuk menyimpan data gambar
        ukuranBufferFrame = kemampuanKamera.sResolutionRange.iWidthMax * kemampuanKamera.sResolutionRange.iHeightMax * (1 if kameraMono else 3)

        # Alokasi buffer frame
        self.penyanggaFrame = mvsdk.CameraAlignMalloc(ukuranBufferFrame, 16)

        # Looping untuk menangkap dan menampilkan gambar sampai pengguna menekan tombol apapun
        self.berhenti = False
        while not self.berhenti:
            self.ambil_dan_tampilkan_gambar(hCamera, kameraMono)

        # Menonaktifkan kamera dan membersihkan buffer
        mvsdk.CameraUnInit(hCamera)
        mvsdk.CameraAlignFree(self.penyanggaFrame)

    def ambil_dan_tampilkan_gambar(self, hCamera, kameraMono):
        try:
            # Mengambil gambar dari kamera
            pRawData, FrameHead = mvsdk.CameraGetImageBuffer(hCamera, 200)
            mvsdk.CameraImageProcess(hCamera, pRawData, self.penyanggaFrame, FrameHead)
            mvsdk.CameraReleaseImageBuffer(hCamera, pRawData)

            # Membalik buffer frame jika di Windows
            if platform.system() == "Windows":
                mvsdk.CameraFlipFrameBuffer(self.penyanggaFrame, FrameHead, 1)

            # Konversi buffer frame menjadi format gambar OpenCV
            dataFrame = (mvsdk.c_ubyte * FrameHead.uBytes).from_address(self.penyanggaFrame)
            frame = np.frombuffer(dataFrame, dtype=np.uint8)
            frame = frame.reshape((FrameHead.iHeight, FrameHead.iWidth, 1 if kameraMono else 3))

            # Resize gambar untuk ditampilkan
            frame = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_LINEAR)

            # Tampilkan gambar menggunakan OpenCV
            cv2.imshow("Tekan sembarang tombol untuk keluar", frame)

            # Periksa jika tombol ditekan untuk keluar dari loop
            if cv2.waitKey(1) != -1:
                self.berhenti = True

        except mvsdk.CameraException as e:
            if e.error_code != mvsdk.CAMERA_STATUS_TIME_OUT:
                print(f"CameraGetImageBuffer gagal ({e.error_code}): {e.message}")

def main():
    try:
        aplikasi = AplikasiKamera()
        aplikasi.main()
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
