const express = require('express');
const mongoose = require('mongoose');

const StrapiProxy = mongoose.model('StrapiProxy', new mongoose.Schema({
    func: String,
    subfunc: String,
    code: String
}));


class Server {
    constructor() {
        this.app = express();
        this.port = 3000; // Define the port for the server
        this.databaseUrl = 'mongodb://localhost:27017/hackathon';

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


        /** All DEG BECKN code is also run through the same concept*/

        this.app.get('/api/dynamic/:func/:subfunc', async (req, res) => {
            const {func, subfunc} = req.params;

            try {
                // Fetch the record from StrapiProxy collection
                const record = await StrapiProxy.findOne({func, subfunc});

                if (!record) {
                    return res.status(404).json({error: 'Record not found'});
                }

                // Execute the code in the context of the application
                const code = record.code;
                if (!code) {
                    return res.status(400).json({error: 'No code found in the record'});
                }

                try {
                    let ress;
                    const result = eval(code); // Use eval (cautiously) to evaluate the code
                    res.json({result: ress});
                } catch (evaluationError) {
                    res.status(500).json({error: 'Error evaluating the code', details: evaluationError.message});
                }
            } catch (error) {
                res.status(500).json({error: 'Internal server error', details: error.message});
            }
        });

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