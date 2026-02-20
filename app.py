import os
import pika
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# FIX 1: Explicitly allow the origin and support credentials if needed
CORS(app, resources={r"/*": {
    "origins": ["https://delightful-grass-0f3dc1c10.1.azurestaticapps.net"],
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

RABBITMQ_URL = os.environ.get('RABBITMQ_URL', 'amqp://admin:123@20.220.228.16:5672/')

@app.route('/products', methods=['GET'])
def get_products():
    # FIX 2: Ensure the RabbitMQ block doesn't hang the request
    # If this takes too long, the browser might time out and trigger a CORS error
    try:
        params = pika.URLParameters(RABBITMQ_URL)
        # Add a short timeout so the web page doesn't wait forever
        params.connection_attempts = 1
        params.retry_delay = 1
        
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue='product_logs')
        channel.basic_publish(exchange='', routing_key='product_logs', body='Product list requested')
        connection.close()
    except Exception as e:
        print(f"RabbitMQ Connection failed: {e}")

    products = [
        {"id": 1, "name": "Dog Food", "price": 19.99},
        {"id": 2, "name": "Cat Food", "price": 34.99},
        {"id": 3, "name": "Bird Seeds", "price": 10.99}
    ]
    return jsonify(products)

if __name__ == '__main__':
    # FIX 3: Azure usually uses port 80 or 8080 by default for Linux containers
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
