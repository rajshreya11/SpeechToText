CREATE TABLE IF NOT EXISTS transcriptions (
    id SERIAL PRIMARY KEY,
    original_text TEXT NOT NULL,
    language VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO transcriptions (original_text, language)
VALUES
('Hello, how are you?', 'English'),
('Namaste, aap kaise hain?', 'Hindi');

SELECT * FROM transcriptions;

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'transcriptions'
AND column_name = 'created_at';