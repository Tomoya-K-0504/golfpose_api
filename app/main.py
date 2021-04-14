from flask import Flask, render_template, jsonify, request
import estimate_pose

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return jsonify({"success": True}), 200


@app.route('/healthz', methods=['GET'])
def healthz():
    return jsonify({"success": True}), 200


@app.route('/predict', methods=['POST'])
def predict():
    res = estimate_pose.estimate(request.form["file_path"])
    print(res)
    return jsonify({"result": res}), 200


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host="0.0.0.0", debug=True, port=80)
