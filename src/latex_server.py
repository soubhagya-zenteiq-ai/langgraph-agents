"""
HTTP server for LaTeX compilation, running inside the TeXLive Docker container.
Receives LaTeX source code via POST, compiles it using pdflatex, and returns the result.
Manages persistent storage of generated PDF documents in the /latex_outputs directory.
Acts as an isolated, secure wrapper around the TeXLive distribution.
"""
import http.server
import json
import subprocess
import tempfile
import os
import shutil
from datetime import datetime

class LatexHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            code = data.get("code", "")
            
            # Directory for persistent outputs
            PERSISTENT_DIR = "/latex_outputs"
            os.makedirs(PERSISTENT_DIR, exist_ok=True)

            with tempfile.NamedTemporaryFile(suffix=".tex", delete=False, mode="w") as f:
                f.write(code)
                tex_path = f.name
                
            try:
                proc = subprocess.run(
                    ["pdflatex", "-halt-on-error", "-interaction=nonstopmode", "-output-directory=/tmp", tex_path],
                    capture_output=True, text=True, timeout=25, errors="replace"
                )
                
                # Check if PDF was generated and move it to persistent storage
                base_path = tex_path[:-4]
                pdf_path = base_path + ".pdf"
                
                saved_pdf_path = None
                if os.path.exists(pdf_path):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    dest_name = f"doc_{timestamp}.pdf"
                    dest_path = os.path.join(PERSISTENT_DIR, dest_name)
                    shutil.copy(pdf_path, dest_path)
                    saved_pdf_path = dest_name

                response = {
                    "exit_code": proc.returncode,
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                    "pdf_filename": saved_pdf_path
                }
            except subprocess.TimeoutExpired:
                response = {"exit_code": 124, "stdout": "", "stderr": "Compilation timed out after 25 seconds."}
            except Exception as e:
                response = {"exit_code": 500, "stdout": "", "stderr": str(e)}
            finally:
                # Clean up /tmp files
                try: 
                    os.unlink(tex_path)
                    base_path = tex_path[:-4]
                    for ext in [".aux", ".log", ".pdf"]:
                        try: os.unlink(base_path + ext)
                        except: pass
                except: pass
                
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except Exception as err:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(err).encode('utf-8'))

if __name__ == '__main__':
    server_address = ('0.0.0.0', 3000)
    print("Starting LaTeX server on port 3000...")
    httpd = http.server.HTTPServer(server_address, LatexHandler)
    httpd.serve_forever()
