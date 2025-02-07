from flask import Flask
from routes import directory, settings, api, error_handlers,terminal,userTerminal


# Create Flask app
app = Flask(__name__)

# Register blueprints
app.register_blueprint(directory.bp)
app.register_blueprint(settings.bp)
app.register_blueprint(api.bp)
app.register_blueprint(error_handlers.bp)
app.register_blueprint(terminal.bp)
app.register_blueprint(userTerminal.bp)

if __name__ == "__main__":
    app.run(debug=True)
    
    
    
    

    