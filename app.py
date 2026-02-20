import os
import pika
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://delightful-grass-0f3dc1c10.1.azurestaticapps.net"}})

# Use your VM's public IP and the admin credentials you set up earlier
RABBITMQ_URL = os.environ.get('RABBITMQ_URL', 'amqp://admin:123@20.220.228.16:5672/')

@app.route('/products', methods=['GET'])
def get_products():
    try:
        # Connect to RabbitMQ on your VM to log the request
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue='product_logs')
        channel.basic_publish(exchange='', routing_key='product_logs', body='Product list requested')
        connection.close()
    except Exception as e:
        print(f"RabbitMQ Connection failed: {e}")

    # The exact same product data from your original service
    products = [
        {"id": 1, "name": "Dog Food", "price": 19.99},
        {"id": 2, "name": "Cat Food", "price": 34.99},
        {"id": 3, "name": "Bird Seeds", "price": 10.99}
    ]
    return jsonify(products)

if __name__ == '__main__':
    # Azure uses the PORT environment variable to route traffic
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
