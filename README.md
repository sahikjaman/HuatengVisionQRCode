# HuatengVision
# HuatengVisionQRCode

A lightweight Python project for reading QR codes using Huateng (MVS) cameras and computer vision. This repository contains utility code to connect to MVS-compatible cameras, capture frames, and decode QR codes from image frames. It is suitable as a starting point for embedded vision, production line scanning, or desktop QR-code-reading utilities.

Highlights
- Uses MVS / Huateng camera SDK integration (mvsdk.py) for camera capture.
- Provides QR-code decoding utilities (qrcodereader.py).
- Includes a test/demo script (tes.py) to quickly try the functionality.

Contents
- mvsdk.py — Camera SDK wrapper and capture helpers for Huateng/MVS devices.
- qrcodereader.py — QR code decoding logic and helpers for processing frames.
- tes.py — Demo script showing how to run a quick live/read test.
- README.md — This document.

Requirements
- Python 3.8+
- OpenCV (opencv-python)
- NumPy
- A QR-code decoding backend such as:
  - pyzbar (recommended) or
  - pylibdmtx / zxing (alternative)
- If using Huateng MVS cameras, the appropriate MVS SDK / drivers available for your platform.

Install (recommended)
1. Clone the repo:
   ```bash
   git clone https://github.com/sahikjaman/HuatengVisionQRCode.git
   cd HuatengVisionQRCode
   ```

2. Install the common Python dependencies:
   ```bash
   python -m pip install --upgrade pip
   pip install opencv-python numpy pyzbar pillow
   ```

   If you plan to use an alternate decoder, install it instead of or in addition to pyzbar:
   - pip install pylibdmtx
   - pip install zxing

3. Install and configure the Huateng/MVS SDK and drivers for your platform per the vendor instructions (if you plan to use mvsdk.py to access hardware cameras).

Quick start / Demo
- Using the included demo (assumes the demo script is configured for your camera):
  ```bash
  python tes.py
  ```
  This should start the demo which captures frames from the configured camera and prints decoded QR-code contents to stdout.

Programmatic usage (example)
- The repository provides utilities to decode frames. A simple OpenCV-based usage:
  ```python
  import cv2
  from qrcodereader import decode_qr_from_frame

  cap = cv2.VideoCapture(0)  # or capture from mvsdk wrapper
  while True:
      ret, frame = cap.read()
      if not ret:
          break
      results = decode_qr_from_frame(frame)  # see qrcodereader.py for function/class name
      for res in results:
          print("Decoded:", res.data, "Type:", res.type)
      cv2.imshow("frame", frame)
      if cv2.waitKey(1) & 0xFF == ord('q'):
          break
  cap.release()
  cv2.destroyAllWindows()
  ```
  Note: The exact function/class names are defined in qrcodereader.py — please refer to the source for available APIs and signatures.

Configuration
- mvsdk.py may require vendor-specific initialisation (device index, IP address, or USB selection). Review and adapt the configuration in tes.py to match your environment and camera model.

Testing and debugging
- If you encounter issues:
  - Verify camera connectivity using vendor tools or simple OpenCV VideoCapture for a conventional camera.
  - Ensure the MVS SDK and drivers are installed and accessible to Python (environment variables / library path).
  - Enable logging/print statements in tes.py and mvsdk.py to inspect device enumeration and frame capture.
  - Try decoding static images with qrcodereader on images you know contain QR codes to isolate whether the problem is capture or decoding.

Contributing
- Contributions, bug reports, and pull requests are welcome.
- To contribute:
  1. Fork the repository.
  2. Create a branch for your change.
  3. Add tests or a demo change where applicable.
  4. Open a pull request with a clear description of the change.

Suggested next improvements
- Add a requirements.txt or pyproject.toml for reproducible installs.
- Expand tes.py to include CLI arguments and better device auto-detection.
- Add unit tests for QR decoding functions and a small sample image dataset.
- Provide example configuration for common Huateng camera models.

License
- No license file is present in the repository. Add an appropriate open-source license (e.g., MIT, Apache-2.0) if you intend to publish the project publicly.

Contact
- Maintainer: sahikjaman (GitHub)
- For questions or support, open an issue in this repository.

See the source files (qrcodereader.py, mvsdk.py, tes.py) for implementation details and the exact function/class names to use in your application.
