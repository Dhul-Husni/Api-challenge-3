import os

from app import create_app

# config_name = os.getenv('APP_SETTINGS')
config_name = "development"
app = create_app(config_name)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port)
    # app.run(port=port)




























