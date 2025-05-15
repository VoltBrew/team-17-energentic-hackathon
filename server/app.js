const express = require('express');
const mongoose = require('mongoose');

class Server {
    constructor() {
        this.app = express();
        this.port = 3000; // Define the port for the server
        this.databaseUrl = 'mongodb://localhost:27017/mydatabase'; // Replace 'mydatabase' with your DB name

        this.connectToDatabase();
        this.middlewares();
        this.routes();
    }

    async connectToDatabase() {
        try {
            await mongoose.connect(this.databaseUrl, {
                useNewUrlParser: true,
                useUnifiedTopology: true,
            });
            console.log('Connected to MongoDB database.');
        } catch (error) {
            console.error('Error connecting to database:', error);
            process.exit(1);
        }
    }

    middlewares() {
        this.app.use(express.json()); // Parse incoming JSON requests
    }

    routes() {
        this.app.get('/', (req, res) => {
            res.send('Welcome to the Express server!');
        });

        // Add more routes here
    }

    start() {
        this.app.listen(this.port, () => {
            console.log(`Server is running on http://localhost:${this.port}`);
        });
    }
}

// Initialize and start the server
const server = new Server();
server.start();