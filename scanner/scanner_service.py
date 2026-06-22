from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import os
import base64
import tempfile
import io

app = Flask(__name__)
CORS(app, origins=[
    "https://lightview.win",
    "https://keiko-dev-lcai.github.io",
    "http://localhost:8300",
    "http://127.0.0.1:8300",
    # Railway-hosted frontend (LightView demo)
    "https://web-production-c7177.up.railway.app",
    # GitHub Pages (lightwatch repo)
    "https://keiko-dev-lcai.github.io",
])

NAPS2_CONSOLE = r"C:\Program Files\NAPS2\NAPS2.Console.exe"
PROFILE_NAME  = "HP ENVY 5660 series (USB)"


@app.route('/health')
def health():
    return jsonify({"status": "ok", "service": "LightView Scanner"})


@app.route('/scan')
def scan():
    try:
        from PIL import Image
    except ImportError:
        return jsonify({"error": "Pillow not installed — run: pip install pillow flask flask-cors"}), 500

    temp_path = os.path.join(tempfile.gettempdir(), "lightview_scan.jpg")

    # Remove stale temp file if it exists
    if os.path.exists(temp_path):
        os.remove(temp_path)

    try:
        # ── Try NAPS2 v1 CLI syntax first ──────────────────────────────────────
        result = subprocess.run(
            [NAPS2_CONSOLE, "-p", PROFILE_NAME, "-o", temp_path, "-n", "0"],
            timeout=90,
            capture_output=True,
            text=True,
        )

        # ── Fallback: NAPS2 v2 CLI syntax ──────────────────────────────────────
        if not os.path.exists(temp_path):
            result = subprocess.run(
                [NAPS2_CONSOLE, "scan", "--profile", PROFILE_NAME, "--output", temp_path],
                timeout=90,
                capture_output=True,
                text=True,
            )

        if not os.path.exists(temp_path):
            stderr = getattr(result, "stderr", "")
            return jsonify({
                "error": (
                    "Scan failed — check that NAPS2 is open, the profile "
                    f"'{PROFILE_NAME}' exists, and the printer is on. "
                    f"NAPS2 said: {stderr[:300]}"
                )
            }), 500

        # ── Rotate 90° clockwise (PIL rotate is CCW, so 270° = 90° CW) ────────
        img     = Image.open(temp_path)
        rotated = img.rotate(270, expand=True)

        buf = io.BytesIO()
        rotated.save(buf, format="JPEG", quality=85)
        b64 = base64.b64encode(buf.getvalue()).decode()

        # Clean up temp file
        try:
            os.remove(temp_path)
        except Exception:
            pass

        return jsonify({"image": b64, "mime": "image/jpeg"})

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Scanner timed out after 90 s — is the printer on and ready?"}), 500
    except FileNotFoundError:
        return jsonify({
            "error": (
                f"NAPS2 not found at {NAPS2_CONSOLE}. "
                "Check the path or reinstall NAPS2."
            )
        }), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("=" * 52)
    print("  LightView Scanner Service")
    print("  http://127.0.0.1:8189")
    print("  Press Ctrl+C to stop")
    print("=" * 52)
    app.run(host="127.0.0.1", port=8189, debug=False)
