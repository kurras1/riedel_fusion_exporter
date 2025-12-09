from flask import Flask
import get_fusion_datum

script_name = "get_fusion_datum.py"

app = Flask(__name__)

@app.route('/fusions')
def get_data():
    data = get_fusion_datum.getPrometheusData()
    #return f"<html><head><meta name=\"color-scheme\" content=\"light dark\"></head><body><pre style=\"word-wrap: break-word; white-space: pre-wrap;\">{data}</pre></body></html>"
    return data

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')