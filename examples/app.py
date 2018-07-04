"""
NB: This example requires Flask to run.
"""
from flask import Flask, jsonify, request
import logging
import b3
from b3 import span


app = Flask("test")

# Before and after request to process B3 values and log span boundaries
app.before_request(lambda: b3.start_span(request.headers))
app.after_request(b3.end_span)

# Set up logging to display trace information
log = logging.getLogger(__name__)


@app.route("/")
def default():
    log.warning("Starting with b3 values: {}".format(b3.values()))

    with b3.SubSpan() as headers:
        # Pretend to call a downstream service in the sub-span
        log.warning("Calling downstream service with b3 values: {}".format(b3.values()))

    log.warning("Finishing with b3 values: {}".format(b3.values()))

    return jsonify(b3.values())


@app.route("/using-decorator")
@span
def decorated():
    log.warning("Using decorator: {}".format(b3.values()))
    return jsonify(b3.values())


app.run(debug=True)
